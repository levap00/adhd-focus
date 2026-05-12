import asyncio
import os
from datetime import date, datetime, time as dt_time, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

import requests
from fastapi import FastAPI

from backend.db import get_db
from backend.utils import utc_now_iso

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
TELEGRAM_ENABLED = str(os.getenv("TELEGRAM_ENABLED", "1")).strip().lower() in {"1", "true", "yes", "on"}
TELEGRAM_SCHEDULE_ENABLED = str(os.getenv("TELEGRAM_SCHEDULE_ENABLED", "1")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
TELEGRAM_TIMEZONE = os.getenv("TELEGRAM_TIMEZONE", "Europe/Warsaw").strip() or "Europe/Warsaw"

_SCHEDULED_EVENTS = [
    ("08:00", "morning"),
    ("16:00", "day_summary"),
    ("19:00", "remaining"),
    ("22:48", "remaining"),
]

_scheduler_task: Optional[asyncio.Task] = None


def _is_configured() -> bool:
    return TELEGRAM_ENABLED and bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)


def _get_tz() -> ZoneInfo:
    try:
        return ZoneInfo(TELEGRAM_TIMEZONE)
    except Exception:
        return ZoneInfo("UTC")


def _parse_due_date(raw: str) -> Optional[date]:
    value = (raw or "").strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_due_time(raw: str, fallback: str = "14:00") -> Optional[dt_time]:
    value = (raw or fallback or "").strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        return None


def _task_due_datetime(task: dict, tz: ZoneInfo) -> Optional[datetime]:
    due_day = _parse_due_date(task.get("due_date", ""))
    if not due_day:
        return None
    due_time = _parse_due_time(task.get("due_time", ""), fallback="14:00") or dt_time(14, 0)
    return datetime.combine(due_day, due_time, tzinfo=tz)


def _priority_rank(priority: str) -> int:
    normalized = (priority or "").strip().upper()
    return {"P1": 0, "P2": 1, "P3": 2}.get(normalized, 3)


def _sorted_open_tasks(open_tasks: list[dict], tz: ZoneInfo) -> list[dict]:
    def _sort_key(task: dict):
        due_at = _task_due_datetime(task, tz)
        due_value = due_at.timestamp() if due_at else float("inf")
        return (due_value, _priority_rank(task.get("priority", "")), (task.get("name") or "").lower())

    return sorted(open_tasks, key=_sort_key)


def _format_task_line(task: dict) -> str:
    module_name = (task.get("module_name") or "?").strip() or "?"
    due_date = (task.get("due_date") or "").strip()
    due_time = (task.get("due_time") or "").strip()
    due_label = "bez terminu"
    if due_date:
        due_label = f"{due_date} {due_time or '14:00'}"
    return f"- {task.get('name', 'bez nazwy')} [{module_name}] ({due_label})"


def _truncate_task_lines(tasks: list[dict], limit: int = 6) -> str:
    if not tasks:
        return "- brak"
    lines = [_format_task_line(task) for task in tasks[:limit]]
    if len(tasks) > limit:
        lines.append(f"- ... +{len(tasks) - limit} kolejnych")
    return "\n".join(lines)


def _load_open_tasks() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT t.id, t.name, t.status, t.priority, t.due_date, t.due_time, m.name AS module_name
            FROM tasks t
            LEFT JOIN modules m ON m.id = t.module_id
            WHERE t.status != 'gotowe'
            """
        ).fetchall()
    return [dict(row) for row in rows]


def _count_done_today(today_key: str) -> int:
    marker = f"[Done: {today_key}]"
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total FROM tasks WHERE status = 'gotowe' AND description LIKE ?",
            (f"%{marker}%",),
        ).fetchone()
    return int(row["total"] if row else 0)


def _overdue_tasks(open_tasks: list[dict], today: date) -> list[dict]:
    overdue = []
    for task in open_tasks:
        due_day = _parse_due_date(task.get("due_date", ""))
        if due_day and due_day < today:
            overdue.append(task)
    return overdue


def _today_tasks(open_tasks: list[dict], today: date) -> list[dict]:
    return [task for task in open_tasks if _parse_due_date(task.get("due_date", "")) == today]


def _tomorrow_tasks(open_tasks: list[dict], today: date) -> list[dict]:
    tomorrow = today + timedelta(days=1)
    return [task for task in open_tasks if _parse_due_date(task.get("due_date", "")) == tomorrow]


def _is_medication_scheduled(schedule_type: str, day: date) -> bool:
    normalized = (schedule_type or "daily").strip().lower()
    if normalized == "weekdays":
        return day.isoweekday() <= 5
    return True


def _load_medication_reminders_for_date(day: date) -> list[dict]:
    day_key = day.isoformat()
    with get_db() as conn:
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
            ORDER BY mr.reminder_time ASC, mr.name COLLATE NOCASE ASC
            """,
            (day_key,),
        ).fetchall()

    return [dict(row) for row in rows if _is_medication_scheduled(row["schedule_type"], day)]


def _build_medication_message(medication: dict, now: datetime) -> str:
    return (
        f"Lek do odhaczenia: {medication.get('name') or 'bez nazwy'}\n"
        f"Godzina: {(medication.get('reminder_time') or '08:00').strip()}\n"
        f"Dzien: {now.date().isoformat()}\n\n"
        "Odhacz w zakladce Leki. Jesli nie odhaczysz, przypomne za 5 minut."
    )


def _read_marker(marker_key: str) -> bool:
    with get_db() as conn:
        row = conn.execute("SELECT 1 FROM notes WHERE key = ?", (marker_key,)).fetchone()
    return bool(row)


def _write_marker(marker_key: str) -> None:
    timestamp = utc_now_iso()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO notes(key, content, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET content=excluded.content, updated_at=excluded.updated_at
            """,
            (marker_key, "1", timestamp),
        )
        conn.commit()


def _send_text(text: str) -> None:
    if not _is_configured() or not text:
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "disable_web_page_preview": True,
            },
            timeout=12,
        ).raise_for_status()
    except Exception:
        # Best-effort notifier: errors should never break main app flows.
        return


def _build_morning_message(now: datetime, open_tasks: list[dict]) -> str:
    today = now.date()
    sorted_tasks = _sorted_open_tasks(open_tasks, now.tzinfo or _get_tz())
    overdue = _overdue_tasks(sorted_tasks, today)
    today_tasks = _today_tasks(sorted_tasks, today)
    tomorrow_tasks = _tomorrow_tasks(sorted_tasks, today)

    return (
        f"Dzien dobry! Plan na {today.isoformat()}\n"
        f"Otwarte lacznie: {len(open_tasks)}\n\n"
        f"Na dzis ({len(today_tasks)}):\n{_truncate_task_lines(today_tasks)}\n\n"
        f"Na jutro ({len(tomorrow_tasks)}):\n{_truncate_task_lines(tomorrow_tasks)}\n\n"
        f"Opoznione ({len(overdue)}):\n{_truncate_task_lines(overdue)}"
    )


def _build_day_summary_message(now: datetime, open_tasks: list[dict]) -> str:
    today_key = now.date().isoformat()
    done_today = _count_done_today(today_key)
    sorted_tasks = _sorted_open_tasks(open_tasks, now.tzinfo or _get_tz())
    overdue = _overdue_tasks(sorted_tasks, now.date())
    in_progress = [task for task in sorted_tasks if (task.get("status") or "") == "todo"]

    return (
        f"Podsumowanie dnia 16:00 ({today_key})\n"
        f"Zrobione dzis: {done_today}\n"
        f"W toku teraz: {len(in_progress)}\n"
        f"Zostalo otwartych: {len(open_tasks)}\n"
        f"Opoznione: {len(overdue)}"
    )


def _build_remaining_message(now: datetime, open_tasks: list[dict]) -> str:
    if not open_tasks:
        return ""

    sorted_tasks = _sorted_open_tasks(open_tasks, now.tzinfo or _get_tz())
    overdue = _overdue_tasks(sorted_tasks, now.date())
    today_tasks = _today_tasks(sorted_tasks, now.date())

    return (
        f"19:00 - co zostalo na {now.date().isoformat()}\n"
        f"Otwarte: {len(open_tasks)}\n"
        f"Opoznione: {len(overdue)}\n"
        f"Na dzis niewykonane: {len(today_tasks)}\n\n"
        f"Top rzeczy do domkniecia:\n{_truncate_task_lines(sorted_tasks, limit=8)}"
    )


def _build_scheduled_message(event_key: str, now: datetime, open_tasks: list[dict]) -> str:
    if event_key == "morning":
        return _build_morning_message(now, open_tasks)
    if event_key == "day_summary":
        return _build_day_summary_message(now, open_tasks)
    if event_key == "remaining":
        return _build_remaining_message(now, open_tasks)
    return ""


def _parse_schedule_time(time_raw: str) -> dt_time:
    return datetime.strptime(time_raw, "%H:%M").time()


def _process_medication_reminders(now: datetime) -> None:
    today = now.date()
    bucket = int(now.timestamp() // 300)

    for medication in _load_medication_reminders_for_date(today):
        if int(medication.get("done") or 0) == 1:
            continue
        try:
            reminder_time = _parse_schedule_time((medication.get("reminder_time") or "08:00").strip())
        except ValueError:
            reminder_time = dt_time(8, 0)

        scheduled_at = datetime.combine(today, reminder_time, tzinfo=now.tzinfo)
        if now < scheduled_at:
            continue

        marker_key = f"telegram-medication:{medication['id']}:{today.isoformat()}:{bucket}"
        if _read_marker(marker_key):
            continue

        _send_text(_build_medication_message(medication, now))
        _write_marker(marker_key)


def _process_scheduled_notifications() -> None:
    if not (_is_configured() and TELEGRAM_SCHEDULE_ENABLED):
        return

    tz = _get_tz()
    now = datetime.now(tz)
    open_tasks = _load_open_tasks()

    for time_raw, event_key in _SCHEDULED_EVENTS:
        planned_time = _parse_schedule_time(time_raw)
        scheduled_at = datetime.combine(now.date(), planned_time, tzinfo=tz)
        if now < scheduled_at:
            continue

        marker_key = f"telegram-scheduled:{event_key}:{now.date().isoformat()}"
        if _read_marker(marker_key):
            continue

        text = _build_scheduled_message(event_key, now, open_tasks)
        if text:
            _send_text(text)
        _write_marker(marker_key)

    _process_medication_reminders(now)


async def _scheduler_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(_process_scheduled_notifications)
        except Exception:
            # Background loop must survive temporary db/network issues.
            pass
        await asyncio.sleep(30)


def register_telegram_scheduler(app: FastAPI) -> None:
    @app.on_event("startup")
    async def _start_scheduler() -> None:
        global _scheduler_task
        if not (_is_configured() and TELEGRAM_SCHEDULE_ENABLED):
            return
        if _scheduler_task is None or _scheduler_task.done():
            _scheduler_task = asyncio.create_task(_scheduler_loop(), name="telegram-scheduler")

    @app.on_event("shutdown")
    async def _stop_scheduler() -> None:
        global _scheduler_task
        if _scheduler_task is None:
            return
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
        _scheduler_task = None


def notify_task_closed(task_name: str) -> None:
    if not _is_configured():
        return

    open_tasks = _load_open_tasks()
    today = datetime.now(_get_tz()).date()
    overdue_count = len(_overdue_tasks(open_tasks, today))
    message = (
        f"Zadanie zeszlo: {task_name}\n"
        f"Zostalo otwartych: {len(open_tasks)}\n"
        f"W tym opoznione: {overdue_count}"
    )
    _send_text(message)
