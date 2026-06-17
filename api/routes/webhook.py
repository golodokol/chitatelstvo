from __future__ import annotations

import logging
import uuid
from typing import TypeVar

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.deps import rate_limit, verify_webhook_secret
from api.event_types import AUTO_LESSON_PLAYER
from api.schemas import EventWebhook, RegisterResponse, RegisterWebhook, WebhookAccepted
from config.settings import PUBLIC_BASE_URL, WEBHOOK_SECRET, resolve_notification_channel
from db import repository as repo
from db.session import get_db
from job_queue.redis_queue import enqueue
from notifications.email_templates import build_welcome_message
from notifications.telegram_bot import build_link_url
from services.enrollment import create_enrollment_from_registration
from services.events import submit_learning_event

logger = logging.getLogger(__name__)
ModelT = TypeVar("ModelT", bound=BaseModel)


def _flatten_tilda_payload(raw: dict) -> dict:
    """ST100 / Tilda Forms: поля могут быть вложены или в массиве inputs."""
    out = dict(raw)
    for key in ("fields", "inputs", "data", "form"):
        nested = raw.get(key)
        if isinstance(nested, dict):
            out.update(nested)
        elif isinstance(nested, list):
            for item in nested:
                if not isinstance(item, dict):
                    continue
                name = item.get("name") or item.get("title") or item.get("variable")
                val = item.get("value")
                if name is not None and val not in (None, ""):
                    out[str(name)] = val
    return out


async def _read_form_or_json(request: Request) -> dict:
    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        raw = await request.json()
        data = raw if isinstance(raw, dict) else {}
    else:
        form = await request.form()
        data = {key: value for key, value in form.items() if value not in (None, "")}
    return _flatten_tilda_payload(data)


async def _parse_webhook_body(request: Request, model: type[ModelT]) -> ModelT:
    """Tilda шлёт form-urlencoded; curl и тесты — JSON."""
    return model.model_validate(await _read_form_or_json(request))


def _is_tilda_ping(data: dict) -> bool:
    return data.get("test") == "test"


_CHANNEL_ALIASES = {
    "email": "email",
    "telegram": "telegram",
    "telegram bot": "telegram",
    "both": "both",
    "web": "web",
    "max": "web",
    "личная страница": "web",
}


def _normalize_register_payload(raw: dict) -> dict:
    data = dict(raw)
    channel = data.get("notification_channel")
    if channel is not None:
        key = str(channel).strip().lower()
        data["notification_channel"] = _CHANNEL_ALIASES.get(key, key)
    return data


router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.get("/register", include_in_schema=False)
def webhook_register_ping() -> PlainTextResponse:
    """Tilda проверяет URL GET-запросом при подключении webhook."""
    return PlainTextResponse("ok")


@router.post("/register", response_model=None)
async def webhook_register(
    request: Request,
    db: Session = Depends(get_db),
):
    rate_limit(request)

    raw = await _read_form_or_json(request)
    if _is_tilda_ping(raw):
        return PlainTextResponse("ok")

    logger.info("Webhook register: keys=%s", list(raw.keys()))

    secret = request.headers.get("x-webhook-secret")
    if not WEBHOOK_SECRET:
        raise HTTPException(500, "WEBHOOK_SECRET не настроен на сервере")
    if secret != WEBHOOK_SECRET:
        raise HTTPException(401, "Неверный webhook secret")

    body = RegisterWebhook.model_validate(_normalize_register_payload(raw))
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
        telegram_chat_id=telegram_chat_id,
    )

    module_id, module_title = create_enrollment_from_registration(db, child, body)

    progress_url = f"{PUBLIC_BASE_URL}/progress/{family.progress_token}"
    link_telegram_page = f"{PUBLIC_BASE_URL}/link-telegram/{family.progress_token}/page"
    telegram_deep_link = build_link_url(family.progress_token)

    welcome = build_welcome_message(
        parent_name=body.parent_name,
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

    if notification_channel in ("email", "both"):
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

    if notification_channel in ("telegram", "both") and telegram_chat_id:
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

    logger.info(
        "Регистрация %s → %s (returning=%s)",
        body.parent_email,
        progress_url,
        is_returning,
    )

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


@router.post("/event", response_model=WebhookAccepted, status_code=202, dependencies=[Depends(verify_webhook_secret)])
async def webhook_event(
    request: Request,
    db: Session = Depends(get_db),
) -> WebhookAccepted:
    rate_limit(request)
    body = await _parse_webhook_body(request, EventWebhook)

    child = repo.find_child(
        db,
        child_id=body.child_id,
        child_name=body.child_name,
        parent_email=str(body.parent_email) if body.parent_email else None,
    )
    if not child:
        raise HTTPException(404, "Ребёнок не найден. Укажите child_id или child_name + parent_email.")

    if body.module_week:
        child.module_week = body.module_week
        db.commit()

    if body.event_type in AUTO_LESSON_PLAYER:
        raise HTTPException(
            400,
            f"Событие «{body.event_type}» засчитывается автоматически в плеере урока.",
        )

    payload = body.model_dump(mode="json")
    status, event_id = submit_learning_event(
        db,
        child_id=child.id,
        event_type=body.event_type,
        tale_title=body.tale_title or "",
        lesson_date=body.lesson_date,
        notes=body.notes,
        payload=payload,
    )
    if status == "duplicate":
        return WebhookAccepted(status="duplicate", event_id=event_id, message="Событие уже обработано")
    return WebhookAccepted(event_id=event_id)
