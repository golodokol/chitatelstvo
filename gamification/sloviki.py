"""Словик — персонаж и картинки для кабинета и урока."""

from __future__ import annotations

from typing import Any

from gamification.rules import EVENT_RULES

STATIC_PREFIX = "/static/sloviki"

SLOVIK_FILES: dict[str, str] = {
    "main": "slovik-main.png",
    "hero": "slovik-hero.png",
    "walks": "slovik-walks.png",
    "reads": "slovik-reads.png",
    "writes": "slovik-writes.png",
    "grows": "slovik-grows.png",
    "dreams": "slovik-dreams.png",
    "cloud": "slovik-cloud.png",
    "reward": "slovik-reward.png",
    "victory": "slovik-victory.png",
}

EVENT_SLOVIK: dict[str, str] = {
    "first_task": "walks",
    "lesson_complete": "reads",
    "comprehension": "writes",
    "meaning_analysis": "dreams",
    "creative_task": "writes",
    "retelling": "reads",
    "live_meeting": "grows",
    "initiative": "grows",
    "streak_3": "grows",
    "streak_5": "grows",
    "module_complete": "victory",
}

BIG_EVENT_SLOVIK: frozenset[str] = frozenset({"module_complete", "streak_3"})

MISSION_SLOVIK: dict[str, str] = {
    "read": "reads",
    "quiz": "writes",
    "points": "reward",
    "chest": "cloud",
    "secret": "dreams",
}

LESSON_STEP_SLOVIK: dict[str, str] = {
    "video": "reads",
    "comprehension": "writes",
    "meaning": "dreams",
    "creative": "writes",
    "manual": "grows",
    "done": "victory",
}

COMPANION_HINTS: dict[str, str] = {
    "main": "Скоро начнётся новое приключение!",
    "walks": "Пора в путь — урок ждёт!",
    "reads": "Смотрим сказку вместе",
    "writes": "Отвечаем на вопросы",
    "dreams": "Ищем смысл и секреты",
    "cloud": "Сундук совсем близко!",
    "reward": "Ещё чуть-чуть!",
    "victory": "Ура! Можно открывать сундук!",
    "grows": "Ты растёшь с каждым днём",
    "hero": "Ты настоящий герой чтения!",
}


def slovik_url(key: str) -> str:
    filename = SLOVIK_FILES.get(key, SLOVIK_FILES["main"])
    return f"{STATIC_PREFIX}/{filename}"


def slovik_urls() -> dict[str, str]:
    return {k: slovik_url(k) for k in SLOVIK_FILES}


def event_slovik_key(event_type: str, *, big: bool = False) -> str:
    if big or event_type in BIG_EVENT_SLOVIK:
        return "victory" if event_type == "module_complete" else "hero"
    return EVENT_SLOVIK.get(event_type, "reward")


def mission_slovik_key(mission_id: str, *, chest_ready: bool = False) -> str:
    if mission_id == "chest" and chest_ready:
        return "victory"
    return MISSION_SLOVIK.get(mission_id, "walks")


def chest_slovik_key(chest: dict[str, Any]) -> str:
    if chest.get("ready"):
        return "victory"
    pct = chest.get("pct") or 0
    if pct >= 50:
        return "cloud"
    if pct > 0:
        return "walks"
    return "walks"


def companion_key(
    events: list[Any],
    lesson: dict | None,
    chest: dict[str, Any],
    *,
    secret_unlocked: bool = False,
) -> str:
    if chest.get("ready"):
        return "victory"

    if not lesson or not lesson.get("url"):
        return "main"

    tale = (lesson.get("title") or "").strip()
    done = {
        e.event_type
        for e in events
        if (getattr(e, "tale_title", None) or "").strip() == tale
    }

    pct = chest.get("pct") or 0
    if pct >= 50 and not chest.get("ready"):
        return "cloud"

    if "meaning_analysis" in done and chest.get("steps_remaining", 1) == 0:
        return "victory"
    if "meaning_analysis" in done:
        return "dreams"
    if "comprehension" in done:
        return "writes"
    if "lesson_complete" in done:
        return "writes"
    if secret_unlocked:
        return "cloud"
    return "reads"


def event_toast_message(event_type: str) -> str:
    rule = EVENT_RULES.get(event_type, {})
    pts = rule.get("points") or 0
    badge = rule.get("badge")
    if badge and pts:
        return f"+{pts} Словиков · бейдж «{badge}»"
    if pts:
        return f"+{pts} Словиков!"
    if badge:
        return f"Бейдж «{badge}»!"
    return "Отличная работа!"


def lesson_step_key(
    *,
    has_comprehension: bool,
    has_meaning: bool,
    video_done: bool = False,
    comprehension_done: bool = False,
    meaning_done: bool = False,
) -> str:
    if meaning_done or (video_done and not has_comprehension and not has_meaning):
        return "grows"
    if comprehension_done and not has_meaning:
        return "grows"
    if comprehension_done:
        return "dreams"
    if video_done:
        return "writes"
    return "reads"


def recent_event_slovik(events: list[Any]) -> dict[str, str] | None:
    """Последнее событие для toast в кабинете."""
    if not events:
        return None
    ev = events[0]
    et = getattr(ev, "event_type", "") or ""
    rule = EVENT_RULES.get(et, {})
    if not rule.get("points") and not rule.get("badge"):
        return None
    key = event_slovik_key(et, big=et in BIG_EVENT_SLOVIK)
    created = getattr(ev, "created_at", None)
    return {
        "key": key,
        "url": slovik_url(key),
        "event_type": et,
        "message": event_toast_message(et),
        "toast_id": f"{et}-{created.isoformat() if created else '0'}",
    }
