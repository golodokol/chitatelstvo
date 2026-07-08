"""Единые подписи шагов урока — один набор для всех сказок."""

from __future__ import annotations

LESSON_STEP_LABELS: dict[str, str] = {
    "video": "Смотрим видео-урок",
    "emotion_quiz": "Изучаем эмоциональный интеллект",
    "reading_practice": "Практика чтения",
    "comprehension_quiz": "Мини-тест по сказке",
    "tasks": "Выполняем задания",
    "retelling": "Пробуем пересказать сказку",
    "creative": "Творчество",
}

LESSON_STEP_NUMBERS: dict[str, int] = {
    "video": 1,
    "emotion_quiz": 2,
    "reading_practice": 3,
    "comprehension_quiz": 4,
    "tasks": 5,
    "retelling": 6,
    "creative": 7,
}

# Порядок блоков на странице урока (block_key → step_key)
LESSON_BLOCKS_IN_ORDER: list[tuple[str, str]] = [
    ("video", "video"),
    ("emotion_quiz", "emotion_quiz"),
    ("reading_practice", "reading_practice"),
    ("comprehension_quiz", "comprehension_quiz"),
    ("meaning_quiz", "tasks"),
    ("retelling_quiz", "retelling"),
    ("creative_tasks", "creative"),
]

# Ключ блока в JSON урока → ключ шага в LESSON_STEP_LABELS
LESSON_BLOCK_TO_STEP: dict[str, str] = {
    "video": "video",
    "emotion_quiz": "emotion_quiz",
    "reading_practice": "reading_practice",
    "comprehension_quiz": "comprehension_quiz",
    "meaning_quiz": "tasks",
    "retelling_quiz": "retelling",
    "creative_tasks": "creative",
}


def lesson_step_labels_payload() -> dict[str, str]:
    return dict(LESSON_STEP_LABELS)


def lesson_step_badge(step_key: str) -> str:
    number = LESSON_STEP_NUMBERS[step_key]
    return f"Шаг {number}"


def lesson_has_block(lesson: dict, block_key: str) -> bool:
    if block_key == "video":
        return bool(lesson.get("video"))
    return bool(lesson.get(block_key))


def lesson_step_badges_for_lesson(lesson: dict) -> dict[str, str]:
    """Нумерация шагов только для блоков, присутствующих в уроке."""
    badges: dict[str, str] = {}
    n = 0
    for block_key, step_key in LESSON_BLOCKS_IN_ORDER:
        if lesson_has_block(lesson, block_key):
            n += 1
            badges[step_key] = f"Шаг {n}"
    return badges


def lesson_step_badges_payload() -> dict[str, str]:
    return {key: lesson_step_badge(key) for key in LESSON_STEP_LABELS}


def lesson_step_label(block_key: str) -> str:
    step_key = LESSON_BLOCK_TO_STEP.get(block_key, block_key)
    return LESSON_STEP_LABELS[step_key]


# slug события в БД → ключ шага в LESSON_STEP_LABELS
EVENT_TYPE_TO_STEP: dict[str, str] = {
    "lesson_complete": "video",
    "emotion_quiz": "emotion_quiz",
    "reading_practice": "reading_practice",
    "comprehension": "comprehension_quiz",
    "meaning_analysis": "tasks",
    "retelling": "retelling",
}

# События вне четырёх шагов урока — отдельные подписи для родителей
EXTRA_EVENT_LABELS: dict[str, str] = {
    "first_task": "Первый шаг",
    "creative_task": "Творческое задание",
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
