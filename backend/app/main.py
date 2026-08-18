from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.errors import install_error_handlers
from app.core.logging import configure_logging
from app.database.session import create_database_engine
from app.services.jobs import recover_interrupted_jobs


def create_app(settings: Settings | None = None) -> FastAPI:
    application_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        Path(application_settings.storage_root).mkdir(parents=True, exist_ok=True)
        engine = create_database_engine(application_settings.database_url)
        if all(
            inspect(engine).has_table(table)
            for table in ("extraction_jobs", "export_jobs", "maintenance_jobs")
        ):
            with Session(engine) as session:
                recover_interrupted_jobs(session)
        engine.dispose()
        yield

    configure_logging()
    app = FastAPI(title=application_settings.app_name, lifespan=lifespan)
    app.state.settings = application_settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=application_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(app)
    app.include_router(api_router, prefix="/api/v1")

    static_root = Path(__file__).resolve().parent / "static"
    index_file = static_root / "index.html"
    if index_file.is_file():

        @app.get("/", include_in_schema=False)
        async def frontend_index() -> FileResponse:
            return FileResponse(index_file)

        @app.get("/{frontend_path:path}", include_in_schema=False)
        async def frontend_route(frontend_path: str) -> FileResponse:
            candidate = (static_root / frontend_path).resolve()
            if candidate.is_relative_to(static_root) and candidate.is_file():
                return FileResponse(candidate)
            if frontend_path.startswith(("api/", "assets/")):
                raise HTTPException(status_code=404, detail="Not found")
            return FileResponse(index_file)

    return app


app = create_app()
