"""Валидация и создание записи на модуль при регистрации."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.schemas import RegisterWebhook
from catalog.loader import get_module
from db import repository as repo
from db.models import Child
from lessons.enrollment_access import normalize_stage, resolve_chosen_tale


def validate_registration_module(body: RegisterWebhook) -> dict | None:
    if body.module_id is None:
        return None

    module = get_module(body.module_id)
    if not module:
        raise HTTPException(400, f"Модуль {body.module_id} не найден в каталоге")

    if module["tariff_code"] == "single":
        stage = normalize_stage(body.chosen_stage)
        if not stage or not body.chosen_tale_number:
            raise HTTPException(
                400,
                "Для разового занятия укажите chosen_stage (1 или 2) и chosen_tale_number (1–4).",
            )
        tale = resolve_chosen_tale(
            group_code=module["group_code"],
            chosen_stage=stage,
            chosen_tale_number=body.chosen_tale_number,
        )
        if not tale:
            raise HTTPException(400, "Сказка не найдена для выбранного периода и номера")
        return {
            "module": module,
            "chosen_stage": stage,
            "chosen_tale_number": body.chosen_tale_number,
            "chosen_tale_slug": tale["slug"],
            "chosen_tale_title": tale["tale_title"],
        }

    stage = normalize_stage(body.chosen_stage)
    if not stage:
        raise HTTPException(
            400,
            "Укажите chosen_stage (1 или 2) — период с 22 июня или с 20 июля.",
        )
    if body.chosen_tale_number:
        raise HTTPException(
            400,
            "chosen_tale_number используется только для разового занятия.",
        )
    return {
        "module": module,
        "chosen_stage": stage,
        "chosen_tale_number": None,
        "chosen_tale_slug": None,
        "chosen_tale_title": None,
    }


def create_enrollment_from_registration(
    db: Session,
    child: Child,
    body: RegisterWebhook,
) -> tuple[int | None, str | None]:
    enrollment_data = validate_registration_module(body)
    if not enrollment_data:
        return None, None

    module = enrollment_data["module"]
    repo.complete_active_enrollments(db, child.id)
    repo.create_enrollment(
        db,
        child_id=child.id,
        module_id=module["id"],
        chosen_stage=enrollment_data["chosen_stage"],
        chosen_tale_number=enrollment_data["chosen_tale_number"],
        chosen_tale_slug=enrollment_data["chosen_tale_slug"],
        chosen_tale_title=enrollment_data["chosen_tale_title"],
    )
    return module["id"], module["title"]
