"""Доступ к урокам по неделям модуля."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from config.settings import MODULE_START_DATE
from db.models import Child, Enrollment
from lessons.schedule import (
    COHORT_GROUPS,
    LEGACY_MODULE_START,
    STANDARD_GRADE_GROUPS,
    cohort_lesson_opens_on,
    effective_module_week,
    format_date_ru,
    lesson_opens_on,
    meeting_on,
    stage_for_week,
    tariff_has_meetings,
    weekday_ru,
    week_in_stage,
)

# Дата выката нового календаря; legacy-недели только для cohort/early, не для 1–4 и внеклассного.
SCHEDULE_SHIFT_DATE = date(2026, 7, 10)

EARLY_GROUPS = frozenset({"early-letters", "early-stories"})
EARLY_MODULE_START = date(2026, 9, 1)  # вторник


def early_lesson_opens_on(module_week: int) -> date:
    """Открытие уроков early-модуля: вт / чт / вт / чт …

    1 → 1 сен, 2 → 3 сен, 3 → 8 сен, 4 → 10 сен и далее.
    """
    week = max(1, int(module_week or 1))
    pair = (week - 1) // 2
    day_in_pair = 0 if week % 2 == 1 else 2  # вт = +0, чт = +2
    return EARLY_MODULE_START + timedelta(days=7 * pair + day_in_pair)


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


def _as_date(value: date | datetime | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value


def _grandfather_schedule_unlock(child: Child, enrollment: Enrollment | None) -> bool:
    """
    Сохранить доступ по старому старту (6 июля) для ранних записей и досрочного доступа.
    Новые записи после переноса дат идут только по новому календарю.
    """
    if (child.module_week or 1) > 1 or (child.bonus_unlock_weeks or 0) > 0:
        return True
    child_created = _as_date(child.created_at)
    if child_created and child_created <= SCHEDULE_SHIFT_DATE:
        return True
    if enrollment:
        enrolled = _as_date(enrollment.created_at)
        if enrolled and enrolled <= SCHEDULE_SHIFT_DATE:
            return True
    return False


def _legacy_unlocked_weeks(
    child: Child,
    *,
    week_days: int = 7,
    cohort_start: date | None = None,
) -> int:
    return unlocked_week_number(
        child,
        week_days=week_days,
        cohort_start=LEGACY_MODULE_START if cohort_start is None else cohort_start,
    )


def is_lesson_unlocked(
    child: Child,
    lesson: dict[str, Any],
    *,
    week_days: int = 7,
    cohort_start: date | None = None,
    enrollment: Enrollment | None = None,
    module: dict[str, Any] | None = None,
) -> bool:
    # Бесплатный пробный early — сразу
    if lesson.get("tariff_code") == "trial" or (module and module.get("tariff_code") == "trial"):
        return True

    lesson_week = effective_module_week(lesson, enrollment, module)
    today = date.today()

    group_code = (lesson.get("group_code") or (module or {}).get("group_code") or "")
    if group_code in EARLY_GROUPS:
        if today >= early_lesson_opens_on(lesson_week):
            return True
        admin_weeks = _admin_unlocked_weeks(child)
        return admin_weeks > 0 and lesson_week <= admin_weeks

    if group_code in COHORT_GROUPS:
        if today >= cohort_lesson_opens_on(group_code, lesson_week):
            return True
        admin_weeks = _admin_unlocked_weeks(child)
        return admin_weeks > 0 and lesson_week <= admin_weeks

    if today >= lesson_opens_on(lesson_week, group_code=group_code):
        return True

    admin_weeks = _admin_unlocked_weeks(child)
    if admin_weeks > 0 and lesson_week <= admin_weeks:
        return True

    # Школьные и внеклассные курсы — только календарь и ручной доступ админа.
    if group_code in STANDARD_GRADE_GROUPS:
        return False

    if _grandfather_schedule_unlock(child, enrollment):
        legacy_weeks = _legacy_unlocked_weeks(
            child, week_days=week_days, cohort_start=cohort_start
        )
        if lesson_week <= legacy_weeks:
            return True

    return False


def unlock_date_for_week(
    child: Child,
    week: int,
    *,
    week_days: int = 7,
    cohort_start: date | None = None,
    group_code: str | None = None,
) -> date:
    """Календарная дата открытия недели."""
    if group_code in EARLY_GROUPS:
        return early_lesson_opens_on(week)
    if group_code in COHORT_GROUPS:
        return cohort_lesson_opens_on(group_code, week)
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
    group_code = (module or {}).get("group_code") or lesson.get("group_code")
    if group_code in EARLY_GROUPS:
        opens = early_lesson_opens_on(week)
        info: dict[str, Any] = {
            "module_week": week,
            "week_in_stage": week,
            "stage": "stage-1",
            "unlocked": unlocked,
            "opens_on": opens.strftime("%d.%m.%Y"),
            "opens_on_label": format_date_ru(opens, weekday=weekday_ru(opens)),
            "opens_on_iso": opens.isoformat(),
        }
    elif group_code in COHORT_GROUPS:
        opens = cohort_lesson_opens_on(group_code, week)
        info = {
            "module_week": week,
            "week_in_stage": week,
            "stage": "stage-1",
            "unlocked": unlocked,
            "opens_on": opens.strftime("%d.%m.%Y"),
            "opens_on_label": format_date_ru(opens, weekday=weekday_ru(opens)),
            "opens_on_iso": opens.isoformat(),
        }
    else:
        opens = lesson_opens_on(week, group_code=group_code)
        info = {
            "module_week": week,
            "week_in_stage": week_in_stage(week),
            "stage": stage_for_week(week),
            "unlocked": unlocked,
            "opens_on": opens.strftime("%d.%m.%Y"),
            "opens_on_label": format_date_ru(opens, weekday=weekday_ru(opens)),
            "opens_on_iso": opens.isoformat(),
        }
    if tariff_has_meetings(module):
        meet = meeting_on(week, group_code=group_code)
        info["meeting_on"] = meet.strftime("%d.%m.%Y")
        info["meeting_on_label"] = format_date_ru(meet, weekday="четверг")
    return info
