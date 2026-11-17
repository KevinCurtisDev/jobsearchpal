"""Stage odds for the application tracker and the How hiring works guide.

Rules (CLAUDE.md rule 5, docs/09 §Stage odds):
- v0 uses published averages (content/hiring_stages.json), labelled "public data", confidence "low".
- v1 (Stage 9) replaces them with Hearback's own rates per role family, shrunk towards the
  public prior (empirical Bayes), once a cohort has enough tracked applications.
- Always odds, never predictions: every result carries its source and confidence.
- Encouragement is framed as progress (how much a stage improved your odds), never as
  pressure, streaks or loss. No fake urgency.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from app.content import content_path

ACTIVE_STAGES = ("applied", "screening", "interview")


@dataclass(frozen=True, slots=True)
class StageOdds:
    stage: str
    p_offer: float
    one_in: int
    multiplier_from_applied: float
    source: Literal["public", "hearback"]
    confidence: Literal["low", "medium", "high"]


@dataclass(frozen=True, slots=True)
class PipelineOdds:
    p_at_least_one_offer: float
    expected_offers: float
    active: int
    biggest_contributor: str | None
    source: Literal["public", "hearback"]
    confidence: Literal["low", "medium", "high"]
    reason: str


@lru_cache(maxsize=1)
def load_benchmarks(path: Path | None = None) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(
        (path or content_path("hiring_stages.json")).read_text(encoding="utf-8")
    )
    return data


def _pass_rates() -> dict[str, float]:
    return {s["key"]: s["pass_rate"] for s in load_benchmarks()["stages"] if "pass_rate" in s}


def p_offer(stage: str, rates: Mapping[str, float] | None = None) -> float:
    """Probability of an offer from `stage`: the product of the remaining pass rates."""
    rates = rates or _pass_rates()
    order = list(ACTIVE_STAGES)
    if stage not in order:
        raise ValueError(f"no odds for stage {stage!r}")
    p = 1.0
    for s in order[order.index(stage) :]:
        p *= rates[s]
    return p


def stage_odds(stage: str) -> StageOdds:
    p = p_offer(stage)
    return StageOdds(
        stage=stage,
        p_offer=p,
        one_in=round(1 / p),
        multiplier_from_applied=round(p / p_offer("applied"), 1),
        source="public",
        confidence="low",
    )


def pipeline_odds(counts: Mapping[str, int]) -> PipelineOdds:
    """Chance at least one active application becomes an offer (independence assumed).

    Independence is a simplification: applications by one person are correlated (same CV,
    same market). That is one reason confidence is never above "medium" for this figure.
    """
    none = 1.0
    expected = 0.0
    contrib: dict[str, float] = {}
    for stage in ACTIVE_STAGES:
        n = counts.get(stage, 0)
        if n < 0:
            raise ValueError("counts cannot be negative")
        p = p_offer(stage)
        none *= (1 - p) ** n
        expected += n * p
        if n:
            contrib[stage] = n * p
    active = sum(counts.get(s, 0) for s in ACTIVE_STAGES)
    biggest = max(contrib, key=lambda k: contrib[k]) if contrib else None
    return PipelineOdds(
        p_at_least_one_offer=1 - none,
        expected_offers=expected,
        active=active,
        biggest_contributor=biggest,
        source="public",
        confidence="low",
        reason="Based on published averages (mostly US), not yet on your own data.",
    )


def encouragement(stage: str) -> str:
    """Progress-framed message for a stage, filled from the same numbers the UI shows."""
    templates: dict[str, str] = load_benchmarks()["encouragement"]
    if stage not in ACTIVE_STAGES:
        return templates.get(stage, "")
    order = list(ACTIVE_STAGES)
    nxt = order[order.index(stage) + 1] if stage != "interview" else None
    values = {
        "multiplier_next": round(p_offer(nxt) / p_offer(stage)) if nxt else "",
        "multiplier_from_applied": round(stage_odds(stage).multiplier_from_applied),
        "one_in_applied": stage_odds("applied").one_in,
        "one_in_here": stage_odds(stage).one_in,
    }
    return templates[stage].format(**values)
