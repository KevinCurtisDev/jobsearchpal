import pytest

from app.insights.stage_odds import encouragement, p_offer, pipeline_odds, stage_odds


def test_stage_odds_from_public_benchmarks() -> None:
    assert stage_odds("applied").one_in == 84
    assert stage_odds("screening").one_in == 7
    assert stage_odds("interview").one_in == 2
    assert stage_odds("screening").multiplier_from_applied == 12.5
    assert (
        stage_odds("interview").source == "public" and stage_odds("interview").confidence == "low"
    )
    with pytest.raises(ValueError):
        p_offer("offer")


def test_pipeline_matches_the_tracker_design() -> None:
    res = pipeline_odds({"applied": 4, "screening": 1, "interview": 1})
    assert round(res.p_at_least_one_offer, 2) == 0.55
    assert round(res.expected_offers, 2) == 0.65
    assert res.active == 6 and res.biggest_contributor == "interview"
    assert (
        pipeline_odds({}).p_at_least_one_offer == 0
        and pipeline_odds({}).biggest_contributor is None
    )
    with pytest.raises(ValueError):
        pipeline_odds({"applied": -1})


def test_encouragement_is_progress_framed_and_uses_real_numbers() -> None:
    assert "12 times better" in encouragement("applied")
    assert "about 1 in 84 to about 1 in 2" in encouragement("interview")
    assert "not a judgement" in encouragement("rejected_fast")
    for stage in ("applied", "screening", "interview"):
        text = encouragement(stage).lower()
        for banned in ("hurry", "don't miss", "last chance", "streak", "only "):
            assert banned not in text
