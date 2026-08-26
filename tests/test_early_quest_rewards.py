from gamification.rules import (
    EARLY_QUEST_COMPLETE_POINTS,
    apply_badge_rules,
    is_early_letters_title,
    is_early_stories_title,
)
from gamification.sloviki import event_toast_message as slovik_toast
from gamification.sloviki import recent_event_slovik


class _Ev:
    def __init__(self, event_type, tale_title, payload=None, created_at=None):
        self.event_type = event_type
        self.tale_title = tale_title
        self.payload = payload or {}
        self.created_at = created_at


def test_reader_badge_not_for_letters_quest():
    reward = apply_badge_rules(
        "lesson_complete",
        [],
        "Старт",
        tale_title="Словик и пропавшие звуки",
    )
    assert reward["badge_name"] is None
    assert reward["points"] == EARLY_QUEST_COMPLETE_POINTS


def test_reader_badge_for_first_story_quest():
    reward = apply_badge_rules(
        "lesson_complete",
        [],
        "Старт",
        tale_title="Спаси первую историю",
    )
    assert reward["badge_name"] == "Читатель"
    assert reward["points"] == EARLY_QUEST_COMPLETE_POINTS


def test_reader_badge_skipped_if_already_owned():
    reward = apply_badge_rules(
        "lesson_complete",
        ["Читатель"],
        "Юный читатель",
        tale_title="Спаси первую историю",
    )
    assert reward["badge_name"] is None
    assert reward["points"] == EARLY_QUEST_COMPLETE_POINTS


def test_regular_tale_still_gives_reader_badge():
    reward = apply_badge_rules(
        "lesson_complete",
        [],
        "Старт",
        tale_title="Сказка о рыбаке и рыбке",
    )
    assert reward["badge_name"] == "Читатель"
    assert reward["points"] == 2


def test_early_title_markers():
    assert is_early_letters_title("Словик и пропавшие звуки")
    assert not is_early_stories_title("Словик и пропавшие звуки")
    assert is_early_stories_title("Спаси первую историю")
    assert not is_early_letters_title("Спаси первую историю")


def test_toast_message_respects_early_quest_rules():
    assert "Читатель" not in slovik_toast(
        "lesson_complete",
        tale_title="Словик и пропавшие звуки",
    )
    assert "+3" in slovik_toast(
        "lesson_complete",
        tale_title="Словик и пропавшие звуки",
    )
    assert "Читатель" in slovik_toast(
        "lesson_complete",
        tale_title="Спаси первую историю",
    )


def test_cabinet_toast_skips_incomplete_early_quest():
    toast = recent_event_slovik(
        [
            _Ev(
                "lesson_complete",
                "Словик и пропавшие звуки",
                {"chest_ready": False, "sparks": 0},
            )
        ]
    )
    assert toast is None


def test_cabinet_toast_letters_complete_shows_syllable_not_reader():
    toast = recent_event_slovik(
        [
            _Ev(
                "lesson_complete",
                "Словик и пропавшие звуки",
                {"chest_ready": True, "sparks": 3},
            )
        ]
    )
    assert toast is not None
    assert toast["badge"] == "Слоговик"
    assert toast["points"] == EARLY_QUEST_COMPLETE_POINTS


def test_cabinet_toast_stories_complete_prefers_spark_over_reader():
    toast = recent_event_slovik(
        [
            _Ev(
                "lesson_complete",
                "Спаси первую историю",
                {"chest_ready": True, "sparks": 3},
            )
        ]
    )
    assert toast is not None
    assert toast["badge"] == "Искатель искорок"


def test_cabinet_toast_stories_shows_reader_when_spark_owned():
    toast = recent_event_slovik(
        [
            _Ev(
                "lesson_complete",
                "Спаси первую историю",
                {"chest_ready": True, "sparks": 3},
            )
        ],
        current_badges=["Искатель искорок"],
    )
    assert toast is not None
    assert toast["badge"] == "Читатель"


def test_cabinet_toast_hides_owned_reader_badge():
    toast = recent_event_slovik(
        [
            _Ev(
                "lesson_complete",
                "Царевна лягушка",
            )
        ],
        current_badges=["Читатель"],
    )
    assert toast is None

