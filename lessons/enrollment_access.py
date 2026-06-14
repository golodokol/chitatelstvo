"""Доступ к урокам по записи на модуль (enrollment)."""

from __future__ import annotations

from typing import Any

from catalog.loader import get_module, get_tale
from db.models import Child, Enrollment
from lessons.loader import get_lesson, list_legacy_lessons, list_module_lessons


def normalize_stage(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip().lower()
    if raw in ("1", "stage-1", "этап 1", "этап1"):
        return "stage-1"
    if raw in ("2", "stage-2", "этап 2", "этап2"):
        return "stage-2"
    if raw.startswith("этап 1"):
        return "stage-1"
    if raw.startswith("этап 2"):
        return "stage-2"
    return None


def resolve_chosen_tale(
    *,
    group_code: str,
    chosen_stage: str | None,
    chosen_tale_number: int | None,
) -> dict[str, Any] | None:
    stage = normalize_stage(chosen_stage)
    if not stage or not chosen_tale_number:
        return None
    return get_tale(group_code, stage, chosen_tale_number)


def get_active_enrollment(child: Child) -> Enrollment | None:
    active = [e for e in child.enrollments if e.status == "active"]
    if not active:
        return None
    return max(active, key=lambda e: e.created_at or e.id)


def child_can_access_lesson(
    child: Child,
    lesson: dict[str, Any],
    enrollment: Enrollment | None,
) -> bool:
    module_id = lesson.get("module_id")
    if module_id is None:
        return enrollment is None

    if enrollment is None or enrollment.status != "active":
        return False
    if enrollment.module_id != module_id:
        return False

    module = get_module(module_id)
    if not module:
        return False

    if module["tariff_code"] == "single":
        if lesson.get("tariff_code") != "single":
            return False
        return True

    if lesson.get("tariff_code") == "single":
        return False

    stage = normalize_stage(enrollment.chosen_stage)
    if stage and lesson.get("stage") and lesson.get("stage") != stage:
        return False
    return True


def _lesson_summary(lesson: dict[str, Any], enrollment: Enrollment | None) -> dict[str, Any]:
    title = lesson["title"]
    if (
        enrollment
        and enrollment.chosen_tale_title
        and lesson.get("tariff_code") == "single"
    ):
        title = enrollment.chosen_tale_title

    return {
        "slug": lesson["slug"],
        "title": title,
        "module_week": lesson.get("module_week", 1),
        "module_id": lesson.get("module_id"),
        "stage_label": lesson.get("stage_label"),
        "active": lesson.get("active", True),
        "playable": bool(lesson.get("active", True) and lesson.get("video")),
    }


def list_lessons_for_child(child: Child) -> list[dict[str, Any]]:
    enrollment = get_active_enrollment(child)

    if enrollment is None:
        return list_legacy_lessons()

    module = get_module(enrollment.module_id)
    if not module:
        return []

    lessons = list_module_lessons(enrollment.module_id, active_only=False)
    if module["tariff_code"] == "single":
        lessons = [les for les in lessons if les.get("tariff_code") == "single"]
    else:
        lessons = [les for les in lessons if les.get("tariff_code") != "single"]
        stage = normalize_stage(enrollment.chosen_stage)
        if stage:
            lessons = [les for les in lessons if les.get("stage") == stage]

    return [_lesson_summary(les, enrollment) for les in lessons]
