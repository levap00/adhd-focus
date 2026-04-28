from fastapi import APIRouter

from backend.db import get_db
from backend.schemas import NotePayload
from backend.utils import utc_now_iso

router = APIRouter()



def ensure_note_exists(note_key: str):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM notes WHERE key = ?", (note_key,)).fetchone()
        if row:
            return dict(row)

        updated_at = utc_now_iso()
        conn.execute(
            "INSERT INTO notes (key, content, updated_at) VALUES (?, ?, ?)",
            (note_key, "", updated_at),
        )
        conn.commit()

        created = conn.execute("SELECT * FROM notes WHERE key = ?", (note_key,)).fetchone()
        return dict(created)


@router.get("/notes/{note_key}")
def get_note(note_key: str):
    return ensure_note_exists(note_key)


@router.put("/notes/{note_key}")
def update_note(note_key: str, payload: NotePayload):
    updated_at = utc_now_iso()
    content = payload.content or ""

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO notes (key, content, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                content = excluded.content,
                updated_at = excluded.updated_at
            """,
            (note_key, content, updated_at),
        )
        conn.commit()

    return {"key": note_key, "content": content, "updated_at": updated_at}
