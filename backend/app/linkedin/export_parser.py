"""Read a LinkedIn data export ("Get a copy of your data") uploaded by the user.

Privacy by design (docs/13, inventory category `linkedin_profile`):
- The ZIP is processed in memory during the request and never written to disk or storage.
- Only profile files are opened (ALLOWED_FILES). Connections, messages, invitations, search
  history and everything else are never read.
- Only the fields we use are kept. Birth date, address, postcode, phone, messaging handles
  and email are dropped at parse time.

No scraping and no LinkedIn login: the user downloads their own data from LinkedIn and
gives it to us. Column names vary between export versions, so matching is case-insensitive
and tolerant of known aliases.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from dataclasses import dataclass, field

MAX_ZIP_BYTES = 20 * 1024 * 1024
MAX_MEMBER_BYTES = 2 * 1024 * 1024
MAX_MEMBERS = 500

#: Files we read. Matched on the base name, case-insensitive.
ALLOWED_FILES = frozenset({"profile.csv", "positions.csv", "skills.csv", "education.csv"})

_ALIASES: dict[str, tuple[str, ...]] = {
    "headline": ("headline",),
    "about": ("summary", "about"),
    "industry": ("industry",),
    "location": ("geo location", "location"),
    "company": ("company name", "company"),
    "title": ("title", "position"),
    "description": ("description",),
    "started": ("started on", "start date", "started"),
    "finished": ("finished on", "end date", "finished"),
    "skill": ("name", "skill"),
    "school": ("school name", "school"),
    "degree": ("degree name", "degree"),
}

_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1
)}  # fmt: skip


class ExportError(ValueError):
    """The upload is not a usable LinkedIn export. Message is safe to show the user."""


@dataclass(frozen=True, slots=True)
class Position:
    company: str
    title: str
    description: str
    start: str | None  # "YYYY-MM" or "YYYY"
    end: str | None  # None = current


@dataclass(frozen=True, slots=True)
class Education:
    school: str
    degree: str
    end: str | None


@dataclass(slots=True)
class LinkedInProfile:
    headline: str = ""
    about: str = ""
    industry: str = ""
    location: str = ""
    positions: list[Position] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    source: str = "export"  # export | pasted | pdf


def normalise_date(value: str) -> str | None:
    """'Jan 2020' → '2020-01'; '2020' → '2020'; '03/2021' → '2021-03'; '' → None."""
    v = value.strip().lower()
    if not v or v in ("present", "current"):
        return None
    if m := re.fullmatch(r"([a-z]{3})[a-z]*\.? (\d{4})", v):
        month = _MONTHS.get(m.group(1))
        return f"{m.group(2)}-{month:02d}" if month else m.group(2)
    if m := re.fullmatch(r"(\d{4})-(\d{1,2})(?:-\d{1,2})?", v):
        return f"{m.group(1)}-{int(m.group(2)):02d}"
    if m := re.fullmatch(r"(\d{1,2})/(\d{4})", v):
        return f"{m.group(2)}-{int(m.group(1)):02d}"
    if m := re.fullmatch(r"(\d{4})", v):
        return m.group(1)
    return None


def _get(row: dict[str, str], key: str) -> str:
    lowered = {k.strip().lower(): (v or "") for k, v in row.items() if k}
    for alias in _ALIASES[key]:
        if alias in lowered:
            return lowered[alias].strip()
    return ""


def _rows(data: bytes) -> list[dict[str, str]]:
    text = data.decode("utf-8-sig", errors="replace")
    # Some exports start with a "Notes:" preamble, then a blank line, then the header row.
    lines = text.splitlines()
    if lines and lines[0].lower().startswith("notes"):
        blank = next((i for i, ln in enumerate(lines) if not ln.strip()), len(lines))
        lines = [ln for ln in lines[blank:] if ln.strip()]
    return list(csv.DictReader(io.StringIO("\n".join(lines))))


def parse_export(data: bytes) -> LinkedInProfile:
    if len(data) > MAX_ZIP_BYTES:
        raise ExportError("That file is too large. LinkedIn exports are usually under 5 MB.")
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise ExportError("That isn't a ZIP file. Upload the file LinkedIn emailed you.") from exc

    with archive:
        members = archive.infolist()
        if len(members) > MAX_MEMBERS:
            raise ExportError("That ZIP has too many files to be a LinkedIn export.")
        wanted: dict[str, bytes] = {}
        for info in members:
            base = info.filename.replace("\\", "/").rsplit("/", 1)[-1].lower()
            if base not in ALLOWED_FILES or info.is_dir():
                continue  # never opened
            if info.file_size > MAX_MEMBER_BYTES:
                raise ExportError("A file in that ZIP is unexpectedly large.")
            with archive.open(info) as fh:
                content = fh.read(MAX_MEMBER_BYTES + 1)
            if len(content) > MAX_MEMBER_BYTES:  # guards against lying headers (zip bombs)
                raise ExportError("A file in that ZIP is unexpectedly large.")
            wanted[base] = content

    if "profile.csv" not in wanted and "positions.csv" not in wanted:
        raise ExportError(
            "We couldn't find your profile in that ZIP. In LinkedIn, request the archive "
            "that includes Profile and Positions."
        )
    return _build(wanted)


def _build(files: dict[str, bytes]) -> LinkedInProfile:
    p = LinkedInProfile()
    if "profile.csv" in files and (rows := _rows(files["profile.csv"])):
        r = rows[0]
        p.headline, p.about = _get(r, "headline"), _get(r, "about")
        p.industry, p.location = _get(r, "industry"), _get(r, "location")
    for r in _rows(files.get("positions.csv", b"")):
        p.positions.append(
            Position(
                company=_get(r, "company"),
                title=_get(r, "title"),
                description=_get(r, "description"),
                start=normalise_date(_get(r, "started")),
                end=normalise_date(_get(r, "finished")),
            )
        )
    p.skills = [s for r in _rows(files.get("skills.csv", b"")) if (s := _get(r, "skill"))]
    for r in _rows(files.get("education.csv", b"")):
        p.education.append(
            Education(
                school=_get(r, "school"),
                degree=_get(r, "degree"),
                end=normalise_date(_get(r, "finished")),
            )
        )
    return p
