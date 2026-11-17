"""Consent rules (GDPR Art 4(11), 7; ePrivacy for marketing email).

A consent is valid only if the user's *latest* record for that kind is a grant of the
*current* version of the wording. Changing the wording materially means bumping the
version below, which makes every earlier grant invalid until the user agrees again.
Records are append-only: withdrawing inserts a new row, it never edits an old one.

Every consent defaults to OFF. Nothing is pre-ticked and no feature is blocked for
saying no, except the feature that needs it (for example voice practice needs
`voice_practice`; text practice does not).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.privacy.registry import ConsentKind


class Acknowledgement(StrEnum):
    """Recorded in the same `consents` table but NOT consent: the basis is contract.

    Users accept the terms and are shown the privacy notice; we keep proof of which
    version and when.
    """

    TERMS = "terms"
    PRIVACY_NOTICE = "privacy_notice"
    AGE_16_PLUS = "age_16_plus"


#: Bump a version whenever the wording shown to the user changes in meaning.
#: Wording lives in content/consents/<kind>.v<version>.md and is shown verbatim.
CURRENT_VERSIONS: dict[ConsentKind | Acknowledgement, int] = {
    ConsentKind.BENCHMARKS: 1,
    ConsentKind.EXPERIMENTS: 1,
    ConsentKind.FAIRNESS_AUDIT: 1,
    ConsentKind.MARKETING: 1,
    ConsentKind.VOICE_PRACTICE: 1,
    ConsentKind.QUESTION_BANK: 1,
    Acknowledgement.TERMS: 1,
    Acknowledgement.PRIVACY_NOTICE: 1,
    Acknowledgement.AGE_16_PLUS: 1,
}

#: Kinds whose wording must say "explicit consent" and use a separate, unbundled screen.
EXPLICIT: frozenset[ConsentKind] = frozenset({ConsentKind.FAIRNESS_AUDIT})


@dataclass(frozen=True, slots=True)
class ConsentRecord:
    kind: str
    version: int
    granted: bool
    recorded_at: datetime
    source: str  # "settings", "onboarding", "email_unsubscribe", "admin_on_request"


class ConsentRequiredError(Exception):
    """Raised when a feature that needs consent is used without a valid one."""

    def __init__(self, kind: ConsentKind) -> None:
        super().__init__(f"consent required: {kind}")
        self.kind = kind


def current_state(records: Iterable[ConsentRecord], kind: ConsentKind | Acknowledgement) -> bool:
    """True only if the most recent record for `kind` grants the current version."""
    relevant = [r for r in records if r.kind == kind]
    if not relevant:
        return False
    latest = max(relevant, key=lambda r: r.recorded_at)
    return latest.granted and latest.version == CURRENT_VERSIONS[kind]


def needs_reconsent(records: Iterable[ConsentRecord], kind: ConsentKind | Acknowledgement) -> bool:
    """True if the user granted an older version and has not answered the current one."""
    relevant = [r for r in records if r.kind == kind]
    if not relevant:
        return False
    latest = max(relevant, key=lambda r: r.recorded_at)
    return latest.granted and latest.version < CURRENT_VERSIONS[kind]


def require(records: Iterable[ConsentRecord], kind: ConsentKind) -> None:
    """Guard for services: call before any processing that relies on consent."""
    if not current_state(records, kind):
        raise ConsentRequiredError(kind)


def validate_new_record(record: ConsentRecord) -> None:
    """Reject records that could not be valid consent."""
    if record.kind not in {k.value for k in CURRENT_VERSIONS}:
        raise ValueError(f"unknown consent kind {record.kind!r}")
    if record.granted and record.version != CURRENT_VERSIONS[_kind(record.kind)]:
        raise ValueError("a grant must be for the current version of the wording")
    if record.source not in {"settings", "onboarding", "email_unsubscribe", "admin_on_request"}:
        raise ValueError(f"unknown consent source {record.source!r}")
    if record.granted and record.source == "email_unsubscribe":
        raise ValueError("an unsubscribe link can only withdraw")


def _kind(value: str) -> ConsentKind | Acknowledgement:
    for enum in (ConsentKind, Acknowledgement):
        try:
            return enum(value)
        except ValueError:
            continue
    raise ValueError(value)
