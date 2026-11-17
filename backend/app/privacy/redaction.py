"""Detect and redact personal data in free text.

Used in three places, so that one set of rules applies everywhere:
1. Logs and error reports (structlog processor and Sentry `before_send`).
2. Text sent to the AI provider (see ai_guard.py).
3. Free text that becomes shared data (for example the anonymised question bank).

Patterns are deliberately broad: a false positive costs a "[email]" placeholder, a false
negative leaks personal data.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, MutableMapping
from typing import Any

_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "url": re.compile(r"\b(?:https?://|www\.)[^\s<>\"']+", re.IGNORECASE),
    "iban": re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){3,7}(?:\s?[A-Z0-9]{1,3})?\b"),
    # Irish PPS number: 7 digits + 1-2 letters
    "ppsn": re.compile(r"\b\d{7}[A-W][A-IW]?\b", re.IGNORECASE),
    # UK National Insurance number
    "ni_number": re.compile(
        r"\b(?!BG|GB|NK|KN|TN|NT|ZZ)[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-D]\b",
        re.IGNORECASE,
    ),
    "card": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "ipv4": re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"),
    "ipv6": re.compile(r"\b(?:[0-9a-f]{1,4}:){2,7}[0-9a-f]{1,4}\b", re.IGNORECASE),
    # Phone numbers: +353 / +44 / 0-prefixed, 9-13 digits with common separators
    "phone": re.compile(r"(?<![\w])(?:\+|00)?\d[\d\s().-]{7,16}\d(?![\w])"),
    # Irish Eircode (routing key + unique identifier)
    "eircode": re.compile(
        r"\b(?:[AC-FHKNPRTV-Y]\d{2}|D6W)\s?[0-9AC-FHKNPRTV-Y]{4}\b", re.IGNORECASE
    ),
    # UK postcode
    "uk_postcode": re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b", re.IGNORECASE),
}

#: Order matters: specific patterns before the broad phone/card patterns.
_ORDER = [
    "email",
    "url",
    "iban",
    "ppsn",
    "ni_number",
    "ipv4",
    "ipv6",
    "card",
    "eircode",
    "uk_postcode",
    "phone",
]

#: Log/event keys whose values are always dropped, whatever they contain.
SENSITIVE_KEYS = frozenset(
    {
        "email", "to", "from", "from_address", "phone", "name", "display_name", "full_name",
        "address", "ip", "ip_address", "user_agent", "token", "code", "otp", "password",
        "authorization", "cookie", "set-cookie", "body", "body_text", "cv", "content",
        "transcript", "answer", "description", "subject", "text", "raw", "payload",
    }
)  # fmt: skip


def find_pii(text: str) -> list[tuple[str, str]]:
    """Return (kind, match) pairs found in `text`."""
    found: list[tuple[str, str]] = []
    remaining = text
    for kind in _ORDER:
        for m in _PATTERNS[kind].finditer(remaining):
            if kind in ("phone", "card") and sum(ch.isdigit() for ch in m.group()) < 9:
                continue
            found.append((kind, m.group()))
        remaining = _PATTERNS[kind].sub(" ", remaining)
    return found


def redact(text: str) -> str:
    """Replace personal data with typed placeholders such as "[email]"."""
    out = text
    for kind in _ORDER:

        def _sub(m: re.Match[str], kind: str = kind) -> str:
            if kind in ("phone", "card") and sum(ch.isdigit() for ch in m.group()) < 9:
                return m.group()
            return f"[{kind}]"

        out = _PATTERNS[kind].sub(_sub, out)
    return out


def scrub(value: Any, depth: int = 0) -> Any:
    """Recursively scrub a log event or error payload."""
    if depth > 6:
        return "[truncated]"
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, Mapping):
        return {
            k: ("[removed]" if str(k).lower() in SENSITIVE_KEYS else scrub(v, depth + 1))
            for k, v in value.items()
        }
    if isinstance(value, list | tuple):
        return [scrub(v, depth + 1) for v in value]
    return value


def structlog_processor(
    _: Any, __: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """structlog processor: runs last before rendering. Keeps request_id/user_id/path."""
    keep = {
        "request_id",
        "user_id",
        "path",
        "level",
        "timestamp",
        "status",
        "method",
        "duration_ms",
    }
    for key in list(event_dict):
        if key in keep:
            continue
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = "[removed]"
        else:
            event_dict[key] = scrub(event_dict[key])
    return event_dict


def sentry_before_send(event: dict[str, Any], _hint: dict[str, Any]) -> dict[str, Any]:
    """Sentry hook. Also set send_default_pii=False when initialising Sentry."""
    event.pop("user", None)
    request = event.get("request")
    if isinstance(request, dict):
        for key in ("cookies", "data", "headers", "query_string", "env"):
            request.pop(key, None)
    scrubbed: dict[str, Any] = scrub(event)
    return scrubbed
