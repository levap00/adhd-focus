import re
from calendar import monthrange
from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Query

from backend.accounts import get_user_by_username
from backend.auth import get_request_user
from backend.db import get_db
from backend.schemas import MonthlyTaskCreate, MonthlyTaskStatePayload, MonthlyTaskUpdate
from backend.utils import normalize_due_time, normalize_month_key, parse_non_negative_int, utc_now_iso

router = APIRouter()
DATE_KEY_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WEEK_KEY_PATTERN = re.compile(r"^week:(\d{4}-\d{2}-\d{2})$")
CARRYOVER_LOOKBACK_DAYS = 370


def _current_user_id() -> int:
    account = get_user_by_username(get_request_user())
    if not account:
        raise HTTPException(status_code=401, detail="Brak aktywnego uzytkownika.")
    return account.id


def normalize_repeat_type(raw: str) -> str:
    value = (raw or "monthly").strip().lower()
    return "weekly" if value.startswith("week") else "monthly"


def normalize_repeat_weekday(raw) -> int:
    weekday = parse_non_negative_int(raw, default=1)
    if weekday < 1 or weekday > 7:
        return 1
    return weekday


def to_week_state_key(date_key: str) -> str:
    point = date.fromisoformat(date_key)
    monday = point - timedelta(days=point.isoweekday() - 1)
    return f"week:{monday.isoformat()}"


def current_week_state_key() -> str:
    today = date.today()
    monday = today - timedelta(days=today.isoweekday() - 1)
    return f"week:{monday.isoformat()}"


def normalize_state_key(raw: str | None, repeat_type: str) -> str:
    value = (raw or "").strip()
    if DATE_KEY_PATTERN.fullmatch(value):
        return value
    if re.fullmatch(r"\d{4}-\d{2}", value):
        return value
    if WEEK_KEY_PATTERN.fullmatch(value):
        return value
    if repeat_type == "weekly":
        return current_week_state_key()
    return normalize_month_key(value)


def _parse_date_key(raw: str | None) -> date | None:
    value = (raw or "").strip()[:10]
    if not DATE_KEY_PATTERN.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _month_bounds(month_key: str) -> tuple[date, date]:
    year, month = month_key.split("-")
    year_num = int(year)
    month_num = int(month)
    days_in_month = monthrange(year_num, month_num)[1]
    return date(year_num, month_num, 1), date(year_num, month_num, days_in_month)


def _next_month(point: date) -> date:
    if point.month == 12:
        return date(point.year + 1, 1, 1)
    return date(point.year, point.month + 1, 1)


def get_occurrence_date_keys(month_key: str, repeat_type: str, due_day: int, repeat_weekday: int) -> list[str]:
    month_start, month_end = _month_bounds(month_key)
    return [item.isoformat() for item in get_occurrence_dates(month_start, month_end, repeat_type, due_day, repeat_weekday)]


def get_occurrence_dates(start_day: date, end_day: date, repeat_type: str, due_day: int, repeat_weekday: int) -> list[date]:
    if end_day < start_day:
        return []
    if repeat_type == "weekly":
        entries: list[date] = []
        offset = (repeat_weekday - start_day.isoweekday()) % 7
        point = start_day + timedelta(days=offset)
        while point <= end_day:
            entries.append(point)
            point += timedelta(days=7)
        return entries

    if due_day <= 0:
        return []

    entries: list[date] = []
    cursor = date(start_day.year, start_day.month, 1)
    while cursor <= end_day:
        days_in_month = monthrange(cursor.year, cursor.month)[1]
        normalized_day = min(days_in_month, max(1, due_day))
        point = date(cursor.year, cursor.month, normalized_day)
        if start_day <= point <= end_day:
            entries.append(point)
        cursor = _next_month(cursor)
    return entries


def _legacy_state_key(repeat_type: str, date_key: str) -> str:
    if repeat_type == "weekly":
        return to_week_state_key(date_key)
    return date_key[:7]


@router.get("/monthly-tasks")
def get_monthly_tasks(month: str = Query(default="")):
    user_id = _current_user_id()
    month_key = normalize_month_key(month)
    month_start, month_end = _month_bounds(month_key)
    today = date.today()
    current_month_key = today.isoformat()[:7]
    carryover_enabled = month_key == current_month_key
    occurrence_start = month_start
    if carryover_enabled:
        occurrence_start = max(date(1970, 1, 1), today - timedelta(days=CARRYOVER_LOOKBACK_DAYS))
    with get_db() as conn:
        base_rows = conn.execute(
            """
            SELECT
                mt.id,
                mt.name,
                COALESCE(mt.due_day, 0) AS due_day,
                COALESCE(mt.due_time, '23:59') AS due_time,
                COALESCE(mt.repeat_type, 'monthly') AS repeat_type,
                COALESCE(mt.repeat_weekday, 1) AS repeat_weekday,
                mt.created_at,
                mt.updated_at
            FROM monthly_tasks mt
            WHERE mt.owner_user_id = ?
            ORDER BY mt.id DESC
            """,
            (user_id,),
        ).fetchall()

        task_ids = [int(row["id"]) for row in base_rows]
        states_by_key: dict[tuple[int, str], dict] = {}
        if task_ids:
            placeholders = ", ".join(["?"] * len(task_ids))
            state_rows = conn.execute(
                f"""
                SELECT monthly_task_id, month_key, done, note, updated_at
                FROM monthly_task_states
                WHERE monthly_task_id IN ({placeholders})
                """,
                task_ids,
            ).fetchall()
            for state_row in state_rows:
                states_by_key[(int(state_row["monthly_task_id"]), state_row["month_key"])] = {
                    "done": bool(state_row["done"]),
                    "note": state_row["note"] or "",
                    "updated_at": state_row["updated_at"] or "",
                }

    items = []
    done_count = 0
    for row in base_rows:
        task_id = int(row["id"])
        repeat_type = normalize_repeat_type(row["repeat_type"] or "monthly")
        repeat_weekday = normalize_repeat_weekday(row["repeat_weekday"])
        due_day = min(31, parse_non_negative_int(row["due_day"]))
        due_time = normalize_due_time(row["due_time"] or "", default="23:59") or "23:59"
        created_day = _parse_date_key(row["created_at"] or "")
        task_occurrence_start = max(occurrence_start, created_day) if created_day else occurrence_start

        occurrence_days = get_occurrence_dates(
            start_day=task_occurrence_start,
            end_day=month_end,
            repeat_type=repeat_type,
            due_day=due_day,
            repeat_weekday=repeat_weekday,
        )
        if not occurrence_days and not carryover_enabled:
            occurrence_days = []

        task_items = []
        carryover_item = None

        for occurrence_day in occurrence_days:
            date_key = occurrence_day.isoformat()
            state_key = date_key
            legacy_key = _legacy_state_key(repeat_type, date_key)
            state = (
                states_by_key.get((task_id, state_key))
                or states_by_key.get((task_id, legacy_key))
                or {"done": False, "note": "", "updated_at": ""}
            )
            done = bool(state["done"])
            display_day = occurrence_day
            overdue = False
            if carryover_enabled and not done and occurrence_day < today:
                display_day = today
                overdue = True
            item = {
                "id": task_id,
                "instance_id": f"{task_id}:{state_key}:{display_day.isoformat()}",
                "name": row["name"] or "",
                "due_day": due_day,
                "due_time": due_time,
                "repeat_type": repeat_type,
                "repeat_weekday": repeat_weekday,
                "date_key": date_key,
                "display_date_key": display_day.isoformat(),
                "state_key": state_key,
                "legacy_state_key": legacy_key,
                "overdue": overdue,
                "done": done,
                "note": state["note"],
                "state_updated_at": state["updated_at"],
                "created_at": row["created_at"] or "",
                "updated_at": row["updated_at"] or "",
                "month_key": month_key,
            }
            if overdue:
                if carryover_item is None or date_key < carryover_item["date_key"]:
                    carryover_item = item
                continue
            if display_day < month_start or display_day > month_end:
                continue
            task_items.append(item)

        if carryover_item is not None:
            task_items = [item for item in task_items if item["done"]]
            task_items.append(carryover_item)

        for item in task_items:
            if item["done"]:
                done_count += 1
            items.append(item)

    items = sorted(
        items,
        key=lambda item: (
            item["display_date_key"] or item["date_key"] or "9999-99-99",
            item["date_key"] or "9999-99-99",
            item["name"].lower(),
            int(item["id"]),
        ),
    )

    return {
        "month_key": month_key,
        "items": items,
        "summary": {
            "total": len(items),
            "done": done_count,
            "open": len(items) - done_count,
        },
    }


@router.post("/monthly-tasks")
def add_monthly_task(payload: MonthlyTaskCreate):
    user_id = _current_user_id()
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Nazwa zadania cyklicznego nie moze byc pusta")
    repeat_type = normalize_repeat_type(payload.repeat_type)
    due_day = min(31, parse_non_negative_int(payload.due_day)) if repeat_type == "monthly" else 0
    due_time = normalize_due_time(payload.due_time, default="23:59") or "23:59"
    repeat_weekday = normalize_repeat_weekday(payload.repeat_weekday)

    now = utc_now_iso()
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO monthly_tasks (name, due_day, due_time, repeat_type, repeat_weekday, owner_user_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, due_day, due_time, repeat_type, repeat_weekday, user_id, now, now),
        )
        conn.commit()

    return {
        "id": cur.lastrowid,
        "name": name,
        "due_day": due_day,
        "due_time": due_time,
        "repeat_type": repeat_type,
        "repeat_weekday": repeat_weekday,
        "created_at": now,
        "updated_at": now,
    }


@router.put("/monthly-tasks/{task_id}")
def update_monthly_task(task_id: int, payload: MonthlyTaskUpdate):
    user_id = _current_user_id()
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Nazwa zadania cyklicznego nie moze byc pusta")
    repeat_type = normalize_repeat_type(payload.repeat_type)
    due_day = min(31, parse_non_negative_int(payload.due_day)) if repeat_type == "monthly" else 0
    due_time = normalize_due_time(payload.due_time, default="23:59") or "23:59"
    repeat_weekday = normalize_repeat_weekday(payload.repeat_weekday)

    now = utc_now_iso()
    with get_db() as conn:
        exists = conn.execute(
            "SELECT id FROM monthly_tasks WHERE id = ? AND owner_user_id = ?",
            (task_id, user_id),
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Zadanie cykliczne nie znalezione")

        conn.execute(
            """
            UPDATE monthly_tasks
            SET name = ?, due_day = ?, due_time = ?, repeat_type = ?, repeat_weekday = ?, updated_at = ?
            WHERE id = ?
            """,
            (name, due_day, due_time, repeat_type, repeat_weekday, now, task_id),
        )
        conn.commit()

    return {
        "status": "updated",
        "id": task_id,
        "name": name,
        "due_day": due_day,
        "due_time": due_time,
        "repeat_type": repeat_type,
        "repeat_weekday": repeat_weekday,
        "updated_at": now,
    }


@router.delete("/monthly-tasks/{task_id}")
def delete_monthly_task(task_id: int):
    user_id = _current_user_id()
    with get_db() as conn:
        exists = conn.execute(
            "SELECT id FROM monthly_tasks WHERE id = ? AND owner_user_id = ?",
            (task_id, user_id),
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Zadanie cykliczne nie znalezione")

        conn.execute("DELETE FROM monthly_tasks WHERE id = ?", (task_id,))
        conn.commit()

    return {"status": "deleted"}


@router.put("/monthly-tasks/{task_id}/state")
def update_monthly_task_state(task_id: int, payload: MonthlyTaskStatePayload):
    user_id = _current_user_id()
    with get_db() as conn:
        task_exists = conn.execute(
            "SELECT id, repeat_type FROM monthly_tasks WHERE id = ? AND owner_user_id = ?",
            (task_id, user_id),
        ).fetchone()
        if not task_exists:
            raise HTTPException(status_code=404, detail="Zadanie cykliczne nie znalezione")
        repeat_type = normalize_repeat_type(task_exists["repeat_type"] or "monthly")
        state_key = normalize_state_key(payload.month_key, repeat_type)

        existing_state = conn.execute(
            "SELECT done, note FROM monthly_task_states WHERE monthly_task_id = ? AND month_key = ?",
            (task_id, state_key),
        ).fetchone()

        if payload.note is not None:
            note = (payload.note or "").strip()
        else:
            note = existing_state["note"] if existing_state else ""

        if len(note) > 240:
            raise HTTPException(status_code=400, detail="Notatka moze miec maksymalnie 240 znakow")

        if payload.done is not None:
            done = 1 if payload.done else 0
        else:
            done = int(existing_state["done"]) if existing_state else 0

        now = utc_now_iso()
        conn.execute(
            """
            INSERT INTO monthly_task_states (monthly_task_id, month_key, done, note, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(monthly_task_id, month_key) DO UPDATE SET
                done = excluded.done,
                note = excluded.note,
                updated_at = excluded.updated_at
            """,
            (task_id, state_key, done, note, now),
        )
        conn.commit()

    return {
        "task_id": task_id,
        "month_key": state_key,
        "done": bool(done),
        "note": note,
        "updated_at": now,
    }
