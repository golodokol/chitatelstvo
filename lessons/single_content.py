"""Контент разового занятия: подставляем урок self_paced для выбранной сказки."""

from __future__ import annotations

from typing import Any

from db.models import Enrollment
from lessons.stages import normalize_stage
from lessons.loader import get_lesson


def content_slug_for_single(
    *,
    group_code: str,
    stage: str,
    tale_number: int,
) -> str:
    return f"{group_code}-self_paced-{stage}-lesson-{tale_number:02d}"


def _content_lesson_for_enrollment(
    lesson: dict[str, Any],
    enrollment: Enrollment,
) -> dict[str, Any] | None:
    stage = normalize_stage(enrollment.chosen_stage)
    tale_number = enrollment.chosen_tale_number
    if not stage or not tale_number:
        return None
    group_code = lesson.get("group_code") or "grade-1"
    slug = content_slug_for_single(
        group_code=group_code,
        stage=stage,
        tale_number=int(tale_number),
    )
    content = get_lesson(slug)
    if not content or not content.get("active", True):
        return None
    return content


def single_lesson_playable(
    lesson: dict[str, Any],
    enrollment: Enrollment | None = None,
) -> bool:
    if lesson.get("tariff_code") != "single":
        return bool(lesson.get("active", True) and lesson.get("video"))
    # Оболочка single может оставаться черновиком: важна готовность контента сказки
    if lesson.get("video"):
        return bool(lesson.get("active", True))
    if enrollment is None:
        return False
    return _content_lesson_for_enrollment(lesson, enrollment) is not None


def merge_single_lesson_content(
    lesson: dict[str, Any],
    enrollment: Enrollment | None = None,
) -> dict[str, Any]:
    """Оболочка разового занятия + контент выбранной сказки из self_paced."""
    if lesson.get("tariff_code") != "single" or enrollment is None:
        return lesson
    if lesson.get("video"):
        return _apply_single_labels(lesson, enrollment)

    content = _content_lesson_for_enrollment(lesson, enrollment)
    if content is None:
        return {**lesson, "active": False}

    merged = dict(content)
    merged.update(
        {
            "slug": lesson["slug"],
            "module_id": lesson["module_id"],
            "group_code": lesson.get("group_code"),
            "group_label": lesson.get("group_label"),
            "tariff_code": lesson["tariff_code"],
            "tariff_label": lesson.get("tariff_label"),
            "stage_label": lesson.get("stage_label"),
            "module_week": lesson.get("module_week", 1),
            "meeting_number": lesson.get("meeting_number"),
            "lesson_number": lesson.get("lesson_number"),
            "badge": lesson.get("badge") or content.get("badge"),
            "points": lesson.get("points") or content.get("points"),
            # Готовность = контент сказки (оболочка single — только маршрутизация)
            "active": bool(content.get("active", True)),
        }
    )
    return _apply_single_labels(merged, enrollment)


def _apply_single_labels(
    lesson: dict[str, Any],
    enrollment: Enrollment,
) -> dict[str, Any]:
    stage = normalize_stage(enrollment.chosen_stage) or lesson.get("stage")
    tale_number = enrollment.chosen_tale_number or lesson.get("tale_number")
    result = dict(lesson)
    if enrollment.chosen_tale_title:
        result["title"] = enrollment.chosen_tale_title
        result["tale_title"] = enrollment.chosen_tale_title
    if enrollment.chosen_tale_slug:
        result["tale_slug"] = enrollment.chosen_tale_slug
    if stage:
        result["stage"] = stage
    if tale_number:
        result["tale_number"] = tale_number
    return result
