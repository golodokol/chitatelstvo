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
from config.settings import LESSON_WEEK_DAYS, ROOT, VIDEO_WATCH_THRESHOLD
from db import repository as repo
from db.session import get_db
from catalog.loader import get_module
from lessons.access import is_lesson_unlocked
from lessons.enrollment_access import child_can_access_lesson, get_active_enrollment
from lessons.schedule import effective_module_week
from lessons.loader import get_lesson, quiz_for_client, score_quiz
from api.event_types import MANUAL_MARK_ONLY
from services.events import submit_learning_event
from gamification.sloviki import LESSON_STEP_SLOVIK, lesson_step_key, slovik_url, slovik_urls
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


class TaleRatingBody(LessonAuth):
    rating: int = Field(ge=1, le=10)


def _verify_access(body: LessonAuth, slug: str) -> uuid.UUID:
    if not verify_lesson_access(body.child_id, slug, body.exp, body.sig):
        raise HTTPException(403, "Ссылка урока недействительна или устарела")
    return body.child_id


def _get_child_or_404(db: Session, child_id: uuid.UUID):
    child = repo.get_child_with_family(db, child_id)
    if not child:
        raise HTTPException(404, "Ребёнок не найден")
    return child


def _require_lesson_unlocked(db: Session, child_id: uuid.UUID, lesson: dict) -> None:
    child = _get_child_or_404(db, child_id)
    enrollment = get_active_enrollment(child)
    if not child_can_access_lesson(child, lesson, enrollment):
        raise HTTPException(403, "Этот урок недоступен для вашего модуля.")
    module = get_module(enrollment.module_id) if enrollment else None
    if not is_lesson_unlocked(
        child,
        lesson,
        week_days=LESSON_WEEK_DAYS,
        enrollment=enrollment,
        module=module,
    ):
        week = effective_module_week(lesson, enrollment, module)
        raise HTTPException(
            403,
            f"Урок недели {week} ещё закрыт. Новая сказка откроется по расписанию модуля.",
        )
    if lesson.get("module_id") is not None and not lesson.get("active", True):
        raise HTTPException(403, "Урок ещё готовится — скоро появится на странице прогресса.")


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

    _require_lesson_unlocked(db, child, lesson)
    child_row = _get_child_or_404(db, child)

    video = lesson.get("video", {})
    video_src = None
    if video.get("type") in ("yandex", "html5"):
        video_src = resolve_video_src(video)

    comprehension = lesson.get("comprehension_quiz")
    meaning = lesson.get("meaning_quiz")

    initial_step = lesson_step_key(
        has_comprehension=bool(comprehension),
        has_meaning=bool(meaning),
    )
    slovik = {
        "urls": slovik_urls(),
        "initial_step": initial_step,
        "initial_url": slovik_url(initial_step),
        "step_keys": LESSON_STEP_SLOVIK,
    }

    existing_rating = repo.get_tale_rating(db, child, slug)
    can_rate = repo.child_has_lesson_complete(db, child, tale_title=lesson["title"])

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
            "comprehension_quiz": quiz_for_client(comprehension) if comprehension else None,
            "meaning_quiz": quiz_for_client(meaning) if meaning else None,
            "slovik": slovik,
            "existing_rating": existing_rating.rating if existing_rating else None,
            "can_rate": can_rate,
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

    _require_lesson_unlocked(db, child_id, lesson)

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

    _require_lesson_unlocked(db, child_id, lesson)

    quiz_key = "comprehension_quiz" if body.quiz_type == "comprehension" else "meaning_quiz"
    quiz = lesson.get(quiz_key)
    if not quiz:
        raise HTTPException(404, "Квиз для этого урока ещё не настроен")
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

    _require_lesson_unlocked(db, child_id, lesson)

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


@router.post("/api/lesson/{slug}/rating")
def tale_rating(
    slug: str,
    body: TaleRatingBody,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    rate_limit(request)
    child_id = _verify_access(body, slug)
    _get_child_or_404(db, child_id)

    lesson = get_lesson(slug)
    if not lesson:
        raise HTTPException(404, "Урок не найден")

    _require_lesson_unlocked(db, child_id, lesson)

    if not repo.child_has_lesson_complete(db, child_id, tale_title=lesson["title"]):
        raise HTTPException(400, "Сначала нужно досмотреть видео-урок по сказке.")

    row = repo.save_tale_rating(
        db,
        child_id=child_id,
        tale_slug=slug,
        tale_title=lesson["title"],
        rating=body.rating,
    )
    return {
        "status": "saved",
        "rating": row.rating,
        "message": "Спасибо! Оценка попала в читательский дневник.",
    }
