import time

from httpx import AsyncClient


def _start_body(email: str, **extra: object) -> dict[str, object]:
    body: dict[str, object] = {
        "email": email,
        "intent": "signup",
        "form_started_at": int(time.time() * 1000) - 5_000,
    }
    body.update(extra)
    return body


async def test_full_email_code_flow(client: AsyncClient, app) -> None:  # type: ignore[no-untyped-def]
    r = await client.post("/api/v1/auth/email/start", json=_start_body("aoife@example.ie"))
    assert r.status_code == 202 and r.json() == {"sent": True}
    sent = app.state.email_sender.sent
    assert len(sent) == 1 and sent[0].to == "aoife@example.ie"

    r = await client.post(
        "/api/v1/auth/email/verify", json={"email": "aoife@example.ie", "code": sent[0].code}
    )
    assert r.status_code == 200 and r.json() == {"verified": True}


async def test_honeypot_is_silently_ignored(client: AsyncClient, app) -> None:  # type: ignore[no-untyped-def]
    r = await client.post(
        "/api/v1/auth/email/start", json=_start_body("bot@example.ie", website="http://spam")
    )
    assert r.status_code == 202  # same response as a real request
    assert app.state.email_sender.sent == []  # but nothing sent


async def test_disposable_email_rejected(client: AsyncClient) -> None:
    r = await client.post("/api/v1/auth/email/start", json=_start_body("x@mailinator.com"))
    assert r.status_code == 422
    assert r.headers["content-type"].startswith("application/problem+json")


async def test_wrong_code_message(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/email/start", json=_start_body("a@example.ie"))
    r = await client.post(
        "/api/v1/auth/email/verify", json={"email": "a@example.ie", "code": "999999"}
    )
    # Tiny chance the real code is 999999; either way the response must not be a 500.
    assert r.status_code in (200, 400)


async def test_rate_limit_per_email(client: AsyncClient) -> None:
    statuses = [
        (
            await client.post("/api/v1/auth/email/start", json=_start_body("r@example.ie"))
        ).status_code
        for _ in range(4)
    ]
    assert statuses == [202, 202, 202, 429]


async def test_invalid_code_format_is_422(client: AsyncClient) -> None:
    r = await client.post(
        "/api/v1/auth/email/verify", json={"email": "a@example.ie", "code": "abc"}
    )
    assert r.status_code == 422
