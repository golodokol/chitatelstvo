"""Публичная выдача бесплатного пробного early-курса."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from api.deps import rate_limit
from config.settings import PUBLIC_BASE_URL
from db.session import get_db
from notifications.email_channel import send_email
from notifications.email_templates import (
    EARLY_COURSE_COPY,
    SUBJECT_QUIZ_EARLY,
    build_early_trial_email,
    build_early_trial_email_html,
    early_course_key,
)
from services.early_trial import grant_early_trial, resolve_trial_module_id
from services.early_trial_leads import append_early_trial_lead
from services.founder_letter_queue import schedule_founder_letter
from services.recommendation_rules import match_recommendation_rule_by_trial_slug

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
    consent_privacy: bool = False
    consent_offer: bool = False
    consent_marketing: bool = False


@router.post("/api/early/trial")
def early_trial_lead(
    body: EarlyTrialLead,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit),
) -> dict:
    if not resolve_trial_module_id(trial_slug=body.trial_slug):
        raise HTTPException(400, "Неизвестный пробный урок")
    if not body.consent_privacy or not body.consent_offer:
        raise HTTPException(
            400,
            "Нужно согласие с политикой конфиденциальности и публичной офертой",
        )

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

    course_key = early_course_key(body.trial_slug)
    course_label = EARLY_COURSE_COPY[course_key]["label"]
    title = body.trial_title or access.get("lesson_title") or "Пробный урок"

    try:
        append_early_trial_lead(
            {
                "parent_name": body.parent_name,
                "parent_email": str(body.parent_email).lower(),
                "phone": body.phone or "",
                "child_name": body.child_name,
                "child_age": body.child_age,
                "trial_slug": body.trial_slug,
                "trial_title": title,
                "course_group": course_key,
                "course_label": course_label,
                "consent_privacy": bool(body.consent_privacy),
                "consent_offer": bool(body.consent_offer),
                "consent_marketing": bool(body.consent_marketing),
                "lesson_url": access.get("lesson_url"),
                "family_id": access.get("family_id"),
                "child_id": access.get("child_id"),
            }
        )
    except Exception:
        logger.exception("early trial lead save failed for %s", body.parent_email)

    try:
        message = build_early_trial_email(
            parent_name=body.parent_name,
            child_name=body.child_name,
            child_age=body.child_age,
            trial_title=title,
            trial_lesson_url=access["lesson_url"],
            trial_progress_url=access["progress_url"],
            trial_slug=body.trial_slug,
            course_group=course_key,
            site_url=SITE_URL,
        )
        html_message = build_early_trial_email_html(
            parent_name=body.parent_name,
            child_name=body.child_name,
            child_age=body.child_age,
            trial_title=title,
            trial_lesson_url=access["lesson_url"],
            trial_progress_url=access["progress_url"],
            trial_slug=body.trial_slug,
            course_group=course_key,
            site_url=SITE_URL,
            assets_url=PUBLIC_BASE_URL,
        )
        send_email(str(body.parent_email), SUBJECT_QUIZ_EARLY, message, html_message)
        email_sent = True
    except Exception:
        logger.exception("early trial email failed for %s", body.parent_email)
        email_sent = False

    rule = match_recommendation_rule_by_trial_slug(body.trial_slug)
    if rule:
        try:
            schedule_founder_letter(
                lead_id=str(uuid.uuid4()),
                parent_email=str(body.parent_email),
                payload={
                    "rule_id": rule.rule_id,
                    "parent_name": body.parent_name,
                    "child_name": body.child_name,
                    "child_age": body.child_age,
                    "trial_lesson_url": access.get("lesson_url"),
                    "trial_progress_url": access.get("progress_url"),
                    "trial_title": title,
                },
            )
        except Exception:
            logger.exception("founder letter schedule failed for %s", body.parent_email)

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
