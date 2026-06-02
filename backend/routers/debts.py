from fastapi import APIRouter, HTTPException, Query

from backend.accounts import get_user_by_username
from backend.auth import get_request_user
from backend.db import get_db
from backend.schemas import DebtCreate, DebtStatePayload, DebtUpdate
from backend.utils import normalize_month_key, parse_non_negative_float, parse_non_negative_int, utc_now_iso

router = APIRouter()


def _current_user_id() -> int:
    account = get_user_by_username(get_request_user())
    if not account:
        raise HTTPException(status_code=401, detail="Brak aktywnego uzytkownika.")
    return account.id



def _normalize_debt_kind(raw):
    value = (raw or "debt").strip().lower()
    if value in {"fixed", "cost", "fixed_cost", "koszt"}:
        return "fixed"
    return "debt"


def _serialize_debt(row):
    item = dict(row)
    item["kind"] = _normalize_debt_kind(item.get("kind"))
    item["total_amount"] = round(float(item.get("total_amount") or 0), 2)
    item["monthly_amount"] = round(float(item.get("monthly_amount") or 0), 2)
    item["due_day"] = min(31, parse_non_negative_int(item.get("due_day")))
    item["paid_months"] = parse_non_negative_int(item.get("paid_months"))
    item["month_done"] = bool(item.get("month_done"))
    return item


def _get_summary(conn, user_id: int):
    summary_row = conn.execute(
        """
        SELECT
            COUNT(*) AS count,
            COALESCE(SUM(total_amount), 0) AS total,
            COALESCE(SUM(monthly_amount), 0) AS monthly,
            COALESCE(SUM(CASE WHEN kind = 'debt' THEN total_amount ELSE 0 END), 0) AS debt_total,
            COALESCE(SUM(CASE WHEN kind = 'debt' THEN monthly_amount ELSE 0 END), 0) AS debt_monthly,
            COALESCE(SUM(CASE WHEN kind = 'fixed' THEN monthly_amount ELSE 0 END), 0) AS fixed_monthly,
            COALESCE(SUM(CASE WHEN kind = 'fixed' THEN 1 ELSE 0 END), 0) AS fixed_count,
            COALESCE(SUM(CASE WHEN kind = 'debt' THEN 1 ELSE 0 END), 0) AS debt_count
        FROM debts
        WHERE owner_user_id = ?
        """,
        (user_id,),
    ).fetchone()
    return {
        "count": int(summary_row["count"]),
        "total": round(float(summary_row["total"] or 0), 2),
        "monthly": round(float(summary_row["monthly"] or 0), 2),
        "debt_total": round(float(summary_row["debt_total"] or 0), 2),
        "debt_monthly": round(float(summary_row["debt_monthly"] or 0), 2),
        "fixed_monthly": round(float(summary_row["fixed_monthly"] or 0), 2),
        "fixed_count": int(summary_row["fixed_count"] or 0),
        "debt_count": int(summary_row["debt_count"] or 0),
    }


@router.get("/debts")
def get_debts(month: str = Query(default="")):
    user_id = _current_user_id()
    month_key = normalize_month_key(month)
    with get_db() as conn:
        items = [
            _serialize_debt(row)
            for row in conn.execute(
                """
                SELECT
                    d.*,
                    COALESCE(ms.done, 0) AS month_done,
                    COALESCE(ps.paid_months, 0) AS paid_months
                FROM debts d
                LEFT JOIN debt_payment_states ms
                    ON ms.debt_id = d.id
                    AND ms.month_key = ?
                LEFT JOIN (
                    SELECT debt_id, COALESCE(SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END), 0) AS paid_months
                    FROM debt_payment_states
                    GROUP BY debt_id
                ) ps ON ps.debt_id = d.id
                WHERE d.owner_user_id = ?
                ORDER BY d.id DESC
                """,
                (month_key, user_id),
            ).fetchall()
        ]
        summary = _get_summary(conn, user_id)

    return {"items": items, "summary": summary, "month_key": month_key}


@router.post("/debts")
def add_debt(payload: DebtCreate):
    user_id = _current_user_id()
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Nazwa pozycji splaty nie moze byc pusta")

    place = (payload.place or "").strip()
    kind = _normalize_debt_kind(payload.kind)
    note = (payload.note or "").strip()
    if len(note) > 300:
        raise HTTPException(status_code=400, detail="Notatka moze miec maksymalnie 300 znakow")

    total_amount = parse_non_negative_float(payload.total_amount)
    monthly_amount = parse_non_negative_float(payload.monthly_amount)
    due_day = min(31, parse_non_negative_int(payload.due_day))

    now = utc_now_iso()

    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO debts (name, place, kind, total_amount, monthly_amount, due_day, owner_user_id, note, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, place, kind, total_amount, monthly_amount, due_day, user_id, note, now, now),
        )
        conn.commit()

    return {
        "id": cur.lastrowid,
        "name": name,
        "place": place,
        "kind": kind,
        "total_amount": total_amount,
        "monthly_amount": monthly_amount,
        "due_day": due_day,
        "note": note,
        "created_at": now,
        "updated_at": now,
    }


@router.put("/debts/{debt_id}")
def update_debt(debt_id: int, payload: DebtUpdate):
    user_id = _current_user_id()
    update_data = payload.model_dump(exclude_none=True)
    if not update_data:
        return {"status": "no_updates"}

    with get_db() as conn:
        existing = conn.execute(
            "SELECT * FROM debts WHERE id = ? AND owner_user_id = ?",
            (debt_id, user_id),
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Pozycja splaty nie znaleziona")

        if "name" in update_data:
            update_data["name"] = (update_data["name"] or "").strip()
            if not update_data["name"]:
                raise HTTPException(status_code=400, detail="Nazwa pozycji splaty nie moze byc pusta")

        if "place" in update_data:
            update_data["place"] = (update_data["place"] or "").strip()

        if "kind" in update_data:
            update_data["kind"] = _normalize_debt_kind(update_data["kind"])

        if "note" in update_data:
            update_data["note"] = (update_data["note"] or "").strip()
            if len(update_data["note"]) > 300:
                raise HTTPException(status_code=400, detail="Notatka moze miec maksymalnie 300 znakow")

        if "total_amount" in update_data:
            update_data["total_amount"] = parse_non_negative_float(update_data["total_amount"])

        if "monthly_amount" in update_data:
            update_data["monthly_amount"] = parse_non_negative_float(update_data["monthly_amount"])

        if "due_day" in update_data:
            update_data["due_day"] = min(31, parse_non_negative_int(update_data["due_day"]))

        update_data["updated_at"] = utc_now_iso()

        keys = ", ".join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values()) + [debt_id]

        conn.execute(f"UPDATE debts SET {keys} WHERE id = ?", values)
        conn.commit()

    return {"status": "updated", "id": debt_id}


@router.delete("/debts/{debt_id}")
def delete_debt(debt_id: int):
    user_id = _current_user_id()
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM debts WHERE id = ? AND owner_user_id = ?",
            (debt_id, user_id),
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Pozycja splaty nie znaleziona")

        conn.execute("DELETE FROM debts WHERE id = ?", (debt_id,))
        conn.commit()

    return {"status": "deleted"}


@router.put("/debts/{debt_id}/state")
def update_debt_state(debt_id: int, payload: DebtStatePayload):
    user_id = _current_user_id()
    if payload.done is None:
        raise HTTPException(status_code=400, detail="Brak statusu splaty do zapisania")

    month_key = normalize_month_key(payload.month_key)
    done = 1 if payload.done else 0
    now = utc_now_iso()

    with get_db() as conn:
        debt_exists = conn.execute(
            "SELECT id FROM debts WHERE id = ? AND owner_user_id = ?",
            (debt_id, user_id),
        ).fetchone()
        if not debt_exists:
            raise HTTPException(status_code=404, detail="Pozycja splaty nie znaleziona")

        conn.execute(
            """
            INSERT INTO debt_payment_states (debt_id, month_key, done, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(debt_id, month_key) DO UPDATE SET
                done = excluded.done,
                updated_at = excluded.updated_at
            """,
            (debt_id, month_key, done, now),
        )
        conn.commit()

    return {
        "debt_id": debt_id,
        "month_key": month_key,
        "done": bool(done),
        "updated_at": now,
    }
