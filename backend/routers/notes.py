from fastapi import APIRouter, HTTPException

from backend.accounts import get_user_by_username
from backend.auth import get_request_user
from backend.db import get_db
from backend.schemas import BrainDumpNoteCreate, BrainDumpNoteUpdate, NotePayload
from backend.utils import utc_now_iso

router = APIRouter()
LEGACY_BRAIN_DUMP_KEY = "brain-dump"
LEGACY_BRAIN_DUMP_MIGRATION_MARKER = "brain-dump-migrated-v2"


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


def _clean_brain_dump_title(title: str, content: str = "") -> str:
    value = (title or "").strip()
    if not value:
        value = next((line.strip() for line in (content or "").splitlines() if line.strip()), "")
    return value[:90] or "Nowa notatka"


def _serialize_brain_dump_note(row) -> dict:
    return {
        "id": int(row["id"]),
        "title": row["title"] or "Nowa notatka",
        "content": row["content"] or "",
        "created_at": row["created_at"] or "",
        "updated_at": row["updated_at"] or "",
    }


def _migrate_legacy_brain_dump_if_needed(conn, user_id: int) -> None:
    existing_count = conn.execute(
        "SELECT COUNT(*) AS total FROM brain_dump_notes WHERE owner_user_id = ?",
        (user_id,),
    ).fetchone()["total"]
    if int(existing_count or 0) > 0:
        return

    marker = conn.execute(
        "SELECT 1 FROM notes WHERE owner_user_id = ? AND key = ?",
        (user_id, LEGACY_BRAIN_DUMP_MIGRATION_MARKER),
    ).fetchone()
    if marker:
        return

    legacy = conn.execute(
        "SELECT content FROM notes WHERE owner_user_id = ? AND key = ?",
        (user_id, LEGACY_BRAIN_DUMP_KEY),
    ).fetchone()
    legacy_content = (legacy["content"] if legacy else "") or ""
    now = utc_now_iso()

    if legacy_content.strip():
        conn.execute(
            """
            INSERT INTO brain_dump_notes (owner_user_id, title, content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, _clean_brain_dump_title("", legacy_content), legacy_content, now, now),
        )

    conn.execute(
        """
        INSERT INTO notes (owner_user_id, key, content, updated_at)
        VALUES (?, ?, '1', ?)
        ON CONFLICT(owner_user_id, key) DO UPDATE SET
            content = excluded.content,
            updated_at = excluded.updated_at
        """,
        (user_id, LEGACY_BRAIN_DUMP_MIGRATION_MARKER, now),
    )


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


@router.get("/brain-dump-notes")
def get_brain_dump_notes():
    user_id = _current_user_id()
    with get_db() as conn:
        _migrate_legacy_brain_dump_if_needed(conn, user_id)
        conn.commit()
        rows = conn.execute(
            """
            SELECT id, title, content, created_at, updated_at
            FROM brain_dump_notes
            WHERE owner_user_id = ?
            ORDER BY updated_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()
    return {"items": [_serialize_brain_dump_note(row) for row in rows]}


@router.post("/brain-dump-notes")
def add_brain_dump_note(payload: BrainDumpNoteCreate):
    user_id = _current_user_id()
    content = payload.content or ""
    title = _clean_brain_dump_title(payload.title, content)
    now = utc_now_iso()
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO brain_dump_notes (owner_user_id, title, content, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, title, content, now, now),
        )
        conn.commit()

        row = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM brain_dump_notes WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
    return _serialize_brain_dump_note(row)


@router.put("/brain-dump-notes/{note_id}")
def update_brain_dump_note(note_id: int, payload: BrainDumpNoteUpdate):
    user_id = _current_user_id()
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM brain_dump_notes WHERE id = ? AND owner_user_id = ?",
            (note_id, user_id),
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Notatka nie znaleziona")

        content = existing["content"] if payload.content is None else (payload.content or "")
        title = existing["title"] if payload.title is None else _clean_brain_dump_title(payload.title, content)
        updated_at = utc_now_iso()

        conn.execute(
            """
            UPDATE brain_dump_notes
            SET title = ?, content = ?, updated_at = ?
            WHERE id = ? AND owner_user_id = ?
            """,
            (title, content, updated_at, note_id, user_id),
        )
        conn.commit()

        row = conn.execute(
            "SELECT id, title, content, created_at, updated_at FROM brain_dump_notes WHERE id = ? AND owner_user_id = ?",
            (note_id, user_id),
        ).fetchone()
    return _serialize_brain_dump_note(row)


@router.delete("/brain-dump-notes/{note_id}")
def delete_brain_dump_note(note_id: int):
    user_id = _current_user_id()
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM brain_dump_notes WHERE id = ? AND owner_user_id = ?",
            (note_id, user_id),
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Notatka nie znaleziona")

        conn.execute("DELETE FROM brain_dump_notes WHERE id = ? AND owner_user_id = ?", (note_id, user_id))
        conn.commit()
    return {"status": "deleted"}
