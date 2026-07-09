"""Регистрация семьи, enrollment и welcome-уведомления (webhook и админка)."""

from __future__ import annotations

import logging
import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.schemas import RegisterResponse, RegisterWebhook
from config.settings import PUBLIC_BASE_URL, resolve_notification_channel
from db import repository as repo
from db.models import Child
from job_queue.redis_queue import enqueue
from notifications.email_templates import build_welcome_message
from notifications.telegram_bot import build_link_url
from services.enrollment import create_enrollment_from_registration, validate_registration_module

logger = logging.getLogger(__name__)


def _registration_response(
    *,
    family,
    child: Child,
    module_id: int | None,
    module_title: str | None,
    is_returning: bool,
) -> RegisterResponse:
    progress_url = f"{PUBLIC_BASE_URL}/progress/{family.progress_token}"
    link_telegram_page = f"{PUBLIC_BASE_URL}/link-telegram/{family.progress_token}/page"
    telegram_deep_link = build_link_url(family.progress_token)
    return RegisterResponse(
        family_id=family.id,
        child_id=child.id,
        progress_url=progress_url,
        link_telegram_page=link_telegram_page,
        telegram_deep_link=telegram_deep_link,
        notification_channel=family.notification_channel,
        module_id=module_id,
        module_title=module_title,
        is_returning=is_returning,
    )


def _webhook_registration_already_processed(
    db: Session,
    child: Child,
    body: RegisterWebhook,
) -> tuple[bool, int | None, str | None]:
    """Повторный webhook после недавней успешной регистрации — не дублировать запись и письма."""
    if body.module_id is None:
        if repo.has_recent_welcome_notification(
            db,
            family_id=child.family_id,
            child_id=child.id,
        ):
            return True, None, None
        return False, None, None

    enrollment_data = validate_registration_module(body)
    if not enrollment_data:
        return False, None, None

    module = enrollment_data["module"]
    existing = repo.find_recent_duplicate_enrollment(
        db,
        child_id=child.id,
        module_id=module["id"],
        chosen_stage=enrollment_data["chosen_stage"],
        chosen_tale_number=enrollment_data["chosen_tale_number"],
    )
    if existing:
        return True, module["id"], module["title"]
    return False, None, None


def _dispatch_welcome(
    db: Session,
    *,
    family,
    child: Child,
    parent_name: str,
    notification_channel: str,
    module_title: str | None,
    is_returning: bool,
    send_email: bool,
) -> RegisterResponse:
    progress_url = f"{PUBLIC_BASE_URL}/progress/{family.progress_token}"
    link_telegram_page = f"{PUBLIC_BASE_URL}/link-telegram/{family.progress_token}/page"
    telegram_deep_link = build_link_url(family.progress_token)

    welcome = build_welcome_message(
        parent_name=parent_name,
        child_name=child.name,
        progress_url=progress_url,
        link_telegram_page=link_telegram_page,
        include_telegram=bool(
            telegram_deep_link and notification_channel in ("telegram", "both")
        ),
        module_title=module_title,
        is_returning=is_returning,
    )
    repo.store_notification(
        db,
        family_id=family.id,
        child_id=child.id,
        event_id=None,
        channel="web",
        message=welcome,
        status="stored",
    )

    if send_email and notification_channel in ("email", "both"):
        note = repo.store_notification(
            db,
            family_id=family.id,
            child_id=child.id,
            event_id=None,
            channel="email",
            message=welcome,
            status="pending",
        )
        enqueue("send_notification", {"notification_id": str(note.id)})

    if notification_channel in ("telegram", "both") and family.telegram_chat_id:
        note = repo.store_notification(
            db,
            family_id=family.id,
            child_id=child.id,
            event_id=None,
            channel="telegram",
            message=welcome,
            status="pending",
        )
        enqueue("send_notification", {"notification_id": str(note.id)})

    return _registration_response(
        family=family,
        child=child,
        module_id=None,
        module_title=module_title,
        is_returning=is_returning,
    )


def process_registration(
    db: Session,
    body: RegisterWebhook,
    *,
    send_email: bool = True,
    log_source: str = "webhook",
) -> RegisterResponse:
    notification_channel = resolve_notification_channel(body.notification_channel)
    telegram_chat_id = body.telegram_chat_id if notification_channel in ("telegram", "both") else None

    family, child, is_returning = repo.resolve_or_create_family_child(
        db,
        parent_name=body.parent_name,
        parent_email=str(body.parent_email),
        parent_telegram=body.parent_telegram,
        notification_channel=notification_channel,
        child_name=body.child_name,
        child_age=body.child_age,
        child_birth_date=body.child_birth_date,
        telegram_chat_id=telegram_chat_id,
    )

    if log_source == "webhook":
        duplicate, dup_module_id, dup_module_title = _webhook_registration_already_processed(
            db, child, body
        )
        if duplicate:
            logger.info(
                "Повтор webhook register %s → child=%s module=%s (пропуск welcome)",
                body.parent_email,
                child.id,
                dup_module_id,
            )
            return _registration_response(
                family=family,
                child=child,
                module_id=dup_module_id,
                module_title=dup_module_title,
                is_returning=is_returning,
            )

    module_id, module_title = create_enrollment_from_registration(db, child, body)

    logger.info(
        "Регистрация [%s] %s → child=%s module=%s (returning=%s)",
        log_source,
        body.parent_email,
        child.id,
        module_id,
        is_returning,
    )

    response = _dispatch_welcome(
        db,
        family=family,
        child=child,
        parent_name=body.parent_name,
        notification_channel=notification_channel,
        module_title=module_title,
        is_returning=is_returning,
        send_email=send_email,
    )
    response.module_id = module_id
    return response


def grant_enrollment_to_child(
    db: Session,
    child_id: uuid.UUID,
    *,
    module_id: int,
    chosen_stage: str | None,
    chosen_tale_number: int | None,
    send_email: bool = True,
) -> RegisterResponse:
    child = repo.get_child_with_family(db, child_id)
    if not child or not child.family:
        raise HTTPException(404, "Ребёнок не найден")

    family = child.family
    body = RegisterWebhook(
        parent_name=family.parent_name,
        parent_email=family.parent_email,
        parent_telegram=family.parent_telegram,
        notification_channel=family.notification_channel,
        child_name=child.name,
        child_age=child.age,
        child_birth_date=child.birth_date,
        module_id=module_id,
        chosen_stage=chosen_stage,
        chosen_tale_number=chosen_tale_number,
    )
    mod_id, module_title = create_enrollment_from_registration(db, child, body)

    logger.info(
        "Выдача доступа [admin] child=%s module=%s",
        child.id,
        mod_id,
    )

    response = _dispatch_welcome(
        db,
        family=family,
        child=child,
        parent_name=family.parent_name,
        notification_channel=family.notification_channel,
        module_title=module_title,
        is_returning=True,
        send_email=send_email,
    )
    response.module_id = mod_id
    return response
