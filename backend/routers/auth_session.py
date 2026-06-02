from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from backend.auth import (
    SESSION_COOKIE_NAME,
    SESSION_REMEMBER_TTL_SECONDS,
    SESSION_TTL_SECONDS,
    create_session_token,
    get_session_user,
    resolve_authenticated_username,
    should_set_secure_cookie,
)

router = APIRouter()


def _render_login_page(show_error: bool = False) -> str:
    error_block = (
        '<div class="error">Nieprawidlowy login lub haslo. Sprobuj ponownie.</div>'
        if show_error
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Logowanie | ADHD Focus OS</title>
  <style>
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
    input[type="text"], input[type="password"] {{
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
    input:focus {{ border-color: #10b981; background: #ffffff; }}
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
      background: #059669;
      color: white;
      font-weight: 800;
      cursor: pointer;
    }}
    button:hover {{ background: #047857; }}
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
    .hint {{ margin-top: 14px; font-size: 0.76rem; color: #64748b; }}
  </style>
</head>
<body>
  <main class="card">
    <h1>ADHD Focus OS</h1>
    <p>Zaloguj sie, aby wejsc do planera.</p>
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
    <div class="hint">Po zalogowaniu sesja zostanie zapisana w bezpiecznym cookie.</div>
  </main>
</body>
</html>
"""


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: int = 0):
    if get_session_user(request):
        return RedirectResponse(url="/", status_code=303)
    return HTMLResponse(_render_login_page(show_error=bool(error)))


@router.post("/auth/login")
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
    token = create_session_token(username=authenticated_username, remember=remember_user)

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_REMEMBER_TTL_SECONDS if remember_user else SESSION_TTL_SECONDS,
        httponly=True,
        secure=should_set_secure_cookie(request),
        samesite="lax",
        path="/",
    )
    return response


@router.post("/auth/logout")
def logout_submit():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return response


@router.get("/auth/session")
def auth_session(request: Request):
    username = get_session_user(request)
    return {
        "authenticated": bool(username),
        "username": username or "",
    }
