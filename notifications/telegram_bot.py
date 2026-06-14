"""Обработка команд Telegram-бота и привязка chat_id к семье."""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib import error, parse, request

from config.settings import PUBLIC_BASE_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_USERNAME, TELEGRAM_ENABLED

logger = logging.getLogger(__name__)

_START_LINK_RE = re.compile(r"^link_(?P<token>[A-Za-z0-9_-]+)$")


def get_bot_username() -> str | None:
    if not TELEGRAM_ENABLED:
        return None
    if TELEGRAM_BOT_USERNAME:
        return TELEGRAM_BOT_USERNAME.lstrip("@")
    if not TELEGRAM_BOT_TOKEN:
        return None
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
        with request.urlopen(url, timeout=10) as resp:
            import json

            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                return data["result"]["username"]
    except Exception as exc:
        logger.warning("Не удалось получить username бота: %s", exc)
    return None


def build_link_url(progress_token: str) -> str | None:
    if not TELEGRAM_ENABLED:
        return None
    username = get_bot_username()
    if not username:
        return None
    # Параметр start ≤ 64 символов; link_ + token_urlsafe(32) ≈ 48
    start = f"link_{progress_token}"
    return f"https://t.me/{username}?start={parse.quote(start)}"


def send_reply(chat_id: int, text: str) -> None:
    if not TELEGRAM_ENABLED:
        logger.info("Telegram отключён — ответ не отправлен (chat_id=%s)", chat_id)
        return
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан")
    import json

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    body = {"chat_id": chat_id, "text": text}
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with request.urlopen(req, timeout=15) as resp:
            if resp.status >= 400:
                raise RuntimeError(f"Telegram HTTP {resp.status}")
    except error.HTTPError as exc:
        raise RuntimeError(exc.read().decode("utf-8", errors="replace")) from exc


def parse_start_token(text: str | None) -> str | None:
    if not text:
        return None
    text = text.strip()
    if not text.startswith("/start"):
        return None
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    match = _START_LINK_RE.match(parts[1].strip())
    return match.group("token") if match else None


def extract_message(update: dict[str, Any]) -> tuple[int, str | None, str | None] | None:
    """Возвращает (chat_id, text, username) или None."""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return None
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if chat_id is None:
        return None
    user = message.get("from") or {}
    username = user.get("username")
    return int(chat_id), message.get("text"), username


def welcome_text(progress_url: str | None = None) -> str:
    lines = [
        "Здравствуйте! Это бот Читательства — литературной школы онлайн.",
        "",
        "Чтобы получать уведомления о прогрессе ребёнка:",
        "1. Зарегистрируйтесь на сайте школы",
        "2. Откройте личную страницу прогресса",
        "3. Нажмите «Привязать Telegram»",
        "",
        "Или перейдите по персональной ссылке из письма после регистрации.",
    ]
    if progress_url:
        lines.extend(["", f"Ваша страница прогресса:\n{progress_url}"])
    return "\n".join(lines)


def linked_text(parent_name: str, child_names: list[str]) -> str:
    kids = ", ".join(child_names) if child_names else "ребёнок"
    return (
        f"Готово, {parent_name}! Telegram привязан.\n"
        f"Будем присылать новости о занятиях ({kids}).\n\n"
        f"Все сообщения также на личной странице прогресса."
    )
