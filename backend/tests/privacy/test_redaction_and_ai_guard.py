import json
import logging

import pytest
import structlog

from app.core.logging import configure_logging
from app.privacy.ai_guard import PersonalDataInAIInputError, guard_text, prepare_cv_for_ai
from app.privacy.redaction import find_pii, redact, scrub, sentry_before_send


@pytest.mark.parametrize(
    ("text", "kind"),
    [
        ("contact aoife.kelly+jobs@example.ie please", "email"),
        ("call me on +353 87 123 4567", "phone"),
        ("or 087 123 4567", "phone"),
        ("UK mobile 07700 900123", "phone"),
        ("PPSN 1234567TA", "ppsn"),
        ("NI AB 12 34 56 C", "ni_number"),
        ("IBAN IE29 AIBK 9311 5212 3456 78", "iban"),
        ("live at D02 X285 Dublin", "eircode"),
        ("London SW1A 1AA", "uk_postcode"),
        ("see https://linkedin.com/in/aoife", "url"),
        ("from 192.168.10.24", "ipv4"),
    ],
)
def test_detects_personal_data(text: str, kind: str) -> None:
    assert kind in {k for k, _ in find_pii(text)}
    assert f"[{kind}]" in redact(text)


@pytest.mark.parametrize(
    "text",
    [
        "Led a team of 12 and cut costs by 18% in 2023",
        "Senior Data Analyst, 2019-2021",
        "Grew revenue from €1.2m to €3.4m",
        "Managed 4,500 tickets a month",
    ],
)
def test_leaves_ordinary_cv_text_alone(text: str) -> None:
    assert redact(text) == text


def test_scrub_removes_sensitive_keys_and_redacts_values() -> None:
    event = {"email": "a@b.ie", "detail": "user a@b.ie failed", "nested": [{"phone": "1"}]}
    assert scrub(event) == {
        "email": "[removed]",
        "detail": "user [email] failed",
        "nested": [{"phone": "[removed]"}],
    }


def test_sentry_event_is_stripped() -> None:
    event = {
        "user": {"email": "a@b.ie", "ip_address": "1.2.3.4"},
        "request": {"cookies": "s=1", "headers": {"Cookie": "x"}, "url": "/x?email=a@b.ie"},
        "message": "failed for a@b.ie",
    }
    out = sentry_before_send(event, {})
    assert "user" not in out
    assert "cookies" not in out["request"] and "headers" not in out["request"]
    assert out["request"]["url"] == "/x?email=[email]"
    assert out["message"] == "failed for [email]"


def test_logs_never_contain_personal_data(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO", json=True)
    structlog.get_logger().info("sign_in_failed", email="aoife@example.ie", note="from 10.0.0.1")
    line = capsys.readouterr().out.strip().splitlines()[-1]
    record = json.loads(line)
    assert record["email"] == "[removed]"
    assert record["note"] == "from [ipv4]"
    assert "aoife" not in line
    logging.getLogger().handlers.clear()


def test_ai_guard_removes_contact_block_and_links() -> None:
    cv = {
        "contact": {"name": "Aoife Kelly", "email": "aoife@example.ie", "phone": "087 123 4567"},
        "summary": "Analyst. Email me at aoife@example.ie",
        "roles": [
            {
                "title": "Analyst",
                "links": ["https://x.ie"],
                "achievements": [{"text": "Cut costs 18%"}],
            }
        ],
    }
    safe = prepare_cv_for_ai(cv)
    dumped = json.dumps(safe)
    assert "contact" not in safe
    assert "aoife@example.ie" not in dumped and "Aoife Kelly" not in dumped
    assert "links" not in safe["roles"][0]
    assert safe["summary"] == "Analyst. Email me at [email]"
    assert safe["roles"][0]["achievements"][0]["text"] == "Cut costs 18%"
    assert cv["contact"]["name"] == "Aoife Kelly"  # original untouched


def test_ai_guard_strict_mode_refuses() -> None:
    with pytest.raises(PersonalDataInAIInputError):
        guard_text("my PPSN is 1234567TA", strict=True)
    assert guard_text("Led a team of 12", strict=True).redactions == 0
