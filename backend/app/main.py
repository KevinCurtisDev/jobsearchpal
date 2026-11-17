"""Application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from app.api.routes import auth, health
from app.auth.email_codes import MemoryEmailCodeStore, RedisEmailCodeStore
from app.auth.email_sender import MemoryEmailSender, SmtpEmailSender
from app.core.config import Settings, get_settings
from app.core.errors import register_error_handlers
from app.core.logging import RequestIdMiddleware, configure_logging
from app.core.observability import init_sentry
from app.core.rate_limit import MemoryRateLimiter, RedisRateLimiter
from app.core.security_headers import SecurityHeadersMiddleware

API_PREFIX = "/api/v1"


def _wire_state(app: FastAPI, settings: Settings) -> None:
    """Attach infrastructure clients. Tests call create_app(Settings(environment='test'))."""
    app.state.http_client = httpx.AsyncClient(timeout=10.0)
    if settings.environment == "test":
        app.state.redis = None
        app.state.rate_limiter = MemoryRateLimiter()
        app.state.code_store = MemoryEmailCodeStore()
        app.state.email_sender = MemoryEmailSender()
        app.state.ready_checks = {}
        return
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis = redis
    app.state.rate_limiter = (
        RedisRateLimiter(redis) if settings.rate_limit_backend == "redis" else MemoryRateLimiter()
    )
    app.state.code_store = RedisEmailCodeStore(redis)
    app.state.email_sender = SmtpEmailSender(
        settings.smtp_host,
        settings.smtp_port,
        settings.email_from,
        settings.app_name,
        settings.public_app_url,
    )

    async def redis_ok() -> bool:
        return bool(await redis.ping())

    app.state.ready_checks = {"redis": redis_ok}  # Stage 0: add the database check


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, json=settings.environment != "development")
    init_sentry(settings, component="api")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        await app.state.http_client.aclose()
        if app.state.redis is not None:
            await app.state.redis.aclose()

    app = FastAPI(
        title=f"{settings.app_name} API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.docs_enabled else None,
        redoc_url=None,
        openapi_url="/api/openapi.json" if settings.docs_enabled else None,
    )
    _wire_state(app, settings)

    app.add_middleware(
        SecurityHeadersMiddleware, hsts=settings.environment in ("staging", "production")
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "X-CSRF-Token", "X-Request-ID", "Idempotency-Key"],
    )
    app.add_middleware(RequestIdMiddleware)
    register_error_handlers(app)

    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(auth.router, prefix=API_PREFIX)
    return app


app = create_app()
