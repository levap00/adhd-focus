from urllib.parse import parse_qs

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from backend.accounts import (
    EmailAlreadyExists,
    InvalidEmail,
    InvalidInviteCode,
    UsernameAlreadyExists,
    get_user_by_id,
    get_user_by_username,
    mark_email_verified,
    register_user,
)
from backend.auth import (
    attach_challenge_cookie,
    attach_device_cookie,
    attach_session_cookie,
    clear_challenge_cookie,
    clear_session_cookie,
    get_challenge_id,
    get_device_token,
    get_session_user,
    request_ip,
    request_user_agent,
    resolve_authenticated_username,
)
from backend.db import init_db_for_username
from backend.devices import (
    ChallengeExpired,
    ChallengeNotFound,
    InvalidOtpCode,
    ResendCooldown,
    TooManyOtpAttempts,
    consume_challenge,
    create_challenge,
    create_trusted_device,
    find_trusted_device,
    get_challenge,
    mask_email,
    resend_challenge,
    touch_trusted_device,
    verify_challenge_code,
)
from backend.mailer import MailerError, is_configured, peek_dev_code, send_login_code
from backend.rate_limit import limiter
from backend.schemas import RegisterPayload, RegisterResponse

router = APIRouter()


def _login_error_message(error: str) -> str:
    return {
        "1": "Nieprawidlowy login lub haslo. Sprobuj ponownie.",
        "mail": "Haslo OK, ale nie udalo sie wyslac kodu na e-mail. Sprobuj ponownie za chwile.",
        "expired": "Kod wygasl albo sesja weryfikacji jest nieaktualna. Zaloguj sie ponownie.",
        "attempts": "Za duzo blednych kodow. Zaloguj sie ponownie.",
    }.get(error, "")


def _auth_css(accent: str) -> str:
    return f"""
    :root {{ color-scheme: light; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      font-family: "Plus Jakarta Sans", system-ui, sans-serif;
      background:
        radial-gradient(circle at 10% 0%, rgba(240, 253, 244, 0.95), transparent 35%),
        linear-gradient(155deg, #ecfeff 0%, #e2e8f0 55%, #eef2ff 100%);
      color: #0f172a;
    }}
    .card {{
      width: min(92vw, 430px);
      border-radius: 24px;
      border: 1px solid #cbd5e1;
      background: rgba(255, 255, 255, 0.92);
      box-shadow: 0 28px 50px rgba(15, 23, 42, 0.16);
      padding: 28px;
      backdrop-filter: blur(8px);
    }}
    h1 {{ margin: 0 0 6px; font-size: 1.7rem; }}
    p {{ margin: 0 0 18px; color: #475569; font-size: 0.94rem; }}
    label {{ display: block; margin-top: 12px; font-weight: 700; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.07em; color: #64748b; }}
    input[type="text"], input[type="password"], input[type="email"] {{
      width: 100%;
      margin-top: 6px;
      padding: 12px 13px;
      border: 1px solid #cbd5e1;
      border-radius: 14px;
      font-size: 0.95rem;
      outline: none;
      box-sizing: border-box;
      background: #f8fafc;
    }}
    input:focus {{ border-color: {accent}; background: #ffffff; }}
    .remember {{
      margin-top: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
      color: #475569;
      font-size: 0.9rem;
    }}
    button {{
      margin-top: 20px;
      width: 100%;
      border: 0;
      border-radius: 14px;
      padding: 12px;
      background: {accent};
      color: white;
      font-weight: 800;
      cursor: pointer;
    }}
    .ghost {{
      margin-top: 10px;
      background: #ffffff;
      color: #0f172a;
      border: 1px solid #cbd5e1;
    }}
    .error {{
      margin: 10px 0 4px;
      border-radius: 12px;
      background: #fef2f2;
      border: 1px solid #fecaca;
      padding: 10px 12px;
      color: #b91c1c;
      font-size: 0.86rem;
      font-weight: 700;
    }}
    .success {{
      margin: 10px 0 4px;
      border-radius: 12px;
      background: #ecfdf5;
      border: 1px solid #bbf7d0;
      padding: 10px 12px;
      color: #047857;
      font-size: 0.86rem;
      font-weight: 700;
    }}
    .dev-code {{
      margin: 10px 0 4px;
      border-radius: 12px;
      background: #fffbeb;
      border: 1px dashed #f59e0b;
      padding: 10px 12px;
      color: #92400e;
      font-size: 0.86rem;
      font-weight: 700;
    }}
    .hint {{ margin-top: 14px; font-size: 0.76rem; color: #64748b; line-height: 1.45; }}
    .secondary-link {{
      display: block;
      margin-top: 12px;
      border-radius: 14px;
      border: 1px solid #cbd5e1;
      padding: 11px 12px;
      text-align: center;
      color: #0f172a;
      font-size: 0.9rem;
      font-weight: 800;
      text-decoration: none;
      background: #ffffff;
    }}
    .code-input {{
      letter-spacing: 0.35em;
      font-weight: 800;
      text-align: center;
      font-size: 1.35rem !important;
    }}
    """


def _render_login_page(error: str = "", show_registered: bool = False) -> str:
    error_message = _login_error_message(error)
    error_block = f'<div class="error">{error_message}</div>' if error_message else ""
    success_block = (
        '<div class="success">Konto utworzone. Mozesz sie teraz zalogowac.</div>'
        if show_registered
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Logowanie | ADHD Focus OS</title>
  <style>{_auth_css("#059669")}</style>
</head>
<body>
  <main class="card">
    <h1>ADHD Focus OS</h1>
    <p>Zaloguj sie, aby wejsc do planera.</p>
    {success_block}
    {error_block}
    <form method="post" action="/auth/login" autocomplete="on">
      <label for="username">Login</label>
      <input id="username" name="username" type="text" autocomplete="username" required />

      <label for="password">Haslo</label>
      <input id="password" name="password" type="password" autocomplete="current-password" required />

      <label class="remember" for="remember">
        <input id="remember" name="remember" value="1" type="checkbox" />
        Zapamietaj mnie
      </label>

      <button type="submit">Zaloguj</button>
    </form>
    <a class="secondary-link" href="/register">Zarejestruj konto</a>
    <div class="hint">Jesli konto ma potwierdzony e-mail, nowe urzadzenie poprosi o kod z poczty.</div>
  </main>
</body>
</html>
"""


def _registration_error_message(error: str) -> str:
    return {
        "invite": "Kod zaproszenia jest niepoprawny albo zostal juz uzyty.",
        "username": "Ta nazwa uzytkownika jest juz zajeta.",
        "invalid": "Sprawdz login, e-mail, haslo i kod zaproszenia. Haslo musi miec 8-72 znaki.",
        "email": "Ten adres e-mail jest juz uzywany albo wyglada na niepoprawny.",
    }.get(error, "")


def _render_register_page(error: str = "") -> str:
    error_message = _registration_error_message(error)
    error_block = f'<div class="error">{error_message}</div>' if error_message else ""
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Rejestracja | ADHD Focus OS</title>
  <style>{_auth_css("#2563eb")}</style>
</head>
<body>
  <main class="card">
    <h1>Utworz konto</h1>
    <p>Wpisz login, e-mail, haslo i jednorazowy kod zaproszenia.</p>
    {error_block}
    <form method="post" action="/auth/register" autocomplete="on">
      <label for="username">Login</label>
      <input id="username" name="username" type="text" autocomplete="username" minlength="3" maxlength="64" required />

      <label for="email">E-mail</label>
      <input id="email" name="email" type="email" autocomplete="email" maxlength="254" required />

      <label for="password">Haslo</label>
      <input id="password" name="password" type="password" autocomplete="new-password" minlength="8" maxlength="72" required />

      <label for="invite_code">Kod zaproszenia</label>
      <input id="invite_code" name="invite_code" type="text" autocomplete="off" required />

      <button type="submit">Zarejestruj</button>
    </form>
    <a class="secondary-link" href="/login">Mam juz konto</a>
    <div class="hint">Kod zaproszenia dziala tylko raz. Przy pierwszym logowaniu wyslemy kod na e-mail, zeby potwierdzic konto i to urzadzenie.</div>
  </main>
</body>
</html>
"""


def _render_verify_page(masked_email: str, error: str = "", info: str = "", dev_code: str = "") -> str:
    error_block = f'<div class="error">{error}</div>' if error else ""
    info_block = f'<div class="success">{info}</div>' if info else ""
    dev_block = (
        f'<div class="dev-code">Tryb deweloperski: kod to {dev_code}</div>'
        if dev_code
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1" />
  <title>Kod z e-maila | ADHD Focus OS</title>
  <style>{_auth_css("#059669")}</style>
</head>
<body>
  <main class="card">
    <h1>Nowe urzadzenie</h1>
    <p>Wpisz 6-cyfrowy kod wyslany na <strong>{masked_email}</strong>. To urzadzenie zapamietamy na pozniej.</p>
    {error_block}
    {info_block}
    {dev_block}
    <form method="post" action="/auth/verify-device" autocomplete="one-time-code">
      <label for="code">Kod z e-maila</label>
      <input id="code" name="code" class="code-input" type="text" inputmode="numeric" pattern="[0-9]*" minlength="6" maxlength="6" autocomplete="one-time-code" required autofocus />
      <button type="submit">Potwierdz i wejdź</button>
    </form>
    <form method="post" action="/auth/resend-code">
      <button class="ghost" type="submit">Wyslij kod ponownie</button>
    </form>
    <a class="secondary-link" href="/login">Wroc do logowania</a>
    <div class="hint">Kod wygasa po 10 minutach. Po potwierdzeniu to urzadzenie nie bedzie juz pytane o maila.</div>
  </main>
</body>
</html>
"""


def _should_challenge_login(account) -> bool:
    return bool(account and account.email and is_configured())


def _finish_login(request: Request, username: str, remember: bool, device_token: str = "") -> RedirectResponse:
    response = RedirectResponse(url="/", status_code=303)
    attach_session_cookie(response, request, username, remember)
    if device_token:
        attach_device_cookie(response, request, device_token)
    clear_challenge_cookie(response)
    return response


def _verify_page_from_request(request: Request, error: str = "", info: str = "") -> HTMLResponse:
    challenge_id = get_challenge_id(request)
    if not challenge_id:
        return HTMLResponse(_render_login_page(error="expired"))
    try:
        challenge = get_challenge(challenge_id)
    except (ChallengeExpired, ChallengeNotFound):
        return HTMLResponse(_render_login_page(error="expired"))
    return HTMLResponse(
        _render_verify_page(
            masked_email=mask_email(challenge.get("email") or ""),
            error=error,
            info=info,
            dev_code=peek_dev_code(challenge.get("email") or ""),
        )
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: str = "", registered: int = 0):
    if get_session_user(request):
        return RedirectResponse(url="/", status_code=303)
    return HTMLResponse(_render_login_page(error=str(error or ""), show_registered=bool(registered)))


@router.get("/login/verify", response_class=HTMLResponse)
def login_verify_page(request: Request):
    if get_session_user(request):
        return RedirectResponse(url="/", status_code=303)
    return _verify_page_from_request(request)


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, error: str = ""):
    if get_session_user(request):
        return RedirectResponse(url="/", status_code=303)
    return HTMLResponse(_render_register_page(error=error))


@router.post("/auth/login")
@limiter.limit("5/minute")
async def login_submit(request: Request):
    body_raw = (await request.body()).decode("utf-8", errors="ignore")
    form_values = parse_qs(body_raw, keep_blank_values=True)
    username = (form_values.get("username", [""])[0] or "").strip()
    password = form_values.get("password", [""])[0] or ""
    remember = form_values.get("remember", [""])[0] or ""

    authenticated_username = resolve_authenticated_username(username, password)
    if not authenticated_username:
        return RedirectResponse(url="/login?error=1", status_code=303)

    remember_user = str(remember).strip().lower() in {"1", "true", "yes", "on"}
    account = get_user_by_username(authenticated_username)
    if not account:
        return RedirectResponse(url="/login?error=1", status_code=303)

    if _should_challenge_login(account):
        existing_token = get_device_token(request)
        trusted = find_trusted_device(account.id, existing_token)
        if trusted:
            touch_trusted_device(int(trusted["id"]), request_ip(request))
            return _finish_login(request, account.username, remember_user, existing_token)

        challenge_id, code = create_challenge(
            user_id=account.id,
            email=account.email,
            purpose="login_device",
            remember=remember_user,
            ip_address=request_ip(request),
            user_agent=request_user_agent(request),
        )
        try:
            send_login_code(account.email, code, account.username, "login_device")
        except MailerError:
            return RedirectResponse(url="/login?error=mail", status_code=303)

        response = RedirectResponse(url="/login/verify", status_code=303)
        attach_challenge_cookie(response, request, challenge_id)
        return response

    return _finish_login(request, account.username, remember_user)


@router.post("/auth/verify-device")
@limiter.limit("10/minute")
async def verify_device_submit(request: Request):
    challenge_id = get_challenge_id(request)
    if not challenge_id:
        return RedirectResponse(url="/login?error=expired", status_code=303)

    body_raw = (await request.body()).decode("utf-8", errors="ignore")
    form_values = parse_qs(body_raw, keep_blank_values=True)
    code = form_values.get("code", [""])[0] or ""

    try:
        challenge = verify_challenge_code(challenge_id, code)
    except InvalidOtpCode:
        return _verify_page_from_request(request, error="Niepoprawny kod. Sprobuj ponownie.")
    except TooManyOtpAttempts:
        response = RedirectResponse(url="/login?error=attempts", status_code=303)
        clear_challenge_cookie(response)
        return response
    except (ChallengeExpired, ChallengeNotFound):
        response = RedirectResponse(url="/login?error=expired", status_code=303)
        clear_challenge_cookie(response)
        return response

    account = get_user_by_id(int(challenge["user_id"]))
    if not account:
        response = RedirectResponse(url="/login?error=expired", status_code=303)
        clear_challenge_cookie(response)
        return response

    if challenge.get("purpose") == "login_device" and not account.email_verified:
        mark_email_verified(account.id, challenge.get("email") or account.email)

    consume_challenge(challenge_id)
    device_token = create_trusted_device(
        account.id,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
    )
    remember_user = bool(int(challenge.get("remember") or 0))
    return _finish_login(request, account.username, remember_user, device_token)


@router.post("/auth/resend-code")
@limiter.limit("3/minute")
async def resend_code_submit(request: Request):
    challenge_id = get_challenge_id(request)
    if not challenge_id:
        return RedirectResponse(url="/login?error=expired", status_code=303)

    try:
        challenge, code = resend_challenge(challenge_id)
        send_login_code(challenge.get("email") or "", code, "", challenge.get("purpose") or "login_device")
    except ResendCooldown as exc:
        return _verify_page_from_request(request, error=f"Poczekaj {exc.retry_after} s przed kolejnym kodem.")
    except MailerError:
        return _verify_page_from_request(request, error="Nie udalo sie wyslac kodu. Sprobuj ponownie.")
    except (ChallengeExpired, ChallengeNotFound):
        response = RedirectResponse(url="/login?error=expired", status_code=303)
        clear_challenge_cookie(response)
        return response

    return _verify_page_from_request(request, info="Wyslalismy nowy kod.")


@router.post("/auth/register")
@limiter.limit("5/minute")
async def register_form_submit(request: Request):
    body_raw = (await request.body()).decode("utf-8", errors="ignore")
    form_values = parse_qs(body_raw, keep_blank_values=True)

    try:
        payload = RegisterPayload(
            username=(form_values.get("username", [""])[0] or "").strip(),
            password=form_values.get("password", [""])[0] or "",
            invite_code=(form_values.get("invite_code", [""])[0] or "").strip(),
            email=(form_values.get("email", [""])[0] or "").strip(),
        )
        account = register_user(payload.username, payload.password, payload.invite_code, payload.email)
    except UsernameAlreadyExists:
        return RedirectResponse(url="/register?error=username", status_code=303)
    except EmailAlreadyExists:
        return RedirectResponse(url="/register?error=email", status_code=303)
    except InvalidInviteCode:
        return RedirectResponse(url="/register?error=invite", status_code=303)
    except (InvalidEmail, ValidationError, ValueError):
        return RedirectResponse(url="/register?error=invalid", status_code=303)

    init_db_for_username(account.username)
    return RedirectResponse(url="/login?registered=1", status_code=303)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register_submit(request: Request, payload: RegisterPayload):
    try:
        account = register_user(payload.username, payload.password, payload.invite_code, payload.email)
    except UsernameAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nazwa uzytkownika jest juz zajeta.") from exc
    except EmailAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ten adres e-mail jest juz uzywany.") from exc
    except InvalidInviteCode as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kod zaproszenia jest niepoprawny albo zuzyty.") from exc
    except InvalidEmail as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Podaj poprawny adres e-mail.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    init_db_for_username(account.username)
    return RegisterResponse(id=account.id, username=account.username, email=account.email)


@router.post("/auth/logout")
def logout_submit():
    response = RedirectResponse(url="/login", status_code=303)
    clear_session_cookie(response)
    return response


@router.get("/auth/session")
def auth_session(request: Request):
    username = get_session_user(request)
    return {
        "authenticated": bool(username),
        "username": username or "",
    }
