from __future__ import annotations

import uuid
from typing import Any, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from api.deps import rate_limit
from api.lesson_signing import verify_lesson_access
from api.test_lesson_auth import verify_test_lesson_key
from config.settings import ROOT, VIDEO_BADGE_THRESHOLD, VIDEO_UNLOCK_SECONDS
from db.session import get_db
from lessons.step_labels import lesson_step_badges_for_lesson, lesson_step_labels_payload
from services.creative_upload import handle_creative_upload
from services.lesson_player import (
    build_lesson_json,
    get_child_or_404,
    handle_emotion_quiz_submit,
    handle_manual_mark,
    handle_quiz_submit,
    handle_reading_practice_submit,
    handle_retelling_submit,
    handle_tale_rating,
    handle_video_unlock,
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


class VideoUnlockBody(LessonAuth):
    watched_seconds: float = Field(ge=0)
    duration_seconds: float | None = Field(default=None, ge=0)


class QuizSubmitBody(LessonAuth):
    quiz_type: Literal["comprehension", "meaning_analysis"]
    answers: dict[str, Any]


class EmotionQuizSubmitBody(LessonAuth):
    answers: dict[str, list[str]]


class RetellingSubmitBody(LessonAuth):
    answers: dict[str, Any]


class ReadingPracticeSubmitBody(LessonAuth):
    cards_read: list[str]


class ManualMarkBody(LessonAuth):
    event_type: Literal["creative_task", "live_meeting"]
    notes: str | None = Field(default=None, max_length=2000)


class TaleRatingBody(LessonAuth):
    rating: int = Field(ge=1, le=10)


def _verify_access_fields(
    child_id: uuid.UUID,
    slug: str,
    exp: int,
    sig: str,
    test_key: str | None,
) -> uuid.UUID:
    if verify_test_lesson_key(test_key):
        return child_id
    if not verify_lesson_access(child_id, slug, exp, sig):
        raise HTTPException(403, "Ссылка урока недействительна или устарела")
    return child_id


def _verify_access(body: LessonAuth, slug: str) -> uuid.UUID:
    return _verify_access_fields(body.child_id, slug, body.exp, body.sig, body.test_key)


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
    nav_urls = {
        "progress_url": payload["progress_url"],
        "chest_url": payload["chest_url"],
    }

    return templates.TemplateResponse(
        request,
        "lesson.html",
        {
            "lesson": payload["lesson"],
            "slug": slug,
            "child_id": str(child),
            "child_name": child_row.name,
            "progress_url": nav_urls["progress_url"],
            "chest_url": nav_urls["chest_url"],
            "exp": exp,
            "sig": sig,
            "video_threshold": VIDEO_BADGE_THRESHOLD,
            "video_unlock_seconds": VIDEO_UNLOCK_SECONDS,
            "video_unlock_minutes": max(1, VIDEO_UNLOCK_SECONDS // 60),
            "video_badge_threshold": VIDEO_BADGE_THRESHOLD,
            "video_src": payload["video"]["src"],
            "comprehension_quiz": payload["comprehension_quiz"],
            "reading_practice": payload.get("reading_practice"),
            "meaning_quiz": payload["meaning_quiz"],
            "retelling_quiz": payload["retelling_quiz"],
            "emotion_quiz": payload["emotion_quiz"],
            "creative_tasks": payload.get("creative_tasks"),
            "live_lesson": payload.get("live_lesson"),
            "slovik": payload["slovik"],
            "existing_rating": payload["existing_rating"],
            "can_rate": payload["can_rate"],
            "progress": payload["progress"],
            "test_key": test_key if test_bypass else None,
            "step_labels": lesson_step_labels_payload(),
            "step_badges": lesson_step_badges_for_lesson(payload["lesson"]),
        },
    )


@router.post("/api/lesson/{slug}/reading-practice")
def reading_practice_submit(
    slug: str,
    body: ReadingPracticeSubmitBody,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child_id = _verify_access(body, slug)
    get_child_or_404(db, child_id)
    return handle_reading_practice_submit(
        db,
        child_id=child_id,
        slug=slug,
        cards_read=body.cards_read,
        test_key=body.test_key,
    )


@router.post("/api/lesson/{slug}/video-unlock")
def video_unlock(
    slug: str,
    body: VideoUnlockBody,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child_id = _verify_access(body, slug)
    get_child_or_404(db, child_id)
    return handle_video_unlock(
        db,
        child_id=child_id,
        slug=slug,
        watched_seconds=body.watched_seconds,
        duration_seconds=body.duration_seconds,
        test_key=body.test_key,
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


@router.post("/api/lesson/{slug}/retelling")
def retelling_submit(
    slug: str,
    body: RetellingSubmitBody,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child_id = _verify_access(body, slug)
    get_child_or_404(db, child_id)
    return handle_retelling_submit(
        db,
        child_id=child_id,
        slug=slug,
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


@router.post("/api/lesson/{slug}/creative-upload")
async def creative_upload(
    slug: str,
    request: Request,
    child_id: uuid.UUID = Form(...),
    exp: int = Form(...),
    sig: str = Form(""),
    test_key: str | None = Form(None),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    verified_id = _verify_access_fields(child_id, slug, exp, sig, test_key)
    get_child_or_404(db, verified_id)
    return await handle_creative_upload(
        db,
        child_id=verified_id,
        slug=slug,
        files=files,
        test_key=test_key,
    )
