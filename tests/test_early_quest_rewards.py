from gamification.rules import (
    EARLY_QUEST_COMPLETE_POINTS,
    apply_badge_rules,
    is_early_letters_title,
    is_early_stories_title,
)
from gamification.sloviki import event_toast_message as slovik_toast


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
