"""RFC 9457 problem+json errors. Never leak internals."""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

PROBLEM_JSON = "application/problem+json"


class ProblemError(Exception):
    def __init__(
        self,
        status: int,
        title: str,
        detail: str | None = None,
        *,
        type_: str = "about:blank",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self.title = title
        self.detail = detail
        self.type_ = type_
        self.headers = headers or {}


def _problem(
    status: int, title: str, detail: str | None, type_: str, **extra: Any
) -> dict[str, Any]:
    body: dict[str, Any] = {"type": type_, "title": title, "status": status}
    if detail:
        body["detail"] = detail
    body.update(extra)
    return body


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProblemError)
    async def _problem_handler(_: Request, exc: ProblemError) -> JSONResponse:
        return JSONResponse(
            _problem(exc.status, exc.title, exc.detail, exc.type_),
            status_code=exc.status,
            media_type=PROBLEM_JSON,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [
            {"field": ".".join(str(p) for p in err["loc"][1:]), "message": err["msg"]}
            for err in exc.errors()
        ]
        return JSONResponse(
            _problem(422, "Check the highlighted fields", None, "about:blank", errors=errors),
            status_code=422,
            media_type=PROBLEM_JSON,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            _problem(exc.status_code, str(exc.detail), None, "about:blank"),
            status_code=exc.status_code,
            media_type=PROBLEM_JSON,
        )
