from __future__ import annotations

import logging
from urllib import error, request

from config.settings import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)


def send_telegram(chat_id: int, text: str) -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    body = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    import json

    data = json.dumps(body).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=15) as resp:
            if resp.status >= 400:
                raise RuntimeError(f"Telegram HTTP {resp.status}")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        logger.error("Telegram error: %s", detail)
        raise RuntimeError(detail) from exc
