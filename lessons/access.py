"""Доступ к урокам по неделям модуля."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from config.settings import MODULE_START_DATE
from db.models import Child, Enrollment
from lessons.schedule import (
    effective_module_week,
    format_date_ru,
    lesson_opens_on,
    meeting_on,
    stage_for_week,
    tariff_has_meetings,
    weekday_ru,
    week_in_stage,
)


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
        unlocked = max(auto_week, manual_week)
    else:
        unlocked = auto_week
    bonus = child.bonus_unlock_weeks or 0
    return unlocked + bonus if bonus > 0 else unlocked


def _admin_unlocked_weeks(child: Child) -> int:
    """Досрочный доступ из админки (module_week / bonus_unlock_weeks)."""
    manual_week = child.module_week or 1
    bonus = child.bonus_unlock_weeks or 0
    if manual_week <= 1 and bonus <= 0:
        return 0
    if bonus > 0:
        return manual_week + bonus
    return manual_week


def is_lesson_unlocked(
    child: Child,
    lesson: dict[str, Any],
    *,
    week_days: int = 7,
    cohort_start: date | None = None,
    enrollment: Enrollment | None = None,
    module: dict[str, Any] | None = None,
) -> bool:
    lesson_week = effective_module_week(lesson, enrollment, module)
    today = date.today()

    if today >= lesson_opens_on(lesson_week):
        return True

    admin_weeks = _admin_unlocked_weeks(child)
    if admin_weeks > 0 and lesson_week <= admin_weeks:
        return True

    return False


def unlock_date_for_week(
    child: Child,
    week: int,
    *,
    week_days: int = 7,
    cohort_start: date | None = None,
) -> date:
    """Календарная дата открытия недели из lessons/schedule.py."""
    return lesson_opens_on(week)


def lesson_access_info(
    child: Child,
    lesson: dict[str, Any],
    *,
    week_days: int = 7,
    cohort_start: date | None = None,
    enrollment: Enrollment | None = None,
    module: dict[str, Any] | None = None,
) -> dict[str, Any]:
    week = effective_module_week(lesson, enrollment, module)
    lesson_for_unlock = {**lesson, "module_week": week}
    unlocked = is_lesson_unlocked(
        child,
        lesson_for_unlock,
        week_days=week_days,
        cohort_start=cohort_start,
        enrollment=enrollment,
        module=module,
    )
    opens = lesson_opens_on(week)
    info: dict[str, Any] = {
        "module_week": week,
        "week_in_stage": week_in_stage(week),
        "stage": stage_for_week(week),
        "unlocked": unlocked,
        "opens_on": opens.strftime("%d.%m.%Y"),
        "opens_on_label": format_date_ru(opens, weekday=weekday_ru(opens)),
        "opens_on_iso": opens.isoformat(),
    }
    if tariff_has_meetings(module):
        meet = meeting_on(week)
        info["meeting_on"] = meet.strftime("%d.%m.%Y")
        info["meeting_on_label"] = format_date_ru(meet, weekday="четверг")
    return info
