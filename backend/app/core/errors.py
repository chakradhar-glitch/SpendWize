from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, OperationalError
from starlette.exceptions import HTTPException


class ApplicationError(Exception):
    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        *,
        fields: list[dict[str, str]] | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status = status
        self.code = code
        self.message = message
        self.fields = fields or []
        self.details = details or {}


def error_response(
    request: Request,
    status: int,
    code: str,
    message: str,
    fields: list[dict[str, str]] | None = None,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "message": message,
                "fields": fields or [],
                "details": details or {},
            },
            "request_id": request.state.request_id,
        },
    )


def application_error(request: Request, exc: ApplicationError) -> JSONResponse:
    return error_response(
        request, exc.status, exc.code, exc.message, exc.fields, exc.details
    )


def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Never return Pydantic's input or ctx: either may contain tokens/passwords.
    fields = [
        {
            "path": ".".join(str(part) for part in error["loc"]),
            "message": "Invalid value",
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return error_response(
        request, 422, "validation_error", "Request validation failed.", fields
    )


def http_error(request: Request, exc: HTTPException) -> JSONResponse:
    if exc.status_code == 404:
        return error_response(request, 404, "not_found", "Resource not found.")
    return error_response(
        request, exc.status_code, "request_error", "Request rejected."
    )


def database_error(request: Request, exc: DBAPIError) -> JSONResponse:
    # Connection failures and lock availability errors are retryable.
    sqlstate = getattr(exc.orig, "sqlstate", "") or ""
    if (
        (isinstance(exc, OperationalError) and not sqlstate)
        or exc.connection_invalidated
        or sqlstate.startswith("08")
        or sqlstate
        in {
            "55P03",
            "40P01",
            "40001",
            "53300",
            "57P01",
        }
    ):
        return error_response(
            request, 503, "temporarily_unavailable", "Please retry later."
        )
    return error_response(request, 500, "internal_error", "Request failed.")


def pool_timeout(request: Request, exc: Exception) -> JSONResponse:
    return error_response(
        request, 503, "temporarily_unavailable", "Please retry later."
    )
