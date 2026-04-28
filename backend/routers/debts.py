from fastapi import APIRouter, HTTPException

from backend.db import get_db
from backend.schemas import DebtCreate, DebtUpdate
from backend.utils import parse_non_negative_float, utc_now_iso

router = APIRouter()



def _serialize_debt(row):
    item = dict(row)
    item["total_amount"] = round(float(item.get("total_amount") or 0), 2)
    item["monthly_amount"] = round(float(item.get("monthly_amount") or 0), 2)
    return item



def _get_summary(conn):
    summary_row = conn.execute(
        "SELECT COUNT(*) AS count, COALESCE(SUM(total_amount), 0) AS total, COALESCE(SUM(monthly_amount), 0) AS monthly FROM debts"
    ).fetchone()
    return {
        "count": int(summary_row["count"]),
        "total": round(float(summary_row["total"] or 0), 2),
        "monthly": round(float(summary_row["monthly"] or 0), 2),
    }


@router.get("/debts")
def get_debts():
    with get_db() as conn:
        items = [
            _serialize_debt(row)
            for row in conn.execute("SELECT * FROM debts ORDER BY id DESC").fetchall()
        ]
        summary = _get_summary(conn)

    return {"items": items, "summary": summary}


@router.post("/debts")
def add_debt(payload: DebtCreate):
    name = (payload.name or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Nazwa pozycji splaty nie moze byc pusta")

    place = (payload.place or "").strip()
    note = (payload.note or "").strip()
    if len(note) > 300:
        raise HTTPException(status_code=400, detail="Notatka moze miec maksymalnie 300 znakow")

    total_amount = parse_non_negative_float(payload.total_amount)
    monthly_amount = parse_non_negative_float(payload.monthly_amount)

    now = utc_now_iso()

    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO debts (name, place, total_amount, monthly_amount, note, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, place, total_amount, monthly_amount, note, now, now),
        )
        conn.commit()

    return {
        "id": cur.lastrowid,
        "name": name,
        "place": place,
        "total_amount": total_amount,
        "monthly_amount": monthly_amount,
        "note": note,
        "created_at": now,
        "updated_at": now,
    }


@router.put("/debts/{debt_id}")
def update_debt(debt_id: int, payload: DebtUpdate):
    update_data = payload.model_dump(exclude_none=True)
    if not update_data:
        return {"status": "no_updates"}

    with get_db() as conn:
        existing = conn.execute("SELECT * FROM debts WHERE id = ?", (debt_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Pozycja splaty nie znaleziona")

        if "name" in update_data:
            update_data["name"] = (update_data["name"] or "").strip()
            if not update_data["name"]:
                raise HTTPException(status_code=400, detail="Nazwa pozycji splaty nie moze byc pusta")

        if "place" in update_data:
            update_data["place"] = (update_data["place"] or "").strip()

        if "note" in update_data:
            update_data["note"] = (update_data["note"] or "").strip()
            if len(update_data["note"]) > 300:
                raise HTTPException(status_code=400, detail="Notatka moze miec maksymalnie 300 znakow")

        if "total_amount" in update_data:
            update_data["total_amount"] = parse_non_negative_float(update_data["total_amount"])

        if "monthly_amount" in update_data:
            update_data["monthly_amount"] = parse_non_negative_float(update_data["monthly_amount"])

        update_data["updated_at"] = utc_now_iso()

        keys = ", ".join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values()) + [debt_id]

        conn.execute(f"UPDATE debts SET {keys} WHERE id = ?", values)
        conn.commit()

    return {"status": "updated", "id": debt_id}


@router.delete("/debts/{debt_id}")
def delete_debt(debt_id: int):
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM debts WHERE id = ?", (debt_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Pozycja splaty nie znaleziona")

        conn.execute("DELETE FROM debts WHERE id = ?", (debt_id,))
        conn.commit()

    return {"status": "deleted"}
