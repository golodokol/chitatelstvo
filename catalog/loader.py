from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CATALOG_DIR = Path(__file__).resolve().parents[1] / "catalog"


def load_modules() -> list[dict[str, Any]]:
    data = json.loads((CATALOG_DIR / "modules.json").read_text(encoding="utf-8"))
    return data["modules"]


def load_tales() -> list[dict[str, Any]]:
    data = json.loads((CATALOG_DIR / "tales.json").read_text(encoding="utf-8"))
    return data["tales"]


def get_module(module_id: int) -> dict[str, Any] | None:
    for module in load_modules():
        if module["id"] == module_id:
            return module
    return None


def get_tale(group_code: str, stage: str, tale_number: int) -> dict[str, Any] | None:
    stage_label = {"stage-1": "Этап 1", "stage-2": "Этап 2"}.get(stage, stage)
    for tale in load_tales():
        if (
            tale["group_code"] == group_code
            and tale["stage"] == stage
            and tale["stage_label"] == stage_label
            and tale["tale_number"] == tale_number
        ):
            return tale
    return None


def get_tale_by_slug(slug: str) -> dict[str, Any] | None:
    for tale in load_tales():
        if tale["slug"] == slug:
            return tale
    return None
