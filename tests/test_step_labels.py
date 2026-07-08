"""Единые подписи шагов урока."""

from lessons.loader import get_lesson
from lessons.step_labels import (
    LESSON_BLOCK_TO_STEP,
    LESSON_STEP_LABELS,
    event_type_label,
    lesson_step_badge,
    lesson_step_badges_for_lesson,
    lesson_step_badges_payload,
    lesson_step_label,
    lesson_step_labels_payload,
)


def test_lesson_step_labels_payload():
    payload = lesson_step_labels_payload()
    assert payload["video"] == "Смотрим видео-урок"
    assert payload["emotion_quiz"] == "Изучаем эмоциональный интеллект"
    assert payload["reading_practice"] == "Практика чтения"
    assert payload["comprehension_quiz"] == "Мини-тест по сказке"
    assert payload["tasks"] == "Выполняем задания"
    assert payload["retelling"] == "Пробуем пересказать сказку"
    assert payload["creative"] == "Творчество"


def test_lesson_step_badge_fixed_numbers():
    assert lesson_step_badge("video") == "Шаг 1"
    assert lesson_step_badge("emotion_quiz") == "Шаг 2"
    assert lesson_step_badge("reading_practice") == "Шаг 3"
    assert lesson_step_badge("comprehension_quiz") == "Шаг 4"
    assert lesson_step_badge("tasks") == "Шаг 5"
    assert lesson_step_badge("retelling") == "Шаг 6"
    assert lesson_step_badge("creative") == "Шаг 7"


def test_lesson_step_badges_payload():
    badges = lesson_step_badges_payload()
    assert badges == {key: lesson_step_badge(key) for key in LESSON_STEP_LABELS}


def test_lesson_step_badges_for_grade1_lesson():
    lesson = get_lesson("grade-1-self_paced-stage-1-lesson-01")
    badges = lesson_step_badges_for_lesson(lesson)
    assert badges["video"] == "Шаг 1"
    assert badges["emotion_quiz"] == "Шаг 2"
    assert badges["reading_practice"] == "Шаг 3"
    assert badges["comprehension_quiz"] == "Шаг 4"
    assert badges["creative"] == "Шаг 7"


def test_lesson_block_to_step_mapping():
    assert lesson_step_label("video") == LESSON_STEP_LABELS["video"]
    assert lesson_step_label("emotion_quiz") == LESSON_STEP_LABELS["emotion_quiz"]
    assert lesson_step_label("reading_practice") == LESSON_STEP_LABELS["reading_practice"]
    assert lesson_step_label("comprehension_quiz") == LESSON_STEP_LABELS["comprehension_quiz"]
    assert lesson_step_label("meaning_quiz") == LESSON_STEP_LABELS["tasks"]
    assert lesson_step_label("retelling_quiz") == LESSON_STEP_LABELS["retelling"]
    assert lesson_step_label("creative_tasks") == LESSON_STEP_LABELS["creative"]
    assert LESSON_BLOCK_TO_STEP["meaning_quiz"] == "tasks"
    assert LESSON_BLOCK_TO_STEP["reading_practice"] == "reading_practice"
    assert LESSON_BLOCK_TO_STEP["retelling_quiz"] == "retelling"


def test_event_type_labels_for_parent_view():
    assert event_type_label("lesson_complete") == "Смотрим видео-урок"
    assert event_type_label("emotion_quiz") == "Изучаем эмоциональный интеллект"
    assert event_type_label("reading_practice") == "Практика чтения"
    assert event_type_label("comprehension") == "Мини-тест по сказке"
    assert event_type_label("meaning_analysis") == "Выполняем задания"
    assert event_type_label("retelling") == "Пробуем пересказать сказку"
    assert event_type_label("creative_task") == "Творческое задание"
    assert event_type_label("live_meeting") == "Живая встреча"
    assert event_type_label("unknown_slug") == "unknown_slug"
