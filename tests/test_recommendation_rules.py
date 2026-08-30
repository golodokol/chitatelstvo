from __future__ import annotations

from services.recommendation_rules import match_recommendation_rule


def test_match_grade_one_by_class() -> None:
    rule = match_recommendation_rule(
        quiz_variant="reading",
        child_age=7,
        answers_by_id={"grade": "1 класс"},
    )
    assert rule is not None
    assert rule.rule_id == "6"
    assert rule.trial_lesson_title == "Царевна-лягушка"


def test_hard_signal_lower_priority_than_grade() -> None:
    rule = match_recommendation_rule(
        quiz_variant="reading",
        child_age=7,
        answers_by_id={"grade": "1 класс", "hard": "Понять, о чём текст"},
    )
    assert rule is not None
    assert rule.rule_id == "6"


def test_early_readiness() -> None:
    rule = match_recommendation_rule(
        quiz_variant="early",
        child_age=5,
        answers_by_id={"readiness": "Ещё почти не знает буквы"},
    )
    assert rule is not None
    assert rule.trial_lesson_slug == "early-letters-trial-lesson-01"
