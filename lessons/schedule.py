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

STAGE_1_START = date(2026, 7, 15)
STAGE_2_START = date(2026, 9, 7)
# Старт до переноса (+1 неделя); для сохранения доступа ранним ученикам.
LEGACY_MODULE_START = date(2026, 7, 6)

# 1–4 класс и внеклассное чтение: уроки 1–2 открыты, 3–4 — 31 авг, 5–6 — 7 сен, 7–8 — 14 сен.
STAGE_1_LESSON_OPENS = (
    date(2026, 7, 15),
    date(2026, 8, 3),
    date(2026, 8, 31),
    date(2026, 8, 31),
)
STAGE_1_MEETINGS = (
    date(2026, 7, 16),
    date(2026, 7, 23),
    date(2026, 7, 30),
    date(2026, 8, 6),
)
STAGE_2_LESSON_OPENS = (
    date(2026, 9, 7),
    date(2026, 9, 7),
    date(2026, 9, 14),
    date(2026, 9, 14),
)
STAGE_2_MEETINGS = (
    date(2026, 9, 10),
    date(2026, 9, 17),
    date(2026, 9, 24),
    date(2026, 10, 1),
)

# Исключение: «Рони» (внеклассное 9–11, этап 1, сказка 2).
RONI_LESSON_OPEN = date(2026, 8, 27)

STANDARD_GRADE_GROUPS = frozenset({
    "grade-1", "grade-2", "grade-3", "grade-4", "extra-6-8", "extra-9-11",
})

# Early-курсы (Буквы оживают / Первые истории), модуль 1 — встречи по четвергам
EARLY_GROUPS = frozenset({"early-letters", "early-stories"})
COHORT_GROUPS = frozenset({"wind", "garden", "rus-6-9", "rus-10-12"})
SLOW_READING_GROUPS = frozenset({"wind", "garden"})
RUSSIAN_TALES_GROUPS = frozenset({"rus-6-9", "rus-10-12"})

# Медленное чтение: старт 15 сентября, далее по вторникам.
SLOW_READING_LESSON_OPENS = (
    date(2026, 9, 15),
    date(2026, 9, 22),
    date(2026, 9, 29),
    date(2026, 10, 6),
)
SLOW_READING_MEETINGS = (
    date(2026, 9, 18),
    date(2026, 9, 25),
    date(2026, 10, 2),
    date(2026, 10, 9),
)

# Русские сказки: 15, 20, 27 октября и 3, 10 ноября (4 урока).
RUSSIAN_TALES_LESSON_OPENS = (
    date(2026, 10, 15),
    date(2026, 10, 20),
    date(2026, 10, 27),
    date(2026, 11, 10),
)
RUSSIAN_TALES_MEETINGS = (
    date(2026, 10, 15),
    date(2026, 10, 23),
    date(2026, 10, 30),
    date(2026, 11, 13),
)
EARLY_MEETINGS = (
    date(2026, 9, 3),
    date(2026, 9, 10),
    date(2026, 9, 17),
    date(2026, 9, 24),
)

STAGE_LABELS = {
    "stage-1": "Этап 1 · сказки 1–4",
    "stage-2": "Этап 2 · сказки 5–8",
}

_WEEKDAYS_RU = (
    "понедельник",
    "вторник",
    "среда",
    "четверг",
    "пятница",
    "суббота",
    "воскресенье",
)


def weekday_ru(d: date) -> str:
    return _WEEKDAYS_RU[d.weekday()]


def format_date_ru(d: date, *, weekday: str | None = None) -> str:
    text = f"{d.day} {_MONTHS_RU[d.month - 1]}"
    if weekday:
        return f"{weekday}, {text}"
    return text


def lesson_opens_on(module_week: int, *, group_code: str | None = None) -> date:
    week = max(1, int(module_week or 1))
    if group_code in SLOW_READING_GROUPS:
        return SLOW_READING_LESSON_OPENS[min(3, week - 1)]
    if group_code in RUSSIAN_TALES_GROUPS:
        return RUSSIAN_TALES_LESSON_OPENS[min(3, week - 1)]
    if group_code == "extra-9-11" and week == 2:
        return RONI_LESSON_OPEN
    if week <= 4:
        return STAGE_1_LESSON_OPENS[week - 1]
    return STAGE_2_LESSON_OPENS[week - 5]


def cohort_lesson_opens_on(group_code: str, module_week: int) -> date:
    return lesson_opens_on(module_week, group_code=group_code)


def meeting_on(module_week: int, *, group_code: str | None = None) -> date:
    week = int(module_week)
    if group_code in EARLY_GROUPS:
        # 4 встречи на модуль: недели 1–2 → 3 сен, 3–4 → 10 сен, …
        idx = min(3, max(0, (max(1, week) - 1) // 2))
        return EARLY_MEETINGS[idx]
    if group_code in SLOW_READING_GROUPS:
        return SLOW_READING_MEETINGS[min(3, max(0, week - 1))]
    if group_code in RUSSIAN_TALES_GROUPS:
        return RUSSIAN_TALES_MEETINGS[min(3, max(0, week - 1))]
    if week <= 4:
        return STAGE_1_MEETINGS[week - 1]
    return STAGE_2_MEETINGS[week - 5]


def early_meeting_labels(*, weekday: str = "четверг", with_year: bool = True) -> list[str]:
    labels: list[str] = []
    for meet in EARLY_MEETINGS:
        text = format_date_ru(meet, weekday=weekday)
        labels.append(f"{text} {meet.year}" if with_year else text)
    return labels


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
    group_code: str | None = None,
) -> str:
    """Подпись даты встречи для апселла и страницы заказа."""
    if module_week is None:
        if stage is None or tale_number is None:
            raise ValueError("meeting_date_label needs module_week or stage+tale_number")
        module_week = module_week_for_tale(stage, tale_number)
    meet = meeting_on(module_week, group_code=group_code)
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
    # Разовое — только онлайн; живые встречи входят в тариф with_teacher
    # или докупаются отдельно (meeting_addon), пока дата встречи не прошла.
    return module.get("tariff_code") == "with_teacher"


def meeting_still_bookable(
    *,
    stage: str | None = None,
    tale_number: int | None = None,
    module_week: int | None = None,
    today: date | None = None,
    group_code: str | None = None,
) -> bool:
    """Можно ли ещё докупить встречу (дата встречи строго в будущем).

    Поток 15 июля (этап 1): живых встреч нет — докупка закрыта.
    Встречи снова доступны со старта 15 августа (этап 2).
    Early: 4 встречи в сентябре — докупка, пока дата встречи в будущем.
    """
    if module_week is None:
        if stage is None or tale_number is None:
            return False
        module_week = module_week_for_tale(stage, tale_number)
    week = int(module_week)
    if group_code in STANDARD_GRADE_GROUPS:
        return False
    if group_code in EARLY_GROUPS:
        meet = meeting_on(week, group_code=group_code)
        return meet > (today or date.today())
    if group_code in COHORT_GROUPS:
        meet = meeting_on(week, group_code=group_code)
        return meet > (today or date.today())
    if week <= 4:
        return False
    meet = meeting_on(week)
    return meet > (today or date.today())


def meeting_addon_closed_message(
    *,
    stage: str | None = None,
    tale_number: int | None = None,
    module_week: int | None = None,
) -> str:
    """Текст отказа в докупке встречи."""
    if module_week is None and stage is not None and tale_number is not None:
        module_week = module_week_for_tale(stage, tale_number)
    if module_week is not None and int(module_week) <= 4:
        return (
            "Встречи по сказкам потока 15 июля не проводятся. "
            "Живые занятия с преподавателем — со старта 15 августа."
        )
    if stage and normalize_stage(stage) == "stage-1":
        return (
            "Встречи по сказкам потока 15 июля не проводятся. "
            "Живые занятия с преподавателем — со старта 15 августа."
        )
    return "Встреча по этой сказке уже прошла — докупить нельзя."
