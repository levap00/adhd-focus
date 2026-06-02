from fastapi import APIRouter, HTTPException

from backend.accounts import get_user_by_username
from backend.auth import get_request_user
from backend.db import get_db
from backend.schemas import NotePayload
from backend.utils import utc_now_iso

router = APIRouter()


def _current_user_id() -> int:
    account = get_user_by_username(get_request_user())
    if not account:
        raise HTTPException(status_code=401, detail="Brak aktywnego uzytkownika.")
    return account.id


def ensure_note_exists(note_key: str):
    user_id = _current_user_id()
    with get_db() as conn:
        row = conn.execute(
            "SELECT key, content, updated_at FROM notes WHERE owner_user_id = ? AND key = ?",
            (user_id, note_key),
        ).fetchone()
        if row:
            return dict(row)

        updated_at = utc_now_iso()
        conn.execute(
            "INSERT INTO notes (owner_user_id, key, content, updated_at) VALUES (?, ?, ?, ?)",
            (user_id, note_key, "", updated_at),
        )
        conn.commit()

        created = conn.execute(
            "SELECT key, content, updated_at FROM notes WHERE owner_user_id = ? AND key = ?",
            (user_id, note_key),
        ).fetchone()
        return dict(created)


@router.get("/notes/{note_key}")
def get_note(note_key: str):
    return ensure_note_exists(note_key)


@router.put("/notes/{note_key}")
def update_note(note_key: str, payload: NotePayload):
    user_id = _current_user_id()
    updated_at = utc_now_iso()
    content = payload.content or ""

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO notes (owner_user_id, key, content, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(owner_user_id, key) DO UPDATE SET
                content = excluded.content,
                updated_at = excluded.updated_at
            """,
            (user_id, note_key, content, updated_at),
        )
        conn.commit()

    return {"key": note_key, "content": content, "updated_at": updated_at}
