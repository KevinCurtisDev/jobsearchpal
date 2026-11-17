import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("ENVIRONMENT", "test")

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(environment="test", min_form_seconds=0.0)


@pytest.fixture
def app(settings: Settings):  # type: ignore[no-untyped-def]
    return create_app(settings)


@pytest.fixture
async def client(app) -> AsyncIterator[AsyncClient]:  # type: ignore[no-untyped-def]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
