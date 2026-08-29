"""Отправка сообщений через MAX Bot API (platform-api2.max.ru)."""

from __future__ import annotations

import json
import logging
from urllib import error, request

from config.settings import MAX_BOT_TOKEN, MAX_ENABLED

logger = logging.getLogger(__name__)

MAX_API_BASE = "https://platform-api2.max.ru"


def send_max(*, text: str, user_id: int | None = None, chat_id: int | None = None) -> None:
    """Отправить текст пользователю (user_id) или в чат/канал (chat_id)."""
    if not MAX_ENABLED:
        logger.info("MAX отключён — уведомление не отправлено")
        return
    if not MAX_BOT_TOKEN:
        raise RuntimeError("MAX_BOT_TOKEN не задан")
    if user_id is None and chat_id is None:
        raise RuntimeError("Нужен user_id или chat_id для MAX")

    params = []
    if user_id is not None:
        params.append(f"user_id={int(user_id)}")
    if chat_id is not None:
        params.append(f"chat_id={int(chat_id)}")
    url = f"{MAX_API_BASE}/messages?{'&'.join(params)}"
    body = {"text": text, "notify": True}
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={
            "Authorization": MAX_BOT_TOKEN,
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=15) as resp:
            if resp.status >= 400:
                raise RuntimeError(f"MAX HTTP {resp.status}")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        logger.error("MAX error: %s", detail)
        raise RuntimeError(detail) from exc
