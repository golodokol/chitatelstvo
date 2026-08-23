"""Дополнительные бейджи по прогрессу (не привязаны к одному событию)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from db import repository as repo
from gamification.rules import (
    LEVELS,
    is_early_letters_title,
    is_early_quest_title,
    is_early_stories_title,
)
from gamification.streak_badges import STREAK_META_EVENTS

FIRST_STEP_BADGE = "Первый шаг"
TALE_TRAVELER_BADGE = "Путешественник по сказке"
TALE_TRAVELER_MIN_TALES = 4
TALE_TRAVELER_LEVEL = "Литературный детектив"

# Пробные early-бейджи (реальная запись в БД + soft в кабинете)
SPARK_HUNTER_BADGE = "Искатель искорок"
CHEST_KEEPER_BADGE = "Хранитель сундука"
SYLLABLE_BADGE = "Слоговик"

# Любая учебная активность = «уже сделал первый шаг в школе»
FIRST_STEP_EVENT_TYPES = frozenset(
    {
        "first_task",
        "video_unlock",
        "lesson_complete",
        "emotion_quiz",
        "reading_practice",
        "comprehension",
        "meaning_analysis",
        "retelling",
        "creative_task",
        "live_meeting",
    }
)


@dataclass(frozen=True)
class BonusBadgeGrant:
    badge_name: str
    level_change: str | None
    child_message: str
    parent_message: str


def _level_upgrade(current_level: str, target: str | None) -> str | None:
    if not target:
        return None
    try:
        if LEVELS.index(target) > LEVELS.index(current_level):
            return target
    except ValueError:
        return None
    return None


def check_first_step_badge(
    *,
    child_name: str,
    current_badges: list[str],
    event_type: str,
) -> BonusBadgeGrant | None:
    """Бейдж «Первый шаг» за первую учебную активность (раньше first_task почти не слали)."""
    if FIRST_STEP_BADGE in current_badges:
        return None
    if event_type in STREAK_META_EVENTS:
        return None
    if event_type not in FIRST_STEP_EVENT_TYPES:
        return None
    name = child_name.strip() or "Читатель"
    return BonusBadgeGrant(
        badge_name=FIRST_STEP_BADGE,
        level_change=None,
        child_message=f"{name}, отличный старт — бейдж «{FIRST_STEP_BADGE}» твой!",
        parent_message=f"{name} сделал(а) первый шаг в школе — бейдж «{FIRST_STEP_BADGE}».",
    )


def check_tale_traveler_badge(
    db: Session,
    *,
    child_id: uuid.UUID,
    child_name: str,
    current_level: str,
    current_badges: list[str],
    event_type: str,
    tale_title: str | None,
) -> BonusBadgeGrant | None:
    """Бейдж за 4 разные пройденные сказки модуля (lesson_complete)."""
    if TALE_TRAVELER_BADGE in current_badges:
        return None
    if event_type != "lesson_complete":
        return None

    tale = (tale_title or "").strip()
    if not tale:
        return None

    tales_count = repo.count_distinct_completed_tales(db, child_id, extra_tale=tale)
    if tales_count < TALE_TRAVELER_MIN_TALES:
        return None

    name = child_name.strip() or "Читатель"
    level_change = _level_upgrade(current_level, TALE_TRAVELER_LEVEL)
    return BonusBadgeGrant(
        badge_name=TALE_TRAVELER_BADGE,
        level_change=level_change,
        child_message=(
            f"{name}, ты прошёл(а) все сказки модуля — "
            f"бейдж «{TALE_TRAVELER_BADGE}» твой!"
        ),
        parent_message=(
            f"{name} прошёл(а) уже {tales_count} разные сказки модуля — "
            f"бейдж «{TALE_TRAVELER_BADGE}»."
        ),
    )


def check_early_quest_badges(
    *,
    child_name: str,
    current_badges: list[str],
    event_type: str,
    tale_title: str | None,
    payload: dict | None = None,
) -> list[BonusBadgeGrant]:
    """Искорки / слоговик после early-квеста; Читатель — только после истории."""
    if event_type != "lesson_complete":
        return []
    if not is_early_quest_title(tale_title):
        return []

    data = payload or {}
    chest_ready = data.get("chest_ready") is True
    try:
        sparks = int(data.get("sparks") or 0)
    except (TypeError, ValueError):
        sparks = 0
    if not chest_ready and sparks < 3:
        return []

    name = child_name.strip() or "Читатель"
    grants: list[BonusBadgeGrant] = []
    owned = set(current_badges)

    if SPARK_HUNTER_BADGE not in owned:
        grants.append(
            BonusBadgeGrant(
                badge_name=SPARK_HUNTER_BADGE,
                level_change=None,
                child_message=f"{name}, ты собрал(а) все искорки — бейдж «{SPARK_HUNTER_BADGE}»!",
                parent_message=f"{name} собрал(а) все искорки квеста — бейдж «{SPARK_HUNTER_BADGE}».",
            )
        )
        owned.add(SPARK_HUNTER_BADGE)

    if is_early_letters_title(tale_title) and SYLLABLE_BADGE not in owned:
        grants.append(
            BonusBadgeGrant(
                badge_name=SYLLABLE_BADGE,
                level_change=None,
                child_message=f"{name}, слог прочитан — бейдж «{SYLLABLE_BADGE}» твой!",
                parent_message=f"{name} прочитал(а) слог в квесте «Буквы» — бейдж «{SYLLABLE_BADGE}».",
            )
        )

    return grants


def check_chest_keeper_badge(
    *,
    child_name: str,
    current_badges: list[str],
    tale_title: str | None = None,
) -> BonusBadgeGrant | None:
    """Бейдж «Хранитель сундука» при открытии сундука early-урока."""
    if CHEST_KEEPER_BADGE in current_badges:
        return None
    if tale_title and not (
        is_early_quest_title(tale_title)
        or is_early_letters_title(tale_title)
        or is_early_stories_title(tale_title)
    ):
        return None
    name = child_name.strip() or "Читатель"
    return BonusBadgeGrant(
        badge_name=CHEST_KEEPER_BADGE,
        level_change=None,
        child_message=f"{name}, сундук открыт — бейдж «{CHEST_KEEPER_BADGE}»!",
        parent_message=f"{name} открыл(а) сундук урока — бейдж «{CHEST_KEEPER_BADGE}».",
    )


def bonus_badges_for_event(
    db: Session,
    *,
    child_id: uuid.UUID,
    child_name: str,
    current_level: str,
    current_badges: list[str],
    event_type: str,
    tale_title: str | None,
    payload: dict | None = None,
) -> list[BonusBadgeGrant]:
    grants: list[BonusBadgeGrant] = []
    first = check_first_step_badge(
        child_name=child_name,
        current_badges=current_badges,
        event_type=event_type,
    )
    if first:
        grants.append(first)
        current_badges = [*current_badges, first.badge_name]
    for early in check_early_quest_badges(
        child_name=child_name,
        current_badges=current_badges,
        event_type=event_type,
        tale_title=tale_title,
        payload=payload,
    ):
        grants.append(early)
        current_badges = [*current_badges, early.badge_name]
    traveler = check_tale_traveler_badge(
        db,
        child_id=child_id,
        child_name=child_name,
        current_level=current_level,
        current_badges=current_badges,
        event_type=event_type,
        tale_title=tale_title,
    )
    if traveler:
        grants.append(traveler)
    return grants
