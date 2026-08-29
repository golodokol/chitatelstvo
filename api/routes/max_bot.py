"""Webhook MAX Bot API — ловит bot_started / /start и пишет user_id в лог."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

from config.settings import MAX_ENABLED, MAX_WEBHOOK_SECRET
from notifications.max_channel import send_max

logger = logging.getLogger(__name__)
router = APIRouter(tags=["max"])


def _user_id_from_update(payload: dict[str, Any]) -> int | None:
    user = payload.get("user")
    if isinstance(user, dict) and user.get("user_id") is not None:
        return int(user["user_id"])
    message = payload.get("message")
    if isinstance(message, dict):
        sender = message.get("sender")
        if isinstance(sender, dict) and sender.get("user_id") is not None:
            return int(sender["user_id"])
    return None


def _text_from_update(payload: dict[str, Any]) -> str:
    message = payload.get("message")
    if not isinstance(message, dict):
        return ""
    body = message.get("body")
    if isinstance(body, dict):
        return str(body.get("text") or "")
    return str(message.get("text") or "")


@router.post("/max/webhook", dependencies=[])
async def max_webhook(
    request: Request,
    x_max_bot_api_secret: str | None = Header(default=None, alias="X-Max-Bot-Api-Secret"),
) -> dict[str, bool]:
    if MAX_WEBHOOK_SECRET and x_max_bot_api_secret != MAX_WEBHOOK_SECRET:
        raise HTTPException(401, "Неверный MAX webhook secret")

    if not MAX_ENABLED:
        return {"ok": True}

    payload: dict[str, Any] = await request.json()
    update_type = str(payload.get("update_type") or "")
    user_id = _user_id_from_update(payload)
    text = _text_from_update(payload).strip()

    logger.info("MAX webhook type=%s user_id=%s text=%r", update_type, user_id, text[:80])

    if user_id is None:
        return {"ok": True}

    if update_type == "bot_started" or text.startswith("/start"):
        reply = (
            "Бот Читательства подключён.\n"
            f"Ваш user_id: {user_id}\n\n"
            "Добавьте в .env на сервере:\n"
            f"ADMIN_MAX_USER_ID={user_id}\n"
            "MAX_ENABLED=1\n"
            "и перезапустите API — сюда будут приходить уведомления об оплатах."
        )
        try:
            send_max(text=reply, user_id=user_id)
        except Exception:
            logger.exception("MAX reply after /start failed (user_id=%s)", user_id)

    return {"ok": True}
