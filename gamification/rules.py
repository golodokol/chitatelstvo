"""Детерминированные правила — fallback без LLM и база для валидации."""

from __future__ import annotations

from lessons.step_labels import EXTRA_EVENT_LABELS, LESSON_STEP_LABELS

LEVELS = [
    "Старт",
    "Юный читатель",
    "Исследователь",
    "Мастер слова",
    "Литературный детектив",
]

# Пороги Словиков для уровней (индекс = уровень в LEVELS).
LEVEL_SLOVIK_THRESHOLDS = [0, 4, 10, 18, 28]


def level_from_points(points: int) -> str:
    """Уровень по накопленным Словикам — единый источник для UI и БД."""
    pts = max(0, int(points))
    level = LEVELS[0]
    for i, name in enumerate(LEVELS):
        if i < len(LEVEL_SLOVIK_THRESHOLDS) and pts >= LEVEL_SLOVIK_THRESHOLDS[i]:
            level = name
    return level

EVENT_RULES: dict[str, dict] = {
    "first_task": {
        "points": 0,
        "badge": "Первый шаг",
        "level": "Старт",
        "reward_type": "badge",
        "next_action": f"Перейти к шагу «{LESSON_STEP_LABELS['video']}».",
    },
    "lesson_complete": {
        "points": 2,
        "badge": "Читатель",
        "level": "Юный читатель",
        "reward_type": "badge",
        "next_action": f"Перейти к шагу «{LESSON_STEP_LABELS['emotion_quiz']}».",
    },
    "emotion_quiz": {
        "points": 1,
        "badge": None,
        "level": None,
        "reward_type": "points",
        "next_action": f"Перейти к шагу «{LESSON_STEP_LABELS['comprehension_quiz']}».",
    },
    "comprehension": {
        "points": 2,
        "badge": "Следопыт",
        "level": "Исследователь",
        "reward_type": "badge",
        "next_action": f"Перейти к шагу «{LESSON_STEP_LABELS['tasks']}».",
    },
    "meaning_analysis": {
        "points": 2,
        "badge": "Ловец смысла",
        "level": "Исследователь",
        "reward_type": "badge",
        "next_action": f"По желанию — шаг «{LESSON_STEP_LABELS['creative']}».",
    },
    "creative_task": {
        "points": 3,
        "badge": "Сказочник",
        "level": "Мастер слова",
        "reward_type": "badge",
        "next_action": "Пересказать сказку своими словами или подготовить вопрос к живой встрече.",
    },
    "retelling": {
        "points": 3,
        "badge": "Мастер пересказа",
        "level": "Мастер слова",
        "reward_type": "badge",
        "next_action": "Посмотреть видео к следующей сказке модуля.",
    },
    "mini_check": {
        "points": 0,
        "badge": None,
        "level": None,
        "reward_type": "none",
        "next_action": "Продолжить следующее задание урока.",
    },
    "live_meeting": {
        "points": 2,
        "badge": "Слушатель",
        "level": "Юный читатель",
        "reward_type": "badge",
        "next_action": "Заполнить рабочий лист к следующей сказке.",
    },
    "initiative": {
        "points": 1,
        "badge": None,
        "level": None,
        "reward_type": "points",
        "next_action": "Продолжить задания урока — любопытство помогает в чтении.",
    },
    "streak_3": {
        "points": 3,
        "badge": "Непрерывная серия",
        "level": "Литературный детектив",
        "reward_type": "badge",
        "next_action": "Сохранить ритм — следующее задание уже ждёт.",
    },
    "streak_5": {
        "points": 5,
        "badge": None,
        "level": None,
        "reward_type": "points",
        "next_action": "Отличная серия! Можно выбрать любимую сказку и пересказать её семье.",
    },
    "module_complete": {
        "points": 0,
        "badge": "Исследователь сказки",
        "level": "Литературный детектив",
        "reward_type": "badge",
        "next_action": "Празднуем завершение модуля! Можно выбрать новую сказку для чтения на выходных.",
    },
}


def apply_badge_rules(
    event_type: str,
    current_badges: list[str],
    current_level: str,
) -> dict:
    """Собирает награду по правилам с учётом уже полученных бейджей."""
    rule = EVENT_RULES.get(event_type)
    if not rule:
        raise ValueError(f"Неизвестный тип события: {event_type}")

    badge = rule["badge"]
    if badge and badge in current_badges:
        badge = None

    level_change = rule["level"]
    if level_change:
        try:
            if LEVELS.index(level_change) <= LEVELS.index(current_level):
                level_change = None
        except ValueError:
            level_change = None

    reward_type = rule["reward_type"]
    if badge is None and rule["points"] == 0:
        reward_type = "none"
    elif badge is None and rule["points"] > 0:
        reward_type = "points"
    elif level_change:
        reward_type = "level_up"

    return {
        "reward_type": reward_type,
        "points": rule["points"],
        "badge_name": badge,
        "level_change": level_change,
        "next_action": rule["next_action"],
    }


def fallback_messages(
    event_type: str,
    child_name: str,
    tale_title: str,
    reward: dict,
) -> dict[str, str]:
    """Короткие шаблонные сообщения без LLM (тон — docs/TILDA_TEXTS.md §10)."""
    name = child_name.strip() or "Читатель"
    tale = f" «{tale_title}»" if tale_title else ""
    badge = reward.get("badge_name")
    points = reward.get("points", 0)

    if badge:
        child = f"{name}, отличная работа{tale}! Бейдж «{badge}» твой."
    elif points:
        child = f"{name}, молодец{tale}! +{points} балла."
    else:
        child = f"{name}, ты на верном пути{tale}! Продолжай в своём темпе."

    parent = _parent_progress_line(name, event_type, tale, badge, points)

    return {"child_message": child, "parent_message": parent}


def _parent_progress_line(
    child_name: str,
    event_type: str,
    tale: str,
    badge: str | None,
    points: int,
) -> str:
    """Текст для родителя в письме / на странице прогресса."""
    pts = f" +{points} балла." if points else ""
    badge_part = f" Бейдж «{badge}»." if badge else ""

    templates: dict[str, str] = {
        "lesson_complete": (
            f"{child_name} завершил(а) шаг «{LESSON_STEP_LABELS['video']}»{tale}.{pts}"
        ),
        "emotion_quiz": (
            f"{child_name} прошёл(а) шаг «{LESSON_STEP_LABELS['emotion_quiz']}»{tale}.{pts}"
        ),
        "comprehension": (
            f"{child_name} прошёл(а) шаг «{LESSON_STEP_LABELS['comprehension_quiz']}»{tale}.{badge_part}{pts}"
        ),
        "meaning_analysis": (
            f"{child_name} прошёл(а) шаг «{LESSON_STEP_LABELS['tasks']}»{tale}.{badge_part}{pts}"
        ),
        "creative_task": (
            f"Шаг «{EXTRA_EVENT_LABELS['creative_task']}» по сказке{tale} отмечен.{badge_part}{pts}"
            f" Можно пересказать историю за ужином — просто для удовольствия."
        ),
        "live_meeting": (
            f"{child_name} был(а) на живой встрече по сказке{tale}.{badge_part}{pts}"
        ),
        "retelling": f"{child_name} пересказал(а) сказку{tale}.{badge_part}{pts}",
        "module_complete": (
            f"Модуль завершён — отличная работа, {child_name}!{badge_part}"
        ),
        "streak_3": f"{child_name} читает три дня подряд — классная серия!{badge_part}{pts}",
        "streak_5": f"Пять дней подряд в Читательстве — так держать, {child_name}!{pts}",
        "tale_traveler": (
            f"{child_name} прошёл(а) все 4 сказки модуля.{badge_part}"
        ),
    }

    if event_type in templates:
        return templates[event_type].strip()

    if badge:
        return f"{child_name} получил(а) бейдж «{badge}»{tale}.{pts}".strip()
    if points:
        return f"Новый прогресс{tale}: +{points} балла.".strip()
    return f"Зафиксирован прогресс{tale}.".strip()
