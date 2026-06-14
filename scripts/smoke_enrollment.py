"""Быстрая проверка enrollment без БД."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from catalog.loader import get_module, get_tale, load_modules
from lessons.loader import list_legacy_lessons, list_module_lessons


def normalize_stage(value: str | None) -> str | None:
    if not value:
        return None
    raw = str(value).strip().lower()
    if raw in ("1", "stage-1", "этап 1", "этап1"):
        return "stage-1"
    if raw in ("2", "stage-2", "этап 2", "этап2"):
        return "stage-2"
    return None


def main() -> None:
    modules = load_modules()
    assert len(modules) == 18, f"expected 18 modules, got {len(modules)}"

    legacy = list_legacy_lessons()
    assert len(legacy) == 1 and legacy[0]["slug"] == "kolobok", legacy

    for module in modules:
        mid = module["id"]
        lessons = list_module_lessons(mid, active_only=False)
        tariff = module["tariff_code"]
        if tariff == "single":
            assert len(lessons) == 1, f"module {mid}: single should have 1 lesson"
        else:
            assert len(lessons) == 8, f"module {mid}: expected 8 lessons, got {len(lessons)}"

    tale = get_tale("grade-1", normalize_stage("1"), 2)
    assert tale and tale.get("tale_title"), tale

    m2 = get_module(2)
    assert m2 and m2["tariff_code"] == "self_paced"

    print("OK: 18 modules, legacy kolobok, lesson counts, tale resolution")


if __name__ == "__main__":
    main()
