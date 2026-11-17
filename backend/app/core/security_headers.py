"""Security headers for API responses.

Caddy sets the full set (including the SPA's CSP) in production.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

API_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "DENY",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-site",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), usb=(), interest-cohort=()",
    # API responses are JSON: nothing should ever execute or frame them.
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
    "Cache-Control": "no-store",
}

HSTS = "max-age=63072000; includeSubDomains; preload"

# Interactive API docs (development only) load their own assets, so they skip the strict CSP.
_DOCS_PATHS = ("/api/docs", "/api/redoc", "/api/openapi.json")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object, *, hsts: bool) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.hsts = hsts

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        for name, value in API_HEADERS.items():
            if name == "Content-Security-Policy" and request.url.path.startswith(_DOCS_PATHS):
                continue
            response.headers.setdefault(name, value)
        if self.hsts:
            response.headers.setdefault("Strict-Transport-Security", HSTS)
        return response
