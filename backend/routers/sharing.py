from fastapi import APIRouter, HTTPException

from backend.accounts import AccountConfig, get_user_by_username
from backend.auth import get_request_user
from backend.db import get_db
from backend.schemas import SharingInvitationCreate
from backend.utils import utc_now_iso

router = APIRouter(prefix="/sharing", tags=["sharing"])


def _current_account() -> AccountConfig:
    account = get_user_by_username(get_request_user())
    if not account:
        raise HTTPException(status_code=401, detail="Brak aktywnego uzytkownika.")
    return account


def _connection_for_pair(conn, first_user_id: int, second_user_id: int):
    return conn.execute(
        """
        SELECT *
        FROM sharing_connections
        WHERE (requester_user_id = ? AND recipient_user_id = ?)
           OR (requester_user_id = ? AND recipient_user_id = ?)
        LIMIT 1
        """,
        (first_user_id, second_user_id, second_user_id, first_user_id),
    ).fetchone()


@router.get("")
def get_sharing_connections():
    account = _current_account()
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT
                sc.*,
                requester.username AS requester_username,
                recipient.username AS recipient_username
            FROM sharing_connections sc
            JOIN users requester ON requester.id = sc.requester_user_id
            JOIN users recipient ON recipient.id = sc.recipient_user_id
            WHERE sc.requester_user_id = ? OR sc.recipient_user_id = ?
            ORDER BY sc.updated_at DESC, sc.id DESC
            """,
            (account.id, account.id),
        ).fetchall()

    connections = []
    incoming = []
    outgoing = []
    for row in rows:
        is_requester = int(row["requester_user_id"]) == account.id
        other_user_id = int(row["recipient_user_id"] if is_requester else row["requester_user_id"])
        other_username = row["recipient_username"] if is_requester else row["requester_username"]
        base = {
            "id": int(row["id"]),
            "user_id": other_user_id,
            "username": other_username or "",
            "created_at": row["created_at"] or "",
            "updated_at": row["updated_at"] or "",
        }
        status = (row["status"] or "").strip().lower()
        if status == "accepted":
            connections.append(base)
        elif status == "pending" and is_requester:
            outgoing.append(base)
        elif status == "pending":
            incoming.append(base)

    connections.sort(key=lambda item: item["username"].lower())
    return {
        "connections": connections,
        "incoming": incoming,
        "outgoing": outgoing,
    }


@router.post("/invitations")
def create_sharing_invitation(payload: SharingInvitationCreate):
    account = _current_account()
    invited = get_user_by_username(payload.username)
    if not invited:
        raise HTTPException(status_code=404, detail="Uzytkownik o tej nazwie nie istnieje.")
    if invited.id == account.id:
        raise HTTPException(status_code=400, detail="Nie mozna zaprosic samego siebie.")

    now = utc_now_iso()
    with get_db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        existing = _connection_for_pair(conn, account.id, invited.id)
        if existing:
            status = (existing["status"] or "").strip().lower()
            if status == "accepted":
                raise HTTPException(status_code=409, detail="Ta osoba jest juz na Twojej liscie udostepniania.")
            if status == "pending":
                if int(existing["recipient_user_id"]) == account.id:
                    raise HTTPException(
                        status_code=409,
                        detail="Ta osoba juz Cie zaprosila. Zaakceptuj oczekujace zaproszenie.",
                    )
                raise HTTPException(status_code=409, detail="Zaproszenie do tej osoby juz czeka na odpowiedz.")

            conn.execute(
                """
                UPDATE sharing_connections
                SET requester_user_id = ?, recipient_user_id = ?, status = 'pending',
                    created_at = ?, updated_at = ?, responded_at = ''
                WHERE id = ?
                """,
                (account.id, invited.id, now, now, int(existing["id"])),
            )
            invitation_id = int(existing["id"])
        else:
            cursor = conn.execute(
                """
                INSERT INTO sharing_connections (
                    requester_user_id, recipient_user_id, status, created_at, updated_at, responded_at
                )
                VALUES (?, ?, 'pending', ?, ?, '')
                """,
                (account.id, invited.id, now, now),
            )
            invitation_id = int(cursor.lastrowid)
        conn.commit()

    return {"status": "pending", "id": invitation_id, "username": invited.username}


def _respond_to_invitation(invitation_id: int, accepted: bool):
    account = _current_account()
    now = utc_now_iso()
    with get_db() as conn:
        invitation = conn.execute(
            """
            SELECT id, recipient_user_id, status
            FROM sharing_connections
            WHERE id = ?
            """,
            (invitation_id,),
        ).fetchone()
        if not invitation:
            raise HTTPException(status_code=404, detail="Zaproszenie nie istnieje.")
        if int(invitation["recipient_user_id"]) != account.id:
            raise HTTPException(status_code=403, detail="To zaproszenie nie jest skierowane do Ciebie.")
        if (invitation["status"] or "").strip().lower() != "pending":
            raise HTTPException(status_code=409, detail="Na to zaproszenie juz odpowiedziano.")

        status = "accepted" if accepted else "declined"
        conn.execute(
            """
            UPDATE sharing_connections
            SET status = ?, updated_at = ?, responded_at = ?
            WHERE id = ?
            """,
            (status, now, now, invitation_id),
        )
        conn.commit()
    return {"status": status, "id": invitation_id}


@router.post("/invitations/{invitation_id}/accept")
def accept_sharing_invitation(invitation_id: int):
    return _respond_to_invitation(invitation_id, accepted=True)


@router.post("/invitations/{invitation_id}/decline")
def decline_sharing_invitation(invitation_id: int):
    return _respond_to_invitation(invitation_id, accepted=False)


@router.delete("/connections/{other_user_id}")
def remove_sharing_connection(other_user_id: int):
    account = _current_account()
    if other_user_id <= 0 or other_user_id == account.id:
        raise HTTPException(status_code=400, detail="Niepoprawna osoba do usuniecia.")

    with get_db() as conn:
        connection = _connection_for_pair(conn, account.id, other_user_id)
        if not connection or (connection["status"] or "").strip().lower() != "accepted":
            raise HTTPException(status_code=404, detail="Nie znaleziono aktywnego polaczenia.")

        conn.execute("DELETE FROM sharing_connections WHERE id = ?", (int(connection["id"]),))
        conn.execute(
            """
            DELETE FROM task_shares
            WHERE (shared_user_id = ? AND task_id IN (
                    SELECT id FROM tasks WHERE owner_user_id = ?
                  ))
               OR (shared_user_id = ? AND task_id IN (
                    SELECT id FROM tasks WHERE owner_user_id = ?
                  ))
            """,
            (other_user_id, account.id, account.id, other_user_id),
        )
        conn.commit()

    return {"status": "removed", "user_id": other_user_id}
