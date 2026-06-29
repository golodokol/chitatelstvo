from __future__ import annotations

import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from api.deps import rate_limit
from api.lesson_signing import verify_lesson_access
from api.test_lesson_auth import verify_test_lesson_key
from config.settings import ROOT, VIDEO_WATCH_THRESHOLD
from db.session import get_db
from lessons.loader import get_lesson, quiz_for_client
from services.lesson_player import (
    build_lesson_json,
    get_child_or_404,
    handle_emotion_quiz_submit,
    handle_manual_mark,
    handle_quiz_submit,
    handle_tale_rating,
    handle_video_complete,
)

router = APIRouter(tags=["lesson"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))


class LessonAuth(BaseModel):
    child_id: uuid.UUID
    exp: int
    sig: str = ""
    test_key: str | None = None

    @model_validator(mode="after")
    def _normalize_sig(self) -> "LessonAuth":
        if verify_test_lesson_key(self.test_key):
            if len(self.sig) < 8:
                self.sig = "00000000"
        elif len(self.sig) < 8:
            raise ValueError("sig must be at least 8 characters")
        return self


class VideoCompleteBody(LessonAuth):
    percent: float = Field(ge=0, le=1)


class QuizSubmitBody(LessonAuth):
    quiz_type: Literal["comprehension", "meaning_analysis"]
    answers: dict[str, str]


class EmotionQuizSubmitBody(LessonAuth):
    answers: dict[str, list[str]]


class ManualMarkBody(LessonAuth):
    event_type: Literal["creative_task", "live_meeting"]
    notes: str | None = Field(default=None, max_length=2000)


class TaleRatingBody(LessonAuth):
    rating: int = Field(ge=1, le=10)


def _verify_access(body: LessonAuth, slug: str) -> uuid.UUID:
    if verify_test_lesson_key(body.test_key):
        return body.child_id
    if not verify_lesson_access(body.child_id, slug, body.exp, body.sig):
        raise HTTPException(403, "Ссылка урока недействительна или устарела")
    return body.child_id


@router.get("/lesson/{slug}", response_class=HTMLResponse)
def lesson_page(
    slug: str,
    request: Request,
    child: uuid.UUID,
    exp: int,
    sig: str,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    test_key = request.query_params.get("test_key")
    test_bypass = verify_test_lesson_key(test_key)
    if not test_bypass and not verify_lesson_access(child, slug, exp, sig):
        raise HTTPException(403, "Ссылка урока недействительна или устарела")

    child_row = get_child_or_404(db, child)
    payload = build_lesson_json(db, child=child_row, slug=slug, test_bypass=test_bypass)

    return templates.TemplateResponse(
        request,
        "lesson.html",
        {
            "lesson": get_lesson(slug),
            "slug": slug,
            "child_id": str(child),
            "child_name": child_row.name,
            "exp": exp,
            "sig": sig,
            "video_threshold": VIDEO_WATCH_THRESHOLD,
            "video_src": payload["video"]["src"],
            "comprehension_quiz": payload["comprehension_quiz"],
            "meaning_quiz": payload["meaning_quiz"],
            "emotion_quiz": payload["emotion_quiz"],
            "slovik": payload["slovik"],
            "existing_rating": payload["existing_rating"],
            "can_rate": payload["can_rate"],
            "test_key": test_key if test_bypass else None,
        },
    )


@router.post("/api/lesson/{slug}/video-complete")
def video_complete(
    slug: str,
    body: VideoCompleteBody,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child_id = _verify_access(body, slug)
    get_child_or_404(db, child_id)
    return handle_video_complete(
        db,
        child_id=child_id,
        slug=slug,
        percent=body.percent,
        test_key=body.test_key,
    )


@router.post("/api/lesson/{slug}/emotion-quiz")
def emotion_quiz_submit(
    slug: str,
    body: EmotionQuizSubmitBody,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child_id = _verify_access(body, slug)
    get_child_or_404(db, child_id)
    return handle_emotion_quiz_submit(
        db,
        child_id=child_id,
        slug=slug,
        answers=body.answers,
        test_key=body.test_key,
    )


@router.post("/api/lesson/{slug}/quiz")
def quiz_submit(
    slug: str,
    body: QuizSubmitBody,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child_id = _verify_access(body, slug)
    get_child_or_404(db, child_id)
    return handle_quiz_submit(
        db,
        child_id=child_id,
        slug=slug,
        quiz_type=body.quiz_type,
        answers=body.answers,
        test_key=body.test_key,
    )


@router.post("/api/lesson/{slug}/manual")
def manual_mark(
    slug: str,
    body: ManualMarkBody,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child_id = _verify_access(body, slug)
    get_child_or_404(db, child_id)
    return handle_manual_mark(
        db,
        child_id=child_id,
        slug=slug,
        event_type=body.event_type,
        notes=body.notes,
        test_key=body.test_key,
    )


@router.post("/api/lesson/{slug}/rating")
def tale_rating(
    slug: str,
    body: TaleRatingBody,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child_id = _verify_access(body, slug)
    get_child_or_404(db, child_id)
    return handle_tale_rating(
        db,
        child_id=child_id,
        slug=slug,
        rating=body.rating,
        test_key=body.test_key,
    )
