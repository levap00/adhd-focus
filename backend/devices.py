import hashlib
import hmac
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from backend.accounts import ACCOUNTS_DB_PATH
from backend.db import get_db
from backend.utils import utc_now_iso

OTP_TTL_SECONDS = 10 * 60
RESEND_COOLDOWN_SECONDS = 45
MAX_OTP_ATTEMPTS = 5
MAX_TRUSTED_DEVICES = 10
DEVICE_TTL_SECONDS = max(86400, int(os.getenv("FOCUS_DEVICE_TTL_SECONDS", str(180 * 24 * 3600))))
SESSION_SECRET = os.getenv("FOCUS_SESSION_SECRET", f"{ACCOUNTS_DB_PATH}:focus-session-secret")

_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


class DeviceAuthError(Exception):
    pass


class ChallengeExpired(DeviceAuthError):
    pass


class ChallengeNotFound(DeviceAuthError):
    pass


class InvalidOtpCode(DeviceAuthError):
    pass


class TooManyOtpAttempts(DeviceAuthError):
    pass


class ResendCooldown(DeviceAuthError):
    def __init__(self, retry_after: int):
        super().__init__("Poczekaj chwilę przed kolejnym kodem.")
        self.retry_after = retry_after


def normalize_email(email: str | None) -> str:
    return (email or "").strip().lower()


def is_valid_email(email: str | None) -> bool:
    value = normalize_email(email)
    return bool(value) and len(value) <= 254 and bool(_EMAIL_PATTERN.match(value))


def mask_email(email: str | None) -> str:
    value = normalize_email(email)
    if "@" not in value:
        return ""
    local, _, domain = value.partition("@")
    visible = local[:1] if local else ""
    return f"{visible}***@{domain}"


def _hash_value(value: str) -> str:
    return hmac.new(SESSION_SECRET.encode("utf-8"), (value or "").encode("utf-8"), hashlib.sha256).hexdigest()


def hash_otp(code: str) -> str:
    return _hash_value((code or "").strip())


def hash_device_token(token: str) -> str:
    return _hash_value(token or "")


def generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def generate_device_token() -> str:
    return secrets.token_urlsafe(32)


def parse_device_label(user_agent: str) -> str:
    ua = user_agent or ""
    browser = "Przegladarka"
    if "Edg/" in ua:
        browser = "Edge"
    elif "OPR/" in ua or "Opera" in ua:
        browser = "Opera"
    elif "Chrome/" in ua and "Chromium" not in ua:
        browser = "Chrome"
    elif "Firefox/" in ua:
        browser = "Firefox"
    elif "Safari/" in ua:
        browser = "Safari"

    device = "komputer"
    if "iPhone" in ua:
        device = "iPhone"
    elif "iPad" in ua:
        device = "iPad"
    elif "Android" in ua:
        device = "Android"
    elif "Mac OS" in ua or "Macintosh" in ua:
        device = "Mac"
    elif "Windows" in ua:
        device = "Windows"
    elif "Linux" in ua:
        device = "Linux"
    return f"{browser} · {device}"


def _parse_iso(value: str) -> Optional[datetime]:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _is_expired(expires_at: str) -> bool:
    parsed = _parse_iso(expires_at)
    if not parsed:
        return True
    return parsed <= datetime.now(timezone.utc)


def _seconds_since(iso_value: str) -> int:
    parsed = _parse_iso(iso_value)
    if not parsed:
        return 10**9
    return int((datetime.now(timezone.utc) - parsed).total_seconds())


def _row_to_dict(row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def purge_expired_security_rows() -> None:
    now = utc_now_iso()
    with get_db() as conn:
        conn.execute(
            "DELETE FROM login_challenges WHERE (consumed_at != '' AND consumed_at < ?) OR expires_at < ?",
            (now, now),
        )
        conn.execute(
            """
            DELETE FROM trusted_devices
            WHERE (revoked_at != '' AND revoked_at < ?) OR (expires_at != '' AND expires_at < ?)
            """,
            (now, now),
        )
        conn.commit()


def create_challenge(
    user_id: int,
    email: str,
    purpose: str,
    remember: bool = False,
    ip_address: str = "",
    user_agent: str = "",
) -> tuple[str, str]:
    purge_expired_security_rows()
    challenge_id = secrets.token_urlsafe(24)
    code = generate_otp_code()
    now = datetime.now(timezone.utc)
    with get_db() as conn:
        conn.execute(
            """
            UPDATE login_challenges
            SET consumed_at = ?
            WHERE user_id = ? AND purpose = ? AND consumed_at = ''
            """,
            (utc_now_iso(), user_id, purpose),
        )
        conn.execute(
            """
            INSERT INTO login_challenges (
                id, user_id, purpose, email, code_hash, remember, attempts,
                max_attempts, ip_address, user_agent, created_at, expires_at,
                consumed_at, last_sent_at
            ) VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, '', ?)
            """,
            (
                challenge_id,
                user_id,
                purpose,
                normalize_email(email),
                hash_otp(code),
                1 if remember else 0,
                MAX_OTP_ATTEMPTS,
                (ip_address or "")[:64],
                (user_agent or "")[:300],
                now.isoformat(),
                (now + timedelta(seconds=OTP_TTL_SECONDS)).isoformat(),
                now.isoformat(),
            ),
        )
        conn.commit()
    return challenge_id, code


def get_challenge(challenge_id: str) -> dict[str, Any]:
    clean_id = (challenge_id or "").strip()
    if not clean_id:
        raise ChallengeNotFound("Brak sesji weryfikacji.")
    with get_db() as conn:
        row = conn.execute("SELECT * FROM login_challenges WHERE id = ?", (clean_id,)).fetchone()
    if not row:
        raise ChallengeNotFound("Sesja weryfikacji wygasla. Zaloguj sie ponownie.")
    payload = _row_to_dict(row)
    if payload.get("consumed_at"):
        raise ChallengeExpired("Ten kod zostal juz uzyty.")
    if _is_expired(payload.get("expires_at") or ""):
        raise ChallengeExpired("Kod wygasl. Zaloguj sie ponownie.")
    return payload


def verify_challenge_code(challenge_id: str, code: str) -> dict[str, Any]:
    challenge = get_challenge(challenge_id)
    attempts = int(challenge.get("attempts") or 0)
    max_attempts = int(challenge.get("max_attempts") or MAX_OTP_ATTEMPTS)
    if attempts >= max_attempts:
        _consume_challenge(challenge_id)
        raise TooManyOtpAttempts("Za duzo blednych kodow. Zaloguj sie ponownie.")

    submitted = re.sub(r"\D", "", code or "")
    expected_hash = challenge.get("code_hash") or ""
    matches = submitted and secrets.compare_digest(hash_otp(submitted), expected_hash)

    with get_db() as conn:
        conn.execute(
            "UPDATE login_challenges SET attempts = attempts + 1 WHERE id = ?",
            (challenge_id,),
        )
        conn.commit()

    if not matches:
        if attempts + 1 >= max_attempts:
            _consume_challenge(challenge_id)
            raise TooManyOtpAttempts("Za duzo blednych kodow. Zaloguj sie ponownie.")
        raise InvalidOtpCode("Niepoprawny kod.")
    return challenge


def _consume_challenge(challenge_id: str) -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE login_challenges SET consumed_at = ? WHERE id = ? AND consumed_at = ''",
            (utc_now_iso(), challenge_id),
        )
        conn.commit()


def consume_challenge(challenge_id: str) -> None:
    _consume_challenge(challenge_id)


def resend_challenge(challenge_id: str) -> tuple[dict[str, Any], str]:
    challenge = get_challenge(challenge_id)
    wait = RESEND_COOLDOWN_SECONDS - _seconds_since(challenge.get("last_sent_at") or "")
    if wait > 0:
        raise ResendCooldown(wait)

    code = generate_otp_code()
    now = datetime.now(timezone.utc)
    with get_db() as conn:
        conn.execute(
            """
            UPDATE login_challenges
            SET code_hash = ?, attempts = 0, last_sent_at = ?, expires_at = ?
            WHERE id = ?
            """,
            (
                hash_otp(code),
                now.isoformat(),
                (now + timedelta(seconds=OTP_TTL_SECONDS)).isoformat(),
                challenge_id,
            ),
        )
        conn.commit()
    challenge["code_hash"] = hash_otp(code)
    return challenge, code


def find_active_email_challenge(user_id: int) -> Optional[dict[str, Any]]:
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT * FROM login_challenges
            WHERE user_id = ? AND purpose = 'verify_email' AND consumed_at = ''
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()
    if not row:
        return None
    payload = _row_to_dict(row)
    if _is_expired(payload.get("expires_at") or ""):
        return None
    return payload


def find_trusted_device(user_id: int, raw_token: str | None) -> Optional[dict[str, Any]]:
    token = (raw_token or "").strip()
    if not token:
        return None
    token_hash = hash_device_token(token)
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT * FROM trusted_devices
            WHERE user_id = ? AND token_hash = ? AND revoked_at = ''
            LIMIT 1
            """,
            (user_id, token_hash),
        ).fetchone()
    if not row:
        return None
    payload = _row_to_dict(row)
    if _is_expired(payload.get("expires_at") or ""):
        return None
    return payload


def create_trusted_device(user_id: int, ip_address: str = "", user_agent: str = "") -> str:
    raw_token = generate_device_token()
    now = datetime.now(timezone.utc)
    label = parse_device_label(user_agent)
    with get_db() as conn:
        extra = conn.execute(
            """
            SELECT id FROM trusted_devices
            WHERE user_id = ? AND revoked_at = ''
            ORDER BY last_seen_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()
        if len(extra) >= MAX_TRUSTED_DEVICES:
            for row in extra[MAX_TRUSTED_DEVICES - 1 :]:
                conn.execute(
                    "UPDATE trusted_devices SET revoked_at = ? WHERE id = ?",
                    (utc_now_iso(), int(row["id"])),
                )
        conn.execute(
            """
            INSERT INTO trusted_devices (
                user_id, token_hash, label, user_agent, ip_address,
                created_at, last_seen_at, expires_at, revoked_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, '')
            """,
            (
                user_id,
                hash_device_token(raw_token),
                label,
                (user_agent or "")[:300],
                (ip_address or "")[:64],
                now.isoformat(),
                now.isoformat(),
                (now + timedelta(seconds=DEVICE_TTL_SECONDS)).isoformat(),
            ),
        )
        conn.commit()
    return raw_token


def touch_trusted_device(device_id: int, ip_address: str = "") -> None:
    with get_db() as conn:
        if ip_address:
            conn.execute(
                "UPDATE trusted_devices SET last_seen_at = ?, ip_address = ? WHERE id = ?",
                (utc_now_iso(), ip_address[:64], device_id),
            )
        else:
            conn.execute(
                "UPDATE trusted_devices SET last_seen_at = ? WHERE id = ?",
                (utc_now_iso(), device_id),
            )
        conn.commit()


def list_trusted_devices(user_id: int, current_token: str = "") -> list[dict[str, Any]]:
    current_hash = hash_device_token(current_token) if current_token else ""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT id, label, user_agent, ip_address, created_at, last_seen_at, expires_at, token_hash
            FROM trusted_devices
            WHERE user_id = ? AND revoked_at = ''
            ORDER BY last_seen_at DESC, id DESC
            """,
            (user_id,),
        ).fetchall()
    devices = []
    for row in rows:
        if _is_expired(row["expires_at"] or ""):
            continue
        devices.append(
            {
                "id": int(row["id"]),
                "label": row["label"] or parse_device_label(row["user_agent"] or ""),
                "ip_address": row["ip_address"] or "",
                "created_at": row["created_at"] or "",
                "last_seen_at": row["last_seen_at"] or "",
                "is_current": bool(current_hash) and secrets.compare_digest(row["token_hash"], current_hash),
            }
        )
    return devices


def revoke_trusted_device(user_id: int, device_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute(
            """
            UPDATE trusted_devices
            SET revoked_at = ?
            WHERE id = ? AND user_id = ? AND revoked_at = ''
            """,
            (utc_now_iso(), device_id, user_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def revoke_all_trusted_devices(user_id: int) -> int:
    with get_db() as conn:
        cursor = conn.execute(
            """
            UPDATE trusted_devices
            SET revoked_at = ?
            WHERE user_id = ? AND revoked_at = ''
            """,
            (utc_now_iso(), user_id),
        )
        conn.commit()
        return int(cursor.rowcount or 0)
