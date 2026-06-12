"""Доступ к урокам по неделям модуля."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from config.settings import MODULE_START_DATE
from db.models import Child


def _registration_date(child: Child) -> date:
    if child.created_at:
        if isinstance(child.created_at, datetime):
            return child.created_at.date()
        return child.created_at
    return date.today()


def monday_on_or_before(d: date) -> date:
    """Понедельник той же недели (или сам день, если понедельник)."""
    return d - timedelta(days=d.weekday())


def module_start_date(child: Child, *, cohort_start: date | None = None) -> date:
    """
    День начала модуля.
    Приоритет: MODULE_START_DATE в .env (общий понедельник для всех),
    иначе — понедельник недели регистрации ребёнка.
    """
    if cohort_start is not None:
        return cohort_start
    if MODULE_START_DATE is not None:
        return MODULE_START_DATE
    return monday_on_or_before(_registration_date(child))


def unlocked_week_number(
    child: Child,
    *,
    week_days: int = 7,
    cohort_start: date | None = None,
) -> int:
    """
    Сколько недель модуля открыто.
    Авто: +1 неделя каждые week_days от старта модуля.
    child.module_week > 1 — досрочное открытие админом.
    """
    start = module_start_date(child, cohort_start=cohort_start)
    today = date.today()

    if today < start:
        auto_week = 0
    else:
        elapsed_days = (today - start).days
        auto_week = 1 + elapsed_days // week_days

    manual_week = child.module_week or 1
    if manual_week > 1:
        return max(auto_week, manual_week)
    return auto_week


def is_lesson_unlocked(
    child: Child,
    lesson: dict[str, Any],
    *,
    week_days: int = 7,
    cohort_start: date | None = None,
) -> bool:
    lesson_week = int(lesson.get("module_week", 1))
    return lesson_week <= unlocked_week_number(child, week_days=week_days, cohort_start=cohort_start)


def unlock_date_for_week(
    child: Child,
    week: int,
    *,
    week_days: int = 7,
    cohort_start: date | None = None,
) -> date:
    """Календарная дата открытия недели (week=1 → понедельник старта)."""
    start = module_start_date(child, cohort_start=cohort_start)
    return start + timedelta(days=(week - 1) * week_days)


def lesson_access_info(
    child: Child,
    lesson: dict[str, Any],
    *,
    week_days: int = 7,
    cohort_start: date | None = None,
) -> dict[str, Any]:
    week = int(lesson.get("module_week", 1))
    unlocked = is_lesson_unlocked(child, lesson, week_days=week_days, cohort_start=cohort_start)
    opens_on = unlock_date_for_week(child, week, week_days=week_days, cohort_start=cohort_start)
    return {
        "module_week": week,
        "unlocked": unlocked,
        "opens_on": opens_on.strftime("%d.%m.%Y"),
        "opens_on_iso": opens_on.isoformat(),
    }
