"""Отметка присутствия на живой встрече (бейдж «Слушатель»)."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from catalog.loader import get_module, get_tale
from db import repository as repo
from lessons.enrollment_access import normalize_stage
from services.events import submit_learning_event


def list_tales_for_enrollment(
    module: dict[str, Any] | None,
    enrollment,
) -> list[str]:
    if not module or not enrollment:
        return []

    group_code = module.get("group_code") or ""
    stage = normalize_stage(enrollment.chosen_stage)
    if not group_code or not stage:
        return []

    if module.get("tariff_code") == "single":
        if enrollment.chosen_tale_title:
            return [enrollment.chosen_tale_title.strip()]
        if enrollment.chosen_tale_number:
            tale = get_tale(group_code, stage, int(enrollment.chosen_tale_number))
            if tale:
                return [tale["tale_title"]]
        return []

    titles: list[str] = []
    for tale_number in range(1, int(module.get("tales_count") or 4) + 1):
        tale = get_tale(group_code, stage, tale_number)
        if tale:
            titles.append(tale["tale_title"])
    return titles


def meeting_tale_options(
    db: Session,
    child_id: uuid.UUID,
    *,
    module: dict[str, Any] | None,
    enrollment,
) -> list[dict[str, Any]]:
    titles = list_tales_for_enrollment(module, enrollment)
    return [
        {
            "title": title,
            "marked": repo.child_has_learning_event(
                db,
                child_id,
                tale_title=title,
                event_type="live_meeting",
            ),
        }
        for title in titles
    ]


def mark_meeting_attendance(
    db: Session,
    *,
    child_id: uuid.UUID,
    tale_title: str,
) -> dict[str, Any]:
    child = repo.get_child_with_family(db, child_id)
    if not child:
        raise HTTPException(404, "Ребёнок не найден")

    title = (tale_title or "").strip()
    if not title:
        raise HTTPException(400, "Укажите сказку встречи")

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type="live_meeting",
        tale_title=title,
        lesson_date=date.today(),
        notes="admin: meeting attendance",
        payload={"source": "admin", "event_type": "live_meeting"},
    )
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "child_name": child.name,
        "tale_title": title,
    }
