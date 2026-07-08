"""Тесты возраста и подарка на день рождения."""

from __future__ import annotations

from datetime import date

from db.child_age import age_on_date, child_age_years, is_birthday_today
from db.models import Child


def test_age_on_date_before_birthday():
    birth = date(2016, 7, 15)
    assert age_on_date(birth, date(2026, 7, 8)) == 9
    assert age_on_date(birth, date(2026, 7, 15)) == 10


def test_child_age_years_prefers_birth_date():
    child = Child(name="Тест", age=5, birth_date=date(2016, 3, 1))
    assert child_age_years(child, on_date=date(2026, 7, 8)) == 10


def test_is_birthday_today():
    birth = date(2016, 7, 8)
    assert is_birthday_today(birth, on_date=date(2026, 7, 8))
    assert not is_birthday_today(birth, on_date=date(2026, 7, 9))
