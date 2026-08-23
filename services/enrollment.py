"""Валидация и создание записи на модуль при регистрации."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.schemas import RegisterWebhook
from catalog.loader import get_module
from db import repository as repo
from db.models import Child
from lessons.enrollment_access import normalize_stage, resolve_chosen_tale
from lessons.schedule import meeting_still_bookable

# Набор на этап 1 (старт 15 июля) с преподавателем закрыт.
WITH_TEACHER_STAGE1_CLOSED = True

COHORT_GROUPS = frozenset({"wind", "garden", "rus-6-9", "rus-10-12"})
NO_WITH_TEACHER_GROUPS = frozenset({
    "grade-1",
    "grade-2",
    "grade-3",
    "grade-4",
    "extra-6-8",
    "extra-9-11",
})


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
                "Для разового занятия укажите chosen_stage и chosen_tale_number "
                "(для классов: этап 1–2 и сказка 1–4; для early: модуль 1 и урок 1–8).",
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

    if module["tariff_code"] == "trial":
        # Бесплатный пробный: всегда stage-1, без выбора сказки
        return {
            "module": module,
            "chosen_stage": "stage-1",
            "chosen_tale_number": None,
            "chosen_tale_slug": None,
            "chosen_tale_title": None,
        }

    group_code = module.get("group_code") or ""
    if group_code in NO_WITH_TEACHER_GROUPS and module["tariff_code"] == "with_teacher":
        raise HTTPException(
            400,
            "Тариф «С преподавателем» для этой программы временно недоступен. "
            "Выберите «Разовое» или «Индивидуальное».",
        )

    if group_code in COHORT_GROUPS and module["tariff_code"] != "single":
        return {
            "module": module,
            "chosen_stage": "stage-1",
            "chosen_tale_number": None,
            "chosen_tale_slug": None,
            "chosen_tale_title": None,
        }

    if module["tariff_code"] == "meeting_addon":
        stage = normalize_stage(body.chosen_stage)
        if not stage or not body.chosen_tale_number:
            raise HTTPException(
                400,
                "Для докупки встречи укажите chosen_stage (1 или 2) и chosen_tale_number (1–4).",
            )
        if not meeting_still_bookable(stage=stage, tale_number=int(body.chosen_tale_number)):
            from lessons.schedule import meeting_addon_closed_message

            raise HTTPException(
                400,
                meeting_addon_closed_message(
                    stage=stage, tale_number=int(body.chosen_tale_number)
                ),
            )
        lesson_slug = (body.lesson_slug or "").strip() or None
        chosen_tale_slug = lesson_slug
        chosen_tale_title = None
        if not chosen_tale_slug:
            for group_code in (
                "grade-1",
                "grade-2",
                "grade-3",
                "grade-4",
                "extra-6-8",
                "extra-9-11",
                "early-letters",
                "early-stories",
            ):
                tale = resolve_chosen_tale(
                    group_code=group_code,
                    chosen_stage=stage,
                    chosen_tale_number=body.chosen_tale_number,
                )
                if tale:
                    chosen_tale_slug = tale["slug"]
                    chosen_tale_title = tale["tale_title"]
                    break
        if not chosen_tale_slug:
            raise HTTPException(400, "Не удалось определить сказку для докупки встречи")
        return {
            "module": module,
            "chosen_stage": stage,
            "chosen_tale_number": body.chosen_tale_number,
            "chosen_tale_slug": chosen_tale_slug,
            "chosen_tale_title": chosen_tale_title,
        }

    stage = normalize_stage(body.chosen_stage)
    # Early modules: default stage-1 if omitted (старт модуля 1)
    if not stage and module.get("group_code") in ("early-letters", "early-stories"):
        stage = "stage-1"
    if not stage:
        raise HTTPException(
            400,
            "Укажите chosen_stage (1 или 2) — период с 15 июля или с 15 августа.",
        )
    if (
        WITH_TEACHER_STAGE1_CLOSED
        and module["tariff_code"] == "with_teacher"
        and stage == "stage-1"
        and module.get("group_code") not in ("early-letters", "early-stories")
        and module.get("group_code") not in COHORT_GROUPS
    ):
        raise HTTPException(
            400,
            "Набор на этап 1 с преподавателем закрыт. Выберите старт 15 августа.",
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
    # Разовые сказки накапливаются: новая не должна закрывать прошлую.
    # Пробный early не закрывает платный модуль той же группы.
    # Блоки (индивидуальное / с преподавателем) по-прежнему сменяют запись в том же направлении.
    if module["tariff_code"] == "trial":
        pass
    elif module["tariff_code"] != "single":
        repo.complete_active_enrollments(db, child.id, group_code=module["group_code"])
    repo.create_enrollment(
        db,
        child_id=child.id,
        module_id=module["id"],
        chosen_stage=enrollment_data["chosen_stage"],
        chosen_tale_number=enrollment_data["chosen_tale_number"],
        chosen_tale_slug=enrollment_data["chosen_tale_slug"],
        chosen_tale_title=enrollment_data["chosen_tale_title"],
        promo_code=body.promo_code,
    )
    return module["id"], module["title"]
