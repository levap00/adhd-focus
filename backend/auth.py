import base64
import binascii
import hashlib
import hmac
import os
import secrets
from contextvars import ContextVar, Token
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from backend.accounts import ACCOUNTS_DB_PATH, get_user_by_username, user_exists
from backend.passwords import get_password_hash, verify_password

load_dotenv()

SESSION_COOKIE_NAME = os.getenv("FOCUS_SESSION_COOKIE_NAME", "focus_session")
SESSION_COOKIE_SECURE_MODE = (os.getenv("FOCUS_COOKIE_SECURE", "auto") or "auto").strip().lower()
SESSION_TTL_SECONDS = max(300, int(os.getenv("FOCUS_SESSION_TTL_SECONDS", "43200")))
SESSION_REMEMBER_TTL_SECONDS = max(300, int(os.getenv("FOCUS_SESSION_REMEMBER_TTL_SECONDS", "2592000")))
SESSION_SECRET = os.getenv("FOCUS_SESSION_SECRET", f"{ACCOUNTS_DB_PATH}:focus-session-secret")

security = HTTPBasic(auto_error=False)
_current_request_user: ContextVar[Optional[str]] = ContextVar("current_request_user", default=None)


def _is_request_https(request: Request) -> bool:
    forwarded_proto = (request.headers.get("x-forwarded-proto") or "").split(",")[0].strip().lower()
    if forwarded_proto:
        return forwarded_proto == "https"
    return request.url.scheme == "https"


def should_set_secure_cookie(request: Request) -> bool:
    if SESSION_COOKIE_SECURE_MODE == "true":
        return True
    if SESSION_COOKIE_SECURE_MODE == "false":
        return False
    return _is_request_https(request)


def authenticate_credentials(username: str, password: str) -> bool:
    return resolve_authenticated_username(username, password) is not None


def resolve_authenticated_username(username: str, password: str) -> Optional[str]:
    username = (username or "").strip()
    account = get_user_by_username(username)
    if not account:
        return None

    if secrets.compare_digest(username, account.username) and verify_password(password, account.hashed_password):
        return account.username
    return None


def _decode_basic_query_token(raw_token: str) -> Optional[tuple[str, str]]:
    clean_token = (raw_token or "").strip().replace(" ", "+")
    if not clean_token:
        return None

    padded_token = clean_token + ("=" * (-len(clean_token) % 4))
    for altchars in (None, b"-_"):
        try:
            decoded = base64.b64decode(
                padded_token.encode("ascii"),
                altchars=altchars,
                validate=True,
            ).decode("utf-8")
        except (binascii.Error, UnicodeEncodeError, UnicodeDecodeError):
            continue

        if ":" not in decoded:
            continue
        username, password = decoded.split(":", 1)
        return username, password

    return None


def resolve_query_token_user(raw_token: str) -> Optional[str]:
    credentials = _decode_basic_query_token(raw_token)
    if not credentials:
        return None
    username, password = credentials
    return resolve_authenticated_username(username, password)


def set_request_user(username: Optional[str]) -> Token:
    normalized = (username or "").strip() or None
    return _current_request_user.set(normalized)


def reset_request_user(token: Token) -> None:
    _current_request_user.reset(token)


def get_request_user() -> Optional[str]:
    return _current_request_user.get()


def _sign_payload(payload: str) -> str:
    return hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def create_session_token(username: str, remember: bool = False) -> str:
    ttl_seconds = SESSION_REMEMBER_TTL_SECONDS if remember else SESSION_TTL_SECONDS
    expires_at = int((datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)).timestamp())
    payload = f"{username}|{expires_at}"
    signature = _sign_payload(payload)
    raw_token = f"{payload}|{signature}".encode("utf-8")
    return base64.urlsafe_b64encode(raw_token).decode("utf-8")


def decode_session_token(token: str) -> Optional[str]:
    if not token:
        return None
    try:
        raw_token = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
    except Exception:
        return None

    parts = raw_token.split("|")
    if len(parts) != 3:
        return None

    username, expires_at_raw, signature = parts
    try:
        expires_at = int(expires_at_raw)
    except ValueError:
        return None

    if expires_at < int(datetime.now(timezone.utc).timestamp()):
        return None

    payload = f"{username}|{expires_at}"
    if not secrets.compare_digest(signature, _sign_payload(payload)):
        return None

    if not user_exists(username):
        return None

    return username


def get_session_user(request: Request) -> Optional[str]:
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    return decode_session_token(token)


async def verify_credentials(
    request: Request,
    credentials: Optional[HTTPBasicCredentials] = Depends(security),
) -> str:
    session_user = get_session_user(request)
    if session_user:
        set_request_user(session_user)
        return session_user

    if credentials:
        basic_user = resolve_authenticated_username(credentials.username, credentials.password)
        if basic_user:
            set_request_user(basic_user)
            return basic_user

    query_token = request.query_params.get("token", "")
    if query_token:
        token_user = resolve_query_token_user(query_token)
        if token_user:
            set_request_user(token_user)
            return token_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Brak dostepu. Zaloguj sie przez /login.",
    )
