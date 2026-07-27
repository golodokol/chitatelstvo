from __future__ import annotations

import html as html_lib

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.deps import rate_limit
from config.settings import CONTACT_EMAIL, PUBLIC_BASE_URL, ROOT
from db import repository as repo
from db.session import get_db
from notifications.email_channel import send_email
from services.cabinet import build_family_cabinet

router = APIRouter(tags=["progress"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))


class ParentFeedbackRequest(BaseModel):
    message: str = Field(min_length=5, max_length=4000)
    child_name: str = Field(default="", max_length=120)


@router.get("/progress/{token}", response_class=HTMLResponse)
def family_progress(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    family = repo.get_family_by_token(db, token)
    if not family:
        raise HTTPException(404, "Страница не найдена")

    payload = build_family_cabinet(db, family)
    return templates.TemplateResponse(
        request,
        "progress.html",
        {
            "progress_token": token,
            "open_chest": request.query_params.get("open_chest") == "1",
            "chest_tale": (request.query_params.get("chest") or "").strip(),
            "parent_name": payload["parent_name"],
            "assets_url": PUBLIC_BASE_URL,
            "logo_url": f"{PUBLIC_BASE_URL}/assets/logo-chitatelstvo.png",
            "channel": payload["notification_channel"],
            "telegram_linked": payload["telegram"]["linked"],
            "telegram_enabled": payload["telegram"]["enabled"],
            "telegram_link": payload["telegram"]["deep_link"],
            "link_page": f"/link-telegram/{token}/page",
            "children": payload["children"],
            "module_start_date": payload["module_start_date"],
            "notifications": payload["notifications"],
            "parent_guide": payload["parent_guide"],
            "contact_email": CONTACT_EMAIL,
        },
    )


@router.post("/progress/{token}/feedback")
def parent_feedback(
    token: str,
    body: ParentFeedbackRequest,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit),
) -> dict:
    family = repo.get_family_by_token(db, token)
    if not family:
        raise HTTPException(404, "Страница не найдена")

    message = body.message.strip()
    if len(message) < 5:
        raise HTTPException(422, "Напишите вопрос чуть подробнее")

    child_name = (body.child_name or "").strip()
    child_line = f"Ребёнок: {child_name}\n" if child_name else ""
    progress_url = f"{PUBLIC_BASE_URL}/progress/{token}"
    subject = f"Срочный вопрос от родителя: {family.parent_name}"
    safe_parent = html_lib.escape(family.parent_name)
    safe_email = html_lib.escape(family.parent_email)
    safe_child = html_lib.escape(child_name)
    safe_message = html_lib.escape(message)
    text = (
        f"Срочный вопрос со страницы родителя\n\n"
        f"Родитель: {family.parent_name}\n"
        f"Email: {family.parent_email}\n"
        f"{child_line}"
        f"Страница: {progress_url}\n\n"
        f"Сообщение:\n{message}\n"
    )
    html = (
        "<p><strong>Срочный вопрос</strong> со страницы родителя</p>"
        f"<p>Родитель: {safe_parent}<br>"
        f"Email: <a href=\"mailto:{safe_email}\">{safe_email}</a><br>"
        f"{('Ребёнок: ' + safe_child + '<br>') if child_name else ''}"
        f"Страница: <a href=\"{html_lib.escape(progress_url)}\">{html_lib.escape(progress_url)}</a></p>"
        f"<p style=\"white-space:pre-wrap\">{safe_message}</p>"
    )

    if not CONTACT_EMAIL:
        raise HTTPException(503, "Почта для обратной связи не настроена")

    try:
        send_email(CONTACT_EMAIL, subject, text, html)
    except Exception as exc:
        raise HTTPException(502, "Не удалось отправить сообщение. Попробуйте позже или напишите на " + CONTACT_EMAIL) from exc

    return {"ok": True, "detail": "Сообщение отправлено"}
