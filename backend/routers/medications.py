from datetime import date

from fastapi import APIRouter, HTTPException, Query

from backend.db import get_db
from backend.schemas import MedicationCreate, MedicationStatePayload, MedicationUpdate
from backend.utils import normalize_due_date, normalize_due_time, utc_now_iso

router = APIRouter()


def normalize_medication_schedule_type(raw: str | None) -> str:
    value = (raw or "daily").strip().lower()
    if value in {"weekdays", "weekday", "workdays", "workday", "pon-pt", "mon-fri"}:
        return "weekdays"
    return "daily"


def normalize_medication_date(raw: str | None = None) -> str:
    return normalize_due_date(raw) or date.today().isoformat()


def is_medication_scheduled_for_date(schedule_type: str, date_key: str) -> bool:
    clean_date = normalize_medication_date(date_key)
    point = date.fromisoformat(clean_date)
    if normalize_medication_schedule_type(schedule_type) == "weekdays":
        return point.isoweekday() <= 5
    return True


def _normalize_reminder_time(raw: str | None) -> str:
    return normalize_due_time(raw, default="08:00") or "08:00"


def _row_to_item(row, state, date_key: str) -> dict:
    schedule_type = normalize_medication_schedule_type(row["schedule_type"])
    scheduled_today = is_medication_scheduled_for_date(schedule_type, date_key)
    done = bool(state["done"]) if state else False
    return {
        "id": int(row["id"]),
        "name": row["name"] or "",
        "schedule_type": schedule_type,
        "reminder_time": _normalize_reminder_time(row["reminder_time"]),
        "active": bool(row["active"]),
        "date_key": date_key,
        "scheduled_today": scheduled_today,
        "done": done,
        "done_at": (state["done_at"] if state else "") or "",
        "state_updated_at": (state["updated_at"] if state else "") or "",
        "created_at": row["created_at"] or "",
        "updated_at": row["updated_at"] or "",
    }


@router.get("/medications")
def get_medications(date_key: str = Query(default="", alias="date")):
    clean_date = normalize_medication_date(date_key)
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, name, schedule_type, reminder_time, active, created_at, updated_at
            FROM medication_reminders
            WHERE active = 1
            ORDER BY reminder_time ASC, name COLLATE NOCASE ASC, id ASC
            """
        ).fetchall()

        states = {
            int(row["medication_id"]): dict(row)
            for row in conn.execute(
                """
                SELECT medication_id, done, done_at, updated_at
                FROM medication_states
                WHERE date_key = ?
                """,
                (clean_date,),
            ).fetchall()
        }

    items = [_row_to_item(row, states.get(int(row["id"])), clean_date) for row in rows]
    scheduled_items = [item for item in items if item["scheduled_today"]]
    done_count = sum(1 for item in scheduled_items if item["done"])
    return {
        "date_key": clean_date,
        "items": items,
        "summary": {
            "total": len(items),
            "scheduled": len(scheduled_items),
            "done": done_count,
            "open": len(scheduled_items) - done_count,
        },
    }


@router.post("/medications")
def add_medication(payload: MedicationCreate):
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Nazwa leku nie moze byc pusta")
    schedule_type = normalize_medication_schedule_type(payload.schedule_type)
    reminder_time = _normalize_reminder_time(payload.reminder_time)
    now = utc_now_iso()

    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO medication_reminders (name, schedule_type, reminder_time, active, created_at, updated_at)
            VALUES (?, ?, ?, 1, ?, ?)
            """,
            (name, schedule_type, reminder_time, now, now),
        )
        conn.commit()

    return {
        "id": int(cur.lastrowid),
        "name": name,
        "schedule_type": schedule_type,
        "reminder_time": reminder_time,
        "active": True,
        "created_at": now,
        "updated_at": now,
    }


@router.put("/medications/{medication_id}")
def update_medication(medication_id: int, payload: MedicationUpdate):
    update_data = payload.model_dump(exclude_none=True)
    if not update_data:
        return {"status": "no_updates"}

    allowed_fields = {"name", "schedule_type", "reminder_time", "active"}
    update_data = {key: value for key, value in update_data.items() if key in allowed_fields}
    if "name" in update_data:
        update_data["name"] = (update_data["name"] or "").strip()
        if not update_data["name"]:
            raise HTTPException(status_code=400, detail="Nazwa leku nie moze byc pusta")
    if "schedule_type" in update_data:
        update_data["schedule_type"] = normalize_medication_schedule_type(update_data["schedule_type"])
    if "reminder_time" in update_data:
        update_data["reminder_time"] = _normalize_reminder_time(update_data["reminder_time"])
    if "active" in update_data:
        update_data["active"] = 1 if update_data["active"] else 0

    update_data["updated_at"] = utc_now_iso()

    with get_db() as conn:
        exists = conn.execute("SELECT id FROM medication_reminders WHERE id = ?", (medication_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Lek nie znaleziony")
        keys = ", ".join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(medication_id)
        conn.execute(f"UPDATE medication_reminders SET {keys} WHERE id = ?", values)
        conn.commit()

    return {"status": "updated", "id": medication_id}


@router.delete("/medications/{medication_id}")
def delete_medication(medication_id: int):
    with get_db() as conn:
        exists = conn.execute("SELECT id FROM medication_reminders WHERE id = ?", (medication_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Lek nie znaleziony")
        conn.execute("DELETE FROM medication_reminders WHERE id = ?", (medication_id,))
        conn.commit()

    return {"status": "deleted"}


@router.put("/medications/{medication_id}/state")
def update_medication_state(medication_id: int, payload: MedicationStatePayload):
    clean_date = normalize_medication_date(payload.date_key)
    done = 1 if payload.done else 0
    now = utc_now_iso()
    done_at = now if done else ""

    with get_db() as conn:
        exists = conn.execute("SELECT id FROM medication_reminders WHERE id = ?", (medication_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Lek nie znaleziony")

        conn.execute(
            """
            INSERT INTO medication_states (medication_id, date_key, done, done_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(medication_id, date_key) DO UPDATE SET
                done = excluded.done,
                done_at = excluded.done_at,
                updated_at = excluded.updated_at
            """,
            (medication_id, clean_date, done, done_at, now),
        )
        conn.commit()

    return {
        "medication_id": medication_id,
        "date_key": clean_date,
        "done": bool(done),
        "done_at": done_at,
        "updated_at": now,
    }
