"""Нормализация кодов этапа (stage-1 … stage-4)."""

from __future__ import annotations


def normalize_stage(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip().lower()
    if raw in ("1", "stage-1", "этап 1", "этап1", "модуль 1", "модуль1"):
        return "stage-1"
    if raw in ("2", "stage-2", "этап 2", "этап2", "модуль 2", "модуль2"):
        return "stage-2"
    if raw in ("3", "stage-3", "этап 3", "этап3", "модуль 3", "модуль3"):
        return "stage-3"
    if raw in ("4", "stage-4", "этап 4", "этап4", "модуль 4", "модуль4"):
        return "stage-4"
    if raw in ("all", "stage-all", "весь", "alphabet"):
        return None  # все этапы (пакет алфавита)
    if raw.startswith("этап 1") or raw.startswith("модуль 1"):
        return "stage-1"
    if raw.startswith("этап 2") or raw.startswith("модуль 2"):
        return "stage-2"
    if raw.startswith("этап 3") or raw.startswith("модуль 3"):
        return "stage-3"
    if raw.startswith("этап 4") or raw.startswith("модуль 4"):
        return "stage-4"
    return None
