from __future__ import annotations

from services.recommendation_rules import load_recommendation_rules, match_recommendation_rule


def setup_function() -> None:
    load_recommendation_rules.cache_clear()


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


def test_teacher_format_9_11_opens_extra_trial() -> None:
    rule = match_recommendation_rule(
        quiz_variant="reading",
        child_age=11,
        answers_by_id={
            "format": "С живым преподавателем в группе",
            "hard": "Начать читать без напоминаний",
        },
    )
    assert rule is not None
    assert rule.rule_id == "20"
    assert rule.trial_lesson_slug == "extra-9-11-self_paced-stage-1-lesson-01"


def test_teacher_format_younger_opens_plushevyi_krolik() -> None:
    rule = match_recommendation_rule(
        quiz_variant="reading",
        child_age=8,
        answers_by_id={"format": "С живым преподавателем в группе"},
    )
    assert rule is not None
    assert rule.rule_id == "16"
    assert rule.trial_lesson_slug == "extra-6-8-self_paced-stage-1-lesson-01"


def test_teacher_format_age_nine_gets_trial() -> None:
    rule = match_recommendation_rule(
        quiz_variant="reading",
        child_age=9,
        answers_by_id={"format": "С живым преподавателем в группе"},
    )
    assert rule is not None
    assert rule.rule_id == "20"
    assert rule.trial_lesson_slug == "extra-9-11-self_paced-stage-1-lesson-01"
