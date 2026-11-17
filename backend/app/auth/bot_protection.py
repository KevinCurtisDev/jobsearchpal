"""Layered bot and automated sign-up protection (docs/06-security.md §2)."""

from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from pathlib import Path

import httpx

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
_DISPOSABLE_FILE = Path(__file__).resolve().parent.parent / "data" / "disposable_domains.txt"


class RejectReason(StrEnum):
    HONEYPOT = "honeypot"
    TOO_FAST = "too_fast"
    DISPOSABLE_EMAIL = "disposable_email"
    TURNSTILE_FAILED = "turnstile_failed"


@lru_cache
def disposable_domains() -> frozenset[str]:
    """Seed list; Stage 1 adds a weekly refresh from the public disposable-email-domains list."""
    lines = _DISPOSABLE_FILE.read_text(encoding="utf-8").splitlines()
    return frozenset(
        line.strip().lower() for line in lines if line.strip() and not line.startswith("#")
    )


def email_domain(email: str) -> str:
    return email.rsplit("@", 1)[-1].strip().lower()


def is_disposable(email: str) -> bool:
    domain = email_domain(email)
    blocked = disposable_domains()
    parts = domain.split(".")
    # Match the domain and any parent domain (sub.mailinator.com → mailinator.com).
    return any(".".join(parts[i:]) in blocked for i in range(len(parts) - 1))


def honeypot_triggered(value: str | None) -> bool:
    return bool(value and value.strip())


def submitted_too_fast(form_started_at_ms: int | None, now_ms: int, min_seconds: float) -> bool:
    """True if the form was submitted faster than a person could fill it.

    Stage 1 TODO: sign `form_started_at` server-side so it cannot be forged.
    Missing values are treated as too fast.
    """
    if form_started_at_ms is None:
        return True
    elapsed = (now_ms - form_started_at_ms) / 1000
    return elapsed < min_seconds or elapsed > 24 * 3600


@dataclass(frozen=True)
class TurnstileResult:
    success: bool
    error_codes: tuple[str, ...] = ()


async def verify_turnstile(
    client: httpx.AsyncClient,
    *,
    token: str | None,
    secret: str,
    remote_ip: str | None,
    expected_hostname: str | None,
    expected_action: str | None,
) -> TurnstileResult:
    if not token:
        return TurnstileResult(False, ("missing-input-response",))
    data = {"secret": secret, "response": token}
    if remote_ip:
        data["remoteip"] = remote_ip
    try:
        resp = await client.post(TURNSTILE_VERIFY_URL, data=data, timeout=5.0)
        body = resp.json()
    except (httpx.HTTPError, ValueError):
        return TurnstileResult(False, ("verification-unavailable",))  # fail closed
    if not body.get("success"):
        return TurnstileResult(False, tuple(body.get("error-codes", [])))
    if expected_hostname and body.get("hostname") != expected_hostname:
        return TurnstileResult(False, ("hostname-mismatch",))
    if expected_action and body.get("action") != expected_action:
        return TurnstileResult(False, ("action-mismatch",))
    return TurnstileResult(True)
