"""Данные для игрового личного кабинета ученика (страница /progress)."""

from __future__ import annotations

from typing import Any

from gamification.badge_assets import BADGE_ASSET_FILES
from gamification.rules import LEVELS
from gamification.sloviki import (
    COMPANION_HINTS,
    chest_slovik_key,
    companion_key,
    mission_slovik_key,
    recent_event_slovik,
    slovik_url,
)
from lessons.schedule import STAGE_LABELS
from notifications.russian_morph import name_genitive

# Пороги Словиков для полоски прогресса до следующего уровня (только UI).
LEVEL_SLOVIK_THRESHOLDS = [0, 4, 10, 18, 28]

LEVEL_IMAGES: dict[str, str] = {
    "Старт": "gamify-level-start.png",
    "Юный читатель": "gamify-level-young-reader.png",
    "Исследователь": "gamify-level-explorer.png",
    "Мастер слова": "gamify-level-word-master.png",
    "Литературный детектив": "gamify-level-detective.png",
}

BADGE_IMAGES: dict[str, str] = BADGE_ASSET_FILES

BADGE_CATALOG: list[dict[str, str]] = [
    {"name": "Первый шаг", "condition": "Первое задание в школе"},
    {"name": "Читатель", "condition": "Первая сказка пройдена"},
    {"name": "Слушатель", "condition": "Первая живая встреча"},
    {"name": "Следопыт", "condition": "Точные ответы на вопросы"},
    {"name": "Ловец смысла", "condition": "Понимание смысла сказки"},
    {"name": "Мастер пересказа", "condition": "Хороший пересказ"},
    {"name": "Сказочник", "condition": "Своё творческое задание"},
    {"name": "Исследователь сказки", "condition": "Весь модуль пройден"},
    {"name": "Непрерывная серия", "condition": "3 задания подряд"},
]

CHEST_STEPS = ("lesson_complete", "comprehension")


def _level_index(level_name: str) -> int:
    try:
        return LEVELS.index(level_name)
    except ValueError:
        return 0


def _asset_url(base: str, filename: str | None) -> str | None:
    if not filename:
        return None
    return f"{base.rstrip('/')}/assets/{filename}"


def _level_progress(points: int, level_name: str) -> dict[str, Any]:
    idx = _level_index(level_name)
    if idx >= len(LEVELS) - 1:
        return {
            "pct": 100,
            "remaining": 0,
            "next_level": None,
            "next_level_name": None,
        }
    cur_thr = LEVEL_SLOVIK_THRESHOLDS[idx]
    next_thr = LEVEL_SLOVIK_THRESHOLDS[idx + 1]
    span = max(next_thr - cur_thr, 1)
    in_level = max(0, points - cur_thr)
    pct = min(100, int(in_level / span * 100))
    remaining = max(0, next_thr - points)
    return {
        "pct": pct,
        "remaining": remaining,
        "next_level": idx + 1,
        "next_level_name": LEVELS[idx + 1],
    }


def _events_for_tale(events: list[Any], tale_title: str) -> set[str]:
    title = (tale_title or "").strip()
    if not title:
        return set()
    return {
        e.event_type
        for e in events
        if (e.tale_title or "").strip() == title
    }


def _current_lesson(lesson_links: list[dict]) -> dict | None:
    for les in lesson_links:
        if les.get("url"):
            return les
    for les in lesson_links:
        if les.get("unlocked"):
            return les
    return lesson_links[0] if lesson_links else None


def _chest_state(events: list[Any], lesson: dict | None) -> dict[str, Any]:
    if not lesson:
        return {
            "title": "Сундук Сказки",
            "subtitle": "Когда откроется первая сказка — здесь появится награда.",
            "reward": "новая сказка, секретная наклейка и бонусная страница",
            "steps_total": 2,
            "steps_done": 0,
            "steps_remaining": 2,
            "pct": 0,
            "ready": False,
            "hint": "До открытия 2 шага",
        }

    tale = lesson.get("title", "")
    done = _events_for_tale(events, tale)
    steps_done = sum(1 for s in CHEST_STEPS if s in done)
    steps_total = len(CHEST_STEPS)
    steps_remaining = max(0, steps_total - steps_done)
    pct = int(steps_done / steps_total * 100) if steps_total else 0
    ready = steps_remaining == 0

    if ready:
        hint = "Сундук готов — можно открывать!"
    elif steps_remaining == 1:
        hint = "До открытия осталось 1 задание"
    else:
        hint = f"До открытия осталось {steps_remaining} задания"

    return {
        "title": "Сундук Сказки",
        "subtitle": (
            "Откроется после завершения сегодняшнего урока и мини-задания."
        ),
        "reward": "новая сказка, секретная наклейка и бонусная страница",
        "steps_total": steps_total,
        "steps_done": steps_done,
        "steps_remaining": steps_remaining,
        "pct": pct,
        "ready": ready,
        "hint": hint,
    }


def _missions(events: list[Any], lesson: dict | None, points: int, chest: dict) -> list[dict]:
    tale = (lesson or {}).get("title", "")
    done = _events_for_tale(events, tale)

    def status(key: str) -> str:
        if key in done:
            return "done"
        if lesson and lesson.get("url"):
            return "active"
        return "locked"

    chest_ready = bool(chest.get("ready"))
    items = [
        {
            "id": "read",
            "text": "Прочитать и посмотреть сказку",
            "status": status("lesson_complete"),
        },
        {
            "id": "quiz",
            "text": "Ответить на 3 вопроса",
            "status": status("comprehension"),
        },
        {
            "id": "points",
            "text": "Собрать 10 Словиков",
            "status": "done" if points >= 10 else "active",
        },
        {
            "id": "chest",
            "text": "Открыть сундук",
            "status": "done" if chest_ready else "active",
        },
        {
            "id": "secret",
            "text": "Найти секретный знак в сказке",
            "status": status("meaning_analysis"),
        },
    ]
    for item in items:
        key = mission_slovik_key(
            item["id"],
            chest_ready=chest_ready and item["id"] == "chest",
        )
        item["slovik_key"] = key
        item["slovik_url"] = slovik_url(key)
    return items


def _collection(events: list[Any], earned_badges: list[str], points: int) -> dict[str, Any]:
    tales = {
        (e.tale_title or "").strip()
        for e in events
        if e.event_type == "lesson_complete" and (e.tale_title or "").strip()
    }
    secrets = sum(1 for e in events if e.event_type == "meaning_analysis")
    return {
        "stories_count": len(tales),
        "stories_preview": sorted(tales)[:4],
        "badges_count": len(earned_badges),
        "points": points,
        "secrets_count": secrets,
        "cards_count": len(earned_badges) + len(tales),
    }


def _parent_summary(
    child_name: str,
    level: str,
    points: int,
    badges_count: int,
    chest: dict,
    lesson: dict | None,
    events: list[Any],
) -> dict[str, str]:
    skill = "понимание текста и поиск смысла в сказке"
    if level in ("Мастер слова", "Литературный детектив"):
        skill = "пересказ, творчество и глубокое чтение"
    elif level == "Исследователь":
        skill = "внимательное чтение и анализ смысла"

    completed = sum(1 for e in events if e.event_type == "lesson_complete")
    lesson_line = lesson["title"] if lesson else "скоро откроется первая сказка"

    return {
        "completed_lessons": str(completed),
        "skill": skill,
        "points": str(points),
        "chest_hint": chest.get("hint", ""),
        "chest_ready": "да, можно открыть" if chest.get("ready") else chest.get("hint", ""),
        "support_tip": (
            f"Сегодня у {name_genitive(child_name)} урок «{lesson_line}». "
            "Можно пройти частями — главное, без спешки и с интересом."
        ),
        "badges_count": str(badges_count),
        "current_lesson": lesson_line,
        "level": level,
    }


def _story_stages(lesson_links: list[dict]) -> list[dict]:
    if not lesson_links:
        return []
    by_stage: dict[str, list[dict]] = {}
    for les in lesson_links:
        stage = les.get("stage") or "stage-1"
        by_stage.setdefault(stage, []).append(les)
    stages: list[dict] = []
    for stage_key in ("stage-1", "stage-2"):
        items = by_stage.get(stage_key)
        if not items:
            continue
        stages.append(
            {
                "key": stage_key,
                "label": STAGE_LABELS.get(stage_key, stage_key),
                "lessons": items,
            }
        )
    return stages


def build_child_cabinet(
    *,
    name: str,
    level: str,
    points: int,
    earned_badges: list[str],
    events: list[Any],
    lesson_links: list[dict],
    assets_base: str,
) -> dict[str, Any]:
    """Собирает контекст игрового кабинета для одного ребёнка."""
    earned_set = set(earned_badges)
    lvl_idx = _level_index(level)
    progress = _level_progress(points, level)
    lesson = _current_lesson(lesson_links)
    chest = _chest_state(events, lesson)

    levels_ui = []
    for i, lvl_name in enumerate(LEVELS):
        if i < lvl_idx:
            st = "done"
        elif i == lvl_idx:
            st = "current"
        elif i == lvl_idx + 1:
            st = "next"
        else:
            st = "locked"
        thr = LEVEL_SLOVIK_THRESHOLDS[i] if i < len(LEVEL_SLOVIK_THRESHOLDS) else 0
        levels_ui.append(
            {
                "name": lvl_name,
                "status": st,
                "image": _asset_url(assets_base, LEVEL_IMAGES.get(lvl_name)),
                "threshold": thr,
                "points_to_unlock": max(0, thr - points) if st == "next" else 0,
            }
        )

    badges_ui = []
    next_badge = None
    for badge in BADGE_CATALOG:
        earned = badge["name"] in earned_set
        if not earned and next_badge is None:
            next_badge = badge["name"]
        badges_ui.append(
            {
                "name": badge["name"],
                "condition": badge["condition"],
                "earned": earned,
                "image": _asset_url(assets_base, BADGE_IMAGES.get(badge["name"])),
                "status": "earned" if earned else ("next" if badge["name"] == next_badge else "locked"),
            }
        )

    daily = None
    if lesson:
        reward_pts = 15
        daily = {
            "title": lesson.get("title", "Урок дня"),
            "goal": "За 10 минут узнаешь, как найти главную мысль сказки.",
            "duration": "≈ 10 мин",
            "reward_pts": reward_pts,
            "url": lesson.get("url"),
            "unlocked": bool(lesson.get("url")),
            "opens_on_label": lesson.get("opens_on_label"),
            "cover_url": lesson.get("cover_url"),
            "cover_state": lesson.get("cover_state", "locked"),
            "week_in_stage": lesson.get("week_in_stage"),
        }

    chest["slovik_key"] = chest_slovik_key(chest)
    chest["slovik_url"] = slovik_url(chest["slovik_key"])

    collection = _collection(events, earned_badges, points)
    missions = _missions(events, lesson, points, chest)
    parent = _parent_summary(name, level, points, len(earned_badges), chest, lesson, events)

    secret_unlocked = len(earned_badges) >= 3 or points >= 15
    secret_slovik_key = "victory" if secret_unlocked else "dreams"

    companion_k = companion_key(
        events,
        lesson,
        chest,
        secret_unlocked=secret_unlocked,
    )
    companion = {
        "key": companion_k,
        "url": slovik_url(companion_k),
        "hint": COMPANION_HINTS.get(companion_k, COMPANION_HINTS["main"]),
    }

    story_stages = _story_stages(lesson_links)

    continue_url = lesson.get("url") if lesson and lesson.get("url") else None
    recent_toast = recent_event_slovik(events)

    return {
        "name": name,
        "level": level,
        "level_image": _asset_url(assets_base, LEVEL_IMAGES.get(level)),
        "points": points,
        "points_label": "Словиков",
        "progress_pct": progress["pct"],
        "points_to_next": progress["remaining"],
        "next_level_name": progress["next_level_name"],
        "levels": levels_ui,
        "badges": badges_ui,
        "badges_earned_count": len(earned_badges),
        "chest": chest,
        "daily_lesson": daily,
        "story_stages": story_stages,
        "missions": missions,
        "collection": collection,
        "parent": parent,
        "secret_unlocked": secret_unlocked,
        "secret_slovik_url": slovik_url(secret_slovik_key),
        "companion": companion,
        "recent_toast": recent_toast,
        "continue_url": continue_url,
        "slovik_main_url": slovik_url("main"),
    }
