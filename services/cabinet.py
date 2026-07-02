"""Сбор данных комнаты приключений — общий источник для HTML и JSON API."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from api.lesson_signing import build_lesson_url
from config.settings import LESSON_WEEK_DAYS, MODULE_START_DATE, PUBLIC_BASE_URL, TELEGRAM_ENABLED
from db import repository as repo
from db.models import Child, Enrollment, Family
from gamification.cabinet_ui import (
    build_child_cabinet,
    parent_lesson_guide_steps,
    parent_points_rows,
)
from gamification.rules import level_from_points
from lessons.access import lesson_access_info
from lessons.covers import enrich_lesson_link
from lessons.enrollment_access import list_enrollment_tracks, list_lessons_for_enrollment
from lessons.schedule import STAGE_LABELS, tariff_has_meetings
from lessons.step_labels import event_type_label
from notifications.telegram_bot import build_link_url


def group_lessons(lesson_links: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not lesson_links:
        return []
    stages: list[dict[str, Any]] = []
    by_stage: dict[str, list[dict[str, Any]]] = {}
    for les in lesson_links:
        stage = les.get("stage") or "stage-1"
        by_stage.setdefault(stage, []).append(les)
    for stage_key in ("stage-1", "stage-2"):
        items = by_stage.get(stage_key)
        if not items:
            continue
        stages.append(
            {
                "key": stage_key,
                "label": STAGE_LABELS.get(stage_key, stage_key),
                "lessons": items,
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
            "ready": les.get("playable", les.get("active", True)),
        }
        if access.get("meeting_on_label"):
            link["meeting_on"] = access["meeting_on"]
            link["meeting_on_label"] = access["meeting_on_label"]
        if access["unlocked"] and les.get("playable", les.get("active", True)):
            link["url"] = build_lesson_url(child.id, les["slug"])
        enrich_lesson_link(link)
        lesson_links.append(link)
    return lesson_links, has_meetings


def build_child_payload(db: Session, child: Child, *, assets_base: str = PUBLIC_BASE_URL) -> dict[str, Any]:
    events = repo.get_child_events(db, child.id, limit=20)
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
        has_meetings = has_meetings or track_meetings
        all_lesson_links.extend(lesson_links)
        tracks.append(
            {
                "group_code": module["group_code"],
                "group_label": module["group_label"],
                "module_title": module["title"],
                "module_id": module["id"],
                "lesson_links": lesson_links,
                "lesson_stages": group_lessons(lesson_links),
                "has_meetings": track_meetings,
            }
        )

    module_titles = [t["module_title"] for t in tracks]
    module_title = " · ".join(module_titles) if module_titles else None

    return {
        "id": str(child.id),
        "name": child.name,
        "age": child.age,
        "level": level,
        "points": points,
        "badges": badges,
        "lessons": all_lesson_links,
        "lesson_stages": group_lessons(all_lesson_links),
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
