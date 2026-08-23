"""JWT API сундука для мобильного приложения."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.deps import get_current_family
from api.routes.chest import _chest_ready_for_tale, _lesson_for_slug
from db import repository as repo
from db.models import Family
from db.session import get_db
from gamification.chest_rewards import canonical_tale_slug, items_for_treasury, rewards_for_tale

router = APIRouter(prefix="/api/v1", tags=["chest"])


class ChestClaimMobileBody(BaseModel):
    child_id: uuid.UUID
    tale_slug: str = Field(min_length=1, max_length=200)


@router.post("/chest/claim")
def claim_chest_jwt(
    body: ChestClaimMobileBody,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
) -> dict:
    child = repo.get_child_with_family(db, body.child_id)
    if not child or child.family_id != family.id:
        raise HTTPException(403, "Ребёнок не найден в этой семье")

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
        early = str(lesson.get("group_code") or "").startswith("early") or lesson.get("lesson_format") == "quest"
        raise HTTPException(
            400,
            (
                "Сундук ещё не готов — сначала собери все искорки в квесте"
                if early
                else "Сундук ещё не готов — посмотрите начало видео, пройдите мини-тест и блок заданий"
            ),
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
    from gamification.bonus_badges import check_chest_keeper_badge

    chest_badge = check_chest_keeper_badge(
        child_name=child.name,
        current_badges=[b.badge_name for b in child.badges],
        tale_title=lesson.get("title"),
    )
    if chest_badge:
        repo.grant_bonus_badge(
            db,
            child,
            badge_name=chest_badge.badge_name,
            level_change=chest_badge.level_change,
        )
    return {
        "status": "claimed",
        "message": "Награда сохранена в сокровищнице",
        "items": row.items,
        "letter_shown": True,
        "claimed_at": row.claimed_at.isoformat() if row.claimed_at else None,
        "badge_name": chest_badge.badge_name if chest_badge else None,
    }
