from fastapi import APIRouter, HTTPException

from backend.db import get_db
from backend.schemas import ModuleCreate
from backend.utils import normalize_module_category

router = APIRouter()


@router.get("/modules")
def get_modules():
    with get_db() as conn:
        query = """
            SELECT m.*,
            (SELECT COUNT(*) FROM tasks WHERE module_id = m.id) AS total_tasks,
            (SELECT COUNT(*) FROM tasks WHERE module_id = m.id AND status = 'gotowe') AS done_tasks
            FROM modules m
        """
        modules = [dict(row) for row in conn.execute(query).fetchall()]
        for module in modules:
            module["category"] = normalize_module_category(module.get("category"))
        return modules


@router.post("/modules")
def add_module(payload: ModuleCreate):
    clean_name = (payload.name or "").strip()
    if not clean_name:
        raise HTTPException(status_code=400, detail="Nazwa modulu nie moze byc pusta")

    clean_category = normalize_module_category(payload.category)

    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO modules (name, category) VALUES (?, ?)",
            (clean_name, clean_category),
        )
        conn.commit()

    return {"id": cur.lastrowid, "name": clean_name, "category": clean_category}


@router.delete("/modules/{module_id}")
def delete_module(module_id: int):
    with get_db() as conn:
        module = conn.execute("SELECT * FROM modules WHERE id = ?", (module_id,)).fetchone()
        if not module:
            raise HTTPException(status_code=404, detail="Modul nie znaleziony")

        deleted_tasks = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE module_id = ?",
            (module_id,),
        ).fetchone()[0]

        conn.execute("DELETE FROM tasks WHERE module_id = ?", (module_id,))
        conn.execute("DELETE FROM modules WHERE id = ?", (module_id,))
        conn.commit()

    return {"status": "deleted", "deleted_tasks": deleted_tasks}


@router.get("/modules/{module_id}/progress")
def get_progress(module_id: int):
    with get_db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE module_id = ?",
            (module_id,),
        ).fetchone()[0]
        done = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE module_id = ? AND status = 'gotowe'",
            (module_id,),
        ).fetchone()[0]

    return {"percent": (done / total * 100) if total > 0 else 0}
