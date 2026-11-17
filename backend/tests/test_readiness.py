import pytest

from app.insights.readiness import GATES, readiness


def test_waiting_states_say_what_they_wait_for() -> None:
    r = readiness("what_works_personal", 14)
    assert r.state == "collecting" and r.progress == pytest.approx(0.7)
    assert r.message == "Unlocks after 20 tracked outcomes: you have 14."
    c = readiness("company_reply_badge", 6)
    assert c.message == "Collecting replies for this company: 6 of 15 tracked applications."
    assert readiness("where_you_stand", 12).state == "public_data"


def test_live_when_threshold_met_and_never_an_invented_number() -> None:
    assert readiness("company_reply_badge", 15).state == "live"
    assert readiness("company_reply_badge", 15).message == ""
    for name in GATES:
        msg = readiness(name, 0).message
        assert "%" not in msg  # waiting states never show a rate


def test_bad_input() -> None:
    with pytest.raises(KeyError):
        readiness("nope", 1)
    with pytest.raises(ValueError):
        readiness("stage_odds", -1)
