"""Нормализация кодов этапа (stage-1 / stage-2)."""

from __future__ import annotations


def normalize_stage(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip().lower()
    if raw in ("1", "stage-1", "этап 1", "этап1"):
        return "stage-1"
    if raw in ("2", "stage-2", "этап 2", "этап2"):
        return "stage-2"
    if raw.startswith("этап 1"):
        return "stage-1"
    if raw.startswith("этап 2"):
        return "stage-2"
    return None
