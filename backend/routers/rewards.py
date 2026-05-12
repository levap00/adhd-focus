import re

from fastapi import APIRouter

from backend.db import get_db
from backend.utils import normalize_status, parse_non_negative_float, utc_now_iso

router = APIRouter()
WALLET_ROW_ID = 1
DONE_STAMP_RE = re.compile(r"\[Done:\s*\d{4}-\d{2}-\d{2}\]")


def _normalize_points_weight(raw_value) -> float:
    value = parse_non_negative_float(raw_value, default=1.0)
    return round(value if value > 0 else 1.0, 2)


def _ensure_wallet_row(conn) -> None:
    conn.execute(
        """
        INSERT INTO reward_wallet (id, spent_points, updated_at)
        VALUES (?, 0, ?)
        ON CONFLICT(id) DO NOTHING
        """,
        (WALLET_ROW_ID, utc_now_iso()),
    )


def _calculate_earned_points(conn) -> float:
    task_rows = conn.execute(
        """
        SELECT id, status, points_weight, description
        FROM tasks
        """
    ).fetchall()

    subtask_rows = conn.execute(
        """
        SELECT
            task_id,
            COUNT(*) AS total_count,
            SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) AS done_count,
            SUM(CASE WHEN done = 1 THEN points_weight ELSE 0 END) AS done_points,
            SUM(CASE WHEN points_weight > 0 THEN 1 ELSE 0 END) AS positive_points_count
        FROM task_subtasks
        GROUP BY task_id
        """
    ).fetchall()
    subtask_stats = {
        int(row["task_id"]): {
            "total": int(row["total_count"] or 0),
            "done": int(row["done_count"] or 0),
            "done_points": round(max(0.0, parse_non_negative_float(row["done_points"], default=0.0)), 2),
            "positive_points_count": int(row["positive_points_count"] or 0),
        }
        for row in subtask_rows
    }

    earned = 0.0
    for task in task_rows:
        task_id = int(task["id"])
        points_weight = _normalize_points_weight(task["points_weight"])
        stats = subtask_stats.get(task_id)

        if stats and stats["total"] > 0:
            # Legacy subtasks may have 0 points. In that case keep backward-compatible equal split.
            if stats["positive_points_count"] == stats["total"]:
                earned += stats["done_points"]
            else:
                done_fraction = min(stats["done"], stats["total"]) / stats["total"]
                earned += points_weight * done_fraction
            continue

        description = (task["description"] or "").strip()
        if normalize_status(task["status"]) == "gotowe" or DONE_STAMP_RE.search(description):
            earned += points_weight

    return round(earned, 2)


def _get_wallet_spent_points(conn) -> float:
    wallet_row = conn.execute(
        "SELECT spent_points FROM reward_wallet WHERE id = ?",
        (WALLET_ROW_ID,),
    ).fetchone()
    if not wallet_row:
        return 0.0
    return round(parse_non_negative_float(wallet_row["spent_points"], default=0.0), 2)


def _build_reward_summary(conn) -> dict:
    earned_points = _calculate_earned_points(conn)
    spent_points = _get_wallet_spent_points(conn)
    available_points = round(max(0.0, earned_points - spent_points), 2)
    effective_spent = round(min(earned_points, spent_points), 2)
    return {
        "earned_points": earned_points,
        "spent_points": effective_spent,
        "available_points": available_points,
        "available_budget_pln": available_points,
        "point_value_pln": 1.0,
    }


@router.get("/rewards/summary")
def get_rewards_summary():
    with get_db() as conn:
        _ensure_wallet_row(conn)
        conn.commit()
        return _build_reward_summary(conn)


@router.post("/rewards/reset")
def reset_rewards_wallet():
    with get_db() as conn:
        _ensure_wallet_row(conn)
        earned_points = _calculate_earned_points(conn)
        conn.execute(
            "UPDATE reward_wallet SET spent_points = ?, updated_at = ? WHERE id = ?",
            (earned_points, utc_now_iso(), WALLET_ROW_ID),
        )
        conn.commit()
        return _build_reward_summary(conn)
