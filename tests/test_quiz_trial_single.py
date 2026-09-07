"""Квиз дарит одну сказку (разовое), а не весь self_paced-модуль."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from catalog.loader import find_module
from lessons.enrollment_access import (
    child_can_access_lesson,
    find_enrollment_for_lesson,
    single_enrollment_covers_content,
)
from lessons.loader import get_lesson
from services.early_trial import resolve_quiz_single_grant


def _enrollment(**kwargs):
    base = {
        "id": uuid4(),
        "module_id": 1,
        "status": "active",
        "chosen_stage": "stage-1",
        "chosen_tale_number": 1,
        "created_at": datetime(2026, 9, 6, tzinfo=timezone.utc),
    }
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_resolve_quiz_grant_uses_single_not_self_paced():
    lesson = get_lesson("grade-1-self_paced-stage-1-lesson-01")
    grant = resolve_quiz_single_grant(lesson)
    assert grant == (1, "stage-1", 1)
    single = find_module(group_code="grade-1", tariff_code="single")
    assert single and single["id"] == 1


def test_extra_quiz_slug_maps_to_single():
    lesson = get_lesson("extra-6-8-self_paced-stage-1-lesson-01")
    grant = resolve_quiz_single_grant(lesson)
    assert grant is not None
    module_id, stage, tale_number = grant
    assert stage == "stage-1"
    assert tale_number == 1
    module = find_module(group_code="extra-6-8", tariff_code="single")
    assert module and module["id"] == module_id
    assert module["tariff_code"] == "single"


def test_single_covers_only_matching_self_paced_tale():
    enrollment = _enrollment()
    frog = get_lesson("grade-1-self_paced-stage-1-lesson-01")
    other = get_lesson("grade-1-self_paced-stage-1-lesson-02")
    assert single_enrollment_covers_content(enrollment, frog)
    assert not single_enrollment_covers_content(enrollment, other)


def test_access_self_paced_url_with_single_enrollment(monkeypatch):
    enrollment = _enrollment()
    child = SimpleNamespace(enrollments=[enrollment], status="active")
    frog = get_lesson("grade-1-self_paced-stage-1-lesson-01")
    other = get_lesson("grade-1-self_paced-stage-1-lesson-02")

    monkeypatch.setattr(
        "lessons.enrollment_access.get_active_enrollments",
        lambda c: [enrollment],
    )

    assert find_enrollment_for_lesson(child, frog, enrollment_id=enrollment.id) is enrollment
    assert child_can_access_lesson(child, frog, enrollment)
    assert not child_can_access_lesson(child, other, enrollment)
    assert find_enrollment_for_lesson(child, other) is None
