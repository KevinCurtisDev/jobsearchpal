"""Waiting-on-data states for features that need Hearback's own data.

The product launches complete (docs/02-build-stages.md §Launch strategy). A feature whose
data is not ready yet still appears, says exactly what it is waiting for, and shows
progress. It never shows an invented number. Thresholds match docs/09 §Data maturity gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

State = Literal["live", "public_data", "collecting"]


@dataclass(frozen=True, slots=True)
class Gate:
    feature: str
    threshold: int
    unit: str  # what is being counted, in plain words
    scope: Literal["user", "company", "cohort"]
    fallback: Literal["public_data", "hidden_value"]
    waiting_text: str  # {have}, {need}, {unit}


GATES: dict[str, Gate] = {
    "company_reply_badge": Gate(
        "company_reply_badge", 15, "tracked applications", "company", "hidden_value",
        "Collecting replies for this company: {have} of {need} {unit}.",
    ),
    "where_you_stand": Gate(
        "where_you_stand", 200, "people in your comparison group", "cohort", "public_data",
        "Showing published averages until {need} {unit} are on Hearback ({have} so far).",
    ),
    "what_works_personal": Gate(
        "what_works_personal", 20, "tracked outcomes", "user", "hidden_value",
        "Unlocks after {need} {unit}: you have {have}.",
    ),
    "stage_odds": Gate(
        "stage_odds", 200, "tracked applications at this stage", "cohort", "public_data",
        "Using published averages until Hearback has {need} {unit} for your kind of role.",
    ),
}  # fmt: skip


@dataclass(frozen=True, slots=True)
class Readiness:
    feature: str
    state: State
    have: int
    need: int
    progress: float  # 0..1, for a progress bar
    message: str  # empty when live


def readiness(feature: str, have: int) -> Readiness:
    if feature not in GATES:
        raise KeyError(f"no data gate for {feature!r}")
    if have < 0:
        raise ValueError("have cannot be negative")
    g = GATES[feature]
    if have >= g.threshold:
        return Readiness(feature, "live", have, g.threshold, 1.0, "")
    state: State = "public_data" if g.fallback == "public_data" else "collecting"
    return Readiness(
        feature,
        state,
        have,
        g.threshold,
        have / g.threshold,
        g.waiting_text.format(have=have, need=g.threshold, unit=g.unit),
    )
