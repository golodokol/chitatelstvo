"""Несколько разовых на один module_id: не путать сказки."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from lessons.enrollment_access import find_enrollment_for_lesson


def _enrollment(**kwargs):
    base = {
        "id": uuid4(),
        "module_id": 1,
        "status": "active",
        "chosen_stage": "stage-1",
        "chosen_tale_number": 1,
        "created_at": datetime(2026, 7, 22, tzinfo=timezone.utc),
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_find_enrollment_prefers_unlocked_over_older_locked(monkeypatch):
    frog = _enrollment(
        chosen_stage="stage-1",
        chosen_tale_number=1,
        created_at=datetime(2026, 7, 27, tzinfo=timezone.utc),
    )
    pike = _enrollment(
        chosen_stage="stage-2",
        chosen_tale_number=1,
        created_at=datetime(2026, 7, 22, tzinfo=timezone.utc),
    )
    child = SimpleNamespace(
        enrollments=[pike, frog],
        module_week=1,
        bonus_unlock_weeks=0,
        created_at=datetime(2026, 7, 20, tzinfo=timezone.utc),
    )
    lesson = {
        "slug": "grade-1-single-lesson-01",
        "module_id": 1,
        "tariff_code": "single",
        "group_code": "grade-1",
        "module_week": 1,
    }

    monkeypatch.setattr(
        "lessons.enrollment_access.get_active_enrollments",
        lambda c: [pike, frog],
    )
    monkeypatch.setattr(
        "lessons.enrollment_access.get_module",
        lambda mid: {"id": mid, "tariff_code": "single", "group_code": "grade-1"},
    )

    chosen = find_enrollment_for_lesson(child, lesson)
    assert chosen is frog

    by_id = find_enrollment_for_lesson(child, lesson, enrollment_id=pike.id)
    assert by_id is pike
