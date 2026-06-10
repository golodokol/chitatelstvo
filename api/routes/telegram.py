from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from config.settings import PUBLIC_BASE_URL, ROOT, TELEGRAM_WEBHOOK_SECRET
from db import repository as repo
from db.session import SessionLocal
from notifications.telegram_bot import (
    build_link_url,
    extract_message,
    get_bot_username,
    linked_text,
    parse_start_token,
    send_reply,
    welcome_text,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["telegram"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def _verify_telegram_secret(x_telegram_bot_api_secret_token: str | None = Header(default=None)) -> None:
    if TELEGRAM_WEBHOOK_SECRET and x_telegram_bot_api_secret_token != TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(401, "Неверный Telegram webhook secret")


@router.post("/telegram/webhook", dependencies=[])
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, bool]:
    if TELEGRAM_WEBHOOK_SECRET:
        _verify_telegram_secret(x_telegram_bot_api_secret_token)

    update: dict[str, Any] = await request.json()
    parsed = extract_message(update)
    if not parsed:
        return {"ok": True}

    chat_id, text, username = parsed
    token = parse_start_token(text)

    db: Session = SessionLocal()
    try:
        if token:
            family = repo.link_telegram_chat(
                db,
                progress_token=token,
                chat_id=chat_id,
                username=username,
            )
            if family:
                full = repo.get_family_by_token(db, token)
                child_names = [c.name for c in full.children] if full and full.children else []
                send_reply(chat_id, linked_text(family.parent_name, child_names))
            else:
                send_reply(
                    chat_id,
                    "Ссылка устарела или неверна. Откройте «Привязать Telegram» на личной странице прогресса.",
                )
        elif text and text.strip().startswith("/start"):
            send_reply(chat_id, welcome_text())
        else:
            send_reply(
                chat_id,
                "Напишите /start или перейдите по персональной ссылке «Привязать Telegram» с сайта.",
            )
    except Exception as exc:
        logger.exception("Ошибка обработки Telegram update: %s", exc)
    finally:
        db.close()

    return {"ok": True}


@router.get("/link-telegram/{token}")
def link_telegram_redirect(token: str) -> RedirectResponse:
    url = build_link_url(token)
    if not url:
        raise HTTPException(503, "Telegram-бот не настроен")
    return RedirectResponse(url, status_code=302)


@router.get("/link-telegram/{token}/page", response_class=HTMLResponse)
def link_telegram_page(token: str, request: Request) -> HTMLResponse:
    db: Session = SessionLocal()
    try:
        family = repo.get_family_by_token(db, token)
        if not family:
            raise HTTPException(404, "Ссылка не найдена")

        bot_username = get_bot_username()
        deep_link = build_link_url(token)
        progress_url = f"{PUBLIC_BASE_URL}/progress/{token}"

        return templates.TemplateResponse(
            request,
            "link_telegram.html",
            {
                "parent_name": family.parent_name,
                "bot_username": bot_username,
                "deep_link": deep_link,
                "progress_url": progress_url,
                "already_linked": family.telegram_chat_id is not None,
            },
        )
    finally:
        db.close()
