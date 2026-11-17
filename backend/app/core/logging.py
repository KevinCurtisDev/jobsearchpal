"""Structured JSON logging. Never log personal data: use user ids, not emails.

As a safety net, every event passes through app.privacy.redaction before it is rendered,
so an email, phone number, PPSN, IP address or CV text that slips into a log is redacted.
"""

import logging
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.privacy.redaction import structlog_processor


def configure_logging(level: str = "INFO", json: bool = True) -> None:
    logging.basicConfig(format="%(message)s", level=level)
    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer() if json else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog_processor,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level)),
    )


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming = request.headers.get("x-request-id", "")
        request_id = (
            incoming if 8 <= len(incoming) <= 64 and incoming.isalnum() else uuid.uuid4().hex
        )
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
