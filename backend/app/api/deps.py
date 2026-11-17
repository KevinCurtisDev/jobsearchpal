"""Shared FastAPI dependencies. Implementations live on app.state (set in main.lifespan);
tests replace them via app.dependency_overrides or by setting app.state directly."""

from typing import Annotated

import httpx
from fastapi import Depends, Request

from app.auth.email_codes import EmailCodeStore
from app.auth.email_sender import EmailSender
from app.core.config import Settings, get_settings
from app.core.rate_limit import RateLimiter


def settings_dep() -> Settings:
    return get_settings()


def rate_limiter_dep(request: Request) -> RateLimiter:
    limiter: RateLimiter = request.app.state.rate_limiter
    return limiter


def code_store_dep(request: Request) -> EmailCodeStore:
    store: EmailCodeStore = request.app.state.code_store
    return store


def email_sender_dep(request: Request) -> EmailSender:
    sender: EmailSender = request.app.state.email_sender
    return sender


def http_client_dep(request: Request) -> httpx.AsyncClient:
    client: httpx.AsyncClient = request.app.state.http_client
    return client


def client_ip(request: Request) -> str:
    """Caddy sets X-Forwarded-For; trust it only behind the proxy (configure in Stage 1)."""
    return request.client.host if request.client else "unknown"


SettingsDep = Annotated[Settings, Depends(settings_dep)]
RateLimiterDep = Annotated[RateLimiter, Depends(rate_limiter_dep)]
CodeStoreDep = Annotated[EmailCodeStore, Depends(code_store_dep)]
EmailSenderDep = Annotated[EmailSender, Depends(email_sender_dep)]
HttpClientDep = Annotated[httpx.AsyncClient, Depends(http_client_dep)]
