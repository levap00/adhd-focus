from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import verify_credentials
from backend.db import init_db
from backend.routers import debts, modules, monthly_tasks, notes, static_files, tasks



def create_app() -> FastAPI:
    app = FastAPI(dependencies=[Depends(verify_credentials)])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(static_files.router)
    app.include_router(modules.router)
    app.include_router(tasks.router)
    app.include_router(notes.router)
    app.include_router(monthly_tasks.router)
    app.include_router(debts.router)

    init_db()
    return app


app = create_app()
