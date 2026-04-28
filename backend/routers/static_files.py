from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STATIC_ROOT = (PROJECT_ROOT / "static").resolve()
INDEX_FILE = PROJECT_ROOT / "index.html"

router = APIRouter()


@router.get("/")
def root() -> FileResponse:
    return FileResponse(INDEX_FILE)


@router.get("/static/{file_path:path}")
def serve_static(file_path: str) -> FileResponse:
    candidate = (STATIC_ROOT / file_path).resolve()
    if STATIC_ROOT not in candidate.parents and candidate != STATIC_ROOT:
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="Plik nie znaleziony")
    return FileResponse(candidate)
