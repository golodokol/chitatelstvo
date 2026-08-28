from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field

from api.deps import rate_limit
from config.settings import PUBLIC_BASE_URL, ROOT
from db.session import get_db
from notifications.email_channel import send_email
from notifications.email_templates import (
    SUBJECT_QUIZ_AUTO,
    SUBJECT_QUIZ_EARLY,
    build_quiz_auto_email,
    build_quiz_auto_email_html,
)
from services.early_trial import grant_early_trial, resolve_trial_module_id
from services.quiz_leads import LEADS_FILE, build_quiz_lead_rows, load_quiz_leads
from sqlalchemy.orm import Session

router = APIRouter(tags=["quiz"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))

logger = logging.getLogger(__name__)

SITE_URL = "https://chitatelstvo.ru"
CHECKLIST_PDF = ROOT / "static" / "quiz-checklist.pdf"
CHECKLIST_PDF_EARLY = ROOT / "static" / "quiz-checklist-early.pdf"
CHECKLIST_PDF_NAME = "10-priznakov-chitatelstvo.pdf"
CHECKLIST_PDF_EARLY_NAME = "10-priznakov-myagkiy-start.pdf"
CHECKLIST_PDF_VERSION = "20260827a"


def checklist_pdf_path(*, early: bool = False) -> Path:
    return CHECKLIST_PDF_EARLY if early else CHECKLIST_PDF


def checklist_pdf_name(*, early: bool = False) -> str:
    return CHECKLIST_PDF_EARLY_NAME if early else CHECKLIST_PDF_NAME


def checklist_pdf_url(*, early: bool = False) -> str:
    """Public URL with cache-bust query (PDFs are aggressively cached by browsers)."""
    path = checklist_pdf_path(early=early)
    slug = "checklist-early.pdf" if early else "checklist.pdf"
    if path.is_file():
        v = int(path.stat().st_mtime)
        return f"{PUBLIC_BASE_URL}/quiz/{slug}?v={v}"
    return f"{PUBLIC_BASE_URL}/quiz/{slug}?v={CHECKLIST_PDF_VERSION}"

PAGE_CONTEXT = {
    "site_url": SITE_URL,
    "api_url": PUBLIC_BASE_URL,
    "legal_politika": f"{PUBLIC_BASE_URL}/legal/politika",
}


class QuizAnswer(BaseModel):
    id: str | None = None
    question: str = Field(min_length=1, max_length=300)
    answer: str = Field(min_length=1, max_length=300)


class QuizLeadRequest(BaseModel):
    parent_name: str = Field(min_length=1, max_length=200)
    parent_email: EmailStr
    phone: str = Field(default='', max_length=40)
    child_name: str = Field(min_length=1, max_length=100)
    child_age: int | None = Field(default=None, ge=1, le=99)
    answers: list[QuizAnswer] = Field(min_length=1, max_length=10)
    trial_age: str | None = Field(default=None, max_length=20)
    trial_slug: str | None = Field(default=None, max_length=120)
    trial_title: str | None = Field(default=None, max_length=200)
    quiz_variant: str | None = Field(default=None, max_length=20)


def _answers_by_id(answers: list[QuizAnswer]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in answers:
        if item.id:
            out[item.id] = item.answer
    return out


def _send_quiz_auto_email(
    body: QuizLeadRequest,
    *,
    trial_access: dict | None = None,
) -> bool:
    quiz_variant = (body.quiz_variant or "").strip() or None
    if not quiz_variant and resolve_trial_module_id(trial_slug=body.trial_slug):
        quiz_variant = "early"
    is_early = quiz_variant == "early"
    checklist_url = checklist_pdf_url(early=is_early)
    trial_title = body.trial_title
    trial_lesson_url = None
    trial_progress_url = None
    if trial_access:
        trial_title = trial_access.get("lesson_title") or trial_title
        trial_lesson_url = trial_access.get("lesson_url")
        trial_progress_url = trial_access.get("progress_url")
    message = build_quiz_auto_email(
        parent_name=body.parent_name,
        child_name=body.child_name,
        child_age=body.child_age,
        answers_by_id=_answers_by_id(body.answers),
        checklist_url=checklist_url,
        site_url=SITE_URL,
        trial_title=trial_title,
        trial_lesson_url=trial_lesson_url,
        trial_progress_url=trial_progress_url,
        quiz_variant=quiz_variant,
    )
    html_message = build_quiz_auto_email_html(
        parent_name=body.parent_name,
        child_name=body.child_name,
        child_age=body.child_age,
        answers_by_id=_answers_by_id(body.answers),
        checklist_url=checklist_url,
        site_url=SITE_URL,
        assets_url=PUBLIC_BASE_URL,
        trial_title=trial_title,
        trial_lesson_url=trial_lesson_url,
        trial_progress_url=trial_progress_url,
        quiz_variant=quiz_variant,
    )
    attachments = []
    pdf_path = checklist_pdf_path(early=is_early)
    if pdf_path.is_file():
        attachments.append((checklist_pdf_name(early=is_early), pdf_path))
    subject = SUBJECT_QUIZ_EARLY if is_early else SUBJECT_QUIZ_AUTO
    send_email(str(body.parent_email), subject, message, html_message, attachments)
    return True


@router.get("/quiz", response_class=HTMLResponse)
def quiz_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "quiz/page.html", PAGE_CONTEXT)


@router.get("/quiz/checklist", response_class=HTMLResponse)
def quiz_checklist(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "quiz/checklist.html", PAGE_CONTEXT)


@router.get("/quiz/checklist.pdf")
def quiz_checklist_pdf() -> FileResponse:
    if not CHECKLIST_PDF.is_file():
        raise HTTPException(404, "PDF-чек-лист пока недоступен")
    return FileResponse(
        CHECKLIST_PDF,
        media_type="application/pdf",
        filename=CHECKLIST_PDF_NAME,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )


@router.get("/quiz/checklist-early.pdf")
def quiz_checklist_early_pdf() -> FileResponse:
    if not CHECKLIST_PDF_EARLY.is_file():
        raise HTTPException(404, "PDF-чек-лист пока недоступен")
    return FileResponse(
        CHECKLIST_PDF_EARLY,
        media_type="application/pdf",
        filename=CHECKLIST_PDF_EARLY_NAME,
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )


@router.post("/api/quiz/lead")
def quiz_lead(
    body: QuizLeadRequest,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit),
) -> dict:
    answers = [a for a in body.answers if a.answer.strip()]
    if not answers:
        raise HTTPException(422, "Ответьте хотя бы на один вопрос квиза")
    body = body.model_copy(update={"answers": answers})

    trial_access = None
    if resolve_trial_module_id(trial_slug=body.trial_slug):
        try:
            trial_access = grant_early_trial(
                db,
                parent_name=body.parent_name,
                parent_email=str(body.parent_email),
                child_name=body.child_name,
                child_age=body.child_age,
                phone=body.phone,
                trial_slug=body.trial_slug,
            )
        except Exception:
            logger.exception("Не удалось выдать пробный early для %s", body.parent_email)

    LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ip": request.client.host if request.client else None,
        "parent_name": body.parent_name,
        "parent_email": str(body.parent_email),
        "phone": body.phone,
        "child_name": body.child_name,
        "child_age": body.child_age,
        "answers": [a.model_dump() for a in body.answers],
        "trial_age": body.trial_age,
        "trial_slug": body.trial_slug,
        "trial_title": body.trial_title,
        "quiz_variant": body.quiz_variant,
        "trial_module_id": (trial_access or {}).get("module_id"),
        "trial_lesson_url": (trial_access or {}).get("lesson_url"),
    }
    with LEADS_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    email_sent = False
    try:
        email_sent = _send_quiz_auto_email(body, trial_access=trial_access)
    except Exception:
        logger.exception("Не удалось отправить автоматическое письмо квиза на %s", body.parent_email)

    if trial_access and trial_access.get("lesson_url"):
        if email_sent:
            message = "Спасибо! Пробный урок открыт — ссылка и PDF уже на email."
        else:
            message = "Спасибо! Пробный урок открыт. Если письмо не пришло — откройте ссылку на этой странице."
    elif email_sent:
        message = "Спасибо! PDF-чек-лист уже отправлен на email."
    else:
        message = "Спасибо! Заявка принята."

    is_early = (body.quiz_variant or "").strip() == "early" or bool(
        resolve_trial_module_id(trial_slug=body.trial_slug)
    )
    return {
        "ok": True,
        "email_sent": email_sent,
        "checklist_url": checklist_pdf_url(early=is_early),
        "trial_lesson_url": (trial_access or {}).get("lesson_url"),
        "trial_progress_url": (trial_access or {}).get("progress_url"),
        "message": message,
    }
