"""JSON API комнаты приключений для мобильного приложения."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_current_family, parse_optional_child_id
from db.models import Family
from db.session import get_db
from services.cabinet import build_family_cabinet

router = APIRouter(prefix="/api/v1", tags=["cabinet"])


@router.get("/cabinet")
def cabinet_json(
    child_id: uuid.UUID | None = Depends(parse_optional_child_id),
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
) -> dict:
    """Комната приключений + блок для родителей.

    Авторизация: `Authorization: Bearer` (после OTP).
    Выбор ребёнка: query `child_id` или заголовок `X-Child-Id`.
    Без child_id — все дети семьи (как на веб-странице).
    """
    selected = child_id
    try:
        return build_family_cabinet(db, family, child_id=selected)
    except ValueError as exc:
        if str(exc) == "child_not_found":
            raise HTTPException(404, "Ребёнок не найден в этой семье") from exc
        raise
