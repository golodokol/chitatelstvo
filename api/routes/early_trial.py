"""Публичная выдача бесплатного пробного early-курса."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from api.deps import rate_limit
from db.session import get_db
from services.early_trial import grant_early_trial, resolve_trial_module_id
from notifications.email_channel import send_email
from notifications.email_templates import (
    SUBJECT_QUIZ_AUTO,
    build_quiz_auto_email,
    build_quiz_auto_email_html,
)
from config.settings import PUBLIC_BASE_URL

logger = logging.getLogger(__name__)
router = APIRouter(tags=["early-trial"])

SITE_URL = "https://chitatelstvo.ru"


class EarlyTrialLead(BaseModel):
    parent_name: str = Field(min_length=1, max_length=200)
    parent_email: EmailStr
    phone: str = Field(default="", max_length=40)
    child_name: str = Field(min_length=1, max_length=100)
    child_age: int | None = Field(default=None, ge=1, le=99)
    trial_slug: str = Field(min_length=1, max_length=120)
    trial_title: str | None = Field(default=None, max_length=200)


@router.post("/api/early/trial")
def early_trial_lead(
    body: EarlyTrialLead,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit),
) -> dict:
    if not resolve_trial_module_id(trial_slug=body.trial_slug):
        raise HTTPException(400, "Неизвестный пробный урок")

    try:
        access = grant_early_trial(
            db,
            parent_name=body.parent_name,
            parent_email=str(body.parent_email),
            child_name=body.child_name,
            child_age=body.child_age,
            phone=body.phone,
            trial_slug=body.trial_slug,
        )
    except Exception:
        logger.exception("early trial grant failed for %s", body.parent_email)
        raise HTTPException(500, "Не удалось открыть пробный урок") from None

    if not access:
        raise HTTPException(400, "Не удалось открыть пробный урок")

    title = body.trial_title or access.get("lesson_title") or "Пробный урок"
    try:
        message = build_quiz_auto_email(
            parent_name=body.parent_name,
            child_name=body.child_name,
            child_age=body.child_age,
            answers_by_id={},
            checklist_url=f"{PUBLIC_BASE_URL}/quiz/checklist.pdf",
            site_url=SITE_URL,
            trial_title=title,
            trial_lesson_url=access["lesson_url"],
            trial_progress_url=access["progress_url"],
        )
        html_message = build_quiz_auto_email_html(
            parent_name=body.parent_name,
            child_name=body.child_name,
            child_age=body.child_age,
            answers_by_id={},
            checklist_url=f"{PUBLIC_BASE_URL}/quiz/checklist.pdf",
            site_url=SITE_URL,
            assets_url=PUBLIC_BASE_URL,
            trial_title=title,
            trial_lesson_url=access["lesson_url"],
            trial_progress_url=access["progress_url"],
        )
        send_email(str(body.parent_email), SUBJECT_QUIZ_AUTO, message, html_message)
        email_sent = True
    except Exception:
        logger.exception("early trial email failed for %s", body.parent_email)
        email_sent = False

    return {
        "ok": True,
        "email_sent": email_sent,
        "lesson_url": access["lesson_url"],
        "progress_url": access["progress_url"],
        "lesson_title": access.get("lesson_title"),
        "message": "Пробный урок открыт. Ссылка отправлена на email."
        if email_sent
        else "Пробный урок открыт. Если письмо не пришло — сохраните ссылку ниже.",
    }
