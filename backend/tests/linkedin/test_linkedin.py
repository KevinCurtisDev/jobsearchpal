import io
import json
import zipfile

import pytest

from app.linkedin.ai_input import rewrite_input
from app.linkedin.checks import consistency_checks, find_banned, keyword_gap, profile_checks
from app.linkedin.export_parser import (
    ExportError,
    LinkedInProfile,
    Position,
    normalise_date,
    parse_export,
)

PROFILE_CSV = (
    "First Name,Last Name,Maiden Name,Address,Birth Date,Headline,Summary,Industry,"
    "Zip Code,Geo Location,Twitter Handles,Websites,Instant Messengers\n"
    'Aoife,Byrne,,"1 Main St, Dublin",Mar 3 1994,Data Analyst,"She is a data analyst.",'
    "Analytics,D02 X285,Dublin,,,\n"
)
POSITIONS_CSV = (
    "Company Name,Title,Description,Location,Started On,Finished On\n"
    "Brightwater Analytics Ltd,Senior Data Analyst,,Dublin,Mar 2022,\n"
    "Kerry Foods,Data Analyst,,Tralee,Sep 2019,Feb 2022\n"
)
SKILLS_CSV = "Name\nSQL\nPython\n"


def make_zip(extra: dict[str, str] | None = None) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Profile.csv", PROFILE_CSV)
        z.writestr("Positions.csv", POSITIONS_CSV)
        z.writestr("Skills.csv", SKILLS_CSV)
        for name, content in (extra or {}).items():
            z.writestr(name, content)
    return buf.getvalue()


# ---- parser ----------------------------------------------------------------------------------


def test_parses_profile_and_drops_unneeded_personal_data() -> None:
    p = parse_export(make_zip())
    assert p.headline == "Data Analyst"
    assert [x.company for x in p.positions] == ["Brightwater Analytics Ltd", "Kerry Foods"]
    assert p.positions[0].start == "2022-03" and p.positions[0].end is None
    assert p.skills == ["SQL", "Python"]
    dumped = json.dumps(p, default=lambda o: getattr(o, "__dict__", None) or str(o))
    for dropped in ("1994", "Main St", "D02 X285", "Byrne"):
        assert dropped not in dumped


def test_never_opens_messages_or_connections(monkeypatch: pytest.MonkeyPatch) -> None:
    data = make_zip({"messages.csv": "secret", "Connections.csv": "x", "x/Profile.txt": "y"})
    opened: list[str] = []
    real_open = zipfile.ZipFile.open

    def spy(self: zipfile.ZipFile, name: object, *a: object, **k: object):  # type: ignore[no-untyped-def]
        opened.append(getattr(name, "filename", str(name)))
        return real_open(self, name, *a, **k)  # type: ignore[arg-type]

    monkeypatch.setattr(zipfile.ZipFile, "open", spy)
    parse_export(data)
    assert set(opened) == {"Profile.csv", "Positions.csv", "Skills.csv"}


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (b"not a zip", "isn't a ZIP"),
        (b"x" * (21 * 1024 * 1024), "too large"),
    ],
)
def test_rejects_bad_uploads(data: bytes, message: str) -> None:
    with pytest.raises(ExportError, match=message):
        parse_export(data)


def test_rejects_zip_without_profile() -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("messages.csv", "hi")
    with pytest.raises(ExportError, match="couldn't find your profile"):
        parse_export(buf.getvalue())


def test_rejects_oversized_member() -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("Profile.csv", "a" * (3 * 1024 * 1024))  # compresses tiny: zip-bomb shape
    with pytest.raises(ExportError, match="unexpectedly large"):
        parse_export(buf.getvalue())


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("Jan 2020", "2020-01"), ("September 2019", "2019-09"), ("2018", "2018"),
     ("03/2021", "2021-03"), ("2021-7", "2021-07"), ("", None), ("Present", None)],
)  # fmt: skip
def test_normalise_date(raw: str, expected: str | None) -> None:
    assert normalise_date(raw) == expected


def test_handles_notes_preamble_and_column_aliases() -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(
            "Positions.csv",
            "Notes:\nSome text\n\ncompany,TITLE,Start Date,End Date\nAcme,Analyst,2020,2021\n",
        )
    p = parse_export(buf.getvalue())
    assert p.positions[0].company == "Acme" and p.positions[0].end == "2021"


# ---- checks ----------------------------------------------------------------------------------


def ids(findings: list) -> set[str]:  # type: ignore[type-arg]
    return {f.id for f in findings}


def test_profile_checks_find_the_obvious_problems() -> None:
    p = parse_export(make_zip())
    found = ids(profile_checks(p))
    assert {"about_short", "headline_too_short", "position_no_description", "skills_few"} <= found
    assert "about_third_person" in found
    assert "headline_is_just_title" not in found  # current title is "Senior Data Analyst"


def test_limits_and_clichés() -> None:
    p = LinkedInProfile(headline="x" * 221, about="I am a results-driven thought leader. " * 80)
    found = {f.id: f for f in profile_checks(p)}
    assert "headline_too_long" in found and "about_too_long" in found
    assert "thought leader" in found["banned_phrases"].evidence
    assert next(iter(found)) in {
        "headline_too_long",
        "about_too_long",
        "headline_missing",
    }  # high first
    assert find_banned("A rockstar developer") == ["rockstar"]
    assert find_banned("rockstars") == []


def test_headline_equal_to_title_flagged() -> None:
    p = LinkedInProfile(
        headline="Senior Data Analyst",
        positions=[Position("A", "Senior Data Analyst", "", "2022", None)],
    )
    assert "headline_is_just_title" in ids(profile_checks(p))


def test_consistency_between_cv_and_linkedin() -> None:
    p = LinkedInProfile()
    p.positions = [
        Position("Brightwater Analytics Ltd", "Senior Data Analyst", "", "2022-03", None),
        Position("Kerry Foods", "Analyst", "", "2018-09", "2022-02"),
        Position("Tesco Ireland", "Store Assistant", "", "2015", "2017"),
    ]
    cv = {"roles": [
        {"employer": "Brightwater Analytics", "title": "Senior Data Analyst", "start": "2022-03", "end": "present"},
        {"employer": "Kerry Foods plc", "title": "Data Analyst", "start": "2019-09", "end": "2022-02"},
        {"employer": "Dublin City University", "title": "Research Assistant", "start": "2018", "end": "2019"},
    ]}  # fmt: skip
    found = consistency_checks(p, cv)
    by_id = {f.id: f for f in found}
    assert "dates_mismatch" in by_id and "Kerry Foods plc" in by_id["dates_mismatch"].evidence
    assert "title_mismatch" in by_id
    assert (
        "cv_role_missing_on_linkedin" in by_id
        and "Dublin City University" in by_id["cv_role_missing_on_linkedin"].evidence
    )
    assert by_id["linkedin_role_missing_on_cv"].evidence == "Store Assistant at Tesco Ireland"
    assert not any("Brightwater" in f.evidence for f in found)


def test_keyword_gap_needs_enough_ads_and_prefers_honest_wins() -> None:
    low = keyword_gap(["SQL"], "", [], {"Power BI": 20}, n_ads=12)
    assert low.gaps == [] and low.confidence == "none"
    res = keyword_gap(
        profile_skills=["SQL"],
        profile_text="I build dashboards in Tableau",
        cv_skills=["Power BI"],
        ad_skill_counts={"SQL": 140, "Power BI": 60, "dbt": 90, "Tableau": 80, "Excel": 10},
        n_ads=200,
    )
    assert [g.skill for g in res.gaps] == ["Power BI", "dbt"]
    assert res.gaps[0].in_cv and not res.gaps[1].in_cv
    assert res.confidence == "medium" and "200 ads" in res.reason


# ---- AI input --------------------------------------------------------------------------------


def test_rewrite_input_is_minimised() -> None:
    p = LinkedInProfile(
        headline="Analyst · aoife@example.ie",
        about="Call 087 123 4567",
        location="Dublin",
        positions=[Position(f"Co{i}", "Analyst", "", f"20{10 + i}", None) for i in range(6)],
    )
    cv = {"contact": {"name": "Aoife Byrne"}, "summary": "Analyst"}
    data = json.dumps(rewrite_input(p, cv))
    assert "aoife@example.ie" not in data and "087 123 4567" not in data
    assert "Aoife Byrne" not in data and "Dublin" not in data
    assert len(rewrite_input(p, cv)["linkedin_profile"]["positions"]) == 4
