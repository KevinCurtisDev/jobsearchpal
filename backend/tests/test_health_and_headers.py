from httpx import AsyncClient


async def test_health_ok(client: AsyncClient) -> None:
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_ready_reports_checks(client: AsyncClient, app) -> None:  # type: ignore[no-untyped-def]
    async def failing() -> bool:
        return False

    app.state.ready_checks = {"redis": failing}
    r = await client.get("/api/v1/ready")
    assert r.status_code == 503
    assert r.json()["checks"] == {"redis": False}


async def test_security_headers_present(client: AsyncClient) -> None:
    r = await client.get("/api/v1/health")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert "default-src 'none'" in r.headers["content-security-policy"]
    assert r.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert len(r.headers["x-request-id"]) >= 8


async def test_unknown_route_is_problem_json(client: AsyncClient) -> None:
    r = await client.get("/api/v1/nope")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
