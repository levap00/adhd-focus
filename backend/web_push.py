import asyncio
import json
import os
from datetime import date, datetime, time as dt_time, timedelta
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo

from fastapi import FastAPI

from backend.accounts import PROJECT_ROOT
from backend.db import get_db
from backend.utils import normalize_due_time, utc_now_iso


WEB_PUSH_SCHEDULE_ENABLED = str(os.getenv("WEB_PUSH_SCHEDULE_ENABLED", "1")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
WEB_PUSH_SCHEDULE_GRACE_MINUTES = max(1, int(os.getenv("WEB_PUSH_SCHEDULE_GRACE_MINUTES", "10")))
WEB_PUSH_MEDICATION_REPEAT_WINDOW_HOURS = min(
    24,
    max(1, int(os.getenv("WEB_PUSH_MEDICATION_REPEAT_WINDOW_HOURS", "12"))),
)
WEB_PUSH_DEFAULT_TIMEZONE = os.getenv("WEB_PUSH_DEFAULT_TIMEZONE", "Europe/Warsaw").strip() or "Europe/Warsaw"
VAPID_SUBJECT = os.getenv("VAPID_SUBJECT", "mailto:admin@example.com").strip() or "mailto:admin@example.com"

_scheduler_task: Optional[asyncio.Task] = None


def get_vapid_public_key() -> str:
    # Replace VAPID_PUBLIC_KEY in .env with the public key generated for this app.
    return os.getenv("VAPID_PUBLIC_KEY", "").strip()


def _resolve_private_key_path(raw_path: str) -> str:
    path = Path(raw_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return str(path.resolve())


def get_vapid_private_key() -> str:
    # Set either VAPID_PRIVATE_KEY_FILE to a PEM path or VAPID_PRIVATE_KEY to the PEM body.
    private_key_file = os.getenv("VAPID_PRIVATE_KEY_FILE", "").strip()
    if private_key_file:
        return _resolve_private_key_path(private_key_file)
    return os.getenv("VAPID_PRIVATE_KEY", "").strip().replace("\\n", "\n")


def is_web_push_configured() -> bool:
    return bool(get_vapid_public_key() and get_vapid_private_key() and VAPID_SUBJECT)


def _subscription_from_row(row) -> dict[str, Any]:
    return {
        "endpoint": row["endpoint"],
        "keys": {
            "p256dh": row["p256dh"],
            "auth": row["auth"],
        },
    }


def send_web_push(subscription_info: dict[str, Any], payload: dict[str, Any]) -> None:
    if not is_web_push_configured():
        raise RuntimeError("Brak konfiguracji VAPID dla Web Push.")

    try:
        from pywebpush import webpush
    except ImportError as exc:
        raise RuntimeError("Brakuje biblioteki pywebpush. Uruchom: pip install -r requirements.txt") from exc

    webpush(
        subscription_info=subscription_info,
        data=json.dumps(payload, ensure_ascii=False),
        vapid_private_key=get_vapid_private_key(),
        vapid_claims={"sub": VAPID_SUBJECT},
    )


def send_notification_to_user(user_id: int, payload: dict[str, Any]) -> dict[str, int]:
    sent = 0
    failed = 0
    inactive = 0
    now = utc_now_iso()

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, endpoint, p256dh, auth
            FROM push_subscriptions
            WHERE owner_user_id = ? AND active = 1
            ORDER BY updated_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()

        for row in rows:
            try:
                send_web_push(_subscription_from_row(row), payload)
                conn.execute(
                    """
                    UPDATE push_subscriptions
                    SET last_success_at = ?, last_error = '', updated_at = ?
                    WHERE id = ?
                    """,
                    (now, now, row["id"]),
                )
                sent += 1
            except Exception as exc:
                failed += 1
                status_code = getattr(getattr(exc, "response", None), "status_code", None)
                deactivate = status_code in {404, 410}
                if deactivate:
                    inactive += 1
                conn.execute(
                    """
                    UPDATE push_subscriptions
                    SET active = ?, last_error = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (0 if deactivate else 1, str(exc)[:500], now, row["id"]),
                )
        conn.commit()

    return {"sent": sent, "failed": failed, "inactive": inactive}


def _settings_from_row(row) -> dict[str, Any]:
    return {
        "enabled": bool(row["enabled"]),
        "opening_enabled": bool(row["opening_enabled"]),
        "opening_time": normalize_due_time(row["opening_time"], "08:00") or "08:00",
        "day_summary_enabled": bool(row["day_summary_enabled"]),
        "day_summary_time": normalize_due_time(row["day_summary_time"], "20:30") or "20:30",
        "medication_enabled": bool(row["medication_enabled"]),
        "medication_repeat_minutes": max(1, int(row["medication_repeat_minutes"] or 5)),
        "task_reminder_enabled": bool(row["task_reminder_enabled"]),
        "task_reminder_repeat_minutes": max(15, int(row["task_reminder_repeat_minutes"] or 120)),
        "timezone": (row["timezone"] or WEB_PUSH_DEFAULT_TIMEZONE).strip() or WEB_PUSH_DEFAULT_TIMEZONE,
    }


def _get_tz(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except Exception:
        return ZoneInfo(WEB_PUSH_DEFAULT_TIMEZONE)


def _parse_schedule_time(raw: str, fallback: str) -> dt_time:
    clean = normalize_due_time(raw, fallback) or fallback
    return datetime.strptime(clean, "%H:%M").time()


def _is_time_due(now: datetime, raw_time: str, fallback: str) -> bool:
    planned_time = _parse_schedule_time(raw_time, fallback)
    scheduled_at = datetime.combine(now.date(), planned_time, tzinfo=now.tzinfo)
    return scheduled_at <= now <= scheduled_at + timedelta(minutes=WEB_PUSH_SCHEDULE_GRACE_MINUTES)


def _user_has_active_subscription(conn, user_id: int) -> bool:
    row = conn.execute(
        "SELECT 1 FROM push_subscriptions WHERE owner_user_id = ? AND active = 1 LIMIT 1",
        (user_id,),
    ).fetchone()
    return bool(row)


def _claim_marker(conn, user_id: int, marker_key: str) -> bool:
    cursor = conn.execute(
        """
        INSERT INTO notification_delivery_markers (owner_user_id, marker_key, created_at)
        VALUES (?, ?, ?)
        ON CONFLICT(owner_user_id, marker_key) DO NOTHING
        """,
        (user_id, marker_key, utc_now_iso()),
    )
    conn.commit()
    return cursor.rowcount > 0


def _release_marker(conn, user_id: int, marker_key: str) -> None:
    conn.execute(
        "DELETE FROM notification_delivery_markers WHERE owner_user_id = ? AND marker_key = ?",
        (user_id, marker_key),
    )
    conn.commit()


def _send_scheduled_notification(conn, user_id: int, payload: dict[str, Any], marker_key: str) -> None:
    result = send_notification_to_user(user_id, payload)
    if int(result.get("sent") or 0) <= 0:
        _release_marker(conn, user_id, marker_key)


def _parse_date(raw: str) -> Optional[date]:
    try:
        return datetime.strptime((raw or "").strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _open_task_rows(conn, user_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT t.id, t.name, t.status, t.priority, t.due_date, t.due_time, m.name AS module_name
        FROM tasks t
        LEFT JOIN modules m ON m.id = t.module_id
        WHERE t.status != 'gotowe'
          AND (
            t.owner_user_id = ?
            OR EXISTS (
                SELECT 1
                FROM task_shares s
                WHERE s.task_id = t.id
                  AND s.shared_user_id = ?
            )
          )
        """,
        (user_id, user_id),
    ).fetchall()
    return [dict(row) for row in rows]


def _task_due_at(task: dict[str, Any], tz: ZoneInfo) -> Optional[datetime]:
    due_day = _parse_date(task.get("due_date", ""))
    if not due_day:
        return None
    due_time = _parse_schedule_time(task.get("due_time", ""), "23:59")
    return datetime.combine(due_day, due_time, tzinfo=tz)


def _sort_tasks(tasks: list[dict[str, Any]], tz: ZoneInfo) -> list[dict[str, Any]]:
    priority_rank = {"P1": 0, "P2": 1, "P3": 2}

    def sort_key(task: dict[str, Any]):
        due_at = _task_due_at(task, tz)
        return (
            due_at.timestamp() if due_at else float("inf"),
            priority_rank.get((task.get("priority") or "").strip().upper(), 4),
            (task.get("name") or "").lower(),
        )

    return sorted(tasks, key=sort_key)


def _format_task_names(tasks: list[dict[str, Any]], limit: int = 3) -> str:
    names = [(task.get("name") or "bez nazwy").strip() for task in tasks[:limit]]
    if not names:
        return "Brak pilnych rzeczy."
    suffix = f" +{len(tasks) - limit}" if len(tasks) > limit else ""
    return ", ".join(names) + suffix


def _count_done_today(conn, user_id: int, today_key: str) -> int:
    marker = f"[Done: {today_key}]"
    row = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM tasks t
        WHERE t.status = 'gotowe'
          AND t.description LIKE ?
          AND (
            t.owner_user_id = ?
            OR EXISTS (
                SELECT 1
                FROM task_shares s
                WHERE s.task_id = t.id
                  AND s.shared_user_id = ?
            )
          )
        """,
        (f"%{marker}%", user_id, user_id),
    ).fetchone()
    return int(row["total"] if row else 0)


def _is_medication_scheduled(schedule_type: str, day: date) -> bool:
    normalized = (schedule_type or "daily").strip().lower()
    if normalized == "weekdays":
        return day.isoweekday() <= 5
    return True


def _medications_for_date(conn, user_id: int, day: date) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT
            mr.id,
            mr.name,
            mr.schedule_type,
            mr.reminder_time,
            COALESCE(ms.done, 0) AS done
        FROM medication_reminders mr
        LEFT JOIN medication_states ms
            ON ms.medication_id = mr.id
           AND ms.date_key = ?
        WHERE mr.active = 1
          AND mr.owner_user_id = ?
        ORDER BY mr.reminder_time ASC, mr.name COLLATE NOCASE ASC
        """,
        (day.isoformat(), user_id),
    ).fetchall()
    medications = []
    for row in rows:
        if not _is_medication_scheduled(row["schedule_type"], day):
            continue
        item = dict(row)
        item["date_key"] = day.isoformat()
        medications.append(item)
    return medications


def _push_payload(title: str, body: str, tag: str, url: str = "/") -> dict[str, Any]:
    return {
        "title": title,
        "body": body,
        "tag": tag,
        "url": url,
        "icon": "/static/apple-touch-icon.png",
        "badge": "/static/apple-touch-icon.png",
    }


def _process_opening(conn, user_id: int, settings: dict[str, Any], now: datetime, tz: ZoneInfo) -> None:
    if not settings["opening_enabled"] or not _is_time_due(now, settings["opening_time"], "08:00"):
        return
    marker = f"webpush:opening:{now.date().isoformat()}:{settings['opening_time']}"
    if not _claim_marker(conn, user_id, marker):
        return

    open_tasks = _sort_tasks(_open_task_rows(conn, user_id), tz)
    today_tasks = [task for task in open_tasks if _parse_date(task.get("due_date", "")) == now.date()]
    overdue = [task for task in open_tasks if (_parse_date(task.get("due_date", "")) or now.date()) < now.date()]
    body = f"Dzis: {len(today_tasks)}. Po terminie: {len(overdue)}. Start: {_format_task_names(today_tasks or overdue or open_tasks)}"
    _send_scheduled_notification(conn, user_id, _push_payload("Start dnia", body, marker, "/"), marker)


def _process_day_summary(conn, user_id: int, settings: dict[str, Any], now: datetime, tz: ZoneInfo) -> None:
    if not settings["day_summary_enabled"] or not _is_time_due(now, settings["day_summary_time"], "20:30"):
        return
    marker = f"webpush:summary:{now.date().isoformat()}:{settings['day_summary_time']}"
    if not _claim_marker(conn, user_id, marker):
        return

    open_tasks = _sort_tasks(_open_task_rows(conn, user_id), tz)
    done_today = _count_done_today(conn, user_id, now.date().isoformat())
    meds = _medications_for_date(conn, user_id, now.date())
    meds_open = len([item for item in meds if int(item.get("done") or 0) == 0])
    body = f"Zrobione: {done_today}. Otwarte: {len(open_tasks)}. Leki do odhaczenia: {meds_open}."
    _send_scheduled_notification(conn, user_id, _push_payload("Podsumowanie dnia", body, marker, "/"), marker)


def _process_medications(conn, user_id: int, settings: dict[str, Any], now: datetime) -> None:
    if not settings["medication_enabled"]:
        return

    repeat_seconds = max(1, int(settings["medication_repeat_minutes"])) * 60
    repeat_window = timedelta(hours=WEB_PUSH_MEDICATION_REPEAT_WINDOW_HOURS)
    dose_days = [now.date(), now.date() - timedelta(days=1)]
    for dose_day in dose_days:
        for medication in _medications_for_date(conn, user_id, dose_day):
            if int(medication.get("done") or 0) == 1:
                continue
            reminder_time = _parse_schedule_time(medication.get("reminder_time", ""), "08:00")
            scheduled_at = datetime.combine(dose_day, reminder_time, tzinfo=now.tzinfo)
            delay = now - scheduled_at
            if delay.total_seconds() < 0 or delay > repeat_window:
                continue

            dose_key = dose_day.isoformat()
            bucket = int(delay.total_seconds() // repeat_seconds)
            marker = f"webpush:med:{medication['id']}:{dose_key}:{bucket}"
            if not _claim_marker(conn, user_id, marker):
                continue
            body = f"{medication.get('name') or 'Lek'} czeka od {dose_key} {reminder_time.strftime('%H:%M')}."
            url = f"/?view=meds&med_date={dose_key}"
            _send_scheduled_notification(conn, user_id, _push_payload("Lek do odhaczenia", body, marker, url), marker)


def _process_task_reminders(conn, user_id: int, settings: dict[str, Any], now: datetime, tz: ZoneInfo) -> None:
    if not settings["task_reminder_enabled"]:
        return

    open_tasks = _sort_tasks(_open_task_rows(conn, user_id), tz)
    due_tasks = [task for task in open_tasks if (_task_due_at(task, tz) and _task_due_at(task, tz) <= now)]
    if not due_tasks:
        return

    repeat_seconds = max(15, int(settings["task_reminder_repeat_minutes"])) * 60
    bucket = int(now.timestamp() // repeat_seconds)
    marker = f"webpush:tasks:{now.date().isoformat()}:{bucket}"
    if not _claim_marker(conn, user_id, marker):
        return

    body = f"Do ogarniecia: {len(due_tasks)}. Najpierw: {_format_task_names(due_tasks)}"
    _send_scheduled_notification(conn, user_id, _push_payload("Przypomnienie fokusowe", body, marker, "/"), marker)


def process_scheduled_web_push_notifications() -> None:
    if not WEB_PUSH_SCHEDULE_ENABLED or not is_web_push_configured():
        return

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT
                u.id AS user_id,
                COALESCE(ns.enabled, 1) AS enabled,
                COALESCE(ns.opening_enabled, 1) AS opening_enabled,
                COALESCE(ns.opening_time, '08:00') AS opening_time,
                COALESCE(ns.day_summary_enabled, 1) AS day_summary_enabled,
                COALESCE(ns.day_summary_time, '20:30') AS day_summary_time,
                COALESCE(ns.medication_enabled, 1) AS medication_enabled,
                COALESCE(ns.medication_repeat_minutes, 5) AS medication_repeat_minutes,
                COALESCE(ns.task_reminder_enabled, 1) AS task_reminder_enabled,
                COALESCE(ns.task_reminder_repeat_minutes, 120) AS task_reminder_repeat_minutes,
                COALESCE(ns.timezone, ?) AS timezone
            FROM users u
            LEFT JOIN notification_settings ns ON ns.owner_user_id = u.id
            """,
            (WEB_PUSH_DEFAULT_TIMEZONE,),
        ).fetchall()

        for row in rows:
            user_id = int(row["user_id"])
            settings = _settings_from_row(row)
            if not settings["enabled"] or not _user_has_active_subscription(conn, user_id):
                continue
            tz = _get_tz(settings["timezone"])
            now = datetime.now(tz)
            _process_opening(conn, user_id, settings, now, tz)
            _process_day_summary(conn, user_id, settings, now, tz)
            _process_medications(conn, user_id, settings, now)
            _process_task_reminders(conn, user_id, settings, now, tz)


async def _scheduler_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(process_scheduled_web_push_notifications)
        except Exception:
            # The scheduler must survive transient network, DB, and push-service errors.
            pass
        await asyncio.sleep(30)


def register_web_push_scheduler(app: FastAPI) -> None:
    @app.on_event("startup")
    async def _start_web_push_scheduler() -> None:
        global _scheduler_task
        if not WEB_PUSH_SCHEDULE_ENABLED:
            return
        if _scheduler_task is None or _scheduler_task.done():
            _scheduler_task = asyncio.create_task(_scheduler_loop(), name="web-push-scheduler")

    @app.on_event("shutdown")
    async def _stop_web_push_scheduler() -> None:
        global _scheduler_task
        if _scheduler_task is None:
            return
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
        _scheduler_task = None
