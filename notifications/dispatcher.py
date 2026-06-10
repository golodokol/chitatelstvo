"""Маршрутизация уведомлений родителям: web + email + telegram."""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.orm import Session

from config.settings import PUBLIC_BASE_URL
from db import repository as repo
from db.models import Child, Family, ParentNotification
from notifications.email_channel import send_email
from notifications.telegram_channel import send_telegram

logger = logging.getLogger(__name__)


def _format_parent_message(child: Child, family: Family, parent_message: str, next_action: str) -> str:
    progress_url = f"{PUBLIC_BASE_URL}/progress/{family.progress_token}"
    return (
        f"Здравствуйте, {family.parent_name}!\n\n"
        f"Ребёнок: {child.name}\n"
        f"{parent_message}\n\n"
        f"Следующий шаг: {next_action}\n\n"
        f"Все обновления также на личной странице:\n{progress_url}"
    )


def dispatch_parent_notifications(
    db: Session,
    *,
    family: Family,
    child: Child,
    event_id: uuid.UUID,
    parent_message: str,
    next_action: str,
) -> list[uuid.UUID]:
    """
    Всегда сохраняет сообщение на web-странице прогресса.
    Дополнительно шлёт email и/или telegram по настройке семьи.
    Возвращает id созданных уведомлений для отложенной отправки push-каналов.
    """
    full_text = _format_parent_message(child, family, parent_message, next_action)
    notification_ids: list[uuid.UUID] = []

    # 1. Web — всегда (альтернатива без Telegram и без спама в почту)
    web_note = repo.store_notification(
        db,
        family_id=family.id,
        child_id=child.id,
        event_id=event_id,
        channel="web",
        message=full_text,
        status="stored",
    )
    notification_ids.append(web_note.id)

    channel = family.notification_channel

    # 2. Email
    if channel in ("email", "both"):
        email_note = repo.store_notification(
            db,
            family_id=family.id,
            child_id=child.id,
            event_id=event_id,
            channel="email",
            message=full_text,
            status="pending",
        )
        notification_ids.append(email_note.id)

    # 3. Telegram
    if channel in ("telegram", "both") and family.telegram_chat_id:
        tg_note = repo.store_notification(
            db,
            family_id=family.id,
            child_id=child.id,
            event_id=event_id,
            channel="telegram",
            message=full_text,
            status="pending",
        )
        notification_ids.append(tg_note.id)

    return notification_ids


def send_pending_notification(db: Session, notification_id: uuid.UUID) -> None:
    note = db.get(ParentNotification, notification_id)
    if not note or note.status != "pending":
        return

    family = db.get(Family, note.family_id)
    if not family:
        repo.mark_notification_failed(db, notification_id, "family not found")
        return

    try:
        if note.channel == "email":
            send_email(
                family.parent_email,
                subject="Читательство — прогресс ребёнка",
                body=note.message,
            )
        elif note.channel == "telegram":
            if not family.telegram_chat_id:
                raise RuntimeError("telegram_chat_id не привязан")
            send_telegram(family.telegram_chat_id, note.message)
        else:
            return
        repo.mark_notification_sent(db, notification_id)
    except Exception as exc:
        logger.exception("Ошибка отправки %s", note.channel)
        repo.mark_notification_failed(db, notification_id, str(exc))
