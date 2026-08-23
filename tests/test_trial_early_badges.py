# -*- coding: utf-8 -*-
from types import SimpleNamespace

from gamification.bonus_badges import (
    CHEST_KEEPER_BADGE,
    SPARK_HUNTER_BADGE,
    SYLLABLE_BADGE,
    check_chest_keeper_badge,
    check_early_quest_badges,
)
from gamification.cabinet_ui import (
    _filter_trial_earned_badges,
    _trial_soft_earned_badges,
)
from gamification.rules import apply_badge_rules


def test_letters_complete_no_reader_badge():
    reward = apply_badge_rules(
        "lesson_complete",
        [],
        "Старт",
        tale_title="Словик и пропавшие звуки",
    )
    assert reward["badge_name"] is None


def test_stories_complete_gives_reader():
    reward = apply_badge_rules(
        "lesson_complete",
        [],
        "Старт",
        tale_title="Спаси первую историю",
    )
    assert reward["badge_name"] == "Читатель"


def test_early_quest_bonus_spark_and_syllable():
    grants = check_early_quest_badges(
        child_name="Аня",
        current_badges=[],
        event_type="lesson_complete",
        tale_title="Словик и пропавшие звуки",
        payload={"chest_ready": True, "sparks": 3},
    )
    names = [g.badge_name for g in grants]
    assert SPARK_HUNTER_BADGE in names
    assert SYLLABLE_BADGE in names
    assert "Читатель" not in names


def test_chest_keeper_on_claim():
    grant = check_chest_keeper_badge(
        child_name="Аня",
        current_badges=[],
        tale_title="Словик и пропавшие звуки",
    )
    assert grant is not None
    assert grant.badge_name == CHEST_KEEPER_BADGE


def test_trial_ui_hides_reader_after_letters_only():
    events = [
        SimpleNamespace(
            event_type="lesson_complete",
            tale_title="Словик и пропавшие звуки",
            payload={"chest_ready": True, "sparks": 3},
        )
    ]
    soft = _trial_soft_earned_badges(events, claims=[object()], lesson_links=[])
    assert SPARK_HUNTER_BADGE in soft
    assert CHEST_KEEPER_BADGE in soft
    assert "Читатель" not in soft
    filtered = _filter_trial_earned_badges(
        {"Читатель", "Первый шаг"},
        soft,
        events,
    )
    assert "Читатель" not in filtered
    assert "Первый шаг" in filtered
