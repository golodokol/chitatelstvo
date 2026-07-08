from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import repository as repo
from db.session import get_db
from gamification.cabinet_ui import CHEST_STEPS, _events_for_tale, chest_ready_from_done
from gamification.chest_rewards import canonical_tale_slug, items_for_treasury, rewards_for_tale
from lessons.enrollment_access import list_lessons_for_child

router = APIRouter(tags=["chest"])


class ChestClaimBody(BaseModel):
    child_id: uuid.UUID
    tale_slug: str = Field(min_length=1, max_length=200)


def _child_in_family(db: Session, token: str, child_id: uuid.UUID):
    family = repo.get_family_by_token(db, token)
    if not family:
        raise HTTPException(404, "Страница не найдена")
    child = repo.get_child_with_family(db, child_id)
    if not child or child.family_id != family.id:
        raise HTTPException(403, "Нет доступа")
    return family, child


def _lesson_for_slug(child, tale_slug: str) -> dict | None:
    needle = canonical_tale_slug(tale_slug.strip())
    for les in list_lessons_for_child(child):
        lesson_slug = les.get("slug") or ""
        lesson_tale = canonical_tale_slug(les.get("tale_slug") or lesson_slug)
        if lesson_slug == tale_slug.strip() or lesson_tale == needle:
            return les
    return None


def _chest_ready_for_tale(db: Session, child_id: uuid.UUID, lesson: dict) -> bool:
    events = repo.get_child_events(db, child_id, limit=50)
    done = _events_for_tale(events, lesson.get("title", ""))
    return chest_ready_from_done(done)


@router.post("/api/progress/{token}/chest/claim")
def claim_chest(
    token: str,
    body: ChestClaimBody,
    db: Session = Depends(get_db),
) -> dict:
    _, child = _child_in_family(db, token, body.child_id)
    tale_slug = body.tale_slug.strip()

    lesson = _lesson_for_slug(child, tale_slug)
    if not lesson:
        raise HTTPException(404, "Сказка не найдена")

    reward_slug = canonical_tale_slug(lesson.get("tale_slug") or lesson.get("slug") or tale_slug)
    existing = repo.get_chest_claim(db, child.id, reward_slug)
    if not existing:
        existing = repo.get_chest_claim(db, child.id, tale_slug)
    if existing:
        return {
            "status": "already_claimed",
            "message": "Награда уже в сокровищнице",
            "items": existing.items,
        }

    if not _chest_ready_for_tale(db, child.id, lesson):
        raise HTTPException(
            400,
            "Сундук ещё не готов — посмотрите начало видео, пройдите мини-тест и блок заданий",
        )

    all_items = rewards_for_tale(reward_slug, lesson.get("title", ""))
    treasury_items = items_for_treasury(all_items)
    row = repo.save_chest_claim(
        db,
        child_id=child.id,
        tale_slug=reward_slug,
        tale_title=lesson.get("title", ""),
        module_week=lesson.get("module_week"),
        items=treasury_items,
    )
    return {
        "status": "claimed",
        "message": "Награда сохранена в сокровищнице",
        "items": row.items,
        "letter_shown": True,
        "claimed_at": row.claimed_at.isoformat() if row.claimed_at else None,
    }
