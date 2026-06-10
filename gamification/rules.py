"""Детерминированные правила — fallback без LLM и база для валидации."""

from __future__ import annotations

LEVELS = [
    "Старт",
    "Юный читатель",
    "Исследователь",
    "Мастер слова",
    "Литературный детектив",
]

EVENT_RULES: dict[str, dict] = {
    "first_task": {
        "points": 0,
        "badge": "Первый шаг",
        "level": "Старт",
        "reward_type": "badge",
        "next_action": "Посмотреть видео-урок и заполнить рабочий лист по сказке.",
    },
    "lesson_complete": {
        "points": 2,
        "badge": "Читатель",
        "level": "Юный читатель",
        "reward_type": "badge",
        "next_action": "Выполнить задание на понимание текста.",
    },
    "comprehension": {
        "points": 2,
        "badge": "Следопыт",
        "level": "Исследователь",
        "reward_type": "badge",
        "next_action": "Перейти к заданию на анализ смысла сказки.",
    },
    "meaning_analysis": {
        "points": 2,
        "badge": "Ловец смысла",
        "level": "Исследователь",
        "reward_type": "badge",
        "next_action": "Выполнить творческое задание — придумать свой вариант конца.",
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
    """Короткие шаблонные сообщения без LLM."""
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

    if badge:
        parent = f"Ребёнок получил бейдж «{badge}» за событие «{event_type}»."
    elif points:
        parent = f"Начислено {points} баллов за событие «{event_type}»."
    else:
        parent = f"Зафиксирован прогресс по событию «{event_type}»."

    return {"child_message": child, "parent_message": parent}
