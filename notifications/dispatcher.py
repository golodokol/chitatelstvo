"""Маршрутизация уведомлений родителям: web + email + telegram.

Письма о прогрессе после покупки копятся и уходят одной сводкой
не чаще одного раза в календарный день (МСК). Welcome / OTP / квиз — сразу.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from config.settings import PUBLIC_BASE_URL, TELEGRAM_ENABLED
from db import repository as repo
from db.models import Child, Family, ParentNotification
from notifications.email_channel import send_email
from notifications.email_templates import (
    SUBJECT_PROGRESS,
    SUBJECT_PROGRESS_DIGEST,
    SUBJECT_WELCOME,
    build_progress_digest_item,
    build_progress_digest_message,
    build_progress_message,
)
from notifications.telegram_channel import send_telegram

logger = logging.getLogger(__name__)

MSK = ZoneInfo("Europe/Moscow")
# После паузы в занятиях или вечером отправляем сводку за день
DIGEST_QUIET_MINUTES = 45
DIGEST_EVENING_HOUR = 19


def _format_parent_message(child: Child, family: Family, parent_message: str, next_action: str) -> str:
    progress_url = f"{PUBLIC_BASE_URL}/progress/{family.progress_token}"
    return build_progress_message(
        parent_name=family.parent_name,
        child_name=child.name,
        parent_message=parent_message,
        next_action=next_action,
        progress_url=progress_url,
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
    Email о прогрессе копит в pending (дневная сводка); telegram — сразу pending.
    Возвращает id уведомлений, которые можно отправить немедленно (не email-прогресс).
    """
    full_text = _format_parent_message(child, family, parent_message, next_action)
    digest_item = build_progress_digest_item(
        child_name=child.name,
        parent_message=parent_message,
        next_action=next_action,
    )
    immediate_ids: list[uuid.UUID] = []

    # 1. Web — всегда
    if not repo.has_notification_for_event(db, event_id=event_id, channel="web"):
        repo.store_notification(
            db,
            family_id=family.id,
            child_id=child.id,
            event_id=event_id,
            channel="web",
            message=full_text,
            status="stored",
        )

    channel = family.notification_channel

    # 2. Email — копим для дневной сводки (не ставим в очередь сразу)
    if channel in ("email", "both"):
        if not repo.has_notification_for_event(db, event_id=event_id, channel="email"):
            repo.store_notification(
                db,
                family_id=family.id,
                child_id=child.id,
                event_id=event_id,
                channel="email",
                message=digest_item,
                status="pending",
            )

    # 3. Telegram — сразу
    if TELEGRAM_ENABLED and channel in ("telegram", "both") and family.telegram_chat_id:
        if not repo.has_notification_for_event(db, event_id=event_id, channel="telegram"):
            tg_note = repo.store_notification(
                db,
                family_id=family.id,
                child_id=child.id,
                event_id=event_id,
                channel="telegram",
                message=full_text,
                status="pending",
            )
            immediate_ids.append(tg_note.id)

    return immediate_ids


def send_pending_notification(db: Session, notification_id: uuid.UUID) -> None:
    note = repo.claim_notification_send(db, notification_id)
    if not note:
        return

    # Письма о прогрессе уходят только через дневную сводку
    if note.channel == "email" and note.event_id is not None:
        note.status = "pending"
        note.error_message = None
        db.commit()
        return

    family = db.get(Family, note.family_id)
    if not family:
        repo.mark_notification_failed(db, notification_id, "family not found")
        return

    try:
        if note.channel == "email":
            subject = SUBJECT_WELCOME if note.event_id is None else SUBJECT_PROGRESS
            send_email(
                family.parent_email,
                subject=subject,
                body=note.message,
            )
        elif note.channel == "telegram":
            if not TELEGRAM_ENABLED:
                repo.mark_notification_failed(db, notification_id, "Telegram временно отключён")
                return
            if not family.telegram_chat_id:
                raise RuntimeError("telegram_chat_id не привязан")
            send_telegram(family.telegram_chat_id, note.message)
        else:
            return
        repo.mark_notification_sent(db, notification_id)
    except Exception as exc:
        logger.exception("Ошибка отправки %s", note.channel)
        repo.mark_notification_failed(db, notification_id, str(exc))


def _msk_day_bounds_utc(now: datetime | None = None) -> tuple[datetime, datetime, datetime]:
    """Возвращает (now_msk, day_start_utc, day_end_utc) для текущего дня МСК."""
    now_utc = now or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    now_msk = now_utc.astimezone(MSK)
    day_start_msk = now_msk.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end_msk = day_start_msk + timedelta(days=1)
    return now_msk, day_start_msk.astimezone(timezone.utc), day_end_msk.astimezone(timezone.utc)


def _note_created_msk(note: ParentNotification) -> datetime:
    created = note.created_at
    if created is None:
        return datetime.now(MSK)
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    return created.astimezone(MSK)


def _should_send_digest(
    pending: list[ParentNotification],
    *,
    already_sent_today: bool,
    now_msk: datetime,
) -> bool:
    if already_sent_today or not pending:
        return False

    # Вчерашние (и старше) pending — отправить при первой возможности
    today = now_msk.date()
    if any(_note_created_msk(n).date() < today for n in pending):
        return True

    # Вечерняя сводка за день
    if now_msk.hour >= DIGEST_EVENING_HOUR:
        return True

    # Днём: после паузы в занятиях (ребёнок закончил «пачку» шагов)
    newest = max(_note_created_msk(n) for n in pending)
    quiet_for = (now_msk - newest).total_seconds()
    if quiet_for >= DIGEST_QUIET_MINUTES * 60:
        return True

    return False


def flush_progress_email_digests(db: Session, *, force: bool = False) -> int:
    """
    Отправляет не более одного email о прогрессе на семью за календарный день (МСК).
    Возвращает число отправленных писем.
    """
    now_msk, day_start_utc, day_end_utc = _msk_day_bounds_utc()
    sent_count = 0

    for family_id in repo.list_family_ids_with_pending_progress_emails(db):
        family = db.get(Family, family_id)
        if not family:
            continue

        pending = repo.list_pending_progress_emails(db, family_id=family_id)
        if not pending:
            continue

        already = repo.family_has_progress_email_sent_on_day(
            db,
            family_id=family_id,
            day_start_utc=day_start_utc,
            day_end_utc=day_end_utc,
        )
        if not force and not _should_send_digest(
            pending, already_sent_today=already, now_msk=now_msk
        ):
            continue

        progress_url = f"{PUBLIC_BASE_URL}/progress/{family.progress_token}"
        body = build_progress_digest_message(
            parent_name=family.parent_name,
            progress_url=progress_url,
            items=[n.message for n in pending],
        )
        note_ids = [n.id for n in pending]

        try:
            send_email(
                family.parent_email,
                subject=SUBJECT_PROGRESS_DIGEST,
                body=body,
            )
            repo.mark_notifications_sent(db, note_ids)
            sent_count += 1
            logger.info(
                "Дневная сводка родителю family=%s items=%s",
                family_id,
                len(note_ids),
            )
        except Exception:
            logger.exception("Ошибка дневной сводки family=%s", family_id)

    return sent_count
