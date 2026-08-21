from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.accounts import (
    AccountConfig,
    EmailAlreadyExists,
    InvalidEmail,
    get_user_by_email,
    get_user_by_username,
    mark_email_verified,
    validate_email,
)
from backend.auth import attach_device_cookie, get_device_token, get_request_user, request_ip, request_user_agent
from backend.devices import (
    ChallengeExpired,
    ChallengeNotFound,
    InvalidOtpCode,
    ResendCooldown,
    TooManyOtpAttempts,
    consume_challenge,
    create_challenge,
    create_trusted_device,
    find_active_email_challenge,
    find_trusted_device,
    list_trusted_devices,
    mask_email,
    resend_challenge,
    revoke_all_trusted_devices,
    revoke_trusted_device,
    verify_challenge_code,
)
from backend.mailer import MailerError, is_configured, peek_dev_code, send_login_code
from backend.rate_limit import limiter
from backend.schemas import EmailConfirmPayload, EmailStartPayload

router = APIRouter(prefix="/security", tags=["security"])


def _current_account() -> AccountConfig:
    account = get_user_by_username(get_request_user())
    if not account:
        raise HTTPException(status_code=401, detail="Brak aktywnego uzytkownika.")
    return account


def _profile_payload(account: AccountConfig, request: Request, device_token: str = "") -> dict:
    current_token = device_token or get_device_token(request)
    pending = find_active_email_challenge(account.id)
    return {
        "username": account.username,
        "email": account.email,
        "email_masked": mask_email(account.email),
        "email_verified": account.email_verified,
        "mailer_configured": is_configured(),
        "pending_email": pending.get("email") if pending else "",
        "pending_email_masked": mask_email(pending.get("email") if pending else ""),
        "devices": list_trusted_devices(account.id, current_token),
        "dev_code": peek_dev_code(pending.get("email") if pending else ""),
    }


@router.get("/profile")
def security_profile(request: Request):
    return _profile_payload(_current_account(), request)


@router.post("/email/start")
@limiter.limit("5/minute")
def start_email_verification(request: Request, payload: EmailStartPayload):
    account = _current_account()
    if not is_configured():
        raise HTTPException(
            status_code=503,
            detail="Wysylka e-mail nie jest jeszcze skonfigurowana na serwerze.",
        )
    try:
        email = validate_email(payload.email, required=True)
    except InvalidEmail as exc:
        raise HTTPException(status_code=422, detail="Podaj poprawny adres e-mail.") from exc

    existing = get_user_by_email(email)
    if existing and existing.id != account.id:
        raise HTTPException(status_code=409, detail="Ten adres e-mail jest juz uzywany.")

    _challenge_id, code = create_challenge(
        user_id=account.id,
        email=email,
        purpose="verify_email",
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
    try:
        send_login_code(email, code, account.username, "verify_email")
    except MailerError as exc:
        raise HTTPException(status_code=502, detail="Nie udalo sie wyslac kodu na e-mail.") from exc

    return {
        "ok": True,
        "email_masked": mask_email(email),
        "dev_code": peek_dev_code(email),
    }


@router.post("/email/resend")
@limiter.limit("3/minute")
def resend_email_verification(request: Request):
    account = _current_account()
    pending = find_active_email_challenge(account.id)
    if not pending:
        raise HTTPException(status_code=400, detail="Najpierw podaj nowy adres e-mail.")
    try:
        challenge, code = resend_challenge(pending["id"])
        send_login_code(challenge.get("email") or "", code, account.username, "verify_email")
    except ResendCooldown as exc:
        raise HTTPException(status_code=429, detail=f"Poczekaj {exc.retry_after} s przed kolejnym kodem.") from exc
    except MailerError as exc:
        raise HTTPException(status_code=502, detail="Nie udalo sie wyslac kodu na e-mail.") from exc
    except (ChallengeExpired, ChallengeNotFound) as exc:
        raise HTTPException(status_code=400, detail="Sesja weryfikacji wygasla. Podaj e-mail ponownie.") from exc
    return {
        "ok": True,
        "email_masked": mask_email(challenge.get("email") or ""),
        "dev_code": peek_dev_code(challenge.get("email") or ""),
    }


@router.post("/email/confirm")
@limiter.limit("10/minute")
def confirm_email_verification(request: Request, payload: EmailConfirmPayload):
    account = _current_account()
    pending = find_active_email_challenge(account.id)
    if not pending:
        raise HTTPException(status_code=400, detail="Brak kodu do potwierdzenia. Wyslij e-mail ponownie.")
    try:
        challenge = verify_challenge_code(pending["id"], payload.code)
    except InvalidOtpCode as exc:
        raise HTTPException(status_code=400, detail="Niepoprawny kod.") from exc
    except TooManyOtpAttempts as exc:
        raise HTTPException(status_code=400, detail="Za duzo blednych kodow. Wyslij e-mail ponownie.") from exc
    except (ChallengeExpired, ChallengeNotFound) as exc:
        raise HTTPException(status_code=400, detail="Kod wygasl. Wyslij e-mail ponownie.") from exc

    try:
        updated = mark_email_verified(account.id, challenge.get("email") or "")
    except EmailAlreadyExists as exc:
        raise HTTPException(status_code=409, detail="Ten adres e-mail jest juz uzywany.") from exc

    consume_challenge(pending["id"])
    current_token = get_device_token(request)
    attach_cookie = False
    if not find_trusted_device(updated.id, current_token):
        current_token = create_trusted_device(
            updated.id,
            ip_address=request_ip(request),
            user_agent=request_user_agent(request),
        )
        attach_cookie = True

    body = _profile_payload(updated, request, current_token)
    if attach_cookie:
        response = JSONResponse(body)
        attach_device_cookie(response, request, current_token)
        return response
    return body


@router.delete("/devices/{device_id}")
def delete_trusted_device(device_id: int):
    account = _current_account()
    if not revoke_trusted_device(account.id, device_id):
        raise HTTPException(status_code=404, detail="Nie znaleziono urzadzenia.")
    return {"ok": True}


@router.post("/devices/revoke-all")
def delete_all_trusted_devices():
    account = _current_account()
    revoked = revoke_all_trusted_devices(account.id)
    return {"ok": True, "revoked": revoked}
