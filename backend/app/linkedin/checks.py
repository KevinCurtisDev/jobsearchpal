"""LinkedIn profile checks — rules and data only, no AI (CLAUDE.md rule 1).

1. Profile checklist from content/linkedin_rules.json (limits, missing sections, clichés).
2. CV ↔ LinkedIn consistency: titles, employers and dates that disagree. Recruiters
   compare the two; a mismatch looks careless or worse.
3. Keyword gap: skills common in recent ads for the user's target role (our own job-ad
   data, ESCO-normalised) that the profile does not mention. Shown only with enough ads.

Every finding carries a reason and, where relevant, its evidence and confidence
(CLAUDE.md rule 5). We never claim a check raises profile views: LinkedIn's ranking is
not public.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from app.content import content_path
from app.linkedin.export_parser import LinkedInProfile, Position

Severity = Literal["high", "medium", "low"]


@dataclass(frozen=True, slots=True)
class Finding:
    id: str
    severity: Severity
    message: str
    field: str
    evidence: str = ""


@lru_cache(maxsize=1)
def load_rules(path: Path | None = None) -> dict[str, Any]:
    path = path or content_path("linkedin_rules.json")
    rules: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return rules


@lru_cache(maxsize=1)
def banned_phrases() -> tuple[str, ...]:
    rules = load_rules()
    phrases = [p["phrase"] for p in rules["linkedin_banned_phrases"]]
    general_path = content_path("banned_phrases.json")
    if general_path.is_file():
        general = json.loads(general_path.read_text(encoding="utf-8"))
        phrases += [p["phrase"] for p in general.get("avoid", [])]
    return tuple(sorted({p.lower() for p in phrases}))


# ---------------------------------------------------------------------------------------------
# 1. Profile checklist
# ---------------------------------------------------------------------------------------------

_THIRD_PERSON = re.compile(r"\b(he|she|they) (is|has|was|leads|works|helps)\b", re.IGNORECASE)
_FIRST_PERSON = re.compile(r"\b(i|i'm|i've|my)\b", re.IGNORECASE)


def _current(p: LinkedInProfile) -> Position | None:
    current = [x for x in p.positions if x.end is None]
    return max(current, key=lambda x: x.start or "", default=None)


def _recent(p: LinkedInProfile, n: int) -> list[Position]:
    return sorted(p.positions, key=lambda x: (x.end is None, x.end or "", x.start or ""))[-n:]


def profile_checks(p: LinkedInProfile) -> list[Finding]:
    rules = load_rules()
    out: list[Finding] = []
    for c in rules["checks"]:
        fld, rule, value = c["field"], c["rule"], c.get("value")
        text = getattr(p, fld, "") if fld in ("headline", "about") else ""
        hit, evidence = False, ""
        if rule == "missing":
            hit = not text.strip()
        elif rule == "min_chars":
            hit = 0 < len(text.strip()) < value
            evidence = f"{len(text.strip())} characters"
        elif rule == "max_chars":
            hit = len(text) > value
            evidence = f"{len(text)} of {value} characters"
        elif rule == "first_line_max_chars":
            first = text.strip().split("\n", 1)[0]
            hit = len(first) > value
            evidence = f"first line is {len(first)} characters"
        elif rule == "third_person":
            hit = bool(_THIRD_PERSON.search(text)) and not _FIRST_PERSON.search(text)
        elif rule == "equals_current_title":
            cur = _current(p)
            hit = bool(cur and text.strip()) and _same(text, cur.title if cur else "")
        elif rule == "recent_without_description":
            empty = [x for x in _recent(p, value) if not x.description.strip()]
            hit = len(p.positions) >= value and len(empty) == value
            evidence = "; ".join(f"{x.title} at {x.company}" for x in empty)
        elif rule == "description_max_chars":
            long = [x for x in p.positions if len(x.description) > value]
            hit, evidence = bool(long), "; ".join(f"{x.title} at {x.company}" for x in long)
        elif rule == "min_count":
            hit, evidence = len(p.skills) < value, f"{len(p.skills)} skills"
        elif rule == "banned_phrases":
            found = find_banned(
                " ".join([p.headline, p.about, *(x.description for x in p.positions)])
            )
            hit, evidence = bool(found), ", ".join(found)
        else:
            raise ValueError(f"unknown rule {rule!r} in linkedin_rules.json")
        if hit:
            out.append(Finding(c["id"], c["severity"], c["message"], fld, evidence))
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(out, key=lambda f: order[f.severity])


def find_banned(text: str) -> list[str]:
    lowered = text.lower()
    return [b for b in banned_phrases() if re.search(rf"(?<!\w){re.escape(b)}(?!\w)", lowered)]


# ---------------------------------------------------------------------------------------------
# 2. CV ↔ LinkedIn consistency
# ---------------------------------------------------------------------------------------------

_COMPANY_SUFFIX = re.compile(r"\b(ltd|limited|plc|dac|inc|llc|gmbh|teoranta|uc|clg)\.?$")


def _norm(s: str) -> str:
    s = re.sub(r"[^\w\s]", " ", s.lower())
    s = _COMPANY_SUFFIX.sub("", " ".join(s.split()))
    return s.strip()


def _same(a: str, b: str, threshold: float = 0.85) -> bool:
    na, nb = _norm(a), _norm(b)
    return bool(na and nb) and (na == nb or SequenceMatcher(None, na, nb).ratio() >= threshold)


def _year(d: str | None) -> str | None:
    return d[:4] if d else None


def consistency_checks(p: LinkedInProfile, cv: Mapping[str, Any]) -> list[Finding]:
    """Compare LinkedIn positions with CV roles (cv.schema.json `roles`)."""
    out: list[Finding] = []
    roles: list[Mapping[str, Any]] = list(cv.get("roles", []))
    unmatched_li = list(p.positions)
    for role in roles:
        employer, title = str(role.get("employer", "")), str(role.get("title", ""))
        match = next((x for x in unmatched_li if _same(x.company, employer)), None)
        if match is None:
            out.append(Finding(
                "cv_role_missing_on_linkedin", "medium",
                "This role is on your CV but not on LinkedIn.", "positions",
                f"{title} at {employer}",
            ))  # fmt: skip
            continue
        unmatched_li.remove(match)
        if not _same(match.title, title, 0.75):
            out.append(Finding(
                "title_mismatch", "medium",
                "Your job title differs between your CV and LinkedIn. Use the same title, "
                "or make sure the difference is easy to explain.", "positions",
                f"CV: {title} · LinkedIn: {match.title} ({employer})",
            ))  # fmt: skip
        cv_start, cv_end = _year(_s(role.get("start"))), _year(_end(role.get("end")))
        li_start, li_end = _year(match.start), _year(match.end)
        if (cv_start and li_start and cv_start != li_start) or (cv_end != li_end):
            out.append(Finding(
                "dates_mismatch", "high",
                "Dates differ between your CV and LinkedIn. Recruiters check these.", "positions",
                f"{employer}: CV {cv_start or '?'} to {cv_end or 'present'} · "
                f"LinkedIn {li_start or '?'} to {li_end or 'present'}",
            ))  # fmt: skip
    for x in unmatched_li:
        out.append(Finding(
            "linkedin_role_missing_on_cv", "low",
            "This role is on LinkedIn but not your CV. That's fine for older or unrelated roles; "
            "check it's deliberate.", "positions", f"{x.title} at {x.company}",
        ))  # fmt: skip
    return out


def _s(v: Any) -> str | None:
    return str(v) if v else None


def _end(v: Any) -> str | None:
    return None if not v or str(v).lower() == "present" else str(v)


# ---------------------------------------------------------------------------------------------
# 3. Keyword gap against real job ads
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class KeywordGap:
    skill: str
    share_of_ads: float
    n_ads: int
    in_cv: bool  # True: on your CV but not LinkedIn (easy, honest win)


@dataclass(frozen=True, slots=True)
class KeywordGapResult:
    gaps: list[KeywordGap]
    n_ads: int
    confidence: Literal["none", "low", "medium", "high"]
    reason: str


def keyword_gap(
    profile_skills: Iterable[str],
    profile_text: str,
    cv_skills: Iterable[str],
    ad_skill_counts: Mapping[str, int],
    n_ads: int,
) -> KeywordGapResult:
    """Skills frequent in recent ads for the target role that the profile never mentions.

    `ad_skill_counts` maps an ESCO preferred label to the number of ads (out of `n_ads`)
    that require it — computed nightly from job_postings, never per request.
    Skills on the CV are listed first: adding them is honest and needs no new evidence.
    Skills not on the CV are shown as "if you have this" — we never suggest claiming them.
    """
    cfg = load_rules()["keyword_gap"]
    if n_ads < cfg["min_ads_for_gap"]:
        return KeywordGapResult(
            [], n_ads, "none", f"Only {n_ads} recent ads for this role — not enough to compare."
        )
    have = {s.lower() for s in profile_skills}
    text = profile_text.lower()
    cv = {s.lower() for s in cv_skills}
    gaps = [
        KeywordGap(skill, count / n_ads, n_ads, skill.lower() in cv)
        for skill, count in ad_skill_counts.items()
        if count / n_ads >= cfg["min_share_to_suggest"]
        and skill.lower() not in have
        and not re.search(rf"(?<!\w){re.escape(skill.lower())}(?!\w)", text)
    ]
    gaps.sort(key=lambda g: (not g.in_cv, -g.share_of_ads, g.skill))
    confidence: Literal["low", "medium", "high"] = (
        "high" if n_ads >= 300 else "medium" if n_ads >= 100 else "low"
    )
    return KeywordGapResult(
        gaps[: cfg["max_gaps_shown"]],
        n_ads,
        confidence,
        f"Based on {n_ads} ads for this role in the last 90 days.",
    )
