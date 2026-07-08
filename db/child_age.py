"""Возраст ребёнка: из даты рождения или legacy-поля age."""

from __future__ import annotations

from datetime import date

from db.models import Child


def age_on_date(birth_date: date, on_date: date | None = None) -> int:
    today = on_date or date.today()
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return max(0, years)


def child_age_years(child: Child, *, on_date: date | None = None) -> int | None:
    if child.birth_date:
        return age_on_date(child.birth_date, on_date)
    return child.age


def is_birthday_today(birth_date: date, *, on_date: date | None = None) -> bool:
    today = on_date or date.today()
    return (birth_date.month, birth_date.day) == (today.month, today.day)
