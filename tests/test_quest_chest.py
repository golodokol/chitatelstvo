from types import SimpleNamespace

from gamification.cabinet_ui import (
    chest_ready_from_done,
    quest_chest_earned,
    quest_goal_count,
    quest_spark_station_ids,
)


LESSON = {
    "group_code": "early-letters",
    "lesson_format": "quest",
    "title": "Словик и пропавшие звуки",
    "stations": [
        {"id": "gate", "spark": False},
        {"id": "whispers", "spark": True, "spark_kind": "sound"},
        {"id": "hunt", "spark": True, "spark_kind": "letter"},
        {"id": "basket", "spark": True, "spark_kind": "syllable"},
        {"id": "reward", "spark": False},
    ],
    "quest": {"goal_count": 3},
}


def _event(payload: dict) -> SimpleNamespace:
    return SimpleNamespace(
        event_type="lesson_complete",
        tale_title=LESSON["title"],
        payload=payload,
        notes="",
    )


def test_spark_station_ids_and_goal():
    assert quest_spark_station_ids(LESSON) == ["whispers", "hunt", "basket"]
    assert quest_goal_count(LESSON) == 3


def test_chest_closed_without_correct_answers():
    events = [_event({"sparks": 3, "format": "quest", "passed_stations": [], "chest_ready": False})]
    assert quest_chest_earned(events, LESSON) is False
    assert chest_ready_from_done({"lesson_complete"}, LESSON, events) is False


def test_chest_closed_if_lesson_complete_missing():
    events = [_event({
        "sparks": 3,
        "passed_stations": ["whispers", "hunt", "basket"],
        "chest_ready": True,
    })]
    assert chest_ready_from_done(set(), LESSON, events) is False


def test_chest_open_when_all_spark_stations_passed():
    events = [_event({
        "sparks": 3,
        "format": "quest",
        "passed_stations": ["whispers", "hunt", "basket"],
        "chest_ready": True,
    })]
    assert quest_chest_earned(events, LESSON) is True
    assert chest_ready_from_done({"lesson_complete"}, LESSON, events) is True


def test_stories_trial_spark_stations():
    import json
    from pathlib import Path

    lesson = json.loads(
        Path("lessons/catalog/early-stories-trial-lesson-01.json").read_text(encoding="utf-8")
    )
    assert quest_spark_station_ids(lesson) == ["word_house", "story_window", "book_key"]
    assert quest_goal_count(lesson) == 3
    assert lesson["quest"]["spark_labels"]["word"] == "Слово"


def test_regular_chest_still_uses_three_steps():
    lesson = {"group_code": "grade-3", "title": "Сказка"}
    done = {"video_unlock", "comprehension", "meaning_analysis"}
    assert chest_ready_from_done(done, lesson) is True
    assert chest_ready_from_done({"lesson_complete"}, lesson) is False


def test_regular_chest_opens_when_quizzes_done_without_video_event():
    """Эмоциометр/квизы могли пройти без записи video_unlock — сундук не должен зависать."""
    lesson = {"group_code": "grade-1", "title": "Царевна лягушка"}
    done = {"emotion_quiz", "comprehension", "meaning_analysis", "retelling"}
    assert chest_ready_from_done(done, lesson) is True
    assert chest_ready_from_done({"comprehension"}, lesson) is False
