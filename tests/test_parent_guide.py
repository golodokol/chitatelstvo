"""Подписи для вкладки родителя на странице прогресса."""

from gamification.cabinet_ui import (
    event_type_label,
    parent_lesson_guide_steps,
    parent_points_rows,
)
from lessons.step_labels import LESSON_STEP_LABELS


def test_event_type_label_uses_human_names():
    assert event_type_label("emotion_quiz") == "Изучаем эмоциональный интеллект"
    assert event_type_label("comprehension") == "Мини-тест по сказке"
    assert event_type_label("unknown_event") == "unknown_event"


def test_parent_lesson_guide_steps_match_lesson_player():
    steps = parent_lesson_guide_steps()
    labels = [step["label"] for step in steps[:4]]
    assert labels == [
        LESSON_STEP_LABELS["video"],
        LESSON_STEP_LABELS["emotion_quiz"],
        LESSON_STEP_LABELS["comprehension_quiz"],
        LESSON_STEP_LABELS["tasks"],
    ]
    assert "Квиз" not in steps[1]["label"]
    assert "эмоцион" in steps[1]["label"].lower()
    assert "+1 Словик" in steps[1]["note"]


def test_parent_points_rows_include_emotion_step():
    rows = {row["label"]: row["value"] for row in parent_points_rows()}
    assert LESSON_STEP_LABELS["emotion_quiz"] in rows
    assert rows[LESSON_STEP_LABELS["emotion_quiz"]] == "+1"
    assert "Квиз «Понимание»" not in rows
