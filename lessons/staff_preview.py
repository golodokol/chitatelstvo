"""Черновики раннего модуля: закрыты для всех, открыты в указанных кабинетах."""

from __future__ import annotations

from typing import Any

from config.settings import STAFF_PREVIEW_PROGRESS_TOKENS

# Модуль 1 «Первые истории» / сетка «Скоро» по умолчанию — 8 уроков.
# Для «Буквы» в staff-кабинете подтягивается весь каталог (модули 1–4).
STAFF_PREVIEW_LESSON_MAX = 8

_STAGE_ORDER = {"stage-1": 1, "stage-2": 2, "stage-3": 3, "stage-4": 4}


def is_staff_preview_token(token: str | None) -> bool:
    value = (token or "").strip()
    return bool(value) and value in STAFF_PREVIEW_PROGRESS_TOKENS


def is_staff_preview_child(child: Any) -> bool:
    family = getattr(child, "family", None)
    return is_staff_preview_token(getattr(family, "progress_token", None))


def is_staff_preview_draft_lesson(lesson: dict[str, Any] | None) -> bool:
    """Любой early-урок (кроме trial) открыт в staff-кабинете — все модули/этапы."""
    if not lesson:
        return False
    group = str(lesson.get("group_code") or "")
    if not group.startswith("early-"):
        return False
    if str(lesson.get("tariff_code") or "") == "trial":
        return False
    return True


def staff_preview_lesson_slug(
    group_code: str,
    week: int,
    *,
    stage: str = "stage-1",
) -> str:
    stage_code = stage if str(stage).startswith("stage-") else f"stage-{stage}"
    return f"{group_code}-self_paced-{stage_code}-lesson-{week:02d}"


def list_staff_preview_catalog(group_code: str) -> list[dict[str, Any]]:
    """Все self_paced-уроки группы из каталога (включая inactive / каркас)."""
    from lessons.loader import list_lessons

    rows: list[dict[str, Any]] = []
    for les in list_lessons(active_only=False):
        if str(les.get("group_code") or "") != group_code:
            continue
        if str(les.get("tariff_code") or "") != "self_paced":
            continue
        rows.append(les)

    def sort_key(les: dict[str, Any]) -> tuple:
        stage = str(les.get("stage") or "stage-1")
        try:
            num = int(les.get("lesson_number") or les.get("module_week") or 0)
        except (TypeError, ValueError):
            num = 0
        return (_STAGE_ORDER.get(stage, 9), num, str(les.get("slug") or ""))

    rows.sort(key=sort_key)
    return rows
