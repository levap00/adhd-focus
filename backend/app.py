import os

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.auth import get_session_user, reset_request_user, set_request_user, verify_credentials
from backend.db import init_db
from backend.rate_limit import install_rate_limiter
from backend.routers import auth_session, debts, medications, modules, monthly_tasks, notes, notifications, rewards, static_files, tasks
from backend.telegram import register_telegram_scheduler
from backend.web_push import register_web_push_scheduler


def _is_https_request(request: Request) -> bool:
    forwarded_proto = (request.headers.get("x-forwarded-proto") or "").split(",")[0].strip().lower()
    if forwarded_proto:
        return forwarded_proto == "https"
    return request.url.scheme == "https"



def create_app() -> FastAPI:
    app = FastAPI()
    install_rate_limiter(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    force_https = str(os.getenv("FORCE_HTTPS", "0")).strip().lower() in {"1", "true", "yes", "on"}
    if force_https:
        @app.middleware("http")
        async def redirect_to_https(request: Request, call_next):
            if not _is_https_request(request):
                secure_url = request.url.replace(scheme="https")
                return RedirectResponse(url=str(secure_url), status_code=307)
            return await call_next(request)

    @app.middleware("http")
    async def bind_request_user(request: Request, call_next):
        token = set_request_user(get_session_user(request))
        try:
            return await call_next(request)
        finally:
            reset_request_user(token)

    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        if _is_https_request(request):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    app.include_router(auth_session.router)
    app.include_router(static_files.router)
    protected = [Depends(verify_credentials)]
    app.include_router(modules.router, dependencies=protected)
    app.include_router(tasks.router, dependencies=protected)
    app.include_router(notes.router, dependencies=protected)
    app.include_router(rewards.router, dependencies=protected)
    app.include_router(monthly_tasks.router, dependencies=protected)
    app.include_router(medications.router, dependencies=protected)
    app.include_router(debts.router, dependencies=protected)
    app.include_router(notifications.router, dependencies=protected)

    init_db()
    register_telegram_scheduler(app)
    register_web_push_scheduler(app)
    return app


app = create_app()
