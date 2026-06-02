import json
import re
from datetime import datetime, timezone
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Query

from backend.db import get_db
from backend.schemas import TaskCreate, TaskMergePayload, TaskUpdate
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


def _normalize_optional_int(raw_value: Any) -> int | None:
    if isinstance(raw_value, int) and not isinstance(raw_value, bool):
        return raw_value
    if isinstance(raw_value, str) and raw_value.isdigit():
        return int(raw_value)
    return None


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
        done_at = ""
        source_task_id = None
        source_module_id = None
        source_due_date = ""
        source_due_time = ""

        if isinstance(item, dict):
            item_id = item.get("id")
            title = (item.get("title") or "").strip()
            done = bool(item.get("done"))
            estimated_time = parse_non_negative_int(item.get("estimated_time"), default=0)
            points_weight = parse_non_negative_float(item.get("points_weight"), default=0.0)
            done_at = (item.get("done_at") or "").strip()
            source_task_id = _normalize_optional_int(item.get("source_task_id"))
            source_module_id = _normalize_optional_int(item.get("source_module_id"))
            source_due_date = normalize_due_date(item.get("source_due_date"))
            source_due_time = normalize_due_time(item.get("source_due_time"), default="")
        else:
            item_id = getattr(item, "id", None)
            title = (getattr(item, "title", "") or "").strip()
            done = bool(getattr(item, "done", False))
            estimated_time = parse_non_negative_int(getattr(item, "estimated_time", 0), default=0)
            points_weight = parse_non_negative_float(getattr(item, "points_weight", 0.0), default=0.0)
            done_at = (getattr(item, "done_at", "") or "").strip()
            source_task_id = _normalize_optional_int(getattr(item, "source_task_id", None))
            source_module_id = _normalize_optional_int(getattr(item, "source_module_id", None))
            source_due_date = normalize_due_date(getattr(item, "source_due_date", ""))
            source_due_time = normalize_due_time(getattr(item, "source_due_time", ""), default="")

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
                "done_at": done_at,
                "source_task_id": source_task_id,
                "source_module_id": source_module_id,
                "source_due_date": source_due_date,
                "source_due_time": source_due_time,
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
        SELECT
            id,
            task_id,
            title,
            position,
            done,
            estimated_time,
            points_weight,
            done_at,
            source_task_id,
            source_module_id,
            source_due_date,
            source_due_time
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
                "source_task_id": int(row["source_task_id"]) if row["source_task_id"] is not None else None,
                "source_module_id": int(row["source_module_id"]) if row["source_module_id"] is not None else None,
                "source_due_date": normalize_due_date(row["source_due_date"] or ""),
                "source_due_time": normalize_due_time(row["source_due_time"] or "", default=""),
            }
        )
    return grouped


def _replace_task_subtasks(conn, task_id: int, subtasks: list[dict]) -> None:
    existing_rows = conn.execute(
        """
        SELECT
            id,
            done,
            done_at,
            source_task_id,
            source_module_id,
            source_due_date,
            source_due_time,
            created_at
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
            elif (subtask.get("done_at") or "").strip():
                done_at = (subtask.get("done_at") or "").strip()
            else:
                done_at = now
        else:
            done_at = ""

        created_at = (prev or {}).get("created_at") or now
        source_task_id = _normalize_optional_int(subtask.get("source_task_id"))
        if source_task_id is None and prev:
            source_task_id = _normalize_optional_int(prev.get("source_task_id"))
        source_module_id = _normalize_optional_int(subtask.get("source_module_id"))
        if source_module_id is None and prev:
            source_module_id = _normalize_optional_int(prev.get("source_module_id"))
        source_due_date = normalize_due_date(subtask.get("source_due_date") or (prev or {}).get("source_due_date") or "")
        source_due_time = normalize_due_time(
            subtask.get("source_due_time") or (prev or {}).get("source_due_time") or "",
            default="",
        )

        conn.execute(
            """
            INSERT INTO task_subtasks (
                task_id,
                title,
                position,
                done,
                estimated_time,
                points_weight,
                done_at,
                source_task_id,
                source_module_id,
                source_due_date,
                source_due_time,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                subtask["title"],
                int(subtask["position"]),
                done,
                parse_non_negative_int(subtask.get("estimated_time"), default=0),
                round(max(0.0, parse_non_negative_float(subtask.get("points_weight"), default=0.0)), 2),
                done_at,
                source_task_id,
                source_module_id,
                source_due_date,
                source_due_time,
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


def _get_daily_planned_minutes(
    conn,
    due_date: str,
    exclude_task_id: int | None = None,
    exclude_task_ids: list[int] | None = None,
) -> int:
    clean_due_date = normalize_due_date(due_date)
    if not clean_due_date:
        return 0
    excluded_ids = {
        int(task_id)
        for task_id in (exclude_task_ids or [])
        if isinstance(task_id, int) and not isinstance(task_id, bool)
    }
    if exclude_task_id is not None:
        excluded_ids.add(int(exclude_task_id))

    query = """
        SELECT id, due_date, estimated_time, status, description
        FROM tasks
        WHERE (
            (due_date = ? AND status != 'gotowe')
            OR (status = 'gotowe' AND description LIKE ?)
        )
    """
    params: list[Any] = [clean_due_date, f"%[Done: {clean_due_date}]%"]
    if excluded_ids:
        placeholders = ", ".join(["?"] * len(excluded_ids))
        query += f" AND id NOT IN ({placeholders})"
        params.extend(sorted(excluded_ids))

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
    if excluded_ids:
        placeholders = ", ".join(["?"] * len(excluded_ids))
        subtask_query += f" AND task_id NOT IN ({placeholders})"
        subtask_params.extend(sorted(excluded_ids))
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


def _priority_rank(priority: str) -> int:
    return {"P1": 0, "P2": 1, "P3": 2, "": 3}.get(normalize_priority(priority), 3)


def _widget_bucket_rank(bucket: str) -> int:
    return {"overdue": 0, "today": 1, "done": 2}.get(bucket, 3)


def _sort_widget_tasks(tasks: list[dict]) -> list[dict]:
    def sort_key(task: dict) -> tuple[int, int, str, int, str, str]:
        bucket = (task.get("bucket") or "").strip().lower()
        priority = normalize_priority(task.get("priority") or "")
        due_time = normalize_due_time(task.get("due_time") or "", default="23:59") or "23:59"
        estimated_time = parse_non_negative_int(task.get("estimated_time"), default=0)
        module_name = (task.get("module_name") or "").strip().lower()
        task_name = (task.get("name") or "").strip().lower()
        return (
            _widget_bucket_rank(bucket),
            _priority_rank(priority),
            due_time,
            -estimated_time,
            module_name,
            task_name,
        )

    return sorted(tasks, key=sort_key)


def _today_key_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _clip_subtask_title(title: str) -> str:
    clean_title = (title or "").strip()
    if len(clean_title) > MAX_SUBTASK_TITLE:
        clean_title = clean_title[:MAX_SUBTASK_TITLE].rstrip()
    return clean_title or "(bez nazwy)"


def _get_task_done_at(task: dict) -> str:
    done_date = _get_task_done_date(task.get("description") or "")
    if done_date:
        return f"{done_date}T12:00:00+00:00"
    if normalize_status(task.get("status")) == "gotowe":
        return utc_now_iso()
    return ""


def _task_to_merge_subtasks(task: dict, subtasks: list[dict], prefix_nested: bool = True) -> list[dict]:
    task_name = _clip_subtask_title(task.get("name") or "(bez nazwy)")
    task_done_at = _get_task_done_at(task)
    task_is_done = bool(task_done_at)
    fallback_count = max(1, len(subtasks))
    fallback_minutes = max(1, round(parse_non_negative_int(task.get("estimated_time"), default=15) / fallback_count))
    fallback_points = round(max(0.1, _normalize_points_weight(task.get("points_weight")) / fallback_count), 2)
    source_due_date = normalize_due_date(task.get("due_date") or "")
    source_due_time = normalize_due_time(task.get("due_time") or "", default="") if source_due_date else ""

    if not subtasks:
        return [
            {
                "id": None,
                "title": task_name,
                "done": task_is_done,
                "estimated_time": max(1, parse_non_negative_int(task.get("estimated_time"), default=15)),
                "points_weight": _normalize_points_weight(task.get("points_weight")),
                "done_at": task_done_at,
                "source_task_id": int(task["id"]),
                "source_module_id": int(task["module_id"]),
                "source_due_date": source_due_date,
                "source_due_time": source_due_time,
                "position": 0,
            }
        ]

    merged = []
    for subtask in subtasks:
        subtask_title = _clip_subtask_title(subtask.get("title") or "")
        title = _clip_subtask_title(f"{task_name}: {subtask_title}" if prefix_nested else subtask_title)
        is_done = bool(subtask.get("done")) or task_is_done
        done_at = (subtask.get("done_at") or "").strip() if is_done else ""
        if is_done and not done_at:
            done_at = task_done_at or utc_now_iso()
        merged.append(
            {
                "id": subtask.get("id"),
                "title": title,
                "done": is_done,
                "estimated_time": max(1, parse_non_negative_int(subtask.get("estimated_time"), default=fallback_minutes)),
                "points_weight": round(
                    max(0.1, parse_non_negative_float(subtask.get("points_weight"), default=fallback_points)),
                    2,
                ),
                "done_at": done_at,
                "source_task_id": _normalize_optional_int(subtask.get("source_task_id")) or int(task["id"]),
                "source_module_id": _normalize_optional_int(subtask.get("source_module_id")) or int(task["module_id"]),
                "source_due_date": normalize_due_date(subtask.get("source_due_date") or "") or source_due_date,
                "source_due_time": normalize_due_time(subtask.get("source_due_time") or "", default="") or source_due_time,
                "position": len(merged),
            }
        )
    return merged


def _renumber_subtasks(subtasks: list[dict]) -> list[dict]:
    normalized = []
    for subtask in subtasks:
        normalized.append({**subtask, "position": len(normalized)})
    return normalized


def _choose_parent_priority(tasks: list[dict]) -> str:
    priorities = [normalize_priority(task.get("priority")) for task in tasks]
    return min(priorities, key=_priority_rank) if priorities else ""


def _choose_parent_status(target_task: dict, source_task: dict, merged_subtasks: list[dict]) -> str:
    target_status = normalize_status(target_task.get("status"))
    source_status = normalize_status(source_task.get("status"))
    if target_status != "gotowe":
        return target_status
    if source_status != "gotowe":
        return source_status
    if merged_subtasks and any(not subtask.get("done") for subtask in merged_subtasks):
        return "oczekujace"
    return "gotowe"


def _choose_parent_due(tasks: list[dict]) -> tuple[str, str]:
    def sort_key(task: dict) -> tuple[str, str]:
        due_date = normalize_due_date(task.get("due_date") or "")
        due_time = normalize_due_time(task.get("due_time") or "", default="14:00") if due_date else ""
        return due_date, due_time or "14:00"

    open_candidates = [
        task
        for task in tasks
        if normalize_status(task.get("status")) != "gotowe" and normalize_due_date(task.get("due_date") or "")
    ]
    candidates = open_candidates or [
        task
        for task in tasks
        if normalize_due_date(task.get("due_date") or "")
    ]
    if not candidates:
        return "", ""

    selected = min(candidates, key=sort_key)
    due_date = normalize_due_date(selected.get("due_date") or "")
    due_time = normalize_due_time(selected.get("due_time") or "", default="14:00") if due_date else ""
    return due_date, due_time


def _format_merge_task_notes(task: dict) -> list[str]:
    lines = [f"- {(task.get('name') or '(bez nazwy)').strip()}"]
    task_description = (task.get("description") or "").strip()
    if not task_description:
        return lines

    lines.append("  Notatki:")
    for note_line in task_description.splitlines():
        clean_line = note_line.strip()
        lines.append(f"    {clean_line}" if clean_line else "")
    return lines


def _simplify_legacy_merge_description(description: str) -> str:
    clean_description = (description or "").strip()
    if not clean_description:
        return ""

    normalized_lines = []
    for line in clean_description.splitlines():
        match = re.match(r"^(\s*)-\s+#\d+\s+(.+?)(?:\s+\([^)]*\))?\s*$", line)
        if match:
            normalized_lines.append(f"{match.group(1)}- {match.group(2).strip()}")
        elif re.match(r"^\s*Notatka:\s*", line):
            normalized_lines.append(re.sub(r"^(\s*)Notatka:\s*", r"\1Notatki: ", line).rstrip())
        else:
            normalized_lines.append(line.rstrip())
    return "\n".join(normalized_lines).strip()


def _build_merge_description(
    existing_description: str,
    merged_tasks: list[dict],
    module_names: dict[int, str],
    header: str,
) -> str:
    lines = []
    clean_existing = _simplify_legacy_merge_description(existing_description)
    if clean_existing:
        lines.append(clean_existing)
        lines.append("")
    lines.append(header)
    for task in merged_tasks:
        lines.extend(_format_merge_task_notes(task))
    return "\n".join(lines).strip()


def _build_merge_task_name(target_task: dict, source_task: dict, module_names: dict[int, str]) -> str:
    target_module_id = int(target_task["module_id"])
    source_module_id = int(source_task["module_id"])
    module_name = module_names.get(target_module_id, "").strip()
    joined_names = f"{target_task.get('name') or ''} {source_task.get('name') or ''}".lower()
    looks_like_fixes = any(keyword in joined_names for keyword in ["popraw", "napraw", "fix", "bug", "blad", "korekt"])

    if target_module_id == source_module_id and module_name and looks_like_fixes:
        return f"Poprawki: {module_name}"[:180].rstrip()
    if target_module_id == source_module_id and module_name:
        return f"{module_name}: pakiet zadan"[:180].rstrip()
    return f"Pakiet: {target_task.get('name') or source_task.get('name') or 'zadania'}"[:180].rstrip()


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
    date: str | None = Query(None),
    due_date: str | None = Query(None),
    exclude_task_id: int | None = Query(None),
):
    requested_date = (date or due_date or "").strip()
    clean_date = normalize_due_date(requested_date)
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


@router.get("/tasks/widget/today")
def get_today_widget_tasks(
    date: str | None = Query(None),
    limit: int = Query(12, ge=1, le=50),
    include_overdue: bool = Query(True),
    include_done: bool = Query(False),
):
    raw_date = (date or "").strip()
    clean_date = normalize_due_date(raw_date) if raw_date else _today_key_utc()
    if raw_date and not clean_date:
        raise HTTPException(status_code=400, detail="Niepoprawna data (format YYYY-MM-DD).")

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT t.*, COALESCE(m.name, '') AS module_name
            FROM tasks t
            LEFT JOIN modules m ON m.id = t.module_id
            """
        ).fetchall()
        tasks = [dict(row) for row in rows]
        task_ids = [int(task["id"]) for task in tasks]
        subtasks_by_task = _list_subtasks_by_task_ids(conn, task_ids)

    widget_tasks: list[dict] = []
    today_open_count = 0
    overdue_open_count = 0
    done_today_count = 0

    for task in tasks:
        task_id = int(task["id"])
        status = normalize_status(task.get("status"))
        due_date = normalize_due_date(task.get("due_date") or "")
        due_time = normalize_due_time(task.get("due_time") or "", default="")
        done_date = _get_task_done_date(task.get("description") or "")

        bucket = ""
        if status == "gotowe":
            if done_date == clean_date:
                done_today_count += 1
                if include_done:
                    bucket = "done"
                else:
                    continue
            else:
                continue
        else:
            if due_date == clean_date:
                bucket = "today"
                today_open_count += 1
            elif include_overdue and due_date and due_date < clean_date:
                bucket = "overdue"
                overdue_open_count += 1
            else:
                continue

        subtasks = subtasks_by_task.get(task_id, [])
        subtasks_total = len(subtasks)
        subtasks_done = sum(1 for item in subtasks if bool(item.get("done")))

        widget_tasks.append(
            {
                "id": task_id,
                "name": (task.get("name") or "").strip() or "(bez nazwy)",
                "module_id": parse_non_negative_int(task.get("module_id"), default=0),
                "module_name": (task.get("module_name") or "").strip(),
                "status": status,
                "priority": normalize_priority(task.get("priority") or ""),
                "due_date": due_date,
                "due_time": due_time,
                "done_date": done_date,
                "bucket": bucket,
                "estimated_time": parse_non_negative_int(task.get("estimated_time"), default=0),
                "points_weight": round(max(0.0, parse_non_negative_float(task.get("points_weight"), default=0.0)), 2),
                "subtasks_total": subtasks_total,
                "subtasks_done": subtasks_done,
                "subtasks_open": max(0, subtasks_total - subtasks_done),
            }
        )

    sorted_tasks = _sort_widget_tasks(widget_tasks)
    limited_tasks = sorted_tasks[:limit]

    return {
        "date": clean_date,
        "generated_at": utc_now_iso(),
        "counts": {
            "today_open": today_open_count,
            "overdue_open": overdue_open_count,
            "done_today": done_today_count,
            "open_total": today_open_count + overdue_open_count,
            "returned": len(limited_tasks),
            "available": len(sorted_tasks),
            "truncated": len(sorted_tasks) > limit,
        },
        "tasks": limited_tasks,
    }


@router.post("/tasks/merge")
def merge_tasks(payload: TaskMergePayload):
    source_task_id = parse_non_negative_int(payload.source_task_id)
    target_task_id = parse_non_negative_int(payload.target_task_id)
    if source_task_id <= 0 or target_task_id <= 0:
        raise HTTPException(status_code=400, detail="Niepoprawne zadania do polaczenia.")
    if source_task_id == target_task_id:
        raise HTTPException(status_code=400, detail="Nie mozna polaczyc zadania z samym soba.")

    requested_name = (payload.name or "").strip()
    allow_time_overflow = bool(payload.allow_time_overflow)

    with get_db() as conn:
        task_rows = conn.execute(
            "SELECT * FROM tasks WHERE id IN (?, ?)",
            (source_task_id, target_task_id),
        ).fetchall()
        tasks_by_id = {int(row["id"]): dict(row) for row in task_rows}
        source_task = tasks_by_id.get(source_task_id)
        target_task = tasks_by_id.get(target_task_id)
        if not source_task or not target_task:
            raise HTTPException(status_code=404, detail="Nie znaleziono jednego z zadan do polaczenia.")

        module_rows = conn.execute("SELECT id, name FROM modules").fetchall()
        module_names = {int(row["id"]): row["name"] or "" for row in module_rows}

        subtasks_by_task = _list_subtasks_by_task_ids(conn, [target_task_id, source_task_id])
        target_subtasks = subtasks_by_task.get(target_task_id, [])
        source_subtasks = subtasks_by_task.get(source_task_id, [])
        target_is_parent = len(target_subtasks) > 0

        if target_is_parent:
            parent_task_id = target_task_id
            next_name = requested_name or (target_task.get("name") or "").strip()
            if not next_name:
                next_name = _build_merge_task_name(target_task, source_task, module_names)
            merged_subtasks = _renumber_subtasks([
                *target_subtasks,
                *_task_to_merge_subtasks(source_task, source_subtasks, prefix_nested=True),
            ])
            next_description = _build_merge_description(
                target_task.get("description") or "",
                [source_task],
                module_names,
                "Dopisane do pakietu:",
            )
            delete_task_ids = [source_task_id]
            excluded_task_ids = [source_task_id, target_task_id]
        else:
            parent_task_id = None
            next_name = requested_name or _build_merge_task_name(target_task, source_task, module_names)
            if not next_name:
                raise HTTPException(status_code=400, detail="Nazwa zadania zbiorczego nie moze byc pusta.")
            merged_subtasks = _renumber_subtasks([
                *_task_to_merge_subtasks(target_task, target_subtasks, prefix_nested=False),
                *_task_to_merge_subtasks(source_task, source_subtasks, prefix_nested=True),
            ])
            next_description = _build_merge_description(
                "",
                [target_task, source_task],
                module_names,
                "Scalone zadania:",
            )
            delete_task_ids = [target_task_id, source_task_id]
            excluded_task_ids = [target_task_id, source_task_id]

        next_name = next_name[:180].rstrip()
        if not next_name:
            raise HTTPException(status_code=400, detail="Nazwa zadania zbiorczego nie moze byc pusta.")

        totals = _calculate_subtasks_totals(merged_subtasks)
        next_estimated_time = parse_non_negative_int(totals["estimated_time"], default=0)
        next_points_weight = _normalize_points_weight(totals["points_weight"])
        next_status = _choose_parent_status(target_task, source_task, merged_subtasks)
        next_priority = _choose_parent_priority([target_task, source_task])
        next_due_date, next_due_time = _choose_parent_due([target_task, source_task])
        next_module_id = int(target_task["module_id"])

        limit_date = _task_limit_date(next_due_date, next_status, next_description)
        planned_before = _get_daily_planned_minutes(conn, limit_date, exclude_task_ids=excluded_task_ids)
        task_minutes = _task_minutes_for_workload_date(
            limit_date,
            next_due_date,
            next_estimated_time,
            next_status,
            next_description,
        )
        _enforce_workday_limit(limit_date, planned_before, task_minutes, allow_time_overflow)

        if parent_task_id is None:
            cur = conn.execute(
                """
                INSERT INTO tasks (name, module_id, estimated_time, points_weight, status, priority, description, due_date, due_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    next_name,
                    next_module_id,
                    next_estimated_time,
                    next_points_weight,
                    next_status,
                    next_priority,
                    next_description,
                    next_due_date,
                    next_due_time,
                ),
            )
            parent_task_id = int(cur.lastrowid)
        else:
            conn.execute(
                """
                UPDATE tasks
                SET name = ?,
                    module_id = ?,
                    estimated_time = ?,
                    points_weight = ?,
                    status = ?,
                    priority = ?,
                    description = ?,
                    due_date = ?,
                    due_time = ?
                WHERE id = ?
                """,
                (
                    next_name,
                    next_module_id,
                    next_estimated_time,
                    next_points_weight,
                    next_status,
                    next_priority,
                    next_description,
                    next_due_date,
                    next_due_time,
                    parent_task_id,
                ),
            )

        _replace_task_subtasks(conn, parent_task_id, merged_subtasks)

        placeholders = ", ".join(["?"] * len(delete_task_ids))
        conn.execute(f"DELETE FROM tasks WHERE id IN ({placeholders})", delete_task_ids)
        conn.commit()

    return {
        "status": "merged",
        "id": parent_task_id,
        "merged_task_ids": delete_task_ids,
        "subtasks_count": len(merged_subtasks),
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
        raise HTTPException(
            status_code=502,
            detail=f"Blad AI (shred): {exc}",
        ) from exc
