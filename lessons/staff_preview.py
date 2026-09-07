"""Черновики раннего модуля: закрыты для всех, открыты в указанных кабинетах."""

from __future__ import annotations

from typing import Any

from config.settings import STAFF_PREVIEW_PROGRESS_TOKENS

STAFF_PREVIEW_LESSON_MAX = 4


def is_staff_preview_token(token: str | None) -> bool:
    value = (token or "").strip()
    return bool(value) and value in STAFF_PREVIEW_PROGRESS_TOKENS


def is_staff_preview_child(child: Any) -> bool:
    family = getattr(child, "family", None)
    return is_staff_preview_token(getattr(family, "progress_token", None))


def is_staff_preview_draft_lesson(lesson: dict[str, Any] | None) -> bool:
    if not lesson:
        return False
    group = str(lesson.get("group_code") or "")
    if not group.startswith("early-"):
        return False
    if str(lesson.get("tariff_code") or "") == "trial":
        return False
    try:
        number = int(lesson.get("lesson_number") or lesson.get("module_week") or 0)
    except (TypeError, ValueError):
        number = 0
    return 1 <= number <= STAFF_PREVIEW_LESSON_MAX


def staff_preview_lesson_slug(group_code: str, week: int) -> str:
    return f"{group_code}-self_paced-stage-1-lesson-{week:02d}"
