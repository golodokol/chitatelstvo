"""Календарь открытия уроков (понедельники) и встреч с преподавателем (четверги)."""

from __future__ import annotations

from datetime import date
from typing import Any

from lessons.stages import normalize_stage

_MONTHS_RU = (
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
)

STAGE_1_START = date(2026, 6, 29)
STAGE_2_START = date(2026, 7, 20)

STAGE_1_LESSON_OPENS = (
    date(2026, 6, 29),
    date(2026, 7, 6),
    date(2026, 7, 13),
    date(2026, 7, 20),
)
STAGE_1_MEETINGS = (
    date(2026, 7, 2),
    date(2026, 7, 9),
    date(2026, 7, 16),
    date(2026, 7, 23),
)
STAGE_2_LESSON_OPENS = (
    date(2026, 7, 20),
    date(2026, 7, 27),
    date(2026, 8, 3),
    date(2026, 8, 10),
)
STAGE_2_MEETINGS = (
    date(2026, 7, 23),
    date(2026, 7, 30),
    date(2026, 8, 6),
    date(2026, 8, 13),
)

STAGE_LABELS = {
    "stage-1": "Этап 1 · старт 29 июня",
    "stage-2": "Этап 2 · старт 20 июля",
}


def format_date_ru(d: date, *, weekday: str | None = None) -> str:
    text = f"{d.day} {_MONTHS_RU[d.month - 1]}"
    if weekday:
        return f"{weekday}, {text}"
    return text


def lesson_opens_on(module_week: int) -> date:
    if module_week <= 4:
        return STAGE_1_LESSON_OPENS[module_week - 1]
    return STAGE_2_LESSON_OPENS[module_week - 5]


def meeting_on(module_week: int) -> date:
    if module_week <= 4:
        return STAGE_1_MEETINGS[module_week - 1]
    return STAGE_2_MEETINGS[module_week - 5]


def module_week_for_tale(stage: str | None, tale_number: int) -> int:
    """Неделя модуля (1–8) по этапу и номеру сказки в блоке."""
    from lessons.stages import normalize_stage

    tale = max(1, min(4, int(tale_number)))
    if normalize_stage(stage) == "stage-2":
        return 4 + tale
    return tale


def meeting_date_label(
    module_week: int | None = None,
    *,
    stage: str | None = None,
    tale_number: int | None = None,
    weekday: str | None = None,
    with_year: bool = True,
) -> str:
    """Подпись даты встречи для апселла и страницы заказа."""
    if module_week is None:
        if stage is None or tale_number is None:
            raise ValueError("meeting_date_label needs module_week or stage+tale_number")
        module_week = module_week_for_tale(stage, tale_number)
    meet = meeting_on(module_week)
    text = format_date_ru(meet, weekday=weekday)
    if with_year:
        return f"{text} {meet.year}"
    return text


def week_in_stage(module_week: int) -> int:
    return module_week if module_week <= 4 else module_week - 4


def stage_for_week(module_week: int) -> str:
    return "stage-1" if module_week <= 4 else "stage-2"


def effective_module_week(
    lesson: dict[str, Any],
    enrollment: Any | None,
    module: dict[str, Any] | None,
) -> int:
    week = int(lesson.get("module_week", 1))
    if not module or module.get("tariff_code") != "single" or enrollment is None:
        return week

    stage = normalize_stage(enrollment.chosen_stage)
    tale = int(enrollment.chosen_tale_number or week)
    if stage == "stage-2":
        return 4 + tale
    return tale


def tariff_has_meetings(module: dict[str, Any] | None) -> bool:
    if not module:
        return False
    return module.get("tariff_code") in ("single", "with_teacher")
