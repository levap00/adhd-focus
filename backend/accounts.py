import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MAX_ADDITIONAL_ACCOUNTS = 8


@dataclass(frozen=True)
class AccountConfig:
    username: str
    password: str
    db_path: Path


def _slug_username(username: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", (username or "").strip())
    slug = slug.strip("_.-")
    return slug or "user"


def _resolve_db_path(raw_path: str, fallback_name: str) -> Path:
    configured = (raw_path or "").strip()
    path = Path(configured) if configured else Path(fallback_name)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def _build_primary_account() -> AccountConfig:
    username = (os.getenv("FOCUS_USERNAME", "admin") or "admin").strip() or "admin"
    password = os.getenv("FOCUS_PASSWORD", "admin")
    db_path = _resolve_db_path(os.getenv("FOCUS_DB_PATH", ""), "tasks.db")
    return AccountConfig(username=username, password=password, db_path=db_path)


def _build_additional_account(index: int) -> AccountConfig | None:
    username = (os.getenv(f"FOCUS_USERNAME_{index}", "") or "").strip()
    password = os.getenv(f"FOCUS_PASSWORD_{index}", "")
    if not username or not password:
        return None

    db_path = _resolve_db_path(
        os.getenv(f"FOCUS_DB_PATH_{index}", ""),
        f"tasks_{_slug_username(username)}.db",
    )
    return AccountConfig(username=username, password=password, db_path=db_path)


def load_accounts() -> list[AccountConfig]:
    accounts: list[AccountConfig] = [_build_primary_account()]

    for index in range(2, 2 + _MAX_ADDITIONAL_ACCOUNTS):
        account = _build_additional_account(index)
        if account:
            accounts.append(account)

    usernames_seen: set[str] = set()
    db_paths_seen: dict[Path, str] = {}
    for account in accounts:
        if account.username in usernames_seen:
            raise RuntimeError(f"Duplicate username in .env: {account.username}")
        usernames_seen.add(account.username)

        existing_owner = db_paths_seen.get(account.db_path)
        if existing_owner and existing_owner != account.username:
            raise RuntimeError(
                f"Users '{existing_owner}' and '{account.username}' point to the same database path: {account.db_path}"
            )
        db_paths_seen[account.db_path] = account.username

    return accounts


ACCOUNTS = load_accounts()
PRIMARY_ACCOUNT = ACCOUNTS[0]
ACCOUNTS_BY_USERNAME = {account.username: account for account in ACCOUNTS}


def get_db_path_for_username(username: str | None) -> Path:
    account = ACCOUNTS_BY_USERNAME.get((username or "").strip())
    if account:
        return account.db_path
    return PRIMARY_ACCOUNT.db_path


def list_unique_db_paths() -> list[Path]:
    unique_paths: list[Path] = []
    seen: set[Path] = set()
    for account in ACCOUNTS:
        if account.db_path in seen:
            continue
        seen.add(account.db_path)
        unique_paths.append(account.db_path)
    return unique_paths
