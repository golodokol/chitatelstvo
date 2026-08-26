"""Словик — персонаж и картинки для кабинета и урока."""

from __future__ import annotations

from typing import Any

from gamification.badge_assets import BADGE_ASSET_FILES
from gamification.rules import (
    EVENT_RULES,
    apply_badge_rules,
    is_early_letters_title,
    is_early_quest_title,
)
from lessons.step_labels import LESSON_STEP_LABELS

STATIC_PREFIX = "/static/sloviki"

SLOVIK_FILES: dict[str, str] = {
    "main": "slovik-main.png",
    "preparing": "slovik-preparing-read.png",
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
    "emotion_quiz": "dreams",
    "reading_practice": "reads",
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

# Иконка счётчика «Словики» в кабинете (монетка), не персонаж шага урока.
POINTS_COUNTER_SLOVIK = "reward"

MISSION_SLOVIK: dict[str, str] = {
    "read": "reads",
    "quiz": "writes",
    "points": "reward",
    "chest": "cloud",
    "secret": "dreams",
}

LESSON_STEP_SLOVIK: dict[str, str] = {
    "video": "reads",
    "emotion": "dreams",
    "reading": "reads",
    "comprehension": "writes",
    "meaning": "dreams",
    "retelling": "reads",
    "creative": "writes",
    "manual": "grows",
    "done": "victory",
}

COMPANION_HINTS: dict[str, str] = {
    "main": "Скоро начнётся новое приключение!",
    "preparing": "Скоро начнётся новое приключение!",
    "walks": "Пора в путь — урок ждёт!",
    "reads": LESSON_STEP_LABELS["video"],
    "reading": LESSON_STEP_LABELS["reading_practice"],
    "emotion": LESSON_STEP_LABELS["emotion_quiz"],
    "writes": LESSON_STEP_LABELS["comprehension_quiz"],
    "dreams": LESSON_STEP_LABELS["tasks"],
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
    urls = {k: slovik_url(k) for k in SLOVIK_FILES}
    for step, img_key in LESSON_STEP_SLOVIK.items():
        urls[step] = slovik_url(img_key)
    return urls


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
) -> str:
    if chest.get("ready"):
        return "victory"

    if not lesson or not lesson.get("url"):
        return "preparing"

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
    if "emotion_quiz" in done:
        return "writes"
    if "lesson_complete" in done:
        return "writes"
    return "reads"


def event_toast_message(
    event_type: str,
    *,
    tale_title: str | None = None,
    current_badges: list[str] | None = None,
) -> str:
    reward = apply_badge_rules(
        event_type,
        list(current_badges or []),
        "Старт",
        tale_title=tale_title,
    )
    pts = reward.get("points") or 0
    badge = reward.get("badge_name")
    if badge and pts:
        return f"+{pts} Словиков · бейдж «{badge}»"
    if pts:
        return f"+{pts} Словиков!"
    if badge:
        return f"Бейдж «{badge}»!"
    return "Отличная работа!"


def lesson_step_key(
    *,
    has_emotion: bool = False,
    has_reading: bool = False,
    has_comprehension: bool,
    has_meaning: bool,
    has_retelling: bool = False,
    video_done: bool = False,
    emotion_done: bool = False,
    reading_done: bool = False,
    comprehension_done: bool = False,
    meaning_done: bool = False,
    retelling_done: bool = False,
) -> str:
    if (
        retelling_done
        or (meaning_done and not has_retelling)
        or (
            video_done
            and not has_emotion
            and not has_reading
            and not has_comprehension
            and not has_meaning
            and not has_retelling
        )
    ):
        return "grows"
    if meaning_done and has_retelling:
        return "retelling"
    if comprehension_done and not has_meaning:
        return "grows"
    if comprehension_done:
        return "dreams"
    if reading_done and has_comprehension:
        return "writes"
    if reading_done:
        return "grows"
    if emotion_done and (has_reading or has_comprehension):
        return "reading" if has_reading else "writes"
    if emotion_done and not has_comprehension:
        return "grows"
    if video_done and has_emotion:
        return "emotion"
    if video_done:
        return "writes"
    return "reads"


def recent_event_slovik(
    events: list[Any],
    *,
    current_badges: list[str] | None = None,
) -> dict[str, Any] | None:
    """Последнее событие для toast в кабинете.

    Уже полученные бейджи не подставляем снова (current_badges → apply_badge_rules).
    Early-квест: сначала бонусные бейджи (Искатель / Слоговик), не только «Читатель».
    """
    if not events:
        return None
    owned = list(current_badges or [])
    owned_set = set(owned)
    ev = events[0]
    et = getattr(ev, "event_type", "") or ""
    tale_title = getattr(ev, "tale_title", None)
    payload = getattr(ev, "payload", None) or {}
    # Early-квест без готового сундука — не празднуем (выход «назад» / недопройдено).
    if et == "lesson_complete" and is_early_quest_title(tale_title):
        if payload.get("chest_ready") is not True:
            return None
    try:
        reward = apply_badge_rules(et, owned, "Старт", tale_title=tale_title)
    except ValueError:
        return None
    # «Читатель» после букв не показываем, даже если в БД бейдж уже ошибочно есть.
    if reward.get("badge_name") == "Читатель" and is_early_letters_title(tale_title):
        reward = {**reward, "badge_name": None}
    badge = reward.get("badge_name")
    pts = int(reward.get("points") or 0)

    # Бонусы early-квеста важнее «Читателя» из EVENT_RULES (иначе всплывает только он).
    # Логика как в check_early_quest_badges — без импорта bonus_badges (тяжёлые зависимости).
    if et == "lesson_complete" and is_early_quest_title(tale_title):
        early_new: list[str] = []
        try:
            sparks = int(payload.get("sparks") or 0) if isinstance(payload, dict) else 0
        except (TypeError, ValueError):
            sparks = 0
        chest_ok = isinstance(payload, dict) and (
            payload.get("chest_ready") is True or sparks >= 3
        )
        if chest_ok:
            if "Искатель искорок" not in owned_set:
                early_new.append("Искатель искорок")
            if is_early_letters_title(tale_title) and "Слоговик" not in owned_set:
                early_new.append("Слоговик")
        if early_new:
            # Слоговик приоритетнее Искателя на уроке букв.
            badge = early_new[-1]
    if not pts and not badge:
        return None
    # Повторный вход: бейдж уже в коллекции — не крутим toast только за старые очки.
    if (
        not badge
        and pts
        and et in ("lesson_complete", "reading_practice")
        and any(b == "Читатель" for b in owned)
    ):
        return None
    key = event_slovik_key(et, big=et in BIG_EVENT_SLOVIK)
    created = getattr(ev, "created_at", None)
    badge_image = None
    if badge:
        filename = BADGE_ASSET_FILES.get(badge)
        if filename:
            badge_image = f"/assets/{filename}"
    msg = event_toast_message(et, tale_title=tale_title, current_badges=owned)
    if badge and badge not in (reward.get("badge_name"), None):
        msg = f"+{pts} Словиков · бейдж «{badge}»" if pts else f"Бейдж «{badge}»!"
    return {
        "key": key,
        "url": slovik_url(key),
        "event_type": et,
        "message": msg,
        "toast_id": f"{et}-{created.isoformat() if created else '0'}-{badge or 'pts'}",
        "points": pts,
        "badge": badge,
        "badge_image": badge_image,
    }
