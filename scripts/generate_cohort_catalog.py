#!/usr/bin/env python3
"""Модули и заглушки уроков для wind / garden / rus-6-9 / rus-10-12."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES_PATH = ROOT / "catalog" / "modules.json"
CATALOG_DIR = ROOT / "lessons" / "catalog"

COHORTS = [
    {
        "group_code": "wind",
        "group_label": "Ветер в ивах",
        "start_note": "Старт 7 сентября · уроки по понедельникам",
        "module_ids": {"single": 28, "self_paced": 29, "with_teacher": 30},
        "lesson_titles": [
            "Знакомство с книгой",
            "Читаем дальше",
            "Главные герои",
            "Итог модуля",
        ],
    },
    {
        "group_code": "garden",
        "group_label": "Таинственный сад",
        "start_note": "Старт 7 сентября · уроки по понедельникам",
        "module_ids": {"single": 31, "self_paced": 32, "with_teacher": 33},
        "lesson_titles": [
            "Знакомство с книгой",
            "Читаем дальше",
            "Тайна сада",
            "Итог модуля",
        ],
    },
    {
        "group_code": "rus-6-9",
        "group_label": "Русские сказки",
        "start_note": "Старт 5 октября · уроки по понедельникам",
        "module_ids": {"single": 34, "self_paced": 35, "with_teacher": 36},
        "lesson_titles": ["Урок 1", "Урок 2", "Урок 3", "Урок 4"],
    },
    {
        "group_code": "rus-10-12",
        "group_label": "Русские сказки",
        "start_note": "Старт 5 октября · уроки по понедельникам",
        "module_ids": {"single": 37, "self_paced": 38, "with_teacher": 39},
        "lesson_titles": ["Урок 1", "Урок 2", "Урок 3", "Урок 4"],
    },
]

TARIFF_META = {
    "single": ("Разовое занятие", "single", 1, 799, 0),
    "self_paced": ("Индивидуальное обучение", "self_paced", 4, 1990, 0),
    "with_teacher": ("Модуль с преподавателем", "with_teacher", 4, 4990, 4),
}


def module_row(
    *,
    module_id: int,
    group_code: str,
    group_label: str,
    tariff_key: str,
    start_note: str,
) -> dict:
    tariff_label, tariff_code, tales, price, meetings = TARIFF_META[tariff_key]
    title_suffix = group_label if group_code not in ("rus-6-9", "rus-10-12") else f"{group_label} ({group_code.split('-')[-1]} лет)"
    return {
        "id": module_id,
        "group_code": group_code,
        "group_label": group_label,
        "tariff_code": tariff_code,
        "tariff_label": tariff_label,
        "title": f"{tariff_label}, {title_suffix}",
        "tales_count": tales,
        "stages": "Модуль 1",
        "tale_numbers": "1–4" if tales > 1 else "любой 1 из 4 (выбор при записи)",
        "meetings": meetings,
        "price_rub": price,
        "status": "активен",
        "note": start_note + ". Контент уроков пополняется.",
    }


def lesson_row(
    *,
    group_code: str,
    group_label: str,
    tariff_code: str,
    tariff_label: str,
    module_id: int,
    week: int,
    title: str,
) -> dict:
    slug = f"{group_code}-{tariff_code}-stage-1-lesson-{week:02d}"
    if tariff_code == "single" and week == 1:
        slug = f"{group_code}-single-lesson-01"
    return {
        "slug": slug,
        "title": title,
        "tale_title": title,
        "module_id": module_id,
        "group_code": group_code,
        "group_label": group_label,
        "tariff_code": tariff_code,
        "tariff_label": tariff_label,
        "stage": "stage-1",
        "stage_label": "Модуль 1",
        "lesson_number": week,
        "tale_number": week,
        "tale_slug": f"{group_code}-stage1-tale-{week:02d}",
        "module_week": week,
        "meeting_number": min(week, 4) if tariff_code == "with_teacher" else 0,
        "active": False,
        "status": "черновик",
        "note": "Заглушка: контент урока в разработке. Доступ по расписанию.",
    }


def main() -> None:
    data = json.loads(MODULES_PATH.read_text(encoding="utf-8"))
    existing_ids = {m["id"] for m in data["modules"]}
    created: list[str] = []

    for cohort in COHORTS:
        gc = cohort["group_code"]
        gl = cohort["group_label"]
        note = cohort["start_note"]
        titles = cohort["lesson_titles"]
        for tariff_key, mid in cohort["module_ids"].items():
            if mid in existing_ids:
                continue
            data["modules"].append(
                module_row(
                    module_id=mid,
                    group_code=gc,
                    group_label=gl,
                    tariff_key=tariff_key,
                    start_note=note,
                )
            )
            existing_ids.add(mid)
            tariff_label, tariff_code, tales, _, _ = TARIFF_META[tariff_key]
            if tariff_code == "single":
                weeks = [1]
                lesson_title = titles[0]
            else:
                weeks = list(range(1, 5))
                lesson_title = None
            for w in weeks:
                title = lesson_title or titles[w - 1]
                row = lesson_row(
                    group_code=gc,
                    group_label=gl,
                    tariff_code=tariff_code,
                    tariff_label=tariff_label,
                    module_id=mid,
                    week=w,
                    title=title,
                )
                path = CATALOG_DIR / f"{row['slug']}.json"
                path.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                created.append(path.name)

    MODULES_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"modules: {len(data['modules'])} total, lessons created: {len(created)}")


if __name__ == "__main__":
    main()
