"""Единые подписи шагов урока — один набор для всех сказок."""

from __future__ import annotations

LESSON_STEP_LABELS: dict[str, str] = {
    "video": "Смотрим видео-урок",
    "emotion_quiz": "Изучаем эмоциональный интеллект",
    "comprehension_quiz": "Мини-тест по сказке",
    "tasks": "Выполняем задания",
    "creative": "Творчество",
}

LESSON_STEP_NUMBERS: dict[str, int] = {
    "video": 1,
    "emotion_quiz": 2,
    "comprehension_quiz": 3,
    "tasks": 4,
    "creative": 5,
}

# Ключ блока в JSON урока → ключ шага в LESSON_STEP_LABELS
LESSON_BLOCK_TO_STEP: dict[str, str] = {
    "video": "video",
    "emotion_quiz": "emotion_quiz",
    "comprehension_quiz": "comprehension_quiz",
    "meaning_quiz": "tasks",
    "creative_tasks": "creative",
}


def lesson_step_labels_payload() -> dict[str, str]:
    return dict(LESSON_STEP_LABELS)


def lesson_step_badge(step_key: str) -> str:
    number = LESSON_STEP_NUMBERS[step_key]
    label = LESSON_STEP_LABELS[step_key]
    return f"Шаг {number} · {label}"


def lesson_step_badges_payload() -> dict[str, str]:
    return {key: lesson_step_badge(key) for key in LESSON_STEP_LABELS}


def lesson_step_label(block_key: str) -> str:
    step_key = LESSON_BLOCK_TO_STEP.get(block_key, block_key)
    return LESSON_STEP_LABELS[step_key]


# slug события в БД → ключ шага в LESSON_STEP_LABELS
EVENT_TYPE_TO_STEP: dict[str, str] = {
    "lesson_complete": "video",
    "emotion_quiz": "emotion_quiz",
    "comprehension": "comprehension_quiz",
    "meaning_analysis": "tasks",
}

# События вне четырёх шагов урока — отдельные подписи для родителей
EXTRA_EVENT_LABELS: dict[str, str] = {
    "first_task": "Первый шаг",
    "creative_task": "Творческое задание",
    "retelling": "Пересказ",
    "live_meeting": "Живая встреча",
    "mini_check": "Мини-проверка",
    "initiative": "Своя инициатива",
    "streak_3": "Серия из 3 дней",
    "streak_5": "Серия из 5 дней",
    "module_complete": "Модуль завершён",
}


def event_type_label(event_type: str) -> str:
    """Человекочитаемая подпись события для блока «Недавние занятия»."""
    step_key = EVENT_TYPE_TO_STEP.get(event_type)
    if step_key:
        return LESSON_STEP_LABELS[step_key]
    return EXTRA_EVENT_LABELS.get(event_type, event_type)


# Ключ картинки Словика на уроке → ключ шага в LESSON_STEP_LABELS
SLOVIK_KEY_TO_STEP: dict[str, str] = {
    "reads": "video",
    "emotion": "emotion_quiz",
    "writes": "comprehension_quiz",
    "dreams": "tasks",
    "grows": "creative",
}


def companion_hint_for_slovik_key(slovik_key: str) -> str | None:
    """Подпись шага для подсказки Словика рядом с уроком."""
    step_key = SLOVIK_KEY_TO_STEP.get(slovik_key)
    if step_key:
        return LESSON_STEP_LABELS[step_key]
    return None
