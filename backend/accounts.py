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


@dataclass(frozen=True)
class AccountConfig:
    username: str
    db_path: Path
    id: int = 0
    hashed_password: str = ""


class AccountRegistrationError(Exception):
    pass


class UsernameAlreadyExists(AccountRegistrationError):
    pass


class InvalidInviteCode(AccountRegistrationError):
    pass


def _slug_username(username: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", (username or "").strip())
    slug = slug.strip("_.-")
    return slug or "user"


def _normalize_username(username: str) -> str:
    return (username or "").strip()


def _validate_username(username: str) -> str:
    normalized = _normalize_username(username)
    if not _USERNAME_PATTERN.match(normalized):
        raise ValueError("Username must be 3-64 chars and contain only letters, digits, dots, dashes or underscores.")
    return normalized


def _resolve_db_path(raw_path: str, fallback_name: str) -> Path:
    configured = (raw_path or "").strip()
    path = Path(configured) if configured else Path(fallback_name)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


ACCOUNTS_DB_PATH = _resolve_db_path(os.getenv("FOCUS_ACCOUNTS_DB_PATH", ""), "accounts.db")
_ACCOUNTS_STORE_INITIALIZED = False


def _connect_accounts_db() -> sqlite3.Connection:
    ACCOUNTS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(ACCOUNTS_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_primary_env_account() -> tuple[str, str, Path]:
    username = (os.getenv("FOCUS_USERNAME", "admin") or "admin").strip() or "admin"
    password = os.getenv("FOCUS_PASSWORD", "admin")
    db_path = _resolve_db_path(os.getenv("FOCUS_DB_PATH", ""), "tasks.db")
    return username, password, db_path


def _build_additional_env_account(index: int) -> tuple[str, str, Path] | None:
    username = (os.getenv(f"FOCUS_USERNAME_{index}", "") or "").strip()
    password = os.getenv(f"FOCUS_PASSWORD_{index}", "")
    if not username or not password:
        return None

    db_path = _resolve_db_path(
        os.getenv(f"FOCUS_DB_PATH_{index}", ""),
        f"tasks_{_slug_username(username)}.db",
    )
    return username, password, db_path


def _load_env_accounts() -> list[tuple[str, str, Path]]:
    accounts: list[tuple[str, str, Path]] = [_build_primary_env_account()]
    for index in range(2, 2 + _MAX_ADDITIONAL_ACCOUNTS):
        account = _build_additional_env_account(index)
        if account:
            accounts.append(account)

    usernames_seen: set[str] = set()
    db_paths_seen: dict[Path, str] = {}
    for username, _password, db_path in accounts:
        if username in usernames_seen:
            raise RuntimeError(f"Duplicate username in .env: {username}")
        usernames_seen.add(username)

        existing_owner = db_paths_seen.get(db_path)
        if existing_owner and existing_owner != username:
            raise RuntimeError(
                f"Users '{existing_owner}' and '{username}' point to the same database path: {db_path}"
            )
        db_paths_seen[db_path] = username

    return accounts


def _configured_invite_codes() -> list[str]:
    raw_codes = os.getenv("FOCUS_INVITE_CODES", "")
    codes = []
    for code in re.split(r"[\s,;]+", raw_codes):
        normalized = code.strip()
        if normalized:
            codes.append(normalized)
    return codes


def _create_accounts_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            db_path TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT ''
        )
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
    for username, password, db_path in _load_env_accounts():
        existing_user = conn.execute(
            """
            SELECT 1
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()
        if existing_user:
            continue

        conn.execute(
            """
            INSERT INTO users (username, hashed_password, db_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, get_password_hash(password), str(db_path), now, now),
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

    with _connect_accounts_db() as conn:
        _create_accounts_schema(conn)
        _seed_env_accounts(conn)
        _seed_invite_codes(conn)
        conn.commit()
    _ACCOUNTS_STORE_INITIALIZED = True


def _row_to_account(row: sqlite3.Row) -> AccountConfig:
    return AccountConfig(
        id=int(row["id"]),
        username=row["username"],
        hashed_password=row["hashed_password"],
        db_path=Path(row["db_path"]).resolve(),
    )


def load_accounts() -> list[AccountConfig]:
    init_accounts_store()
    with _connect_accounts_db() as conn:
        rows = conn.execute(
            """
            SELECT id, username, hashed_password, db_path
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
    with _connect_accounts_db() as conn:
        row = conn.execute(
            """
            SELECT id, username, hashed_password, db_path
            FROM users
            WHERE username = ?
            """,
            (normalized,),
        ).fetchone()
    return _row_to_account(row) if row else None


def user_exists(username: str | None) -> bool:
    return get_user_by_username(username) is not None


def get_db_path_for_username(username: str | None) -> Path:
    account = get_user_by_username(username)
    if account:
        return account.db_path
    return PRIMARY_ACCOUNT.db_path


def list_unique_db_paths() -> list[Path]:
    accounts = load_accounts()
    unique_paths: list[Path] = []
    seen: set[Path] = set()
    for account in accounts:
        if account.db_path in seen:
            continue
        seen.add(account.db_path)
        unique_paths.append(account.db_path)
    return unique_paths


def _db_path_exists(conn: sqlite3.Connection, db_path: Path) -> bool:
    row = conn.execute(
        """
        SELECT 1
        FROM users
        WHERE db_path = ?
        """,
        (str(db_path.resolve()),),
    ).fetchone()
    return row is not None


def _new_user_db_dir(conn: sqlite3.Connection) -> Path:
    row = conn.execute(
        """
        SELECT db_path
        FROM users
        ORDER BY id
        LIMIT 1
        """
    ).fetchone()
    if row:
        return Path(row["db_path"]).resolve().parent
    return PROJECT_ROOT


def _next_db_path_for_username(conn: sqlite3.Connection, username: str) -> Path:
    slug = _slug_username(username)
    db_dir = _new_user_db_dir(conn)
    candidate = (db_dir / f"tasks_{slug}.db").resolve()
    if not _db_path_exists(conn, candidate):
        return candidate

    suffix = 2
    while True:
        candidate = (db_dir / f"tasks_{slug}_{suffix}.db").resolve()
        if not _db_path_exists(conn, candidate):
            return candidate
        suffix += 1


def register_user(username: str, password: str, invite_code: str) -> AccountConfig:
    normalized_username = _validate_username(username)
    normalized_code = (invite_code or "").strip()
    if not normalized_code:
        raise InvalidInviteCode("Invite code is required.")

    init_accounts_store()
    with _connect_accounts_db() as conn:
        conn.execute("BEGIN IMMEDIATE")

        existing_user = conn.execute(
            """
            SELECT 1
            FROM users
            WHERE username = ?
            """,
            (normalized_username,),
        ).fetchone()
        if existing_user:
            raise UsernameAlreadyExists("Username is already taken.")

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
        db_path = _next_db_path_for_username(conn, normalized_username)
        cursor = conn.execute(
            """
            INSERT INTO users (username, hashed_password, db_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (normalized_username, get_password_hash(password), str(db_path), now, now),
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
        db_path=db_path,
    )


init_accounts_store()
ACCOUNTS = load_accounts()
PRIMARY_ACCOUNT = ACCOUNTS[0]
ACCOUNTS_BY_USERNAME = {account.username: account for account in ACCOUNTS}
