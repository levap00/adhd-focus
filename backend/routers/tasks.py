import json

import requests
from fastapi import APIRouter, HTTPException

from backend.db import get_db
from backend.schemas import TaskCreate, TaskUpdate
from backend.utils import (
    normalize_due_date,
    normalize_priority,
    normalize_status,
    parse_non_negative_int,
)

router = APIRouter()


@router.get("/tasks")
def get_all_tasks():
    with get_db() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM tasks").fetchall()]


@router.post("/tasks")
def add_task(payload: TaskCreate):
    clean_name = (payload.name or "").strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Nazwa zadania nie moze byc pusta")

    clean_priority = normalize_priority(payload.priority)
    clean_status = normalize_status(payload.status)
    clean_description = (payload.description or "").strip()
    clean_due_date = normalize_due_date(payload.due_date)
    safe_estimated_time = parse_non_negative_int(payload.estimated_time)

    with get_db() as conn:
        module_exists = conn.execute(
            "SELECT 1 FROM modules WHERE id = ?",
            (payload.module_id,),
        ).fetchone()
        if not module_exists:
            raise HTTPException(status_code=404, detail="Modul nie znaleziony")

        cur = conn.execute(
            """
            INSERT INTO tasks (name, module_id, estimated_time, status, priority, description, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                clean_name,
                payload.module_id,
                safe_estimated_time,
                clean_status,
                clean_priority,
                clean_description,
                clean_due_date,
            ),
        )
        conn.commit()

    return {"id": cur.lastrowid}


@router.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):
    raw_update_data = task_data.model_dump(exclude_none=True)
    allowed_fields = {
        "status",
        "name",
        "module_id",
        "priority",
        "description",
        "due_date",
        "estimated_time",
    }
    update_data = {key: value for key, value in raw_update_data.items() if key in allowed_fields}

    if "name" in update_data:
        update_data["name"] = (update_data["name"] or "").strip()
        if not update_data["name"]:
            raise HTTPException(status_code=400, detail="Nazwa zadania nie moze byc pusta")

    if "priority" in update_data:
        update_data["priority"] = normalize_priority(update_data["priority"])

    if "status" in update_data:
        update_data["status"] = normalize_status(update_data["status"])

    if "description" in update_data:
        update_data["description"] = (update_data["description"] or "").strip()

    if "due_date" in update_data:
        update_data["due_date"] = normalize_due_date(update_data["due_date"])

    if "estimated_time" in update_data:
        update_data["estimated_time"] = parse_non_negative_int(update_data["estimated_time"])

    with get_db() as conn:
        existing_task = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not existing_task:
            raise HTTPException(status_code=404, detail="Zadanie nie znalezione")

        if "module_id" in update_data:
            module_exists = conn.execute(
                "SELECT 1 FROM modules WHERE id = ?",
                (update_data["module_id"],),
            ).fetchone()
            if not module_exists:
                raise HTTPException(status_code=404, detail="Modul nie znaleziony")

        if not update_data:
            return {"status": "no_updates"}

        keys = ", ".join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(task_id)
        conn.execute(f"UPDATE tasks SET {keys} WHERE id = ?", values)
        conn.commit()

    return {"status": "updated"}


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    return {"status": "deleted"}


@router.post("/tasks/{task_id}/shred")
def shred_task(task_id: int):
    with get_db() as conn:
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not task:
            raise HTTPException(status_code=404, detail="Zadanie nie znalezione")

    prompt = (
        f"Jestes asystentem produktywnosci. Zadanie: \"{task['name']}\". "
        "Rozbij je na 3-4 male kroki (max 15 min kazdy). "
        "Odpowiadaj po polsku w formacie JSON: {\"tasks\": [\"krok1\", \"krok2\"]}."
    )

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=35,
        )
        res.raise_for_status()

        response_payload = res.json()
        model_json = json.loads(response_payload.get("response", "{}"))
        sub_tasks = model_json.get("tasks", [])

        with get_db() as conn:
            conn.execute("UPDATE tasks SET status = 'gotowe' WHERE id = ?", (task_id,))
            for sub_task in sub_tasks:
                task_name = str(list(sub_task.values())[0]) if isinstance(sub_task, dict) else str(sub_task)
                task_name = task_name.strip()
                if not task_name:
                    continue
                conn.execute(
                    """
                    INSERT INTO tasks (name, module_id, status, estimated_time, priority)
                    VALUES (?, ?, 'oczekujace', 15, ?)
                    """,
                    (task_name, task["module_id"], task["priority"] or ""),
                )
            conn.commit()

        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - dependent on external model server
        return {"error": str(exc)}
