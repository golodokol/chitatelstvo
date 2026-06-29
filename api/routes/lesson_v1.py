"""JSON API урока для мобильного приложения (JWT + child_id)."""

from __future__ import annotations

import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.deps import get_current_family, get_family_child, rate_limit
from api.test_lesson_auth import verify_test_lesson_key
from db import repository as repo
from db.models import Child, Family
from db.session import get_db
from services.lesson_player import (
    build_lesson_json,
    handle_emotion_quiz_submit,
    handle_manual_mark,
    handle_quiz_submit,
    handle_tale_rating,
    handle_video_complete,
)

router = APIRouter(prefix="/api/v1/lessons", tags=["lessons"])


class LessonChildBody(BaseModel):
    child_id: uuid.UUID
    test_key: str | None = None


class VideoCompleteMobileBody(LessonChildBody):
    percent: float = Field(ge=0, le=1)


class QuizSubmitMobileBody(LessonChildBody):
    quiz_type: Literal["comprehension", "meaning_analysis"]
    answers: dict[str, str]


class EmotionQuizSubmitMobileBody(LessonChildBody):
    answers: dict[str, list[str]]


class ManualMarkMobileBody(LessonChildBody):
    event_type: Literal["creative_task", "live_meeting"]
    notes: str | None = Field(default=None, max_length=2000)


class TaleRatingMobileBody(LessonChildBody):
    rating: int = Field(ge=1, le=10)


def _child_in_family(db: Session, family: Family, child_id: uuid.UUID) -> Child:
    child = repo.get_child_with_family(db, child_id)
    if not child or child.family_id != family.id:
        raise HTTPException(403, "Ребёнок не найден в этой семье")
    return child


@router.get("/{slug}")
def lesson_json(
    slug: str,
    child: Child = Depends(get_family_child),
    test_key: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict:
    """Метаданные урока: видео, квизы, slovik, lesson_url для WebView."""
    return build_lesson_json(
        db,
        child=child,
        slug=slug,
        test_bypass=verify_test_lesson_key(test_key),
    )


@router.post("/{slug}/video-complete")
def video_complete_v1(
    slug: str,
    body: VideoCompleteMobileBody,
    request: Request,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child = _child_in_family(db, family, body.child_id)
    return handle_video_complete(
        db,
        child_id=child.id,
        slug=slug,
        percent=body.percent,
        test_key=body.test_key,
    )


@router.post("/{slug}/emotion-quiz")
def emotion_quiz_submit_v1(
    slug: str,
    body: EmotionQuizSubmitMobileBody,
    request: Request,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child = _child_in_family(db, family, body.child_id)
    return handle_emotion_quiz_submit(
        db,
        child_id=child.id,
        slug=slug,
        answers=body.answers,
        test_key=body.test_key,
    )


@router.post("/{slug}/quiz")
def quiz_submit_v1(
    slug: str,
    body: QuizSubmitMobileBody,
    request: Request,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child = _child_in_family(db, family, body.child_id)
    return handle_quiz_submit(
        db,
        child_id=child.id,
        slug=slug,
        quiz_type=body.quiz_type,
        answers=body.answers,
        test_key=body.test_key,
    )


@router.post("/{slug}/manual")
def manual_mark_v1(
    slug: str,
    body: ManualMarkMobileBody,
    request: Request,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child = _child_in_family(db, family, body.child_id)
    return handle_manual_mark(
        db,
        child_id=child.id,
        slug=slug,
        event_type=body.event_type,
        notes=body.notes,
        test_key=body.test_key,
    )


@router.post("/{slug}/rating")
def tale_rating_v1(
    slug: str,
    body: TaleRatingMobileBody,
    request: Request,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child = _child_in_family(db, family, body.child_id)
    return handle_tale_rating(
        db,
        child_id=child.id,
        slug=slug,
        rating=body.rating,
        test_key=body.test_key,
    )
