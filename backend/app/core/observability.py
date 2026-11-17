import logging
from time import perf_counter
from uuid import UUID, uuid4

from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.errors import error_response

logger = logging.getLogger("spendwise.requests")


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope)
        try:
            request_id = str(UUID(request.headers.get("x-request-id", "")))
        except ValueError:
            request_id = str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id
        started = perf_counter()
        status = 500
        response_started = False

        async def send_with_id(message: Message) -> None:
            nonlocal status, response_started
            if message["type"] == "http.response.start":
                status = message["status"]
                response_started = True
                message.setdefault("headers", []).append(
                    (b"x-request-id", request_id.encode("ascii"))
                )
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        except Exception:
            if response_started:
                raise
            response = error_response(request, 500, "internal_error", "Request failed.")
            await response(scope, receive, send_with_id)
        finally:
            # Deliberate allowlist: no URL, query, headers, body or exception text.
            logger.info(
                "request_id=%s status=%s duration_ms=%.2f",
                request_id,
                status,
                (perf_counter() - started) * 1000,
            )
