import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

load_dotenv()

USERNAME = os.getenv("FOCUS_USERNAME", "admin")
PASSWORD = os.getenv("FOCUS_PASSWORD", "admin")
SESSION_COOKIE_NAME = os.getenv("FOCUS_SESSION_COOKIE_NAME", "focus_session")
SESSION_COOKIE_SECURE_MODE = (os.getenv("FOCUS_COOKIE_SECURE", "auto") or "auto").strip().lower()
SESSION_TTL_SECONDS = max(300, int(os.getenv("FOCUS_SESSION_TTL_SECONDS", "43200")))
SESSION_REMEMBER_TTL_SECONDS = max(300, int(os.getenv("FOCUS_SESSION_REMEMBER_TTL_SECONDS", "2592000")))
SESSION_SECRET = os.getenv("FOCUS_SESSION_SECRET", f"{USERNAME}:{PASSWORD}:focus-session-secret")

security = HTTPBasic(auto_error=False)


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
    return secrets.compare_digest(username or "", USERNAME) and secrets.compare_digest(password or "", PASSWORD)


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

    if not secrets.compare_digest(username, USERNAME):
        return None

    return username


def get_session_user(request: Request) -> Optional[str]:
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    return decode_session_token(token)


def verify_credentials(
    request: Request,
    credentials: Optional[HTTPBasicCredentials] = Depends(security),
) -> str:
    session_user = get_session_user(request)
    if session_user:
        return session_user

    if credentials and authenticate_credentials(credentials.username, credentials.password):
        return credentials.username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Brak dostepu. Zaloguj sie przez /login.",
    )
