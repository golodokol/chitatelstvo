"""Импорт CSV из docs/google_sheets/ в catalog/ и lessons/catalog/."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SHEETS = ROOT / "docs" / "google_sheets"
CATALOG_DIR = ROOT / "catalog"
LESSONS_CATALOG = ROOT / "lessons" / "catalog"

STAGE_TO_CODE = {
    "Этап 1": "stage-1",
    "Этап 2": "stage-2",
}


def read_csv(name: str) -> list[dict[str, str]]:
    path = SHEETS / name
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def stage_code(stage_label: str) -> str | None:
    if stage_label in STAGE_TO_CODE:
        return STAGE_TO_CODE[stage_label]
    if stage_label.startswith("Этап 1"):
        return "stage-1"
    if stage_label.startswith("Этап 2"):
        return "stage-2"
    return None


def build_modules(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    modules = []
    for row in rows:
        modules.append(
            {
                "id": parse_int(row["ID модуля"]),
                "group_code": row["Группа (код)"].strip(),
                "group_label": row["Группа"].strip(),
                "tariff_code": row["Тариф (код)"].strip(),
                "tariff_label": row["Тариф"].strip(),
                "title": row["Название модуля"].strip(),
                "tales_count": parse_int(row["Сказок в модуле"]),
                "stages": row["Этапы"].strip(),
                "tale_numbers": row["№ сказок"].strip(),
                "meetings": parse_int(row["Встреч"]),
                "price_rub": parse_int(row["Цена (руб)"]),
                "status": row.get("Статус", "черновик").strip() or "черновик",
                "note": row.get("Примечание", "").strip(),
            }
        )
    return modules


def build_tales(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    tales = []
    for row in rows:
        stage = row["Этап"].strip()
        tales.append(
            {
                "id": parse_int(row["ID сказки"]),
                "group_code": row["Группа (код)"].strip(),
                "group_label": row["Группа"].strip(),
                "stage": stage_code(stage) or stage,
                "stage_label": stage,
                "tale_number": parse_int(row["№ сказки в этапе"]),
                "tale_title": row["Сказка (заполнить)"].strip(),
                "lesson_title": row["Название урока (заполнить)"].strip(),
                "slug": row["Slug (не менять)"].strip(),
            }
        )
    return tales


def tale_lookup(tales: list[dict[str, Any]]) -> dict[tuple[str, str, int], dict[str, Any]]:
    index: dict[tuple[str, str, int], dict[str, Any]] = {}
    for tale in tales:
        key = (tale["group_code"], tale["stage"], tale["tale_number"])
        index[key] = tale
    return index


def build_lesson_json(
    row: dict[str, str],
    module: dict[str, Any],
    tale: dict[str, Any] | None,
) -> dict[str, Any]:
    slug = row["Slug (не менять)"].strip()
    stage_label = row["Этап"].strip()
    stage = stage_code(stage_label)
    tale_num_raw = row["№ сказки в этапе"].strip()

    if module["tariff_code"] == "single":
        title = f"Разовое занятие — {module['group_label']}"
        tale_title = None
        tale_slug = None
        tale_number = None
    else:
        assert tale is not None
        title = tale["lesson_title"]
        tale_title = tale["tale_title"]
        tale_slug = tale["slug"]
        tale_number = parse_int(tale_num_raw)

    lesson_number = parse_int(row["ID урока"])

    return {
        "slug": slug,
        "title": title,
        "tale_title": tale_title,
        "module_id": module["id"],
        "group_code": module["group_code"],
        "group_label": module["group_label"],
        "tariff_code": module["tariff_code"],
        "tariff_label": module["tariff_label"],
        "stage": stage,
        "stage_label": stage_label if stage else stage_label,
        "lesson_number": lesson_number,
        "tale_number": tale_number,
        "tale_slug": tale_slug,
        "module_week": parse_int(row["Неделя открытия"], 1),
        "meeting_number": parse_int(row["Номер встречи"]),
        "badge": row["Бейдж"].strip(),
        "points": parse_int(row["Баллы"], 2),
        "active": False,
        "status": row.get("Статус", "черновик").strip() or "черновик",
        "note": row.get("Примечание", "").strip(),
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    modules = build_modules(read_csv("МОДУЛИ.csv"))
    tales = build_tales(read_csv("СКАЗКИ.csv"))
    lessons_rows = read_csv("УРОКИ.csv")
    modules_by_id = {m["id"]: m for m in modules}
    tales_by_key = tale_lookup(tales)

    write_json(CATALOG_DIR / "modules.json", {"modules": modules})
    write_json(CATALOG_DIR / "tales.json", {"tales": tales})

    LESSONS_CATALOG.mkdir(parents=True, exist_ok=True)
    for old in LESSONS_CATALOG.glob("*.json"):
        old.unlink()

    created = 0
    for row in lessons_rows:
        module_id = parse_int(row["ID модуля"])
        module = modules_by_id.get(module_id)
        if not module:
            raise ValueError(f"Unknown module_id {module_id} in УРОКИ.csv")

        tale = None
        if module["tariff_code"] != "single":
            stage = stage_code(row["Этап"].strip())
            tale_num = parse_int(row["№ сказки в этапе"])
            if not stage:
                raise ValueError(f"Cannot resolve stage for lesson {row['Slug (не менять)']}")
            key = (module["group_code"], stage, tale_num)
            tale = tales_by_key.get(key)
            if not tale:
                raise ValueError(f"No tale for {key} (lesson {row['Slug (не менять)']})")

        lesson = build_lesson_json(row, module, tale)
        write_json(LESSONS_CATALOG / f"{lesson['slug']}.json", lesson)
        created += 1

    print(f"catalog/modules.json: {len(modules)} modules")
    print(f"catalog/tales.json: {len(tales)} tales")
    print(f"lessons/catalog/: {created} lesson stubs")


if __name__ == "__main__":
    main()
