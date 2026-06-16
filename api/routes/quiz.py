from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field

from api.deps import rate_limit
from config.settings import PUBLIC_BASE_URL, ROOT
from services.quiz_leads import LEADS_FILE, build_quiz_lead_rows, load_quiz_leads
from notifications.email_channel import send_email
from notifications.email_templates import (
    SUBJECT_QUIZ_AUTO,
    build_quiz_auto_email,
    build_quiz_auto_email_html,
)

router = APIRouter(tags=["quiz"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))

logger = logging.getLogger(__name__)

SITE_URL = "https://chitatelstvo.ru"
CHECKLIST_PDF = ROOT / "static" / "quiz-checklist.pdf"
CHECKLIST_PDF_NAME = "10-priznakov-chitatelstvo.pdf"
CHECKLIST_PDF_VERSION = "20260615b"


def checklist_pdf_url() -> str:
    """Public URL with cache-bust query (PDFs are aggressively cached by browsers)."""
    if CHECKLIST_PDF.is_file():
        v = int(CHECKLIST_PDF.stat().st_mtime)
        return f"{PUBLIC_BASE_URL}/quiz/checklist.pdf?v={v}"
    return f"{PUBLIC_BASE_URL}/quiz/checklist.pdf?v={CHECKLIST_PDF_VERSION}"

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


def _answers_by_id(answers: list[QuizAnswer]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in answers:
        if item.id:
            out[item.id] = item.answer
    return out


def _send_quiz_auto_email(body: QuizLeadRequest) -> bool:
    checklist_url = checklist_pdf_url()
    message = build_quiz_auto_email(
        parent_name=body.parent_name,
        child_name=body.child_name,
        child_age=body.child_age,
        answers_by_id=_answers_by_id(body.answers),
        checklist_url=checklist_url,
        site_url=SITE_URL,
    )
    html_message = build_quiz_auto_email_html(
        parent_name=body.parent_name,
        child_name=body.child_name,
        child_age=body.child_age,
        answers_by_id=_answers_by_id(body.answers),
        checklist_url=checklist_url,
        site_url=SITE_URL,
        assets_url=PUBLIC_BASE_URL,
    )
    attachments = []
    if CHECKLIST_PDF.is_file():
        attachments.append((CHECKLIST_PDF_NAME, CHECKLIST_PDF))
    send_email(str(body.parent_email), SUBJECT_QUIZ_AUTO, message, html_message, attachments)
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


@router.post("/api/quiz/lead")
def quiz_lead(body: QuizLeadRequest, request: Request, _: None = Depends(rate_limit)) -> dict:
    answers = [a for a in body.answers if a.answer.strip()]
    if not answers:
        raise HTTPException(422, "Ответьте хотя бы на один вопрос квиза")
    body = body.model_copy(update={"answers": answers})
    LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ip": request.client.host if request.client else None,
        "parent_name": body.parent_name,
        "parent_email": str(body.parent_email),
        "phone": body.phone,
        "child_name": body.child_name,
        "child_age": body.child_age,
        "answers": [a.model_dump() for a in body.answers],
    }
    with LEADS_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    email_sent = False
    try:
        email_sent = _send_quiz_auto_email(body)
    except Exception:
        logger.exception("Не удалось отправить автоматическое письмо квиза на %s", body.parent_email)

    return {
        "ok": True,
        "email_sent": email_sent,
        "checklist_url": checklist_pdf_url(),
        "message": (
            "Спасибо! PDF-чек-лист уже отправлен на email. "
            "Личное письмо от основателя школы придёт чуть позже."
        ),
    }
