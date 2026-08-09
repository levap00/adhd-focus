from fastapi import APIRouter, Header, HTTPException, Query
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from backend.accounts import get_user_by_username
from backend.auth import get_request_user
from backend.db import get_db
from backend.schemas import NotificationSettingsPayload, PushSubscriptionPayload
from backend.utils import normalize_due_time, utc_now_iso
from backend.web_push import (
    get_vapid_public_key,
    is_web_push_configured,
    record_notification_history,
    send_notification_to_user,
)

router = APIRouter()

DEFAULT_SETTINGS = {
    "enabled": True,
    "quiet_hours_enabled": True,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "07:00",
    "opening_enabled": True,
    "opening_time": "08:00",
    "day_summary_enabled": True,
    "day_summary_time": "20:30",
    "medication_enabled": True,
    "medication_repeat_enabled": False,
    "medication_repeat_minutes": 5,
    "medication_repeat_window_minutes": 120,
    "task_due_enabled": True,
    "task_reminder_enabled": True,
    "task_reminder_repeat_minutes": 120,
    "task_reminder_window_minutes": 480,
    "timezone": "Europe/Warsaw",
}


def _current_user_id() -> int:
    account = get_user_by_username(get_request_user())
    if not account:
        raise HTTPException(status_code=401, detail="Brak aktywnego uzytkownika.")
    return account.id


def _settings_from_row(row) -> dict:
    if not row:
        return dict(DEFAULT_SETTINGS)
    return {
        "enabled": bool(row["enabled"]),
        "quiet_hours_enabled": bool(row["quiet_hours_enabled"]),
        "quiet_hours_start": normalize_due_time(row["quiet_hours_start"], "22:00") or "22:00",
        "quiet_hours_end": normalize_due_time(row["quiet_hours_end"], "07:00") or "07:00",
        "opening_enabled": bool(row["opening_enabled"]),
        "opening_time": normalize_due_time(row["opening_time"], "08:00") or "08:00",
        "day_summary_enabled": bool(row["day_summary_enabled"]),
        "day_summary_time": normalize_due_time(row["day_summary_time"], "20:30") or "20:30",
        "medication_enabled": bool(row["medication_enabled"]),
        "medication_repeat_enabled": bool(row["medication_repeat_enabled"]),
        "medication_repeat_minutes": max(1, int(row["medication_repeat_minutes"] or 5)),
        "medication_repeat_window_minutes": max(1, int(row["medication_repeat_window_minutes"] or 120)),
        "task_due_enabled": bool(row["task_due_enabled"]),
        "task_reminder_enabled": bool(row["task_reminder_enabled"]),
        "task_reminder_repeat_minutes": max(15, int(row["task_reminder_repeat_minutes"] or 120)),
        "task_reminder_window_minutes": max(15, int(row["task_reminder_window_minutes"] or 480)),
        "timezone": (row["timezone"] or "Europe/Warsaw").strip() or "Europe/Warsaw",
    }


def _ensure_settings(conn, user_id: int) -> dict:
    row = conn.execute(
        """
        SELECT enabled, quiet_hours_enabled, quiet_hours_start, quiet_hours_end,
               opening_enabled, opening_time, day_summary_enabled, day_summary_time,
               medication_enabled, medication_repeat_enabled, medication_repeat_minutes,
               medication_repeat_window_minutes, task_due_enabled, task_reminder_enabled,
               task_reminder_repeat_minutes, task_reminder_window_minutes, timezone
        FROM notification_settings
        WHERE owner_user_id = ?
        """,
        (user_id,),
    ).fetchone()
    if row:
        return _settings_from_row(row)

    now = utc_now_iso()
    conn.execute(
        """
        INSERT INTO notification_settings (
            owner_user_id, enabled, quiet_hours_enabled, quiet_hours_start, quiet_hours_end,
            opening_enabled, opening_time, day_summary_enabled, day_summary_time,
            medication_enabled, medication_repeat_enabled, medication_repeat_minutes,
            medication_repeat_window_minutes, task_due_enabled, task_reminder_enabled,
            task_reminder_repeat_minutes, task_reminder_window_minutes, timezone, updated_at
        )
        VALUES (?, 1, 1, '22:00', '07:00', 1, '08:00', 1, '20:30', 1, 0, 5, 120, 1, 1, 120, 480, 'Europe/Warsaw', ?)
        """,
        (user_id, now),
    )
    conn.commit()
    return dict(DEFAULT_SETTINGS)


def _subscription_count(conn, user_id: int) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS total FROM push_subscriptions WHERE owner_user_id = ? AND active = 1",
        (user_id,),
    ).fetchone()
    return int(row["total"] if row else 0)


def _clean_minutes(value, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return min(maximum, max(minimum, parsed))


@router.get("/notifications/vapid-public-key")
def get_public_vapid_key():
    return {
        "public_key": get_vapid_public_key(),
        "configured": is_web_push_configured(),
    }


@router.get("/notifications/settings")
def get_notification_settings():
    user_id = _current_user_id()
    with get_db() as conn:
        settings = _ensure_settings(conn, user_id)
        count = _subscription_count(conn, user_id)
    return {
        "settings": settings,
        "subscription_count": count,
        "vapid_configured": is_web_push_configured(),
    }


@router.get("/notifications/history")
def get_notification_history(limit: int = Query(default=25, ge=1, le=100)):
    user_id = _current_user_id()
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, kind, title, body, reason, status, sent_count, failed_count, created_at
            FROM notification_delivery_history
            WHERE owner_user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return {"items": [dict(row) for row in rows]}


@router.put("/notifications/settings")
def update_notification_settings(payload: NotificationSettingsPayload):
    user_id = _current_user_id()
    timezone = (payload.timezone or "Europe/Warsaw").strip()[:64] or "Europe/Warsaw"
    try:
        ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(status_code=400, detail="Niepoprawna strefa czasowa.")
    settings = {
        "enabled": 1 if payload.enabled else 0,
        "quiet_hours_enabled": 1 if payload.quiet_hours_enabled else 0,
        "quiet_hours_start": normalize_due_time(payload.quiet_hours_start, "22:00") or "22:00",
        "quiet_hours_end": normalize_due_time(payload.quiet_hours_end, "07:00") or "07:00",
        "opening_enabled": 1 if payload.opening_enabled else 0,
        "opening_time": normalize_due_time(payload.opening_time, "08:00") or "08:00",
        "day_summary_enabled": 1 if payload.day_summary_enabled else 0,
        "day_summary_time": normalize_due_time(payload.day_summary_time, "20:30") or "20:30",
        "medication_enabled": 1 if payload.medication_enabled else 0,
        "medication_repeat_enabled": 1 if payload.medication_repeat_enabled else 0,
        "medication_repeat_minutes": _clean_minutes(payload.medication_repeat_minutes, 5, 1, 1440),
        "medication_repeat_window_minutes": _clean_minutes(payload.medication_repeat_window_minutes, 120, 1, 1440),
        "task_due_enabled": 1 if payload.task_due_enabled else 0,
        "task_reminder_enabled": 1 if payload.task_reminder_enabled else 0,
        "task_reminder_repeat_minutes": _clean_minutes(payload.task_reminder_repeat_minutes, 120, 15, 1440),
        "task_reminder_window_minutes": _clean_minutes(payload.task_reminder_window_minutes, 480, 15, 10080),
        "timezone": timezone,
    }
    now = utc_now_iso()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO notification_settings (
                owner_user_id, enabled, quiet_hours_enabled, quiet_hours_start, quiet_hours_end,
                opening_enabled, opening_time, day_summary_enabled, day_summary_time,
                medication_enabled, medication_repeat_enabled, medication_repeat_minutes,
                medication_repeat_window_minutes, task_due_enabled, task_reminder_enabled,
                task_reminder_repeat_minutes, task_reminder_window_minutes, timezone, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(owner_user_id) DO UPDATE SET
                enabled = excluded.enabled,
                quiet_hours_enabled = excluded.quiet_hours_enabled,
                quiet_hours_start = excluded.quiet_hours_start,
                quiet_hours_end = excluded.quiet_hours_end,
                opening_enabled = excluded.opening_enabled,
                opening_time = excluded.opening_time,
                day_summary_enabled = excluded.day_summary_enabled,
                day_summary_time = excluded.day_summary_time,
                medication_enabled = excluded.medication_enabled,
                medication_repeat_enabled = excluded.medication_repeat_enabled,
                medication_repeat_minutes = excluded.medication_repeat_minutes,
                medication_repeat_window_minutes = excluded.medication_repeat_window_minutes,
                task_due_enabled = excluded.task_due_enabled,
                task_reminder_enabled = excluded.task_reminder_enabled,
                task_reminder_repeat_minutes = excluded.task_reminder_repeat_minutes,
                task_reminder_window_minutes = excluded.task_reminder_window_minutes,
                timezone = excluded.timezone,
                updated_at = excluded.updated_at
            """,
            (
                user_id,
                settings["enabled"],
                settings["quiet_hours_enabled"],
                settings["quiet_hours_start"],
                settings["quiet_hours_end"],
                settings["opening_enabled"],
                settings["opening_time"],
                settings["day_summary_enabled"],
                settings["day_summary_time"],
                settings["medication_enabled"],
                settings["medication_repeat_enabled"],
                settings["medication_repeat_minutes"],
                settings["medication_repeat_window_minutes"],
                settings["task_due_enabled"],
                settings["task_reminder_enabled"],
                settings["task_reminder_repeat_minutes"],
                settings["task_reminder_window_minutes"],
                settings["timezone"],
                now,
            ),
        )
        conn.commit()
        updated = _ensure_settings(conn, user_id)
        count = _subscription_count(conn, user_id)
    return {
        "settings": updated,
        "subscription_count": count,
        "vapid_configured": is_web_push_configured(),
    }


@router.post("/notifications/subscribe")
def save_push_subscription(payload: PushSubscriptionPayload, user_agent: str = Header(default="")):
    user_id = _current_user_id()
    subscription = payload.subscription or {}
    endpoint = (subscription.get("endpoint") or "").strip()
    keys = subscription.get("keys") or {}
    p256dh = (keys.get("p256dh") or "").strip()
    auth = (keys.get("auth") or "").strip()
    if not endpoint or not p256dh or not auth:
        raise HTTPException(status_code=400, detail="Niepelna subskrypcja Web Push.")

    clean_user_agent = (payload.user_agent or user_agent or "").strip()[:500]
    now = utc_now_iso()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO push_subscriptions (
                owner_user_id, endpoint, p256dh, auth, content_encoding, user_agent,
                active, created_at, updated_at, last_error
            )
            VALUES (?, ?, ?, ?, 'aes128gcm', ?, 1, ?, ?, '')
            ON CONFLICT(endpoint) DO UPDATE SET
                owner_user_id = excluded.owner_user_id,
                p256dh = excluded.p256dh,
                auth = excluded.auth,
                content_encoding = excluded.content_encoding,
                user_agent = excluded.user_agent,
                active = 1,
                updated_at = excluded.updated_at,
                last_error = ''
            """,
            (user_id, endpoint, p256dh, auth, clean_user_agent, now, now),
        )
        conn.commit()
        count = _subscription_count(conn, user_id)
    return {"status": "subscribed", "subscription_count": count}


@router.post("/notifications/unsubscribe")
def remove_push_subscription(payload: dict):
    user_id = _current_user_id()
    endpoint = (payload.get("endpoint") or "").strip()
    if not endpoint:
        raise HTTPException(status_code=400, detail="Brak endpointu subskrypcji.")

    with get_db() as conn:
        conn.execute(
            "UPDATE push_subscriptions SET active = 0, updated_at = ? WHERE owner_user_id = ? AND endpoint = ?",
            (utc_now_iso(), user_id, endpoint),
        )
        conn.commit()
        count = _subscription_count(conn, user_id)
    return {"status": "unsubscribed", "subscription_count": count}


@router.post("/notifications/test")
def send_test_notification():
    user_id = _current_user_id()
    if not is_web_push_configured():
        raise HTTPException(status_code=400, detail="Brak VAPID_PUBLIC_KEY/VAPID_PRIVATE_KEY po stronie serwera.")

    with get_db() as conn:
        count = _subscription_count(conn, user_id)
    if count <= 0:
        raise HTTPException(status_code=400, detail="Najpierw wlacz powiadomienia na tym urzadzeniu.")

    test_marker = f"webpush-test:{utc_now_iso()}"
    test_payload = {
        "title": "Test powiadomienia",
        "body": "Web Push dziala dla tej aplikacji.",
        "tag": test_marker,
        "url": "/",
        "icon": "/static/apple-touch-icon.png",
        "badge": "/static/apple-touch-icon.png",
        "renotify": True,
    }
    result = send_notification_to_user(user_id, test_payload)
    record_notification_history(
        user_id,
        test_payload,
        "test",
        "Ręczny test uruchomiony w ustawieniach powiadomień.",
        result,
        test_marker,
    )
    if int(result.get("sent") or 0) <= 0:
        raise HTTPException(
            status_code=502,
            detail=f"Nie udalo sie wyslac powiadomienia. Bledy: {result.get('failed', 0)}.",
        )
    return {"status": "sent", **result}
