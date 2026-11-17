"""Build the minimised input for the linkedin_rewrite prompt (CLAUDE.md rules 4 and 12).

Only headline, About, industry, positions (title, employer, dates, description) and skills
are sent. Location and education institutions are not needed for the rewrite and are left
out. Every string passes app.privacy.ai_guard.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.linkedin.export_parser import LinkedInProfile
from app.privacy.ai_guard import guard_text, prepare_cv_for_ai

MAX_ROLES = 4


def linkedin_for_ai(p: LinkedInProfile) -> dict[str, Any]:
    recent = sorted(p.positions, key=lambda x: (x.end is None, x.end or "", x.start or ""))
    return {
        "headline": guard_text(p.headline).text,
        "about": guard_text(p.about).text,
        "industry": p.industry,
        "positions": [
            {k: (guard_text(v).text if isinstance(v, str) else v) for k, v in asdict(x).items()}
            for x in recent[-MAX_ROLES:]
        ],
        "skills": p.skills[:50],
    }


def rewrite_input(p: LinkedInProfile, cv: dict[str, Any]) -> dict[str, Any]:
    return {"linkedin_profile": linkedin_for_ai(p), "cv": prepare_cv_for_ai(cv)}
