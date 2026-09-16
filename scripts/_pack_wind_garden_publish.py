# -*- coding: utf-8 -*-
"""Update wind/garden teacher copy (Olga leads) + write Tilda publish pack."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "course-pages" / "course-lite-data.js"
SEO = ROOT / "docs" / "course-pages" / "course-seo.json"
PUB = ROOT / "docs" / "course-pages" / "tilda-publish"
REDIR = ROOT / "docs" / "course-pages" / "tilda-redirects"


def patch_js_text(text: str) -> str:
    reps = [
        (
            "Встречи с преподавателем — по четвергам.",
            "Живые встречи ведёт Ольга Рощина — по четвергам.",
        ),
        (
            "На тарифе с преподавателем — живые занятия в мини-группе.",
            "На тарифе с живыми встречами занятия ведёт Ольга Рощина — в мини-группе.",
        ),
        (
            "Живые встречи — на тарифе «С преподавателем».",
            "Живые встречи с Ольгой — на тарифе «С преподавателем».",
        ),
        (
            "С преподавателем — 4 990 ₽: та же основа плюс живые встречи по четвергам.",
            "С преподавателем — 4 990 ₽: та же основа плюс живые встречи с Ольгой по четвергам.",
        ),
    ]
    for a, b in reps:
        text = text.replace(a, b)
    return text


def patch_seo(seo: dict) -> None:
    for key in ("wind", "garden"):
        c = seo["lite"][key]
        c["lead"] = c["lead"].replace(
            "Встречи с преподавателем — по четвергам.",
            "Живые встречи ведёт Ольга Рощина — по четвергам.",
        )
        c["inside"] = [
            x.replace(
                "На тарифе с преподавателем — живые встречи по четвергам в мини-группе",
                "На тарифе с живыми встречами занятия ведёт Ольга Рощина — по четвергам в мини-группе",
            )
            for x in c.get("inside", [])
        ]
        for item in c.get("faq", []):
            if item.get("a"):
                item["a"] = (
                    item["a"]
                    .replace(
                        "Живые встречи — на тарифе «С преподавателем».",
                        "Живые встречи с Ольгой — на тарифе «С преподавателем».",
                    )
                    .replace(
                        "плюс живые встречи по четвергам.",
                        "плюс живые встречи с Ольгой по четвергам.",
                    )
                )
        # Stronger SEO titles for Tilda page settings
        if key == "wind":
            c["seoTitle"] = "Ветер в ивах — медленное чтение для детей 6–9 | Читательство"
            c["keywords"] = (
                "ветер в ивах, медленное чтение, курс по книге для детей 6-9, "
                "кеннет грэм, Читательство, онлайн школа чтения"
            )
        else:
            c["seoTitle"] = "Таинственный сад — медленное чтение для детей 10–12 | Читательство"
            c["keywords"] = (
                "таинственный сад, тайный сад, медленное чтение, курс по книге для детей 10-12, "
                "бернетт, Читательство, онлайн школа чтения"
            )


def write_publish_sheet(seo: dict) -> None:
    wind = seo["lite"]["wind"]
    garden = seo["lite"]["garden"]
    org = seo["org"]
    site = seo["site"]
    assets = seo["assets"]

    def block(name: str, c: dict, group: str) -> str:
        url = f"{site}/{c['slug']}"
        cover = {
            "wind": f"{assets}/course-cover-wind.webp",
            "garden": f"{assets}/course-cover-garden.webp",
        }[group]
        lessons = "\n".join(f"{i}. {t}" for i, t in enumerate(c["lessons"], 1))
        return f"""## {name}

| Поле в Tilda | Значение |
|---|---|
| **Название страницы** (в списке страниц) | {c['h1']} |
| **Адрес страницы** (URL) | `/{c['slug']}` |
| **Полный URL** | {url} |
| **Title** (SEO) | {c['seoTitle']} |
| **Description** (SEO) | {c['description']} |
| **Keywords** | {c['keywords']} |
| **Canonical** | {url} |
| **og:image** | {cover} |
| **H1 на странице** | {c['h1']} |
| **Возраст** | {c['age']} |
| **Бейдж** | {c['badge']} |
| **Старт** | 22 сентября |
| **Открытие уроков** | 22 и 28 сентября, 5 и 12 октября |
| **Живые встречи** | по четвергам, ведёт Ольга Рощина |
| **Файл для Zero Block** | `tilda-publish/{c['slug']}.html` |

### Уроки
{lessons}

### Короткий lead
{c['lead']}

### Intro
{c['intro']}
"""

    md = f"""# Публикация: Ветер в ивах + Таинственный сад

Организация: **{org}** · сайт: {site}  
Контакт: info@chitatelstvo.ru · ИП Рощина Ольга Владимировна · ИНН 231150315327

## Как опубликовать в Tilda

1. **Страницы** → **Добавить страницу** (или открыть уже созданную).
2. Заполнить **Title / Description** из таблицы ниже (Настройки страницы → SEO).
3. Задать **адрес** (`veter-v-ivah` / `tainstvenny-sad`).
4. Добавить **Zero Block** → HTML-элемент `</>` → вставить **весь** файл из `tilda-publish/`.
5. Артборд **1200**, высота **авто**, выравнивание сверху.
6. Убрать лишние стандартные блоки Tilda на странице (оставить Zero Block).
7. **Опубликовать**.

Опционально: скрытая форма «Жду с преподавателем» (Email + Phone), если нужна заявка на живые встречи.

---

{block("1. Ветер в ивах", wind, "wind")}

---

{block("2. Таинственный сад", garden, "garden")}

---

## Тарифы (обе страницы)

| Тариф | Цена | Что входит |
|---|---|---|
| Разовое | 799 ₽ | 1 занятие на платформе |
| Индивидуальное | 1 990 ₽ | 4 занятия, свой темп |
| С преподавателем | 4 990 ₽ | 4 занятия + живые встречи с Ольгой |

## Меню / ссылки

- https://chitatelstvo.ru/veter-v-ivah
- https://chitatelstvo.ru/tainstvenny-sad
- Карточки на главной уже ведут на эти URL (после деплоя главной).
"""
    PUB.mkdir(parents=True, exist_ok=True)
    (PUB / "SEO-PUBLISH.md").write_text(md, encoding="utf-8")
    print("wrote", PUB / "SEO-PUBLISH.md")


def main() -> None:
    DATA.write_text(patch_js_text(DATA.read_text(encoding="utf-8")), encoding="utf-8")
    seo = json.loads(SEO.read_text(encoding="utf-8"))
    patch_seo(seo)
    SEO.write_text(json.dumps(seo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("patched data + seo")

    # regenerate shells
    import subprocess
    import sys

    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "_gen_course_pages.py")], cwd=str(ROOT))

    PUB.mkdir(parents=True, exist_ok=True)
    for slug in ("veter-v-ivah", "tainstvenny-sad"):
        src = REDIR / f"{slug}.html"
        dst = PUB / f"{slug}.html"
        shutil.copyfile(src, dst)
        print("copied", dst)

    write_publish_sheet(seo)
    print("OK")


if __name__ == "__main__":
    main()
