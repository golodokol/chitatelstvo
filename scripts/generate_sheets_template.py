"""Генерация CSV-шаблонов для Google Sheets."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "google_sheets"

TALES_PER_STAGE = 4
BADGES = ["Первый шаг", "Читатель", "Следопыт", "Мастер пересказа"]
POINTS = [2, 2, 2, 3]

GROUPS = [
    {"code": "grade-1", "label": "1 класс", "short": "1 класс"},
    {"code": "grade-2", "label": "2 класс", "short": "2 класс"},
    {"code": "grade-3", "label": "3 класс", "short": "3 класс"},
    {"code": "grade-4", "label": "4 класс", "short": "4 класс"},
    {
        "code": "extra-6-8",
        "label": "Внеклассное чтение 6–8 лет",
        "short": "Внекл. 6–8 лет",
    },
    {
        "code": "extra-9-11",
        "label": "Внеклассное чтение 9–11 лет",
        "short": "Внекл. 9–11 лет",
    },
]

STAGES = [
    {"code": "stage-1", "label": "Этап 1", "week_offset": 0, "meeting_offset": 0},
    {"code": "stage-2", "label": "Этап 2", "week_offset": 4, "meeting_offset": 4},
]

TARIFFS = [
    (
        "single",
        "Разовое занятие",
        1,
        1,
        1490,
        "single",
    ),
    (
        "self_paced",
        "Индивидуальное обучение",
        8,
        0,
        1990,
        "full",
    ),
    (
        "with_teacher",
        "Модуль с преподавателем",
        8,
        8,
        4990,
        "full",
    ),
]

TALE_BLOCKS = [
    {"code": "stage-1", "label": "Этап 1", "slug_part": "stage1-tale"},
    {"code": "stage-2", "label": "Этап 2", "slug_part": "stage2-tale"},
]


def week_for(tariff_code: str, tale_index: int, stage: dict) -> int:
    if tariff_code == "single":
        return 1
    return stage["week_offset"] + tale_index + 1


def meeting_for(tariff_code: str, tale_index: int, stage: dict) -> int:
    if tariff_code == "single":
        return 1
    if tariff_code == "with_teacher":
        return stage["meeting_offset"] + tale_index + 1
    return 0


def stage_note(stage: dict) -> str:
    if stage["code"] == "stage-1":
        return "Этап 1: 4 недели, 4 сказки"
    return "Этап 2: ещё 4 занятия через месяц после этапа 1"


def tale_slug(group_code: str, block: dict, n: int) -> str:
    return f"{group_code}-{block['slug_part']}-{n:02d}"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_tales() -> list[dict]:
    rows = []
    tale_id = 0

    for group in GROUPS:
        for block in TALE_BLOCKS:
            for n in range(1, TALES_PER_STAGE + 1):
                tale_id += 1
                rows.append(
                    {
                        "ID сказки": tale_id,
                        "Группа (код)": group["code"],
                        "Группа": group["label"],
                        "Этап": block["label"],
                        "№ сказки в этапе": n,
                        "Сказка (заполнить)": "",
                        "Название урока (заполнить)": "",
                        "Slug (не менять)": tale_slug(group["code"], block, n),
                        "Примечание": stage_note(
                            STAGES[0] if block["code"] == "stage-1" else STAGES[1]
                        ),
                    }
                )

    return rows


def build_modules() -> list[dict]:
    rows = []
    module_id = 0

    for group in GROUPS:
        for code, label, count, meetings, price, lesson_mode in TARIFFS:
            module_id += 1
            if code == "single":
                tale_nums = "любая 1 из 4 (выбор этапа и сказки при записи)"
                block_label = "Этап 1 или Этап 2"
                note = (
                    "Одна сказка на выбор: любая из 4 выбранного этапа. "
                    "Номер сказки не назначается по умолчанию — указывается при записи. "
                    "Сказки — лист СКАЗКИ"
                )
            else:
                tale_nums = "1, 2, 3, 4 (этап 1) + 1, 2, 3, 4 (этап 2)"
                block_label = "Этап 1 + Этап 2"
                note = (
                    "Этап 1: 4 недели и 4 сказки. "
                    "Через месяц — этап 2: ещё 4 занятия. "
                    "Сказки — лист СКАЗКИ"
                )

            rows.append(
                {
                    "ID модуля": module_id,
                    "Группа (код)": group["code"],
                    "Группа": group["label"],
                    "Тариф (код)": code,
                    "Тариф": label,
                    "Название модуля": f"{label}, {group['short']}",
                    "Сказок в модуле": count,
                    "Этапы": block_label,
                    "№ сказок": tale_nums,
                    "Встреч": meetings,
                    "Цена (руб)": price,
                    "Статус": "черновик",
                    "Примечание": note,
                }
            )

    return rows


def build_lessons() -> list[dict]:
    rows = []
    lesson_id = 0
    module_id = 0

    for group in GROUPS:
        for code, label, _count, _meetings, _price, lesson_mode in TARIFFS:
            module_id += 1

            if lesson_mode == "single":
                lesson_id += 1
                rows.append(
                    {
                        "ID урока": lesson_id,
                        "ID модуля": module_id,
                        "Группа": group["label"],
                        "Тариф": label,
                        "Этап": "Этап 1 или Этап 2 (выбор)",
                        "№ сказки в этапе": "1–4 (выбор при записи)",
                        "Неделя открытия": 1,
                        "Номер встречи": 1,
                        "Видео (ссылка)": "",
                        "Рабочий лист (ссылка)": "",
                        "Задания (текст)": "",
                        "Бейдж": "Первый шаг",
                        "Баллы": 2,
                        "Slug (не менять)": f"{group['code']}-{code}-lesson-01",
                        "Статус": "черновик",
                        "Примечание": (
                            "Разовое занятие: при записи выбирают этап (1 или 2) "
                            "и любую сказку № 1–4 этого этапа"
                        ),
                    }
                )
                continue

            for stage in STAGES:
                block = next(b for b in TALE_BLOCKS if b["code"] == stage["code"])
                for pos, tale_num in enumerate(range(1, TALES_PER_STAGE + 1)):
                    lesson_id += 1
                    rows.append(
                        {
                            "ID урока": lesson_id,
                            "ID модуля": module_id,
                            "Группа": group["label"],
                            "Тариф": label,
                            "Этап": stage["label"],
                            "№ сказки в этапе": tale_num,
                            "Неделя открытия": week_for(code, pos, stage),
                            "Номер встречи": meeting_for(code, pos, stage),
                            "Видео (ссылка)": "",
                            "Рабочий лист (ссылка)": "",
                            "Задания (текст)": "",
                            "Бейдж": BADGES[pos] if pos < len(BADGES) else BADGES[-1],
                            "Баллы": POINTS[pos] if pos < len(POINTS) else 2,
                            "Slug (не менять)": (
                                f"{group['code']}-{code}-{stage['code']}-lesson-{pos + 1:02d}"
                            ),
                            "Статус": "черновик",
                            "Примечание": stage_note(stage),
                        }
                    )

    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tales = build_tales()
    modules = build_modules()
    lessons = build_lessons()

    write_csv(OUT / "СКАЗКИ.csv", tales, list(tales[0].keys()))
    write_csv(OUT / "МОДУЛИ.csv", modules, list(modules[0].keys()))
    write_csv(OUT / "УРОКИ.csv", lessons, list(lessons[0].keys()))

    print(f"Сказки: {len(tales)}, Модули: {len(modules)}, Уроки: {len(lessons)}")


if __name__ == "__main__":
    main()
