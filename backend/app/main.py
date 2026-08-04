from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    return app


app = create_app()
