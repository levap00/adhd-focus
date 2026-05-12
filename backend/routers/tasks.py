import json
import re
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Query

from backend.db import get_db
from backend.schemas import TaskCreate, TaskUpdate
from backend.telegram import notify_task_closed
from backend.utils import (
    normalize_due_date,
    normalize_due_time,
    normalize_priority,
    normalize_status,
    parse_non_negative_float,
    parse_non_negative_int,
    utc_now_iso,
)

router = APIRouter()
MAX_SUBTASK_TITLE = 180
WORKDAY_LIMIT_MINUTES = 8 * 60
DONE_STAMP_RE = re.compile(r"\[Done:\s*(\d{4}-\d{2}-\d{2})\]")


def _normalize_subtasks(raw_subtasks: Any) -> list[dict]:
    normalized: list[dict] = []
    if not isinstance(raw_subtasks, list):
        return normalized

    for item in raw_subtasks:
        item_id = None
        title = ""
        done = False
        estimated_time = 0
        points_weight = 0.0

        if isinstance(item, dict):
            item_id = item.get("id")
            title = (item.get("title") or "").strip()
            done = bool(item.get("done"))
            estimated_time = parse_non_negative_int(item.get("estimated_time"), default=0)
            points_weight = parse_non_negative_float(item.get("points_weight"), default=0.0)
        else:
            item_id = getattr(item, "id", None)
            title = (getattr(item, "title", "") or "").strip()
            done = bool(getattr(item, "done", False))
            estimated_time = parse_non_negative_int(getattr(item, "estimated_time", 0), default=0)
            points_weight = parse_non_negative_float(getattr(item, "points_weight", 0.0), default=0.0)

        if not title:
            continue
        if len(title) > MAX_SUBTASK_TITLE:
            title = title[:MAX_SUBTASK_TITLE].rstrip()

        normalized_id = None
        if isinstance(item_id, int) and not isinstance(item_id, bool):
            normalized_id = item_id
        elif isinstance(item_id, str) and item_id.isdigit():
            normalized_id = int(item_id)

        normalized.append(
            {
                "id": normalized_id,
                "title": title,
                "done": done,
                "estimated_time": estimated_time,
                "points_weight": round(max(0.0, points_weight), 2),
                "position": len(normalized),
            }
        )
    return normalized


def _list_subtasks_by_task_ids(conn, task_ids: list[int]) -> dict[int, list[dict]]:
    if not task_ids:
        return {}
    placeholders = ", ".join(["?"] * len(task_ids))
    rows = conn.execute(
        f"""
        SELECT id, task_id, title, position, done, estimated_time, points_weight, done_at
        FROM task_subtasks
        WHERE task_id IN ({placeholders})
        ORDER BY task_id ASC, position ASC, id ASC
        """,
        task_ids,
    ).fetchall()
    grouped: dict[int, list[dict]] = {task_id: [] for task_id in task_ids}
    for row in rows:
        task_id = int(row["task_id"])
        grouped.setdefault(task_id, []).append(
            {
                "id": int(row["id"]),
                "title": row["title"] or "",
                "done": bool(row["done"]),
                "estimated_time": parse_non_negative_int(row["estimated_time"], default=0),
                "points_weight": round(max(0.0, parse_non_negative_float(row["points_weight"], default=0.0)), 2),
                "position": int(row["position"] or 0),
                "done_at": row["done_at"] or "",
            }
        )
    return grouped


def _replace_task_subtasks(conn, task_id: int, subtasks: list[dict]) -> None:
    existing_rows = conn.execute(
        """
        SELECT id, done, done_at, created_at
        FROM task_subtasks
        WHERE task_id = ?
        """,
        (task_id,),
    ).fetchall()
    existing_by_id = {int(row["id"]): dict(row) for row in existing_rows}
    now = utc_now_iso()

    conn.execute("DELETE FROM task_subtasks WHERE task_id = ?", (task_id,))

    for subtask in subtasks:
        prev = existing_by_id.get(int(subtask["id"])) if subtask.get("id") else None
        done = 1 if subtask.get("done") else 0
        if done:
            if prev and int(prev.get("done") or 0) == 1 and (prev.get("done_at") or "").strip():
                done_at = prev.get("done_at") or now
            else:
                done_at = now
        else:
            done_at = ""

        created_at = (prev or {}).get("created_at") or now

        conn.execute(
            """
            INSERT INTO task_subtasks (task_id, title, position, done, estimated_time, points_weight, done_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                subtask["title"],
                int(subtask["position"]),
                done,
                parse_non_negative_int(subtask.get("estimated_time"), default=0),
                round(max(0.0, parse_non_negative_float(subtask.get("points_weight"), default=0.0)), 2),
                done_at,
                created_at,
                now,
            ),
        )


def _normalize_points_weight(raw_value: Any) -> float:
    value = parse_non_negative_float(raw_value, default=1.0)
    if value <= 0:
        raise HTTPException(status_code=400, detail="Waga zadania musi byc wieksza od 0.")
    return round(value, 2)


def _calculate_subtasks_totals(subtasks: list[dict]) -> dict[str, float | int]:
    if not subtasks:
        return {"estimated_time": 0, "points_weight": 0.0}

    total_minutes = 0
    total_points = 0.0
    for index, subtask in enumerate(subtasks, start=1):
        estimated_time = parse_non_negative_int(subtask.get("estimated_time"), default=0)
        points_weight = round(max(0.0, parse_non_negative_float(subtask.get("points_weight"), default=0.0)), 2)
        if estimated_time <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Podzadanie #{index} musi miec czas wiekszy od 0 minut.",
            )
        if points_weight <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Podzadanie #{index} musi miec punkty wieksze od 0.",
            )
        total_minutes += estimated_time
        total_points += points_weight

    return {
        "estimated_time": total_minutes,
        "points_weight": round(total_points, 2),
    }


def _get_task_done_date(description: str) -> str:
    matches = DONE_STAMP_RE.findall(description or "")
    if not matches:
        return ""
    return normalize_due_date(matches[-1])


def _task_limit_date(due_date: str, status: str, description: str) -> str:
    if normalize_status(status) == "gotowe":
        return _get_task_done_date(description)
    return normalize_due_date(due_date)


def _task_minutes_for_workload_date(
    target_date: str,
    due_date: str,
    estimated_time: int,
    status: str,
    description: str,
) -> int:
    clean_target_date = normalize_due_date(target_date)
    if not clean_target_date:
        return 0
    if normalize_status(status) == "gotowe":
        return parse_non_negative_int(estimated_time) if _get_task_done_date(description) == clean_target_date else 0
    return parse_non_negative_int(estimated_time) if normalize_due_date(due_date) == clean_target_date else 0


def _get_daily_planned_minutes(conn, due_date: str, exclude_task_id: int | None = None) -> int:
    clean_due_date = normalize_due_date(due_date)
    if not clean_due_date:
        return 0

    query = """
        SELECT id, due_date, estimated_time, status, description
        FROM tasks
        WHERE (
            (due_date = ? AND status != 'gotowe')
            OR (status = 'gotowe' AND description LIKE ?)
        )
    """
    params: list[Any] = [clean_due_date, f"%[Done: {clean_due_date}]%"]
    if exclude_task_id is not None:
        query += " AND id != ?"
        params.append(exclude_task_id)

    rows = conn.execute(query, params).fetchall()
    total = 0
    counted_task_ids: list[int] = []
    for row in rows:
        minutes = _task_minutes_for_workload_date(
            clean_due_date,
            row["due_date"] or "",
            row["estimated_time"],
            row["status"] or "",
            row["description"] or "",
        )
        if minutes > 0:
            total += minutes
            counted_task_ids.append(int(row["id"]))

    subtask_query = """
        SELECT task_id, estimated_time
        FROM task_subtasks
        WHERE done_at LIKE ?
          AND estimated_time > 0
    """
    subtask_params: list[Any] = [f"{clean_due_date}%"]
    if exclude_task_id is not None:
        subtask_query += " AND task_id != ?"
        subtask_params.append(exclude_task_id)
    if counted_task_ids:
        placeholders = ", ".join(["?"] * len(counted_task_ids))
        subtask_query += f" AND task_id NOT IN ({placeholders})"
        subtask_params.extend(counted_task_ids)

    subtask_rows = conn.execute(subtask_query, subtask_params).fetchall()
    total += sum(parse_non_negative_int(row["estimated_time"]) for row in subtask_rows)
    return total


def _format_minutes(minutes: int) -> str:
    safe_minutes = parse_non_negative_int(minutes)
    hours = safe_minutes // 60
    rest = safe_minutes % 60
    if hours and rest:
        return f"{hours}h {rest} min"
    if hours:
        return f"{hours}h"
    return f"{rest} min"


def _enforce_workday_limit(
    due_date: str,
    planned_before_minutes: int,
    task_minutes: int,
    allow_overflow: bool,
) -> None:
    clean_due_date = normalize_due_date(due_date)
    if not clean_due_date or allow_overflow:
        return

    projected = parse_non_negative_int(planned_before_minutes) + parse_non_negative_int(task_minutes)
    if projected <= WORKDAY_LIMIT_MINUTES:
        return

    raise HTTPException(
        status_code=409,
        detail={
            "code": "daily_limit_exceeded",
            "message": (
                f"Plan na {clean_due_date} przekroczy 8h (aktualnie {_format_minutes(projected)}). "
                "Mozesz zapisac mimo to, jesli to swiadomy wyjatek."
            ),
            "date": clean_due_date,
            "projected_minutes": projected,
            "limit_minutes": WORKDAY_LIMIT_MINUTES,
        },
    )


@router.get("/tasks")
def get_all_tasks():
    with get_db() as conn:
        tasks = [dict(row) for row in conn.execute("SELECT * FROM tasks").fetchall()]
        task_ids = [int(task["id"]) for task in tasks]
        subtasks_by_task = _list_subtasks_by_task_ids(conn, task_ids)
        for task in tasks:
            task["subtasks"] = subtasks_by_task.get(int(task["id"]), [])
        return tasks


@router.get("/tasks/workload")
def get_day_workload(
    date: str = Query(..., alias="date"),
    exclude_task_id: int | None = Query(None),
):
    clean_date = normalize_due_date(date)
    if not clean_date:
        raise HTTPException(status_code=400, detail="Niepoprawna data (format YYYY-MM-DD).")

    with get_db() as conn:
        planned_minutes = _get_daily_planned_minutes(conn, clean_date, exclude_task_id=exclude_task_id)

    return {
        "date": clean_date,
        "planned_minutes": planned_minutes,
        "limit_minutes": WORKDAY_LIMIT_MINUTES,
        "is_over_limit": planned_minutes > WORKDAY_LIMIT_MINUTES,
        "includes_carry_over": False,
    }


@router.post("/tasks")
def add_task(payload: TaskCreate):
    clean_name = (payload.name or "").strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Nazwa zadania nie moze byc pusta")

    clean_priority = normalize_priority(payload.priority)
    clean_status = normalize_status(payload.status)
    clean_description = (payload.description or "").strip()
    clean_due_date = normalize_due_date(payload.due_date)
    clean_due_time = normalize_due_time(payload.due_time, default="14:00") if clean_due_date else ""
    safe_estimated_time = parse_non_negative_int(payload.estimated_time)
    safe_points_weight = _normalize_points_weight(payload.points_weight)
    allow_time_overflow = bool(payload.allow_time_overflow)
    clean_subtasks = _normalize_subtasks(payload.subtasks)
    if clean_subtasks:
        subtasks_totals = _calculate_subtasks_totals(clean_subtasks)
        safe_estimated_time = parse_non_negative_int(subtasks_totals["estimated_time"], default=0)
        safe_points_weight = _normalize_points_weight(subtasks_totals["points_weight"])
    elif safe_estimated_time <= 0:
        raise HTTPException(status_code=400, detail="Podaj szacowany czas zadania (minuty, wiecej niz 0).")

    with get_db() as conn:
        module_exists = conn.execute(
            "SELECT 1 FROM modules WHERE id = ?",
            (payload.module_id,),
        ).fetchone()
        if not module_exists:
            raise HTTPException(status_code=404, detail="Modul nie znaleziony")

        limit_date = _task_limit_date(clean_due_date, clean_status, clean_description)
        planned_before = _get_daily_planned_minutes(conn, limit_date)
        task_minutes = _task_minutes_for_workload_date(
            limit_date,
            clean_due_date,
            safe_estimated_time,
            clean_status,
            clean_description,
        )
        _enforce_workday_limit(limit_date, planned_before, task_minutes, allow_time_overflow)

        cur = conn.execute(
            """
            INSERT INTO tasks (name, module_id, estimated_time, points_weight, status, priority, description, due_date, due_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                clean_name,
                payload.module_id,
                safe_estimated_time,
                safe_points_weight,
                clean_status,
                clean_priority,
                clean_description,
                clean_due_date,
                clean_due_time,
            ),
        )
        task_id = int(cur.lastrowid)
        if clean_subtasks:
            _replace_task_subtasks(conn, task_id, clean_subtasks)
        conn.commit()

    return {"id": task_id}


@router.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):
    raw_update_data = task_data.model_dump(exclude_none=True)
    allow_time_overflow = bool(raw_update_data.pop("allow_time_overflow", False))
    subtasks_data = _normalize_subtasks(raw_update_data.get("subtasks")) if "subtasks" in raw_update_data else None
    allowed_fields = {
        "status",
        "name",
        "module_id",
        "priority",
        "description",
        "due_date",
        "due_time",
        "estimated_time",
        "points_weight",
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

    if "estimated_time" in update_data:
        update_data["estimated_time"] = parse_non_negative_int(update_data["estimated_time"])
        if update_data["estimated_time"] <= 0:
            raise HTTPException(status_code=400, detail="Szacowany czas zadania musi byc wiekszy od 0.")

    if "points_weight" in update_data:
        update_data["points_weight"] = _normalize_points_weight(update_data["points_weight"])

    with get_db() as conn:
        existing_task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not existing_task:
            raise HTTPException(status_code=404, detail="Zadanie nie znalezione")

        existing_task = dict(existing_task)

        if "module_id" in update_data:
            module_exists = conn.execute(
                "SELECT 1 FROM modules WHERE id = ?",
                (update_data["module_id"],),
            ).fetchone()
            if not module_exists:
                raise HTTPException(status_code=404, detail="Modul nie znaleziony")

        if "due_date" in update_data or "due_time" in update_data:
            next_due_date = normalize_due_date(update_data.get("due_date", existing_task.get("due_date", "")))
            due_time_default = "14:00" if next_due_date else ""
            next_due_time = normalize_due_time(
                update_data.get("due_time", existing_task.get("due_time", "")),
                default=due_time_default,
            )
            update_data["due_date"] = next_due_date
            update_data["due_time"] = next_due_time if next_due_date else ""

        if subtasks_data is not None and len(subtasks_data) > 0:
            subtasks_totals = _calculate_subtasks_totals(subtasks_data)
            update_data["estimated_time"] = parse_non_negative_int(subtasks_totals["estimated_time"], default=0)
            update_data["points_weight"] = _normalize_points_weight(subtasks_totals["points_weight"])

        if not update_data and subtasks_data is None:
            return {"status": "no_updates"}

        next_due_date_for_limit = update_data.get("due_date", existing_task.get("due_date", ""))
        next_estimated_time = parse_non_negative_int(update_data.get("estimated_time", existing_task.get("estimated_time", 0)))
        next_status_for_limit = update_data.get("status", existing_task.get("status", ""))
        next_description_for_limit = update_data.get("description", existing_task.get("description", ""))
        limit_date = _task_limit_date(next_due_date_for_limit, next_status_for_limit, next_description_for_limit)
        planned_before = _get_daily_planned_minutes(conn, limit_date, exclude_task_id=task_id)
        task_minutes = _task_minutes_for_workload_date(
            limit_date,
            next_due_date_for_limit,
            next_estimated_time,
            next_status_for_limit,
            next_description_for_limit,
        )
        _enforce_workday_limit(limit_date, planned_before, task_minutes, allow_time_overflow)

        was_open = normalize_status(existing_task.get("status", "")) != "gotowe"
        next_status = update_data.get("status", existing_task.get("status", ""))
        will_be_open = normalize_status(next_status) != "gotowe"

        if update_data:
            keys = ", ".join([f"{key} = ?" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(task_id)
            conn.execute(f"UPDATE tasks SET {keys} WHERE id = ?", values)

        if subtasks_data is not None:
            _replace_task_subtasks(conn, task_id, subtasks_data)

        conn.commit()

    if was_open and not will_be_open:
        notify_task_closed(update_data.get("name") or existing_task.get("name") or "(bez nazwy)")

    return {"status": "updated"}


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    task_name = ""
    was_open = False

    with get_db() as conn:
        task = conn.execute("SELECT name, status FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if task:
            task_name = task["name"] or "(bez nazwy)"
            was_open = normalize_status(task["status"]) != "gotowe"

        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

    if was_open:
        notify_task_closed(task_name)

    return {"status": "deleted"}


@router.post("/tasks/{task_id}/shred")
def shred_task(task_id: int):
    with get_db() as conn:
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not task:
            raise HTTPException(status_code=404, detail="Zadanie nie znalezione")
    was_open_before_shred = normalize_status(task["status"]) != "gotowe"

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
                    INSERT INTO tasks (name, module_id, status, estimated_time, priority, due_date, due_time)
                    VALUES (?, ?, 'oczekujace', 15, ?, '', '')
                    """,
                    (task_name, task["module_id"], task["priority"] or ""),
                )
            conn.commit()

        if was_open_before_shred:
            notify_task_closed(task["name"] or "(bez nazwy)")
        return {"status": "ok"}
    except Exception as exc:  # pragma: no cover - dependent on external model server
        return {"error": str(exc)}
