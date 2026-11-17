"""Locate files in the repository's content/ folder (wording and rules, edited without code).

Order: CONTENT_DIR environment variable → ../content next to the backend (local and CI)
→ /content (mounted read-only in Docker; baked into production images — Stage 0 task).
"""

import os
from pathlib import Path

_REPO_CONTENT = Path(__file__).resolve().parents[3] / "content"


def content_dir() -> Path:
    env = os.environ.get("CONTENT_DIR")
    if env:
        return Path(env)
    return _REPO_CONTENT if _REPO_CONTENT.is_dir() else Path("/content")


def content_path(name: str) -> Path:
    return content_dir() / name
