"""JSON API комнаты приключений для мобильного приложения."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_current_family
from db.models import Family
from db.session import get_db
from services.cabinet import build_family_cabinet

router = APIRouter(prefix="/api/v1", tags=["cabinet"])


def _parse_child_id(
    child_id: uuid.UUID | None,
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


@router.get("/cabinet")
def cabinet_json(
    child_id: uuid.UUID | None = Query(default=None, description="UUID ребёнка — один профиль в ответе"),
    x_child_id: Annotated[str | None, Header()] = None,
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
) -> dict:
    """Комната приключений + блок для родителей.

    Авторизация: `Authorization: Bearer` (после OTP).
    Выбор ребёнка: query `child_id` или заголовок `X-Child-Id`.
    Без child_id — все дети семьи (как на веб-странице).
    """
    selected = _parse_child_id(child_id, x_child_id)
    try:
        return build_family_cabinet(db, family, child_id=selected)
    except ValueError as exc:
        if str(exc) == "child_not_found":
            raise HTTPException(404, "Ребёнок не найден в этой семье") from exc
        raise
