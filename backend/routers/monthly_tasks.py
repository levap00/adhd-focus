from fastapi import APIRouter, HTTPException, Query

from backend.db import get_db
from backend.schemas import MonthlyTaskCreate, MonthlyTaskStatePayload, MonthlyTaskUpdate
from backend.utils import normalize_month_key, parse_non_negative_int, utc_now_iso

router = APIRouter()


@router.get("/monthly-tasks")
def get_monthly_tasks(month: str = Query(default="")):
    month_key = normalize_month_key(month)
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT
                mt.id,
                mt.name,
                COALESCE(mt.due_day, 0) AS due_day,
                mt.created_at,
                mt.updated_at,
                COALESCE(ms.done, 0) AS done,
                COALESCE(ms.note, '') AS note,
                COALESCE(ms.updated_at, '') AS state_updated_at
            FROM monthly_tasks mt
            LEFT JOIN monthly_task_states ms
                ON ms.monthly_task_id = mt.id
                AND ms.month_key = ?
            ORDER BY mt.id DESC
            """,
            (month_key,),
        ).fetchall()

    items = []
    done_count = 0
    for row in rows:
        item = dict(row)
        item["done"] = bool(item.get("done"))
        if item["done"]:
            done_count += 1
        item["month_key"] = month_key
        items.append(item)

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
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Nazwa zadania miesiecznego nie moze byc pusta")
    due_day = min(31, parse_non_negative_int(payload.due_day))

    now = utc_now_iso()
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO monthly_tasks (name, due_day, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (name, due_day, now, now),
        )
        conn.commit()

    return {"id": cur.lastrowid, "name": name, "due_day": due_day, "created_at": now, "updated_at": now}


@router.put("/monthly-tasks/{task_id}")
def update_monthly_task(task_id: int, payload: MonthlyTaskUpdate):
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Nazwa zadania miesiecznego nie moze byc pusta")
    due_day = min(31, parse_non_negative_int(payload.due_day))

    now = utc_now_iso()
    with get_db() as conn:
        exists = conn.execute("SELECT id FROM monthly_tasks WHERE id = ?", (task_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Zadanie miesieczne nie znalezione")

        conn.execute(
            "UPDATE monthly_tasks SET name = ?, due_day = ?, updated_at = ? WHERE id = ?",
            (name, due_day, now, task_id),
        )
        conn.commit()

    return {"status": "updated", "id": task_id, "name": name, "due_day": due_day, "updated_at": now}


@router.delete("/monthly-tasks/{task_id}")
def delete_monthly_task(task_id: int):
    with get_db() as conn:
        exists = conn.execute("SELECT id FROM monthly_tasks WHERE id = ?", (task_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Zadanie miesieczne nie znalezione")

        conn.execute("DELETE FROM monthly_tasks WHERE id = ?", (task_id,))
        conn.commit()

    return {"status": "deleted"}


@router.put("/monthly-tasks/{task_id}/state")
def update_monthly_task_state(task_id: int, payload: MonthlyTaskStatePayload):
    month_key = normalize_month_key(payload.month_key)

    with get_db() as conn:
        task_exists = conn.execute("SELECT id FROM monthly_tasks WHERE id = ?", (task_id,)).fetchone()
        if not task_exists:
            raise HTTPException(status_code=404, detail="Zadanie miesieczne nie znalezione")

        existing_state = conn.execute(
            "SELECT done, note FROM monthly_task_states WHERE monthly_task_id = ? AND month_key = ?",
            (task_id, month_key),
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
            (task_id, month_key, done, note, now),
        )
        conn.commit()

    return {
        "task_id": task_id,
        "month_key": month_key,
        "done": bool(done),
        "note": note,
        "updated_at": now,
    }
