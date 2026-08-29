"""Разовое занятие не должно ждать календарь потока."""

from __future__ import annotations

from types import SimpleNamespace

from lessons.access import is_lesson_unlocked


def test_single_lesson_unlocked_before_calendar_week():
    child = SimpleNamespace(module_week=1, bonus_unlock_weeks=0)
    lesson = {
        "slug": "grade-1-single-lesson-01",
        "tariff_code": "single",
        "group_code": "grade-1",
        "module_week": 1,
    }
    enrollment = SimpleNamespace(chosen_stage="stage-2", chosen_tale_number=1)
    module = {"tariff_code": "single", "group_code": "grade-1"}

    assert is_lesson_unlocked(
        child,
        lesson,
        enrollment=enrollment,
        module=module,
    )
