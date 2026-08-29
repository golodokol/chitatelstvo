"""Авто-выдача бесплатного пробного early-урока после заявки."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from api.lesson_signing import build_lesson_url
from api.schemas import RegisterWebhook
from catalog.loader import get_module
from config.settings import PUBLIC_BASE_URL
from db import repository as repo
from lessons.enrollment_access import find_enrollment_for_lesson, get_active_enrollments, list_lessons_for_enrollment
from lessons.loader import get_lesson
from services.enrollment import create_enrollment_from_registration

logger = logging.getLogger(__name__)

TRIAL_BY_SLUG = {
    "early-letters-trial-lesson-01": 20,
    "early-stories-trial-lesson-01": 23,
}

TRIAL_BY_GROUP = {
    "early-letters": 20,
    "early-stories": 23,
}


def resolve_trial_module_id(
    *,
    trial_slug: str | None = None,
    group_code: str | None = None,
) -> int | None:
    slug = (trial_slug or "").strip()
    if slug in TRIAL_BY_SLUG:
        return TRIAL_BY_SLUG[slug]
    group = (group_code or "").strip()
    if group in TRIAL_BY_GROUP:
        return TRIAL_BY_GROUP[group]
    # Infer from slug prefix
    if slug.startswith("early-letters"):
        return 20
    if slug.startswith("early-stories"):
        return 23
    return None


def grant_early_trial(
    db: Session,
    *,
    parent_name: str,
    parent_email: str,
    child_name: str,
    child_age: int | None = None,
    phone: str | None = None,
    trial_slug: str | None = None,
    group_code: str | None = None,
) -> dict[str, Any] | None:
    """Создаёт/переиспользует семью и выдаёт trial enrollment. Возвращает ссылки для письма."""
    module_id = resolve_trial_module_id(trial_slug=trial_slug, group_code=group_code)
    if module_id is None:
        return None

    module = get_module(module_id)
    if not module:
        return None

    family, child, _is_returning = repo.resolve_or_create_family_child(
        db,
        parent_name=parent_name,
        parent_email=parent_email,
        parent_telegram=None,
        notification_channel="email",
        child_name=child_name,
        child_age=child_age,
        child_birth_date=None,
        telegram_chat_id=None,
    )

    # Уже есть активный trial этого модуля — не дублируем
    existing = None
    for enrollment in get_active_enrollments(child):
        if enrollment.module_id == module_id:
            existing = enrollment
            break

    if existing is None:
        body = RegisterWebhook(
            parent_name=parent_name,
            parent_email=parent_email,
            parent_telegram=None,
            notification_channel="email",
            child_name=child_name,
            child_age=child_age,
            module_id=module_id,
            chosen_stage="stage-1",
            chosen_tale_number=None,
        )
        create_enrollment_from_registration(db, child, body)
        db.refresh(child)
        logger.info(
            "Early trial granted email=%s child=%s module=%s phone=%s",
            parent_email,
            child.id,
            module_id,
            phone or "",
        )
    else:
        logger.info(
            "Early trial already active email=%s child=%s module=%s",
            parent_email,
            child.id,
            module_id,
        )

    enrollment = existing
    if enrollment is None:
        for e in get_active_enrollments(child):
            if e.module_id == module_id:
                enrollment = e
                break

    lesson_slug = (trial_slug or "").strip()
    if not lesson_slug:
        lessons = list_lessons_for_enrollment(enrollment) if enrollment else []
        lesson_slug = lessons[0]["slug"] if lessons else ""
    lesson = get_lesson(lesson_slug) if lesson_slug else None
    lesson_title = (lesson or {}).get("title") or module.get("title") or "Пробный урок"

    progress_url = f"{PUBLIC_BASE_URL}/progress/{family.progress_token}"
    if lesson_slug and enrollment:
        lesson_url = build_lesson_url(child.id, lesson_slug, enrollment_id=enrollment.id)
    elif lesson_slug:
        lesson_url = build_lesson_url(child.id, lesson_slug)
    else:
        lesson_url = progress_url

    return {
        "module_id": module_id,
        "module_title": module.get("title"),
        "lesson_slug": lesson_slug,
        "lesson_title": lesson_title,
        "progress_url": progress_url,
        "lesson_url": lesson_url,
        "child_id": str(child.id),
        "family_id": str(family.id),
    }


def ensure_sibling_early_trial(
    db: Session,
    *,
    child,
    lesson_slug: str,
) -> None:
    """Grant the other early trial module when a child follows a cross-promo link."""
    module_id = resolve_trial_module_id(trial_slug=lesson_slug)
    if module_id is None:
        return
    lesson = get_lesson(lesson_slug)
    if lesson and find_enrollment_for_lesson(child, lesson):
        return
    family = child.family
    if not family:
        return
    has_early = False
    for enrollment in get_active_enrollments(child):
        mod = get_module(enrollment.module_id)
        if mod and mod.get("group_code") in {"early-letters", "early-stories"}:
            has_early = True
            break
    if not has_early:
        return
    grant_early_trial(
        db,
        parent_name=family.parent_name or "",
        parent_email=family.parent_email or "",
        child_name=child.name,
        child_age=child.age,
        trial_slug=lesson_slug,
    )
    db.refresh(child)
