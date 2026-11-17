from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DBAPIError, TimeoutError
from starlette.exceptions import HTTPException

from app.core.config import Settings
from app.core.database import create_session_factory
from app.core.errors import (
    ApplicationError,
    application_error,
    database_error,
    http_error,
    pool_timeout,
    validation_error,
)
from app.core.observability import RequestContextMiddleware


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings if settings is not None else Settings()
    sessions = create_session_factory(config)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        bind = sessions.kw["bind"]
        bind.dispose()

    app = FastAPI(title="SpendWise API", version="0.1.0", lifespan=lifespan)
    app.state.session_factory = sessions
    app.add_middleware(RequestContextMiddleware)
    app.add_exception_handler(ApplicationError, application_error)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_error)  # type: ignore[arg-type]
    app.add_exception_handler(DBAPIError, database_error)  # type: ignore[arg-type]
    app.add_exception_handler(TimeoutError, pool_timeout)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
