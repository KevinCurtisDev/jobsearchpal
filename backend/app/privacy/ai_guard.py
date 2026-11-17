"""Data minimisation for calls to the AI provider (GDPR Art 5(1)(c), Art 25).

Every AI call must go through `prepare_cv_for_ai` / `guard_text` — the AI client in
`app/integrations/ai` refuses input that has not been through `guard_text`.

1. Remove the contact block and links from structured CV content.
2. Redact anything that still looks like personal data (email, phone, PPSN, NI number,
   IBAN, postcode, URL, IP).
3. Block the call (raise) if redaction was needed in a field that should never contain it,
   so the bug is found in tests rather than leaking quietly.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from app.privacy.redaction import find_pii, redact

#: Top-level CV keys never sent to the AI provider.
CV_KEYS_NEVER_SENT = frozenset({"contact"})


class PersonalDataInAIInputError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class GuardedText:
    """Text that has passed the guard. The AI client only accepts this type."""

    text: str
    redactions: int


def guard_text(text: str, *, strict: bool = False) -> GuardedText:
    """Redact personal data. With strict=True, refuse instead of redacting."""
    hits = find_pii(text)
    if hits and strict:
        kinds = sorted({k for k, _ in hits})
        raise PersonalDataInAIInputError(f"personal data found in AI input: {kinds}")
    return GuardedText(text=redact(text) if hits else text, redactions=len(hits))


def prepare_cv_for_ai(cv: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of structured CV content safe to send to the AI provider."""
    safe = {k: copy.deepcopy(v) for k, v in cv.items() if k not in CV_KEYS_NEVER_SENT}
    redacted: dict[str, Any] = _redact_tree(safe)
    return redacted


def _redact_tree(value: Any) -> Any:
    if isinstance(value, str):
        return guard_text(value).text
    if isinstance(value, dict):
        return {k: _redact_tree(v) for k, v in value.items() if k != "links"}
    if isinstance(value, list):
        return [_redact_tree(v) for v in value]
    return value
