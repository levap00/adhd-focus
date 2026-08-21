import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from backend.passwords import get_password_hash

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MAX_ADDITIONAL_ACCOUNTS = 8
_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,64}$")
_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
_USER_COLUMNS = "id, username, hashed_password, email, email_verified_at"


@dataclass(frozen=True)
class AccountConfig:
    username: str
    id: int = 0
    hashed_password: str = ""
    email: str = ""
    email_verified_at: str = ""

    @property
    def email_verified(self) -> bool:
        return bool(self.email and self.email_verified_at)


class AccountRegistrationError(Exception):
    pass


class UsernameAlreadyExists(AccountRegistrationError):
    pass


class EmailAlreadyExists(AccountRegistrationError):
    pass


class InvalidInviteCode(AccountRegistrationError):
    pass


class InvalidEmail(AccountRegistrationError):
    pass


def _resolve_db_path(raw_path: str, fallback_name: str) -> Path:
    configured = (raw_path or "").strip()
    path = Path(configured) if configured else Path(fallback_name)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


DATABASE_PATH = _resolve_db_path(os.getenv("FOCUS_APP_DB_PATH", ""), "app.db")
ACCOUNTS_DB_PATH = DATABASE_PATH
_ACCOUNTS_STORE_INITIALIZED = False


def _connect_database() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_username(username: str) -> str:
    return (username or "").strip()


def normalize_email(email: str | None) -> str:
    return (email or "").strip().lower()


def _validate_username(username: str) -> str:
    normalized = _normalize_username(username)
    if not _USERNAME_PATTERN.match(normalized):
        raise ValueError("Username must be 3-64 chars and contain only letters, digits, dots, dashes or underscores.")
    return normalized


def validate_email(email: str | None, required: bool = True) -> str:
    normalized = normalize_email(email)
    if not normalized:
        if required:
            raise InvalidEmail("Email is required.")
        return ""
    if len(normalized) > 254 or not _EMAIL_PATTERN.match(normalized):
        raise InvalidEmail("Email is invalid.")
    return normalized


def _build_primary_env_account() -> tuple[str, str, str]:
    username = (os.getenv("FOCUS_USERNAME", "admin") or "admin").strip() or "admin"
    password = os.getenv("FOCUS_PASSWORD", "admin")
    email = normalize_email(os.getenv("FOCUS_EMAIL", ""))
    return username, password, email


def _build_additional_env_account(index: int) -> tuple[str, str, str] | None:
    username = (os.getenv(f"FOCUS_USERNAME_{index}", "") or "").strip()
    password = os.getenv(f"FOCUS_PASSWORD_{index}", "")
    if not username or not password:
        return None
    email = normalize_email(os.getenv(f"FOCUS_EMAIL_{index}", ""))
    return username, password, email


def _load_env_accounts() -> list[tuple[str, str, str]]:
    accounts: list[tuple[str, str, str]] = [_build_primary_env_account()]
    for index in range(2, 2 + _MAX_ADDITIONAL_ACCOUNTS):
        account = _build_additional_env_account(index)
        if account:
            accounts.append(account)

    usernames_seen: set[str] = set()
    for username, _password, _email in accounts:
        if username in usernames_seen:
            raise RuntimeError(f"Duplicate username in .env: {username}")
        usernames_seen.add(username)

    return accounts


def _configured_invite_codes() -> list[str]:
    raw_codes = os.getenv("FOCUS_INVITE_CODES", "")
    codes = []
    for code in re.split(r"[\s,;]+", raw_codes):
        normalized = code.strip()
        if normalized:
            codes.append(normalized)
    return codes


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def _create_accounts_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT '',
            email TEXT NOT NULL DEFAULT '',
            email_verified_at TEXT NOT NULL DEFAULT ''
        )
        """
    )
    _ensure_column(conn, "users", "email", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(conn, "users", "email_verified_at", "TEXT NOT NULL DEFAULT ''")
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique
        ON users(email) WHERE email != ''
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS invite_codes (
            code TEXT PRIMARY KEY,
            used_by_user_id INTEGER,
            created_at TEXT NOT NULL DEFAULT '',
            used_at TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (used_by_user_id) REFERENCES users(id)
        )
        """
    )


def _seed_env_accounts(conn: sqlite3.Connection) -> None:
    now = _utc_now_iso()
    for username, password, email in _load_env_accounts():
        existing_user = conn.execute(
            f"SELECT {_USER_COLUMNS} FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if existing_user:
            continue

        verified_at = now if email else ""
        conn.execute(
            """
            INSERT INTO users (username, hashed_password, created_at, updated_at, email, email_verified_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, get_password_hash(password), now, now, email, verified_at),
        )


def _seed_invite_codes(conn: sqlite3.Connection) -> None:
    now = _utc_now_iso()
    for code in _configured_invite_codes():
        conn.execute(
            """
            INSERT INTO invite_codes (code, created_at, used_at)
            VALUES (?, ?, '')
            ON CONFLICT(code) DO NOTHING
            """,
            (code, now),
        )


def init_accounts_store() -> None:
    global _ACCOUNTS_STORE_INITIALIZED
    if _ACCOUNTS_STORE_INITIALIZED:
        return

    with _connect_database() as conn:
        _create_accounts_schema(conn)
        _seed_env_accounts(conn)
        _seed_invite_codes(conn)
        conn.commit()
    _ACCOUNTS_STORE_INITIALIZED = True


def _row_to_account(row: sqlite3.Row) -> AccountConfig:
    keys = row.keys()
    return AccountConfig(
        id=int(row["id"]),
        username=row["username"],
        hashed_password=row["hashed_password"],
        email=row["email"] if "email" in keys else "",
        email_verified_at=row["email_verified_at"] if "email_verified_at" in keys else "",
    )


def load_accounts() -> list[AccountConfig]:
    init_accounts_store()
    with _connect_database() as conn:
        rows = conn.execute(
            f"""
            SELECT {_USER_COLUMNS}
            FROM users
            ORDER BY id
            """
        ).fetchall()
    return [_row_to_account(row) for row in rows]


def refresh_accounts_cache() -> None:
    global ACCOUNTS, PRIMARY_ACCOUNT, ACCOUNTS_BY_USERNAME
    ACCOUNTS = load_accounts()
    PRIMARY_ACCOUNT = ACCOUNTS[0]
    ACCOUNTS_BY_USERNAME = {account.username: account for account in ACCOUNTS}


def get_user_by_username(username: str | None) -> AccountConfig | None:
    normalized = _normalize_username(username or "")
    if not normalized:
        return None

    init_accounts_store()
    with _connect_database() as conn:
        row = conn.execute(
            f"""
            SELECT {_USER_COLUMNS}
            FROM users
            WHERE username = ?
            """,
            (normalized,),
        ).fetchone()
    return _row_to_account(row) if row else None


def get_user_by_id(user_id: int) -> AccountConfig | None:
    init_accounts_store()
    with _connect_database() as conn:
        row = conn.execute(
            f"SELECT {_USER_COLUMNS} FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return _row_to_account(row) if row else None


def get_user_by_email(email: str | None) -> AccountConfig | None:
    normalized = normalize_email(email)
    if not normalized:
        return None
    init_accounts_store()
    with _connect_database() as conn:
        row = conn.execute(
            f"SELECT {_USER_COLUMNS} FROM users WHERE email = ?",
            (normalized,),
        ).fetchone()
    return _row_to_account(row) if row else None


def user_exists(username: str | None) -> bool:
    return get_user_by_username(username) is not None


def set_user_email(user_id: int, email: str, verified: bool = False) -> AccountConfig:
    normalized = validate_email(email, required=True)
    now = _utc_now_iso()
    init_accounts_store()
    with _connect_database() as conn:
        taken = conn.execute(
            "SELECT id FROM users WHERE email = ? AND id != ?",
            (normalized, user_id),
        ).fetchone()
        if taken:
            raise EmailAlreadyExists("Ten adres e-mail jest juz uzywany.")
        conn.execute(
            """
            UPDATE users
            SET email = ?, email_verified_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (normalized, now if verified else "", now, user_id),
        )
        conn.commit()
        row = conn.execute(f"SELECT {_USER_COLUMNS} FROM users WHERE id = ?", (user_id,)).fetchone()
    refresh_accounts_cache()
    if not row:
        raise ValueError("User not found.")
    return _row_to_account(row)


def mark_email_verified(user_id: int, email: str | None = None) -> AccountConfig:
    now = _utc_now_iso()
    init_accounts_store()
    with _connect_database() as conn:
        if email:
            normalized = validate_email(email, required=True)
            taken = conn.execute(
                "SELECT id FROM users WHERE email = ? AND id != ?",
                (normalized, user_id),
            ).fetchone()
            if taken:
                raise EmailAlreadyExists("Ten adres e-mail jest juz uzywany.")
            conn.execute(
                """
                UPDATE users
                SET email = ?, email_verified_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (normalized, now, now, user_id),
            )
        else:
            conn.execute(
                """
                UPDATE users
                SET email_verified_at = ?, updated_at = ?
                WHERE id = ? AND email != ''
                """,
                (now, now, user_id),
            )
        conn.commit()
        row = conn.execute(f"SELECT {_USER_COLUMNS} FROM users WHERE id = ?", (user_id,)).fetchone()
    refresh_accounts_cache()
    if not row:
        raise ValueError("User not found.")
    return _row_to_account(row)


def register_user(username: str, password: str, invite_code: str, email: str = "") -> AccountConfig:
    normalized_username = _validate_username(username)
    normalized_code = (invite_code or "").strip()
    normalized_email = validate_email(email, required=True)
    if not normalized_code:
        raise InvalidInviteCode("Invite code is required.")

    init_accounts_store()
    with _connect_database() as conn:
        conn.execute("BEGIN IMMEDIATE")

        existing_user = conn.execute(
            "SELECT 1 FROM users WHERE username = ?",
            (normalized_username,),
        ).fetchone()
        if existing_user:
            raise UsernameAlreadyExists("Username is already taken.")

        existing_email = conn.execute(
            "SELECT 1 FROM users WHERE email = ?",
            (normalized_email,),
        ).fetchone()
        if existing_email:
            raise EmailAlreadyExists("Email is already taken.")

        invite = conn.execute(
            """
            SELECT code, used_by_user_id
            FROM invite_codes
            WHERE code = ?
            """,
            (normalized_code,),
        ).fetchone()
        if not invite or invite["used_by_user_id"] is not None:
            raise InvalidInviteCode("Invite code is invalid or already used.")

        now = _utc_now_iso()
        cursor = conn.execute(
            """
            INSERT INTO users (username, hashed_password, created_at, updated_at, email, email_verified_at)
            VALUES (?, ?, ?, ?, ?, '')
            """,
            (normalized_username, get_password_hash(password), now, now, normalized_email),
        )
        user_id = int(cursor.lastrowid)
        conn.execute(
            """
            UPDATE invite_codes
            SET used_by_user_id = ?, used_at = ?
            WHERE code = ?
            """,
            (user_id, now, normalized_code),
        )
        conn.commit()

    refresh_accounts_cache()
    return AccountConfig(
        id=user_id,
        username=normalized_username,
        hashed_password="",
        email=normalized_email,
        email_verified_at="",
    )


init_accounts_store()
ACCOUNTS = load_accounts()
PRIMARY_ACCOUNT = ACCOUNTS[0]
ACCOUNTS_BY_USERNAME = {account.username: account for account in ACCOUNTS}
