import httpx
import respx

from app.auth import bot_protection as bots


def test_disposable_domains_and_subdomains() -> None:
    assert bots.is_disposable("x@mailinator.com")
    assert bots.is_disposable("x@sub.mailinator.com")
    assert not bots.is_disposable("aoife@gmail.com")
    assert not bots.is_disposable("aoife@company.ie")


def test_honeypot() -> None:
    assert bots.honeypot_triggered("https://spam.example")
    assert not bots.honeypot_triggered("")
    assert not bots.honeypot_triggered(None)


def test_form_timing() -> None:
    now = 1_000_000
    assert bots.submitted_too_fast(now - 500, now, 2.0)
    assert not bots.submitted_too_fast(now - 5_000, now, 2.0)
    assert bots.submitted_too_fast(None, now, 2.0)


@respx.mock
async def test_turnstile_success_checks_hostname_and_action() -> None:
    respx.post(bots.TURNSTILE_VERIFY_URL).mock(
        return_value=httpx.Response(
            200, json={"success": True, "hostname": "app.example", "action": "signup"}
        )
    )
    async with httpx.AsyncClient() as client:
        ok = await bots.verify_turnstile(
            client,
            token="t",
            secret="s",
            remote_ip=None,
            expected_hostname="app.example",
            expected_action="signup",
        )
        wrong_action = await bots.verify_turnstile(
            client,
            token="t",
            secret="s",
            remote_ip=None,
            expected_hostname="app.example",
            expected_action="signin",
        )
    assert ok.success
    assert not wrong_action.success and wrong_action.error_codes == ("action-mismatch",)


@respx.mock
async def test_turnstile_fails_closed_when_unreachable() -> None:
    respx.post(bots.TURNSTILE_VERIFY_URL).mock(side_effect=httpx.ConnectError("down"))
    async with httpx.AsyncClient() as client:
        result = await bots.verify_turnstile(
            client,
            token="t",
            secret="s",
            remote_ip=None,
            expected_hostname=None,
            expected_action=None,
        )
    assert not result.success


async def test_turnstile_missing_token() -> None:
    async with httpx.AsyncClient() as client:
        result = await bots.verify_turnstile(
            client,
            token=None,
            secret="s",
            remote_ip=None,
            expected_hostname=None,
            expected_action=None,
        )
    assert not result.success
