"""Дополнительные бейджи по прогрессу (не привязаны к одному событию)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from db import repository as repo
from gamification.rules import LEVELS

TALE_TRAVELER_BADGE = "Путешественник по сказке"
TALE_TRAVELER_MIN_TALES = 4
TALE_TRAVELER_LEVEL = "Литературный детектив"


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


def bonus_badges_for_event(
    db: Session,
    *,
    child_id: uuid.UUID,
    child_name: str,
    current_level: str,
    current_badges: list[str],
    event_type: str,
    tale_title: str | None,
) -> list[BonusBadgeGrant]:
    grant = check_tale_traveler_badge(
        db,
        child_id=child_id,
        child_name=child_name,
        current_level=current_level,
        current_badges=current_badges,
        event_type=event_type,
        tale_title=tale_title,
    )
    return [grant] if grant else []
