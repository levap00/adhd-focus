import re
from calendar import monthrange
from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Query

from backend.accounts import get_user_by_username
from backend.auth import get_request_user
from backend.db import get_db
from backend.schemas import MonthlyTaskCreate, MonthlyTaskStatePayload, MonthlyTaskUpdate
from backend.utils import normalize_month_key, parse_non_negative_int, utc_now_iso

router = APIRouter()
WEEK_KEY_PATTERN = re.compile(r"^week:(\d{4}-\d{2}-\d{2})$")


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
    if re.fullmatch(r"\d{4}-\d{2}", value):
        return value
    if WEEK_KEY_PATTERN.fullmatch(value):
        return value
    if repeat_type == "weekly":
        return current_week_state_key()
    return normalize_month_key(value)


def get_occurrence_date_keys(month_key: str, repeat_type: str, due_day: int, repeat_weekday: int) -> list[str]:
    year, month = month_key.split("-")
    year_num = int(year)
    month_num = int(month)
    days_in_month = monthrange(year_num, month_num)[1]

    if repeat_type == "weekly":
        entries: list[str] = []
        for day in range(1, days_in_month + 1):
            point = date(year_num, month_num, day)
            if point.isoweekday() == repeat_weekday:
                entries.append(point.isoformat())
        return entries

    if due_day <= 0:
        return []
    normalized_day = min(days_in_month, max(1, due_day))
    return [f"{year_num:04d}-{month_num:02d}-{normalized_day:02d}"]


@router.get("/monthly-tasks")
def get_monthly_tasks(month: str = Query(default="")):
    user_id = _current_user_id()
    month_key = normalize_month_key(month)
    with get_db() as conn:
        base_rows = conn.execute(
            """
            SELECT
                mt.id,
                mt.name,
                COALESCE(mt.due_day, 0) AS due_day,
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

        occurrence_date_keys = get_occurrence_date_keys(
            month_key=month_key,
            repeat_type=repeat_type,
            due_day=due_day,
            repeat_weekday=repeat_weekday,
        )
        if not occurrence_date_keys:
            occurrence_date_keys = [""]

        for date_key in occurrence_date_keys:
            state_key = to_week_state_key(date_key) if repeat_type == "weekly" and date_key else month_key
            state = states_by_key.get((task_id, state_key), {"done": False, "note": "", "updated_at": ""})
            done = bool(state["done"])
            if done:
                done_count += 1
            items.append(
                {
                    "id": task_id,
                    "instance_id": f"{task_id}:{state_key}:{date_key or 'none'}",
                    "name": row["name"] or "",
                    "due_day": due_day,
                    "repeat_type": repeat_type,
                    "repeat_weekday": repeat_weekday,
                    "date_key": date_key,
                    "state_key": state_key,
                    "done": done,
                    "note": state["note"],
                    "state_updated_at": state["updated_at"],
                    "created_at": row["created_at"] or "",
                    "updated_at": row["updated_at"] or "",
                    "month_key": month_key,
                }
            )

    items = sorted(
        items,
        key=lambda item: (
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
        raise HTTPException(status_code=400, detail="Nazwa zadania miesiecznego nie moze byc pusta")
    repeat_type = normalize_repeat_type(payload.repeat_type)
    due_day = min(31, parse_non_negative_int(payload.due_day)) if repeat_type == "monthly" else 0
    repeat_weekday = normalize_repeat_weekday(payload.repeat_weekday)

    now = utc_now_iso()
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO monthly_tasks (name, due_day, repeat_type, repeat_weekday, owner_user_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, due_day, repeat_type, repeat_weekday, user_id, now, now),
        )
        conn.commit()

    return {
        "id": cur.lastrowid,
        "name": name,
        "due_day": due_day,
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
        raise HTTPException(status_code=400, detail="Nazwa zadania miesiecznego nie moze byc pusta")
    repeat_type = normalize_repeat_type(payload.repeat_type)
    due_day = min(31, parse_non_negative_int(payload.due_day)) if repeat_type == "monthly" else 0
    repeat_weekday = normalize_repeat_weekday(payload.repeat_weekday)

    now = utc_now_iso()
    with get_db() as conn:
        exists = conn.execute(
            "SELECT id FROM monthly_tasks WHERE id = ? AND owner_user_id = ?",
            (task_id, user_id),
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Zadanie miesieczne nie znalezione")

        conn.execute(
            """
            UPDATE monthly_tasks
            SET name = ?, due_day = ?, repeat_type = ?, repeat_weekday = ?, updated_at = ?
            WHERE id = ?
            """,
            (name, due_day, repeat_type, repeat_weekday, now, task_id),
        )
        conn.commit()

    return {
        "status": "updated",
        "id": task_id,
        "name": name,
        "due_day": due_day,
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
            raise HTTPException(status_code=404, detail="Zadanie miesieczne nie znalezione")

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
            raise HTTPException(status_code=404, detail="Zadanie miesieczne nie znalezione")
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
