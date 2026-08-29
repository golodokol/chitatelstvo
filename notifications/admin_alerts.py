"""Мгновенные уведомления админу об оплатах / регистрациях (Telegram + MAX)."""

from __future__ import annotations

import logging
from typing import Any

from config.settings import (
    ADMIN_MAX_CHAT_ID,
    ADMIN_MAX_USER_ID,
    ADMIN_TELEGRAM_CHAT_ID,
    MAX_BOT_TOKEN,
    MAX_ENABLED,
    TELEGRAM_BOT_TOKEN,
)
from notifications.max_channel import send_max
from notifications.telegram_channel import send_telegram

logger = logging.getLogger(__name__)


def _html_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def format_payment_alert(
    *,
    parent_name: str,
    parent_email: str,
    parent_phone: str | None,
    child_name: str,
    child_age: int | None,
    module_id: int | None,
    module_title: str | None,
    chosen_stage: str | None = None,
    chosen_tale_number: int | None = None,
    promo_code: str | None = None,
    source: str = "webhook",
    is_returning: bool = False,
) -> str:
    lines = [
        "Оплата / запись",
        f"Источник: {source}" + (" · повторный клиент" if is_returning else ""),
        "",
        f"Родитель: {parent_name}",
        f"Email: {parent_email}",
    ]
    if parent_phone:
        lines.append(f"Телефон: {parent_phone}")
    lines.append(f"Ребёнок: {child_name}" + (f", {child_age} лет" if child_age is not None else ""))
    if module_title or module_id:
        title = module_title or f"модуль {module_id}"
        lines.append(f"Программа: {title}")
    if module_id is not None:
        lines.append(f"module_id: {module_id}")
    if chosen_stage:
        lines.append(f"Блок: {chosen_stage}")
    if chosen_tale_number is not None:
        lines.append(f"Сказка/урок №: {chosen_tale_number}")
    if promo_code:
        lines.append(f"Промокод: {promo_code}")
    return "\n".join(lines)


def format_payment_alert_html(**kwargs: Any) -> str:
    plain = format_payment_alert(**kwargs)
    parts = []
    for line in plain.split("\n"):
        if not line:
            parts.append("")
            continue
        if line.startswith("Оплата"):
            parts.append(f"<b>{_html_escape(line)}</b>")
        elif ":" in line:
            key, _, val = line.partition(":")
            parts.append(f"<b>{_html_escape(key.strip())}:</b> {_html_escape(val.strip())}")
        else:
            parts.append(_html_escape(line))
    return "\n".join(parts)


def notify_admin_payment(**kwargs: Any) -> None:
    """Не роняет оплату: ошибки каналов только в лог."""
    plain = format_payment_alert(**kwargs)
    html = format_payment_alert_html(**kwargs)

    if ADMIN_TELEGRAM_CHAT_ID and TELEGRAM_BOT_TOKEN:
        try:
            # force=True: админ-алерты независимо от TELEGRAM_ENABLED (родительский канал)
            send_telegram(int(ADMIN_TELEGRAM_CHAT_ID), html, force=True)
            logger.info("Admin TG alert sent to %s", ADMIN_TELEGRAM_CHAT_ID)
        except Exception:
            logger.exception("Admin Telegram alert failed")

    if MAX_ENABLED and MAX_BOT_TOKEN and (ADMIN_MAX_USER_ID or ADMIN_MAX_CHAT_ID):
        try:
            send_max(
                text=plain,
                user_id=int(ADMIN_MAX_USER_ID) if ADMIN_MAX_USER_ID else None,
                chat_id=int(ADMIN_MAX_CHAT_ID) if ADMIN_MAX_CHAT_ID else None,
            )
            logger.info(
                "Admin MAX alert sent user=%s chat=%s",
                ADMIN_MAX_USER_ID or "-",
                ADMIN_MAX_CHAT_ID or "-",
            )
        except Exception:
            logger.exception("Admin MAX alert failed")
