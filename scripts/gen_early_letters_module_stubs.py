"""Generate placeholder early-letters lessons for modules 2–4 (stage-2…4).

Run: python scripts/gen_early_letters_module_stubs.py
Does not overwrite lessons that already have real stations (status != каркас).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "lessons" / "catalog"
TALES_PATH = ROOT / "catalog" / "tales.json"

MODULES = [
    {
        "stage": "stage-2",
        "stage_label": "Модуль 2 · Шипящая тропа",
        "module_id_self": 41,
        "letters": ["Ш", "И", "Л", "П", "К", "Ы"],
        "lesson_titles": [
            "Шипит буква Ш",
            "И — как иголка",
            "Л — лодочка",
            "П — пух",
            "К — капля",
            "Ы — мычит",
            "Слоги шипят",
            "Первые слова тропы",
            "Мост: повтор",
            "Праздник шипящей тропы",
        ],
    },
    {
        "stage": "stage-3",
        "stage_label": "Модуль 3 · Звонкие и поющие",
        "module_id_self": 42,
        "letters": ["Ж", "Ч", "Н", "З", "В", "Е", "Ё", "Э"],
        "lesson_titles": [
            "Жужжит Ж",
            "Ч — чашка",
            "Н — нос",
            "З — зубки",
            "В — ветер",
            "Е — ель",
            "Ё — ёжик",
            "Э — эхо",
            "Слоги звонкие",
            "Слова поют",
            "Повтор модуля",
            "Праздник звонких",
        ],
    },
    {
        "stage": "stage-4",
        "stage_label": "Модуль 4 · Последние на тропе",
        "module_id_self": 43,
        "letters": ["Д", "Г", "Х", "Я", "Б", "Ф", "Ю", "Ц", "Щ", "ЬЪ", "Й"],
        "lesson_titles": [
            "Д — дом",
            "Г — гусь",
            "Х — хлеб",
            "Я — яблоко",
            "Б — барабан",
            "Ф — фонарь",
            "Ю — юла",
            "Ц — цапля",
            "Щ — щука",
            "Ь и Ъ — тихие знаки",
            "Й — йогурт",
            "Слоги финала",
            "Большая азбука",
            "Выпускной праздник",
        ],
    },
]

STAGE_PART = {"stage-2": "stage2", "stage-3": "stage3", "stage-4": "stage4"}


def stub_stations(title: str, stage_label: str) -> list[dict]:
    return [
        {
            "id": "trail",
            "title": "Скоро на тропе",
            "kind": "intro_video",
            "slovik_line": f"Урок «{title}» из {stage_label.lower()} ещё готовится. Скоро откроем!",
            "slovik_pose": "wave",
            "scene_image": "/static/early/letters/scene-map-sounds-where-01.png",
            "audio": "bo-m1-l01-hi",
            "cta_label": "Понятно",
            "spark": False,
        },
        {
            "id": "chest",
            "title": "Пока ждём",
            "kind": "reward",
            "slovik_line": "А пока можно перечитать модуль 1 — буквы А М У О С Р Т.",
            "audio": "bo-m1-l01-reward",
            "spark": False,
            "parent": "Этот урок ещё в работе. Ребёнку доступен модуль 1.",
        },
    ]


def build_lesson(
    *,
    tariff: str,
    module_id: int,
    stage: str,
    stage_label: str,
    lesson_number: int,
    title: str,
) -> dict:
    stage_part = STAGE_PART[stage]
    slug = f"early-letters-{tariff}-{stage}-lesson-{lesson_number:02d}"
    return {
        "slug": slug,
        "title": title,
        "tale_title": title,
        "module_id": module_id,
        "group_code": "early-letters",
        "group_label": "Буквы оживают",
        "tariff_code": tariff,
        "tariff_label": (
            "Индивидуальное обучение"
            if tariff == "self_paced"
            else "Модуль с преподавателем"
        ),
        "stage": stage,
        "stage_label": stage_label,
        "lesson_number": lesson_number,
        "tale_number": lesson_number,
        "tale_slug": f"early-letters-{stage_part}-tale-{lesson_number:02d}",
        "module_week": lesson_number,
        "meeting_number": 0,
        "badge": "Скоро",
        "points": 2,
        "active": False,
        "status": "каркас",
        "note": "Заготовка модуля: станции появятся по мере публикации.",
        "lesson_format": "quest",
        "stations": stub_stations(title, stage_label),
    }


def upsert_tales(mod: dict) -> None:
    data = json.loads(TALES_PATH.read_text(encoding="utf-8"))
    tales = data.get("tales") or []
    max_id = max((int(t.get("id") or 0) for t in tales), default=0)
    stage = mod["stage"]
    stage_part = STAGE_PART[stage]
    existing = {
        t.get("slug")
        for t in tales
        if str(t.get("group_code")) == "early-letters" and str(t.get("stage")) == stage
    }
    for i, title in enumerate(mod["lesson_titles"], start=1):
        slug = f"early-letters-{stage_part}-tale-{i:02d}"
        if slug in existing:
            continue
        max_id += 1
        tales.append(
            {
                "id": max_id,
                "group_code": "early-letters",
                "group_label": "Буквы оживают",
                "stage": stage,
                "stage_label": mod["stage_label"].split(" · ")[0],
                "tale_number": i,
                "tale_title": title,
                "lesson_title": title,
                "slug": slug,
            }
        )
        existing.add(slug)
    data["tales"] = tales
    TALES_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    written = 0
    skipped = 0
    for mod in MODULES:
        upsert_tales(mod)
        for tariff, mid in (
            ("self_paced", mod["module_id_self"]),
            # with_teacher for M2–4 — later; pack unlocks self_paced modules 41–43
        ):
            for i, title in enumerate(mod["lesson_titles"], start=1):
                lesson = build_lesson(
                    tariff=tariff,
                    module_id=mid,
                    stage=mod["stage"],
                    stage_label=mod["stage_label"],
                    lesson_number=i,
                    title=title,
                )
                path = CATALOG / f"{lesson['slug']}.json"
                if path.exists():
                    prev = json.loads(path.read_text(encoding="utf-8"))
                    if prev.get("status") not in ("каркас", "черновик") or len(
                        prev.get("stations") or []
                    ) > 3:
                        skipped += 1
                        continue
                    if prev.get("status") == "черновик" and len(
                        prev.get("stations") or []
                    ) > 3:
                        skipped += 1
                        continue
                path.write_text(
                    json.dumps(lesson, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                written += 1
    print(f"written={written} skipped={skipped}")


if __name__ == "__main__":
    main()
