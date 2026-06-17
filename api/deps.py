from __future__ import annotations

import time
import uuid
from collections import defaultdict
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query, Request
from sqlalchemy.orm import Session

from config.settings import JWT_SECRET, RATE_LIMIT_PER_MINUTE, WEBHOOK_SECRET
from db import repository as repo
from db.models import Family
from db.session import get_db
from services.auth_jwt import AuthError, decode_access_token

_hits: dict[str, list[float]] = defaultdict(list)


def verify_webhook_secret(x_webhook_secret: str | None = Header(default=None)) -> None:
    if not WEBHOOK_SECRET:
        raise HTTPException(500, "WEBHOOK_SECRET не настроен на сервере")
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(401, "Неверный webhook secret")


def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = _hits[ip]
    _hits[ip] = [t for t in window if now - t < 60]
    if len(_hits[ip]) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(429, "Слишком много запросов")
    _hits[ip].append(now)


def parse_optional_child_id(
    child_id: uuid.UUID | None = Query(default=None),
    x_child_id: Annotated[str | None, Header()] = None,
) -> uuid.UUID | None:
    if child_id is not None:
        return child_id
    if not x_child_id:
        return None
    try:
        return uuid.UUID(x_child_id.strip())
    except ValueError as exc:
        raise HTTPException(400, "Неверный заголовок X-Child-Id") from exc


def parse_required_child_id(
    child_id: uuid.UUID | None = Query(default=None),
    x_child_id: Annotated[str | None, Header()] = None,
) -> uuid.UUID:
    parsed = parse_optional_child_id(child_id, x_child_id)
    if not parsed:
        raise HTTPException(400, "Укажите child_id (query) или X-Child-Id (заголовок)")
    return parsed


def get_family_child(
    child_id: uuid.UUID = Depends(parse_required_child_id),
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
):
    child = repo.get_child_with_family(db, child_id)
    if not child or child.family_id != family.id:
        raise HTTPException(403, "Ребёнок не найден в этой семье")
    return child


def get_current_family(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
) -> Family:
    if not JWT_SECRET:
        raise HTTPException(503, "JWT_SECRET не настроен на сервере")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Требуется авторизация")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(401, "Требуется авторизация")

    try:
        payload = decode_access_token(token)
    except AuthError as exc:
        raise HTTPException(401, str(exc)) from exc

    try:
        family_id = uuid.UUID(str(payload["family_id"]))
    except (KeyError, ValueError) as exc:
        raise HTTPException(401, "Неверный токен") from exc

    family = repo.get_family_by_id(db, family_id)
    if not family:
        raise HTTPException(401, "Семья не найдена")

    email = str(payload.get("sub", "")).strip().lower()
    if email and family.parent_email != email:
        raise HTTPException(401, "Неверный токен")

    return family
