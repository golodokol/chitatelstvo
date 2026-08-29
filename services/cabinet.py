"""Сбор данных комнаты приключений — общий источник для HTML и JSON API."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from api.lesson_signing import build_lesson_url
from config.settings import LESSON_WEEK_DAYS, MODULE_START_DATE, PUBLIC_BASE_URL, TELEGRAM_ENABLED
from notifications.telegram_bot import build_link_url
from db import repository as repo
from db.child_age import child_age_years
from db.models import Child, Enrollment, Family
from gamification.cabinet_ui import (
    build_child_cabinet,
    parent_lesson_guide_steps,
    parent_points_rows,
    sort_lessons_by_access,
    sort_tracks_by_access,
)
from gamification.rules import level_from_points
from lessons.access import lesson_access_info
from lessons.covers import enrich_lesson_link
from lessons.enrollment_access import list_enrollment_tracks, list_lessons_for_enrollment
from lessons.schedule import (
    EARLY_GROUPS,
    RUSSIAN_TALES_GROUPS,
    SLOW_READING_GROUPS,
    STAGE_LABELS,
    STANDARD_GRADE_GROUPS,
    tariff_has_meetings,
)
from lessons.step_labels import event_type_label
from services.birthday_gift import maybe_grant_birthday_gift


def build_schedule_intro(
    lesson_links: list[dict[str, Any]],
    *,
    has_meetings: bool = False,
) -> dict[str, str]:
    """Текст шапки расписания на странице родителя (с учётом смешанных курсов)."""
    codes = {str(link.get("group_code") or "") for link in lesson_links}
    has_early = bool(codes & EARLY_GROUPS) or any(c.startswith("early-") for c in codes)
    has_standard = bool(codes & STANDARD_GRADE_GROUPS)
    has_slow = bool(codes & SLOW_READING_GROUPS)
    has_rus = bool(codes & RUSSIAN_TALES_GROUPS)

    parts: list[str] = []
    if has_standard:
        parts.append(
            "Курсы 1–4 класса и внеклассное чтение: сказки 1–2 уже открыты; "
            "3–4 — с 31 августа; 5–6 — с 7 сентября; 7–8 — с 14 сентября."
        )
    if has_early:
        parts.append(
            "«Буквы оживают» и «Первые истории»: модуль с 1 сентября, "
            "новые уроки по вторникам и четвергам."
        )
    if has_slow:
        parts.append("Медленное чтение: старт 15 сентября, далее по вторникам.")
    if has_rus:
        parts.append("Русские сказки: старт 15 октября.")
    if not parts:
        parts.append("Даты открытия указаны у каждого урока ниже.")

    text = " ".join(parts)
    if has_meetings:
        text += " Встречи с преподавателем — по четвергам."

    if has_early and not (has_standard or has_slow or has_rus):
        heading = "Расписание уроков"
    elif has_early:
        heading = "Расписание"
    else:
        heading = "Расписание сказок"

    return {"heading": heading, "text": text}


def _lesson_is_ready(lesson: dict[str, Any]) -> bool:
    """playable/active: null в JSON не должен считаться «не готово»."""
    if "playable" in lesson and lesson["playable"] is not None:
        return bool(lesson["playable"])
    if "active" in lesson and lesson["active"] is not None:
        return bool(lesson["active"])
    return True


def group_lessons(lesson_links: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not lesson_links:
        return []
    ordered = sort_lessons_by_access(lesson_links)
    stages: list[dict[str, Any]] = []
    by_stage: dict[str, list[dict[str, Any]]] = {}
    stage_order: list[str] = []
    for les in ordered:
        stage = les.get("stage") or "stage-1"
        if stage not in by_stage:
            stage_order.append(stage)
            by_stage[stage] = []
        by_stage[stage].append(les)

    def stage_key(stage: str) -> tuple:
        items = by_stage[stage]
        has_url = any(les.get("url") for les in items)
        preferred = {"stage-1": 0, "stage-2": 1}.get(stage, 9)
        return (0 if has_url else 1, preferred, stage)

    for stage_key_name in sorted(stage_order, key=stage_key):
        stages.append(
            {
                "key": stage_key_name,
                "label": STAGE_LABELS.get(stage_key_name, stage_key_name),
                "lessons": by_stage[stage_key_name],
            }
        )
    return stages


def build_lesson_links_for_track(
    db: Session,
    child: Child,
    enrollment: Enrollment,
    module: dict[str, Any],
) -> tuple[list[dict[str, Any]], bool]:
    has_meetings = tariff_has_meetings(module)
    lesson_links: list[dict[str, Any]] = []
    for les in list_lessons_for_enrollment(enrollment):
        access = lesson_access_info(
            child,
            les,
            week_days=LESSON_WEEK_DAYS,
            enrollment=enrollment,
            module=module,
        )
        link: dict[str, Any] = {
            "slug": les["slug"],
            "title": les["title"],
            "module_week": access["module_week"],
            "week_in_stage": access["week_in_stage"],
            "stage": access["stage"],
            "unlocked": access["unlocked"],
            "opens_on": access["opens_on"],
            "opens_on_label": access["opens_on_label"],
            "opens_on_iso": access.get("opens_on_iso"),
            "stage_label": les.get("stage_label"),
            "tale_slug": les.get("tale_slug") or les["slug"],
            "module_id": les.get("module_id"),
            "group_code": module.get("group_code"),
            "ready": _lesson_is_ready(les),
        }
        if access.get("meeting_on_label"):
            link["meeting_on"] = access["meeting_on"]
            link["meeting_on_label"] = access["meeting_on_label"]
        if access["unlocked"] and _lesson_is_ready(les):
            link["url"] = build_lesson_url(child.id, les["slug"], enrollment_id=enrollment.id)
        enrich_lesson_link(link)
        lesson_links.append(link)
    return lesson_links, has_meetings


def _maybe_heal_first_step_badge(db: Session, child: Child) -> None:
    """Выдаёт «Первый шаг», если есть учебные события, а бейджа ещё нет."""
    from gamification.bonus_badges import FIRST_STEP_BADGE, FIRST_STEP_EVENT_TYPES

    badge_names = {b.badge_name for b in child.badges}
    if FIRST_STEP_BADGE in badge_names:
        return
    events = repo.get_child_events(db, child.id, limit=50)
    if not any(e.event_type in FIRST_STEP_EVENT_TYPES for e in events):
        return
    if repo.grant_bonus_badge(db, child, badge_name=FIRST_STEP_BADGE):
        db.refresh(child)


def build_child_payload(db: Session, child: Child, *, assets_base: str = PUBLIC_BASE_URL) -> dict[str, Any]:
    maybe_grant_birthday_gift(db, child)
    _maybe_heal_first_step_badge(db, child)
    events = repo.get_child_events(db, child.id, limit=120)
    tale_ratings = repo.get_child_tale_ratings(db, child.id)
    chest_claims = repo.get_child_chest_claims(db, child.id)
    badges = [b.badge_name for b in child.badges]
    points = child.total_points or 0
    level = level_from_points(points)

    tracks: list[dict[str, Any]] = []
    all_lesson_links: list[dict[str, Any]] = []
    has_meetings = False

    for track in list_enrollment_tracks(child):
        enrollment = track["enrollment"]
        module = track["module"]
        lesson_links, track_meetings = build_lesson_links_for_track(db, child, enrollment, module)
        lesson_links = sort_lessons_by_access(lesson_links)
        has_meetings = has_meetings or track_meetings
        all_lesson_links.extend(lesson_links)
        tracks.append(
            {
                "group_code": module["group_code"],
                "group_label": module["group_label"],
                "module_title": module["title"],
                "module_id": module["id"],
                "tariff_code": module.get("tariff_code") or "",
                "tariff_label": module.get("tariff_label") or "",
                "lesson_links": lesson_links,
                "lesson_stages": group_lessons(lesson_links),
                "has_meetings": track_meetings,
            }
        )

    tracks = sort_tracks_by_access(tracks)
    all_lesson_links = sort_lessons_by_access(all_lesson_links)
    module_titles = [t["module_title"] for t in tracks]
    module_title = " · ".join(module_titles) if module_titles else None

    return {
        "id": str(child.id),
        "name": child.name,
        "age": child_age_years(child),
        "birth_date": child.birth_date.isoformat() if child.birth_date else None,
        "level": level,
        "points": points,
        "badges": badges,
        "lessons": all_lesson_links,
        "lesson_stages": group_lessons(all_lesson_links),
        "schedule_intro": build_schedule_intro(
            all_lesson_links, has_meetings=has_meetings
        ),
        "module_title": module_title,
        "has_meetings": has_meetings,
        "tracks": tracks,
        "cabinet": build_child_cabinet(
            name=child.name,
            level=level,
            points=points,
            earned_badges=badges,
            events=events,
            lesson_links=all_lesson_links,
            tracks=tracks,
            tale_ratings=tale_ratings,
            chest_claims=chest_claims,
            assets_base=assets_base,
            child_id=str(child.id),
        ),
        "events": [
            {
                "type": e.event_type,
                "type_label": event_type_label(e.event_type),
                "tale": e.tale_title or "—",
                "date": e.created_at.strftime("%d.%m.%Y %H:%M") if e.created_at else "",
            }
            for e in events
        ],
    }


def build_family_cabinet(
    db: Session,
    family: Family,
    *,
    child_id: uuid.UUID | None = None,
    assets_base: str = PUBLIC_BASE_URL,
) -> dict[str, Any]:
    family = repo.get_family_by_id(db, family.id) or family
    children_rows = list(family.children)
    if not children_rows:
        children_rows = [
            c for c in repo.list_children_by_parent_email(db, family.parent_email) if c.family_id == family.id
        ]

    if child_id is not None:
        selected = next((c for c in children_rows if c.id == child_id), None)
        if not selected:
            child = repo.get_child_with_family(db, child_id)
            if not child or child.family_id != family.id:
                raise ValueError("child_not_found")
            selected = child
        children_rows = [selected]

    token = family.progress_token
    notifications = repo.get_family_notifications(db, family.id, limit=30)

    return {
        "email": family.parent_email,
        "parent_name": family.parent_name,
        "family_id": str(family.id),
        "progress_token": token,
        "progress_url": f"{assets_base.rstrip('/')}/progress/{token}",
        "notification_channel": family.notification_channel,
        "module_start_date": (
            MODULE_START_DATE.strftime("%d.%m.%Y") if MODULE_START_DATE else None
        ),
        "telegram": {
            "enabled": TELEGRAM_ENABLED,
            "linked": family.telegram_chat_id is not None,
            "link_page": f"{assets_base.rstrip('/')}/link-telegram/{token}/page",
            "deep_link": build_link_url(token),
        },
        "notifications": [
            {
                "message": n.message,
                "channel": n.channel,
                "date": n.created_at.strftime("%d.%m.%Y %H:%M") if n.created_at else "",
            }
            for n in notifications
        ],
        "selected_child_id": str(child_id) if child_id else None,
        "children": [build_child_payload(db, child, assets_base=assets_base) for child in children_rows],
        "parent_guide": {
            "steps": parent_lesson_guide_steps(),
            "points": parent_points_rows(),
        },
    }
