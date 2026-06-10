from __future__ import annotations

import uuid
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.deps import rate_limit
from api.lesson_signing import verify_lesson_access
from config.settings import ROOT, VIDEO_WATCH_THRESHOLD
from db import repository as repo
from db.session import get_db
from lessons.loader import get_lesson, quiz_for_client, score_quiz
from api.event_types import MANUAL_MARK_ONLY
from services.events import submit_learning_event
from storage.yandex import resolve_video_src

router = APIRouter(tags=["lesson"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))


class LessonAuth(BaseModel):
    child_id: uuid.UUID
    exp: int
    sig: str = Field(min_length=8)


class VideoCompleteBody(LessonAuth):
    percent: float = Field(ge=0, le=1)


class QuizSubmitBody(LessonAuth):
    quiz_type: Literal["comprehension", "meaning_analysis"]
    answers: dict[str, str]


class ManualMarkBody(LessonAuth):
    event_type: Literal["creative_task", "live_meeting"]
    notes: str | None = Field(default=None, max_length=2000)


def _verify_access(body: LessonAuth, slug: str) -> uuid.UUID:
    if not verify_lesson_access(body.child_id, slug, body.exp, body.sig):
        raise HTTPException(403, "Ссылка урока недействительна или устарела")
    return body.child_id


def _get_child_or_404(db: Session, child_id: uuid.UUID):
    child = repo.get_child_with_family(db, child_id)
    if not child:
        raise HTTPException(404, "Ребёнок не найден")
    return child


@router.get("/lesson/{slug}", response_class=HTMLResponse)
def lesson_page(
    slug: str,
    request: Request,
    child: uuid.UUID,
    exp: int,
    sig: str,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    if not verify_lesson_access(child, slug, exp, sig):
        raise HTTPException(403, "Ссылка урока недействительна или устарела")

    lesson = get_lesson(slug)
    if not lesson:
        raise HTTPException(404, "Урок не найден")

    child_row = _get_child_or_404(db, child)

    video = lesson.get("video", {})
    video_src = None
    if video.get("type") in ("yandex", "html5"):
        video_src = resolve_video_src(video)

    return templates.TemplateResponse(
        request,
        "lesson.html",
        {
            "lesson": lesson,
            "slug": slug,
            "child_id": str(child),
            "child_name": child_row.name,
            "exp": exp,
            "sig": sig,
            "video_threshold": VIDEO_WATCH_THRESHOLD,
            "video_src": video_src,
            "comprehension_quiz": quiz_for_client(lesson["comprehension_quiz"]),
            "meaning_quiz": quiz_for_client(lesson["meaning_quiz"]),
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
    _get_child_or_404(db, child_id)

    lesson = get_lesson(slug)
    if not lesson:
        raise HTTPException(404, "Урок не найден")

    if body.percent < VIDEO_WATCH_THRESHOLD:
        raise HTTPException(400, f"Нужно досмотреть минимум {int(VIDEO_WATCH_THRESHOLD * 100)}%")

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type="lesson_complete",
        tale_title=lesson["title"],
        lesson_date=date.today(),
        notes=f"auto: video {int(body.percent * 100)}%",
        payload={"source": "lesson_player", "percent": body.percent},
    )
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "message": "Урок засчитан" if status == "accepted" else "Уже было засчитано ранее",
    }


@router.post("/api/lesson/{slug}/quiz")
def quiz_submit(
    slug: str,
    body: QuizSubmitBody,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child_id = _verify_access(body, slug)
    _get_child_or_404(db, child_id)

    lesson = get_lesson(slug)
    if not lesson:
        raise HTTPException(404, "Урок не найден")

    quiz_key = "comprehension_quiz" if body.quiz_type == "comprehension" else "meaning_quiz"
    quiz = lesson[quiz_key]
    correct, total = score_quiz(quiz, body.answers)
    passed = correct >= int(quiz.get("pass_score", total))

    if not passed:
        return {
            "status": "failed",
            "score": correct,
            "total": total,
            "message": "Попробуйте ещё раз — перечитайте вопросы вместе с ребёнком.",
        }

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type=body.quiz_type,
        tale_title=lesson["title"],
        lesson_date=date.today(),
        notes=f"auto: quiz {correct}/{total}",
        payload={"source": "lesson_player", "score": correct, "total": total},
    )
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "score": correct,
        "total": total,
        "message": "Задание засчитано!" if status == "accepted" else "Уже было засчитано ранее",
    }


@router.post("/api/lesson/{slug}/manual")
def manual_mark(
    slug: str,
    body: ManualMarkBody,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child_id = _verify_access(body, slug)
    _get_child_or_404(db, child_id)

    lesson = get_lesson(slug)
    if not lesson:
        raise HTTPException(404, "Урок не найден")

    if body.event_type not in MANUAL_MARK_ONLY:
        raise HTTPException(400, "Этот тип события только для ручной отметки")

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type=body.event_type,
        tale_title=lesson["title"],
        lesson_date=date.today(),
        notes=body.notes or "manual: parent mark",
        payload={"source": "lesson_player_manual", "event_type": body.event_type},
    )
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "message": "Отметка сохранена" if status == "accepted" else "Уже отмечено ранее",
    }
