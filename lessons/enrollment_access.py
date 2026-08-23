"""Доступ к урокам по записи на модуль (enrollment)."""

from __future__ import annotations

from typing import Any

from catalog.loader import get_module, get_tale
from db.models import Child, Enrollment
from lessons.loader import list_legacy_lessons, list_module_lessons
from lessons.single_content import single_lesson_playable
from lessons.stages import normalize_stage

EARLY_GROUPS = frozenset({"early-letters", "early-stories"})
# Пробные сказки, доступные после early-квестов (без записи на модуль).
PROMO_LESSON_SLUGS = frozenset({"tsarevna-lyagushka"})


def is_promo_lesson(lesson: dict[str, Any] | None) -> bool:
    return str((lesson or {}).get("slug") or "").strip() in PROMO_LESSON_SLUGS


def resolve_chosen_tale(
    *,
    group_code: str,
    chosen_stage: str | None,
    chosen_tale_number: int | None,
) -> dict[str, Any] | None:
    stage = normalize_stage(chosen_stage)
    if not stage or chosen_tale_number is None:
        return None
    return get_tale(group_code, stage, chosen_tale_number)


def get_active_enrollments(child: Child) -> list[Enrollment]:
    active = [e for e in child.enrollments if e.status == "active"]
    return sorted(active, key=lambda e: (e.created_at or e.id, str(e.id)))


def get_active_enrollment(child: Child) -> Enrollment | None:
    active = get_active_enrollments(child)
    if not active:
        return None
    return active[-1]


def find_enrollment_for_lesson(child: Child, lesson: dict[str, Any]) -> Enrollment | None:
    module_id = lesson.get("module_id")
    if module_id is None:
        return get_active_enrollment(child)
    for enrollment in get_active_enrollments(child):
        if enrollment.module_id == module_id:
            return enrollment
    return None


def child_can_access_lesson(
    child: Child,
    lesson: dict[str, Any],
    enrollment: Enrollment | None = None,
) -> bool:
    if is_promo_lesson(lesson):
        return True
    module_id = lesson.get("module_id")
    if module_id is None:
        return enrollment is None

    active = enrollment or find_enrollment_for_lesson(child, lesson)
    if active is None or active.status != "active":
        return False
    if active.module_id != module_id:
        return False

    module = get_module(module_id)
    if not module:
        return False

    if module["tariff_code"] in ("single", "trial"):
        return lesson.get("tariff_code") == module["tariff_code"]

    if lesson.get("tariff_code") in ("single", "trial"):
        return False

    stage = normalize_stage(active.chosen_stage)
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

    stage = lesson.get("stage")
    if enrollment and lesson.get("tariff_code") == "single":
        stage = normalize_stage(enrollment.chosen_stage) or stage

    tale_slug = lesson.get("tale_slug") or lesson["slug"]
    if enrollment and lesson.get("tariff_code") == "single" and enrollment.chosen_tale_slug:
        tale_slug = enrollment.chosen_tale_slug

    return {
        "slug": lesson["slug"],
        "title": title,
        "tale_slug": tale_slug,
        "module_week": lesson.get("module_week", 1),
        "module_id": lesson.get("module_id"),
        "stage_label": lesson.get("stage_label"),
        "stage": stage,
        "group_code": lesson.get("group_code"),
        "active": lesson.get("active", True),
        "playable": single_lesson_playable(lesson, enrollment),
    }


def list_lessons_for_enrollment(enrollment: Enrollment) -> list[dict[str, Any]]:
    module = get_module(enrollment.module_id)
    if not module:
        return []

    lessons = list_module_lessons(enrollment.module_id, active_only=False)
    tariff = module["tariff_code"]
    if tariff in ("single", "trial"):
        lessons = [les for les in lessons if les.get("tariff_code") == tariff]
    else:
        lessons = [les for les in lessons if les.get("tariff_code") not in ("single", "trial")]
        stage = normalize_stage(enrollment.chosen_stage)
        if stage:
            lessons = [les for les in lessons if les.get("stage") == stage]

    return [_lesson_summary(les, enrollment) for les in lessons]


def list_lessons_for_child(child: Child) -> list[dict[str, Any]]:
    enrollments = get_active_enrollments(child)
    if not enrollments:
        return list_legacy_lessons()

    lessons: list[dict[str, Any]] = []
    for enrollment in enrollments:
        lessons.extend(list_lessons_for_enrollment(enrollment))
    return lessons


def list_enrollment_tracks(child: Child) -> list[dict[str, Any]]:
    tracks: list[dict[str, Any]] = []
    for enrollment in get_active_enrollments(child):
        module = get_module(enrollment.module_id)
        if not module:
            continue
        tracks.append(
            {
                "enrollment": enrollment,
                "module": module,
                "lessons": list_lessons_for_enrollment(enrollment),
            }
        )
    return tracks
