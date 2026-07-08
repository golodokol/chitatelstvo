"""Автовыдача бейджа «Непрерывная серия» за 3 календарных дня активности подряд."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from db import repository as repo
from db.models import Event
from services.events import submit_learning_event

STREAK_BADGE = "Непрерывная серия"
STREAK_DAYS_REQUIRED = 3

STREAK_META_EVENTS = frozenset({"streak_3", "streak_5"})

ACTIVITY_EVENT_TYPES = frozenset(
    {
        "first_task",
        "video_unlock",
        "lesson_complete",
        "emotion_quiz",
        "comprehension",
        "meaning_analysis",
        "retelling",
        "creative_task",
        "live_meeting",
        "initiative",
        "mini_check",
    }
)


def _event_activity_date(event: Event) -> date | None:
    if event.lesson_date:
        return event.lesson_date
    if event.processed_at:
        return event.processed_at.date()
    if event.created_at:
        return event.created_at.date()
    return None


def activity_dates_for_child(db: Session, child_id: uuid.UUID) -> set[date]:
    stmt = (
        select(Event)
        .where(
            Event.child_id == child_id,
            Event.status == "done",
            Event.event_type.in_(ACTIVITY_EVENT_TYPES),
        )
    )
    dates: set[date] = set()
    for event in db.scalars(stmt):
        day = _event_activity_date(event)
        if day:
            dates.add(day)
    return dates


def consecutive_activity_days(dates: set[date], *, ending: date) -> int:
    count = 0
    day = ending
    while day in dates:
        count += 1
        day -= timedelta(days=1)
    return count


def maybe_award_streak_3(
    db: Session,
    *,
    child_id: uuid.UUID,
    activity_date: date | None = None,
) -> tuple[str, uuid.UUID | None] | None:
    """Создаёт streak_3, если 3 дня подряд с активностью и бейдж ещё не выдан."""
    child = repo.get_child_with_family(db, child_id)
    if not child:
        return None

    badge_names = {badge.badge_name for badge in child.badges}
    if STREAK_BADGE in badge_names:
        return None

    existing = db.scalars(
        select(Event.id)
        .where(
            Event.child_id == child_id,
            Event.event_type == "streak_3",
            Event.status == "done",
        )
        .limit(1)
    ).first()
    if existing:
        return None

    today = activity_date or date.today()
    dates = activity_dates_for_child(db, child_id)
    dates.add(today)

    if consecutive_activity_days(dates, ending=today) < STREAK_DAYS_REQUIRED:
        return None

    return submit_learning_event(
        db,
        child_id=child_id,
        event_type="streak_3",
        tale_title="",
        lesson_date=today,
        notes="auto: 3 activity days in a row",
        payload={"source": "streak_badges", "days": STREAK_DAYS_REQUIRED},
    )
