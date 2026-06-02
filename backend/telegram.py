import asyncio
import os
import re
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, time as dt_time, timedelta
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import requests
from fastapi import FastAPI

from backend.accounts import ACCOUNTS, PRIMARY_ACCOUNT, get_user_by_username
from backend.auth import get_request_user, reset_request_user, set_request_user
from backend.db import get_db
from backend.utils import normalize_module_category, normalize_priority, normalize_status, utc_now_iso

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_ENABLED = str(os.getenv("TELEGRAM_ENABLED", "1")).strip().lower() in {"1", "true", "yes", "on"}
TELEGRAM_SCHEDULE_ENABLED = str(os.getenv("TELEGRAM_SCHEDULE_ENABLED", "1")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
TELEGRAM_INBOX_ENABLED = str(os.getenv("TELEGRAM_INBOX_ENABLED", "1")).strip().lower() in {"1", "true", "yes", "on"}
TELEGRAM_FREE_TEXT_ADD_ENABLED = str(os.getenv("TELEGRAM_FREE_TEXT_ADD_ENABLED", "0")).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
TELEGRAM_TIMEZONE = os.getenv("TELEGRAM_TIMEZONE", "Europe/Warsaw").strip() or "Europe/Warsaw"
TELEGRAM_DEFAULT_MODULE_NAME = os.getenv("TELEGRAM_DEFAULT_MODULE_NAME", "Inbox Telegram").strip() or "Inbox Telegram"
TELEGRAM_DEFAULT_MODULE_CATEGORY = normalize_module_category(os.getenv("TELEGRAM_DEFAULT_MODULE_CATEGORY", "praca"))
_UPDATES_OFFSET_FILE_RAW = os.getenv("TELEGRAM_UPDATES_OFFSET_FILE", ".telegram_updates_offset").strip()

_SCHEDULED_EVENTS = [
    ("08:00", "morning"),
    ("16:00", "day_summary"),
    ("19:00", "remaining"),
    ("22:48", "remaining"),
]

_WEEKDAY_ALIASES = {
    "pon": 1,
    "pn": 1,
    "poniedzialek": 1,
    "wt": 2,
    "wtorek": 2,
    "sro": 3,
    "sr": 3,
    "sroda": 3,
    "czw": 4,
    "cz": 4,
    "czwartek": 4,
    "pt": 5,
    "piatek": 5,
    "sob": 6,
    "sobota": 6,
    "nd": 7,
    "niedz": 7,
    "niedziela": 7,
}

_TOKEN_TIME_RE = re.compile(r"^(?:[01]?\d|2[0-3]):[0-5]\d$")
_TOKEN_PRIORITY_RE = re.compile(r"^(?:!|p)([123])$", re.IGNORECASE)
_TOKEN_DURATION_MIN_RE = re.compile(r"^(\d{1,3})(?:m|min)$", re.IGNORECASE)
_TOKEN_DURATION_H_RE = re.compile(r"^(\d{1,2}(?:[.,]\d+)?)h$", re.IGNORECASE)
_TOKEN_DATE_DOT_RE = re.compile(r"^(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?$")
_TOKEN_MODULE_RE = re.compile(r"^#([\w-]{2,40})$", re.UNICODE)
_TOKEN_STATUS_RE = re.compile(r"^%(todo|prep|hold|wait)$", re.IGNORECASE)

_scheduler_task: Optional[asyncio.Task] = None


def _parse_positive_int(raw_value: str, default: int, minimum: int = 1) -> int:
    try:
        value = int((raw_value or "").strip())
    except Exception:
        value = default
    return max(minimum, value)


TELEGRAM_DEFAULT_ESTIMATED_MINUTES = _parse_positive_int(
    os.getenv("TELEGRAM_DEFAULT_ESTIMATED_MINUTES", "30"),
    default=30,
    minimum=5,
)
TELEGRAM_SCHEDULE_GRACE_MINUTES = _parse_positive_int(
    os.getenv("TELEGRAM_SCHEDULE_GRACE_MINUTES", "10"),
    default=10,
    minimum=1,
)


@dataclass(frozen=True)
class TelegramAccountRoute:
    username: str
    account_index: int
    chat_ids: tuple[str, ...]


def _resolve_offset_file_path(raw_path: str) -> Path:
    target = Path(raw_path) if raw_path else Path(".telegram_updates_offset")
    if not target.is_absolute():
        target = PROJECT_ROOT / target
    return target.resolve()


UPDATES_OFFSET_FILE = _resolve_offset_file_path(_UPDATES_OFFSET_FILE_RAW)


def _split_chat_ids(raw_value: str) -> list[str]:
    values = []
    for part in (raw_value or "").split(","):
        normalized = part.strip()
        if normalized:
            values.append(normalized)
    return values


def _account_env_key(base_key: str, account_index: int) -> str:
    return base_key if account_index == 1 else f"{base_key}_{account_index}"


def _account_env_value(base_key: str, account_index: int, fallback: str = "") -> str:
    key = _account_env_key(base_key, account_index)
    value = (os.getenv(key, "") or "").strip()
    return value if value else fallback


def _build_account_routes() -> list[TelegramAccountRoute]:
    routes: list[TelegramAccountRoute] = []
    for account_index, account in enumerate(ACCOUNTS, start=1):
        chat_key = _account_env_key("TELEGRAM_CHAT_ID", account_index)
        chat_ids = tuple(_split_chat_ids(os.getenv(chat_key, "")))
        if not chat_ids:
            continue
        routes.append(
            TelegramAccountRoute(
                username=account.username,
                account_index=account_index,
                chat_ids=chat_ids,
            )
        )
    return routes


ACCOUNT_ROUTES = _build_account_routes()
ACCOUNT_ROUTES_BY_USERNAME = {route.username: route for route in ACCOUNT_ROUTES}
ACCOUNT_ROUTES_BY_CHAT_ID = {
    chat_id: route
    for route in ACCOUNT_ROUTES
    for chat_id in route.chat_ids
}


def _load_updates_offset() -> int:
    try:
        raw_value = UPDATES_OFFSET_FILE.read_text(encoding="utf-8").strip()
        if not raw_value:
            return 0
        value = int(raw_value)
        return value if value >= 0 else 0
    except Exception:
        return 0


def _save_updates_offset(offset: int) -> None:
    try:
        UPDATES_OFFSET_FILE.parent.mkdir(parents=True, exist_ok=True)
        UPDATES_OFFSET_FILE.write_text(str(max(0, int(offset))), encoding="utf-8")
    except Exception:
        return


_incoming_updates_offset: int = _load_updates_offset()


def _is_configured() -> bool:
    return TELEGRAM_ENABLED and bool(TELEGRAM_BOT_TOKEN and ACCOUNT_ROUTES)


def _scheduler_should_run() -> bool:
    return _is_configured() and (TELEGRAM_SCHEDULE_ENABLED or TELEGRAM_INBOX_ENABLED)


@contextmanager
def _as_account(username: str):
    token = set_request_user(username)
    try:
        yield
    finally:
        reset_request_user(token)


def _current_user_id() -> int:
    username = get_request_user() or PRIMARY_ACCOUNT.username
    account = get_user_by_username(username)
    return account.id if account else PRIMARY_ACCOUNT.id


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
    user_id = _current_user_id()
    with get_db() as conn:
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


def _count_done_today(today_key: str) -> int:
    user_id = _current_user_id()
    marker = f"[Done: {today_key}]"
    with get_db() as conn:
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
    user_id = _current_user_id()
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
              AND mr.owner_user_id = ?
            ORDER BY mr.reminder_time ASC, mr.name COLLATE NOCASE ASC
            """,
            (day_key, user_id),
        ).fetchall()

    return [dict(row) for row in rows if _is_medication_scheduled(row["schedule_type"], day)]


def _build_medication_message(medication: dict, now: datetime) -> str:
    return (
        f"Lek do odhaczenia: {medication.get('name') or 'bez nazwy'}\n"
        f"Godzina: {(medication.get('reminder_time') or '08:00').strip()}\n"
        f"Dzien: {now.date().isoformat()}\n\n"
        "Odhacz w zakladce Leki. Jesli nie odhaczysz, przypomne za 5 minut."
    )


def _claim_marker(marker_key: str) -> bool:
    user_id = _current_user_id()
    timestamp = utc_now_iso()
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO notes(owner_user_id, key, content, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(owner_user_id, key) DO NOTHING
            """,
            (user_id, marker_key, "pending", timestamp),
        )
        conn.commit()
        return cursor.rowcount > 0


def _write_marker(marker_key: str) -> None:
    user_id = _current_user_id()
    timestamp = utc_now_iso()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO notes(owner_user_id, key, content, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(owner_user_id, key) DO UPDATE SET content=excluded.content, updated_at=excluded.updated_at
            """,
            (user_id, marker_key, "1", timestamp),
        )
        conn.commit()


def _send_text(chat_id: str, text: str) -> None:
    if not _is_configured() or not text:
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "disable_web_page_preview": True,
            },
            timeout=12,
        ).raise_for_status()
    except Exception:
        # Best-effort notifier: errors should never break main app flows.
        return


def _send_to_account(username: str, text: str) -> None:
    route = ACCOUNT_ROUTES_BY_USERNAME.get((username or "").strip())
    if not route or not text:
        return
    for chat_id in route.chat_ids:
        _send_text(chat_id, text)


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


def _process_medication_reminders(now: datetime, username: str) -> None:
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
        if not _claim_marker(marker_key):
            continue

        _send_to_account(username, _build_medication_message(medication, now))
        _write_marker(marker_key)


def _process_scheduled_notifications_for_account(route: TelegramAccountRoute, now: datetime, tz: ZoneInfo) -> None:
    username = route.username
    with _as_account(username):
        open_tasks = _load_open_tasks()
        for time_raw, event_key in _SCHEDULED_EVENTS:
            planned_time = _parse_schedule_time(time_raw)
            scheduled_at = datetime.combine(now.date(), planned_time, tzinfo=tz)
            if now < scheduled_at:
                continue

            delay = now - scheduled_at
            if delay > timedelta(minutes=TELEGRAM_SCHEDULE_GRACE_MINUTES):
                continue

            marker_key = f"telegram-scheduled:{event_key}:{time_raw}:{now.date().isoformat()}"
            if not _claim_marker(marker_key):
                continue

            text = _build_scheduled_message(event_key, now, open_tasks)
            if text:
                _send_to_account(username, text)
            _write_marker(marker_key)

        _process_medication_reminders(now, username)


def _process_scheduled_notifications() -> None:
    if not (_is_configured() and TELEGRAM_SCHEDULE_ENABLED):
        return

    tz = _get_tz()
    now = datetime.now(tz)
    for route in ACCOUNT_ROUTES:
        _process_scheduled_notifications_for_account(route, now, tz)


def _normalize_module_hint(raw_hint: str) -> str:
    value = (raw_hint or "").strip().replace("_", " ").replace("-", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value[:80]


def _parse_module_from_token(token: str) -> Optional[str]:
    match = _TOKEN_MODULE_RE.fullmatch(token)
    if not match:
        return None
    return _normalize_module_hint(match.group(1))


def _parse_priority_from_token(token: str) -> Optional[str]:
    match = _TOKEN_PRIORITY_RE.fullmatch(token)
    if not match:
        return None
    return normalize_priority(f"P{match.group(1)}")


def _parse_time_from_token(token: str) -> Optional[str]:
    if not _TOKEN_TIME_RE.fullmatch(token):
        return None
    hour, minute = token.split(":")
    return f"{int(hour):02d}:{minute}"


def _parse_duration_from_token(token: str) -> Optional[int]:
    match_minutes = _TOKEN_DURATION_MIN_RE.fullmatch(token)
    if match_minutes:
        return max(5, min(720, int(match_minutes.group(1))))

    match_hours = _TOKEN_DURATION_H_RE.fullmatch(token)
    if match_hours:
        hours = float(match_hours.group(1).replace(",", "."))
        return max(5, min(720, int(round(hours * 60))))
    return None


def _parse_status_from_token(token: str) -> Optional[str]:
    match = _TOKEN_STATUS_RE.fullmatch(token)
    if not match:
        return None
    mapped = {
        "todo": "todo",
        "prep": "przygotowanie",
        "hold": "przygotowanie",
        "wait": "oczekujace",
    }.get(match.group(1).lower(), "oczekujace")
    return normalize_status(mapped)


def _parse_date_from_token(token: str, now_local: datetime) -> Optional[str]:
    clean = (token or "").strip().lower()
    today = now_local.date()
    if clean in {"dzis", "today"}:
        return today.isoformat()
    if clean in {"jutro", "tomorrow"}:
        return (today + timedelta(days=1)).isoformat()

    weekday = _WEEKDAY_ALIASES.get(clean)
    if weekday:
        delta = (weekday - today.isoweekday()) % 7
        return (today + timedelta(days=delta)).isoformat()

    try:
        parsed_iso = datetime.strptime(token, "%Y-%m-%d").date()
        return parsed_iso.isoformat()
    except ValueError:
        pass

    match_dot = _TOKEN_DATE_DOT_RE.fullmatch(clean)
    if not match_dot:
        return None

    day_value = int(match_dot.group(1))
    month_value = int(match_dot.group(2))
    year_raw = match_dot.group(3)
    if year_raw:
        year_value = int(year_raw)
        if year_value < 100:
            year_value += 2000
    else:
        year_value = today.year

    try:
        parsed = date(year_value, month_value, day_value)
    except ValueError:
        return None

    if not year_raw and parsed < today:
        try:
            parsed = date(year_value + 1, month_value, day_value)
        except ValueError:
            return None
    return parsed.isoformat()


def _parse_quick_add_payload(raw_payload: str, now_local: datetime) -> tuple[Optional[dict], Optional[str]]:
    payload = (raw_payload or "").strip()
    if not payload:
        return None, "Wpisz nazwe zadania, np. `+ raport jutro 09:00 !1 30m`."

    remaining_tokens: list[str] = []
    due_date = ""
    due_time = ""
    priority = ""
    estimated_minutes = TELEGRAM_DEFAULT_ESTIMATED_MINUTES
    status = "oczekujace"
    module_hint = ""

    for raw_token in payload.replace("\n", " ").split():
        token = raw_token.strip()
        if not token:
            continue
        normalized = token.strip(",;").strip()
        lower_token = normalized.lower()

        parsed_module = _parse_module_from_token(normalized)
        if parsed_module and not module_hint:
            module_hint = parsed_module
            continue

        parsed_priority = _parse_priority_from_token(lower_token)
        if parsed_priority and not priority:
            priority = parsed_priority
            continue

        parsed_duration = _parse_duration_from_token(lower_token)
        if parsed_duration:
            estimated_minutes = parsed_duration
            continue

        parsed_status = _parse_status_from_token(lower_token)
        if parsed_status:
            status = parsed_status
            continue

        parsed_time = _parse_time_from_token(normalized)
        if parsed_time and not due_time:
            due_time = parsed_time
            continue

        parsed_date = _parse_date_from_token(normalized, now_local)
        if parsed_date and not due_date:
            due_date = parsed_date
            continue

        remaining_tokens.append(raw_token)

    clean_name = " ".join(remaining_tokens).strip()
    clean_name = re.sub(r"\s+", " ", clean_name)[:180].rstrip()
    if not clean_name:
        return None, "Nie widze nazwy zadania. Najpierw podaj tekst zadania, potem opcjonalne tokeny."

    if due_time and not due_date:
        due_date = now_local.date().isoformat()

    return (
        {
            "name": clean_name,
            "due_date": due_date,
            "due_time": due_time,
            "priority": normalize_priority(priority),
            "estimated_time": max(5, int(estimated_minutes)),
            "status": normalize_status(status),
            "module_hint": module_hint,
        },
        None,
    )


def _find_or_create_module(route: TelegramAccountRoute, module_hint: str) -> tuple[int, str, bool]:
    user_id = _current_user_id()
    requested_name = _normalize_module_hint(module_hint)
    if not requested_name:
        requested_name = _account_env_value("TELEGRAM_DEFAULT_MODULE_NAME", route.account_index, TELEGRAM_DEFAULT_MODULE_NAME)
    if not requested_name:
        requested_name = TELEGRAM_DEFAULT_MODULE_NAME

    default_category = normalize_module_category(
        _account_env_value("TELEGRAM_DEFAULT_MODULE_CATEGORY", route.account_index, TELEGRAM_DEFAULT_MODULE_CATEGORY)
    )

    with get_db() as conn:
        exact = conn.execute(
            "SELECT id, name FROM modules WHERE owner_user_id = ? AND lower(name) = lower(?) LIMIT 1",
            (user_id, requested_name),
        ).fetchone()
        if exact:
            return int(exact["id"]), exact["name"] or requested_name, False

        similar = conn.execute(
            """
            SELECT id, name
            FROM modules
            WHERE owner_user_id = ? AND lower(name) LIKE lower(?)
            ORDER BY id
            LIMIT 1
            """,
            (user_id, f"%{requested_name}%"),
        ).fetchone()
        if similar:
            return int(similar["id"]), similar["name"] or requested_name, False

        cur = conn.execute(
            "INSERT INTO modules (name, category, owner_user_id) VALUES (?, ?, ?)",
            (requested_name[:120], default_category, user_id),
        )
        conn.commit()
        return int(cur.lastrowid), requested_name[:120], True


def _create_task_from_telegram(route: TelegramAccountRoute, payload: dict) -> dict:
    user_id = _current_user_id()
    module_id, module_name, module_created = _find_or_create_module(route, payload.get("module_hint") or "")
    due_date = (payload.get("due_date") or "").strip()
    due_time = (payload.get("due_time") or "").strip()
    if due_date and not due_time:
        due_time = "14:00"

    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO tasks (
                name,
                module_id,
                status,
                estimated_time,
                points_weight,
                priority,
                description,
                due_date,
                due_time,
                owner_user_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("name", "").strip()[:180],
                module_id,
                normalize_status(payload.get("status") or "oczekujace"),
                max(5, int(payload.get("estimated_time") or TELEGRAM_DEFAULT_ESTIMATED_MINUTES)),
                1.0,
                normalize_priority(payload.get("priority") or ""),
                "Dodane z Telegrama.",
                due_date,
                due_time if due_date else "",
                user_id,
            ),
        )
        task_id = int(cur.lastrowid)
        conn.commit()

    return {
        "id": task_id,
        "name": payload.get("name", "").strip(),
        "module_name": module_name,
        "module_created": module_created,
        "due_date": due_date,
        "due_time": due_time if due_date else "",
        "estimated_time": max(5, int(payload.get("estimated_time") or TELEGRAM_DEFAULT_ESTIMATED_MINUTES)),
        "priority": normalize_priority(payload.get("priority") or ""),
        "status": normalize_status(payload.get("status") or "oczekujace"),
    }


def _build_quick_help(route: TelegramAccountRoute) -> str:
    default_module = _account_env_value("TELEGRAM_DEFAULT_MODULE_NAME", route.account_index, TELEGRAM_DEFAULT_MODULE_NAME)
    return (
        "Szybkie dodawanie zadan:\n"
        "+ nazwa zadania\n"
        "+ raport jutro 09:00 !1 30m\n"
        "+ zakupy #dom dzis 18:15 20m\n\n"
        "Tokeny:\n"
        "- !1 / !2 / !3 = priorytet\n"
        "- dzis | jutro | pon/wt/sr/czw/pt/sob/nd | YYYY-MM-DD | DD.MM\n"
        "- HH:MM = godzina\n"
        "- 15m lub 1h = czas\n"
        "- #modul = modul (np. #praca, #dom)\n"
        "- %todo | %prep | %wait = status\n\n"
        f"Gdy nie podasz modulu, zadanie wpada do: {default_module}.\n"
        "Komendy: /add ... , /list, /help"
    )


def _build_today_list(username: str) -> str:
    with _as_account(username):
        tz = _get_tz()
        now = datetime.now(tz)
        open_tasks = _sorted_open_tasks(_load_open_tasks(), tz)
        today_tasks = _today_tasks(open_tasks, now.date())
        overdue_tasks = _overdue_tasks(open_tasks, now.date())

    return (
        f"Dzis: {now.date().isoformat()}\n"
        f"Na dzis: {len(today_tasks)}\n"
        f"Opoznione: {len(overdue_tasks)}\n"
        f"Otwarte lacznie: {len(open_tasks)}\n\n"
        f"Top:\n{_truncate_task_lines([*overdue_tasks, *today_tasks], limit=8)}"
    )


def _extract_add_payload(text: str) -> tuple[Optional[str], Optional[str]]:
    clean_text = (text or "").strip()
    if not clean_text:
        return None, None

    if clean_text.startswith("+"):
        return clean_text[1:].strip(), None

    if not clean_text.startswith("/"):
        if TELEGRAM_FREE_TEXT_ADD_ENABLED:
            return clean_text, None
        return None, None

    parts = clean_text.split(None, 1)
    command_raw = parts[0].split("@", 1)[0].lower()
    command_payload = parts[1].strip() if len(parts) > 1 else ""

    if command_raw == "/add":
        return command_payload, None
    if command_raw in {"/help", "/start", "/list", "/today"}:
        return None, command_raw
    return None, "unknown_command"


def _send_added_task_confirmation(chat_id: str, created_task: dict) -> None:
    due_label = "bez terminu"
    if created_task.get("due_date"):
        due_label = f"{created_task.get('due_date')} {created_task.get('due_time') or '14:00'}"

    priority_label = created_task.get("priority") or "-"
    module_created_line = "\n(Utworzono nowy modul)." if created_task.get("module_created") else ""
    _send_text(
        chat_id,
        (
            f"Dodane: {created_task.get('name')}\n"
            f"Modul: {created_task.get('module_name')}\n"
            f"Termin: {due_label}\n"
            f"Czas: {created_task.get('estimated_time')} min\n"
            f"Priorytet: {priority_label}{module_created_line}"
        ),
    )


def _handle_incoming_message(route: TelegramAccountRoute, chat_id: str, text: str) -> None:
    add_payload, command = _extract_add_payload(text)
    if command in {"/help", "/start"}:
        _send_text(chat_id, _build_quick_help(route))
        return
    if command in {"/list", "/today"}:
        _send_text(chat_id, _build_today_list(route.username))
        return
    if command == "unknown_command":
        _send_text(chat_id, "Nieznana komenda. Uzyj /help.")
        return

    if not add_payload:
        if TELEGRAM_FREE_TEXT_ADD_ENABLED:
            _send_text(chat_id, "Nie odczytalem zadania. Sprobuj np. `+ oddzwonic jutro 09:30 !1 20m`.")
        else:
            _send_text(chat_id, "Aby dodac zadanie, zacznij wiadomosc od `+` albo uzyj `/add ...`.")
        return

    now_local = datetime.now(_get_tz())
    parsed_payload, error = _parse_quick_add_payload(add_payload, now_local)
    if error or not parsed_payload:
        _send_text(chat_id, error or "Nie udalo sie odczytac zadania. Uzyj /help.")
        return

    try:
        with _as_account(route.username):
            created_task = _create_task_from_telegram(route, parsed_payload)
    except Exception:
        _send_text(chat_id, "Nie udalo sie dodac zadania. Sprobuj ponownie za chwile.")
        return

    _send_added_task_confirmation(chat_id, created_task)


def _process_incoming_updates() -> None:
    global _incoming_updates_offset
    if not (_is_configured() and TELEGRAM_INBOX_ENABLED):
        return

    params: dict[str, object] = {
        "timeout": 0,
        "allowed_updates": ["message"],
    }
    if _incoming_updates_offset > 0:
        params["offset"] = _incoming_updates_offset

    try:
        response = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates",
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return

    if not payload.get("ok"):
        return

    updates = payload.get("result") or []
    next_offset = _incoming_updates_offset
    for update in updates:
        try:
            update_id = int(update.get("update_id"))
        except Exception:
            continue
        next_offset = max(next_offset, update_id + 1)

        message = update.get("message") or {}
        sender = message.get("from") or {}
        if sender.get("is_bot"):
            continue

        chat_id_raw = (message.get("chat") or {}).get("id")
        text = (message.get("text") or "").strip()
        if chat_id_raw is None or not text:
            continue

        chat_id = str(chat_id_raw).strip()
        route = ACCOUNT_ROUTES_BY_CHAT_ID.get(chat_id)
        if not route:
            continue
        _handle_incoming_message(route, chat_id, text)

    if next_offset != _incoming_updates_offset:
        _incoming_updates_offset = next_offset
        _save_updates_offset(next_offset)


def _process_background_cycle() -> None:
    if TELEGRAM_SCHEDULE_ENABLED:
        _process_scheduled_notifications()
    if TELEGRAM_INBOX_ENABLED:
        _process_incoming_updates()


async def _scheduler_loop() -> None:
    while True:
        try:
            await asyncio.to_thread(_process_background_cycle)
        except Exception:
            # Background loop must survive temporary db/network issues.
            pass
        await asyncio.sleep(30)


def register_telegram_scheduler(app: FastAPI) -> None:
    @app.on_event("startup")
    async def _start_scheduler() -> None:
        global _scheduler_task
        if not _scheduler_should_run():
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


def notify_task_closed(task_name: str, username: Optional[str] = None) -> None:
    if not _is_configured():
        return

    resolved_user = (username or get_request_user() or PRIMARY_ACCOUNT.username).strip()
    route = ACCOUNT_ROUTES_BY_USERNAME.get(resolved_user)
    if not route:
        return

    with _as_account(route.username):
        open_tasks = _load_open_tasks()
        today = datetime.now(_get_tz()).date()
        overdue_count = len(_overdue_tasks(open_tasks, today))

    message = (
        f"Zadanie zeszlo: {task_name}\n"
        f"Zostalo otwartych: {len(open_tasks)}\n"
        f"W tym opoznione: {overdue_count}"
    )
    _send_to_account(route.username, message)
