from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse

from backend.auth import get_session_user

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_ROOT = (PROJECT_ROOT / "static").resolve()
INDEX_FILE = PROJECT_ROOT / "index.html"
WIDGET_FILE = STATIC_ROOT / "widget.html"
PROGRESS_WIDGET_FILE = STATIC_ROOT / "progress-widget.html"

router = APIRouter()


@router.get("/")
def root(request: Request):
    if not get_session_user(request):
        return RedirectResponse(url="/login", status_code=303)
    return FileResponse(INDEX_FILE)


@router.get("/widget")
def widget() -> FileResponse:
    if not WIDGET_FILE.is_file():
        raise HTTPException(status_code=404, detail="Widget nie znaleziony")
    return FileResponse(
        WIDGET_FILE,
        media_type="text/html",
        headers={"Cache-Control": "no-cache"},
    )


@router.get("/widget/progress")
def progress_widget() -> FileResponse:
    if not PROGRESS_WIDGET_FILE.is_file():
        raise HTTPException(status_code=404, detail="Widget nie znaleziony")
    return FileResponse(
        PROGRESS_WIDGET_FILE,
        media_type="text/html",
        headers={"Cache-Control": "no-cache"},
    )


@router.get("/static/{file_path:path}")
def serve_static(file_path: str) -> FileResponse:
    candidate = (STATIC_ROOT / file_path).resolve()
    if STATIC_ROOT not in candidate.parents and candidate != STATIC_ROOT:
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")
    return FileResponse(candidate)


@router.get("/sw.js")
def serve_service_worker() -> FileResponse:
    service_worker = (STATIC_ROOT / "sw.js").resolve()
    if not service_worker.is_file():
        raise HTTPException(status_code=404, detail="Service Worker nie znaleziony")
    return FileResponse(
        service_worker,
        media_type="application/javascript",
        headers={
            "Cache-Control": "no-cache",
            "Service-Worker-Allowed": "/",
        },
    )
