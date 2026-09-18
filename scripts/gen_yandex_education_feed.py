# -*- coding: utf-8 -*-
"""Generate Yandex Webmaster education YML feed from course-seo.json."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SEO_JSON = ROOT / "docs" / "course-pages" / "course-seo.json"
OUT = ROOT / "static" / "feeds" / "education.yml"

# --- from Yandex rubricator (education.html → Рубрикатор категорий) ---
CATEGORY_PARENT_ID = "10000"
CATEGORY_PARENT_NAME = "Школьные предметы"  # parent of Литература; rename if rubricator differs
CATEGORY_ID = "10010"  # Литература
CATEGORY_ID_EARLY = "10010"  # same until a narrower preschool id is known
CATEGORY_NAME = "Литература"
CATEGORY_NAME_EARLY = "Литература"

SHOP_NAME = "Читательство"
SHOP_URL = "https://chitatelstvo.ru"
SHOP_EMAIL = "info@chitatelstvo.ru"
SHOP_PICTURE = "https://api.chitatelstvo.ru/assets/logo-chitatelstvo-square.png"
SHOP_DESCRIPTION = (
    "Онлайн-школа литературного чтения для детей 4–12 лет: "
    "буквы, первые истории, сказки по классам и внеклассное чтение."
)

SITE = "https://chitatelstvo.ru"
ASSETS = "https://api.chitatelstvo.ru/assets"

# Module price shown on course pages (Индивидуальное)
PRICE_MODULE = 1990


def xml_text(s: str) -> str:
    return escape(s or "", {"'": "&apos;", '"': "&quot;"})


def cdata(s: str) -> str:
    return f"<![CDATA[{s}]]>"


def plan_items(course: dict) -> list[tuple[str, str]]:
    """Return at least 3 (unit_title, description) plan steps."""
    items: list[tuple[str, str]] = []
    prog = course.get("program") or {}
    for block_key, label in (("block1", "Блок 1"), ("block2", "Блок 2")):
        for i, title in enumerate(prog.get(block_key) or [], 1):
            items.append((f"{label} · урок {i}", str(title)))
    for i, title in enumerate(course.get("lessons") or [], 1):
        items.append((f"Урок {i}", str(title)))
    # fallback from outcome
    if len(items) < 3:
        for i, t in enumerate(course.get("outcome") or [], 1):
            items.append((f"Результат {i}", str(t)))
    while len(items) < 3:
        items.append((f"Этап {len(items) + 1}", course.get("description") or course.get("h1") or "Занятие"))
    return items[:8]


def hours_for(course: dict, *, lite: bool) -> str:
    n = 0
    prog = course.get("program") or {}
    n += len(prog.get("block1") or []) + len(prog.get("block2") or [])
    if not n:
        n = len(course.get("lessons") or []) or (4 if lite else 8)
    # ~20 min per lesson → hours rounded
    h = max(1, round(n * 20 / 60))
    return str(h)


def grades_param(slug: str) -> str | None:
    m = {
        "1-klass": "1",
        "2-klass": "2",
        "3-klass": "3",
        "4-klass": "4",
        "6-8-let": "1-2",
        "9-11-let": "3-4",
        "russkie-skazki-6-9": "1-3",
        "russkie-skazki-10-12": "4-5",
        "veter-v-ivah": "1-3",
        "tainstvenny-sad": "4-5",
    }
    return m.get(slug)


def set_ids(slug: str, *, early: bool) -> str:
    if early or slug in ("bukvy-ozhivayut", "pervye-istorii"):
        return "s-early"
    if slug in ("veter-v-ivah", "tainstvenny-sad", "russkie-skazki-6-9", "russkie-skazki-10-12"):
        return "s-slow"
    return "s-school"


def cover_url(slug: str) -> str:
    # Prefer known covers; fallback to founder photo
    covers = {
        "veter-v-ivah": f"{ASSETS}/course-cover-wind.webp",
        "tainstvenny-sad": f"{ASSETS}/course-cover-garden.webp",
        "bukvy-ozhivayut": f"{ASSETS}/course-cover-letters.webp",
        "pervye-istorii": f"{ASSETS}/course-cover-stories.webp",
    }
    return covers.get(slug, f"{ASSETS}/founder-olga.jpg")


def offer_xml(course: dict, *, offer_id: str, early: bool) -> str:
    slug = course["slug"]
    name = course.get("seoTitle") or course.get("h1") or slug
    # unique names for two russian fairy tales
    if slug == "russkie-skazki-6-9":
        name = "Русские сказки 6–9 лет — Читательство"
    elif slug == "russkie-skazki-10-12":
        name = "Русские сказки 10–12 лет — Читательство"

    url = f"{SITE}/{slug}"
    desc = course.get("description") or course.get("lead") or ""
    cat = CATEGORY_ID_EARLY if early else CATEGORY_ID
    plans = plan_items(course)
    hours = hours_for(course, lite=early or slug.startswith("russkie") or slug in ("veter-v-ivah", "tainstvenny-sad"))
    grades = grades_param(slug)

    lines = [
        f'    <offer id="{xml_text(offer_id)}">',
        f"      <name>{xml_text(name)}</name>",
        f"      <url>{xml_text(url)}</url>",
        f"      <categoryId>{xml_text(cat)}</categoryId>",
        f"      <set-ids>{set_ids(slug, early=early)}</set-ids>",
        f"      <price>{PRICE_MODULE}</price>",
        "      <currencyId>RUR</currencyId>",
        f'      <param name="Продолжительность" unit="час">{hours}</param>',
    ]
    for i, (unit, body) in enumerate(plans, 1):
        lines.append(
            f'      <param name="План" order="{i}" unit="{xml_text(unit)}" hours="1">{cdata(body)}</param>'
        )
    lines += [
        '      <param name="Формат обучения">Самостоятельно</param>',
        '      <param name="Есть видеоуроки">true</param>',
        '      <param name="Есть текстовые уроки">true</param>',
        '      <param name="Есть домашние работы">true</param>',
        '      <param name="Есть тренажеры">false</param>',
        '      <param name="Есть вебинары">false</param>',
        '      <param name="Есть сообщество">false</param>',
        '      <param name="Сложность">Для новичков</param>',
        '      <param name="Тип обучения">Курс</param>',
        '      <param name="Есть бесплатная часть">true</param>',
    ]
    if grades:
        lines.append(f'      <param name="Классы">{xml_text(grades)}</param>')
    lines += [
        f"      <picture>{xml_text(cover_url(slug))}</picture>",
        f"      <description>{cdata(desc)}</description>",
        "    </offer>",
    ]
    return "\n".join(lines)


def main() -> None:
    data = json.loads(SEO_JSON.read_text(encoding="utf-8"))
    offers: list[str] = []
    n = 0

    for key, course in (data.get("full") or {}).items():
        n += 1
        offers.append(offer_xml(course, offer_id=f"full-{course['slug']}", early=False))

    for key, course in (data.get("lite") or {}).items():
        n += 1
        early = key.startswith("early")
        offers.append(offer_xml(course, offer_id=f"lite-{course['slug']}", early=early))

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<yml_catalog date="{now}">
  <shop>
    <name>{xml_text(SHOP_NAME)}</name>
    <company>{xml_text(SHOP_NAME)}</company>
    <url>{xml_text(SHOP_URL)}</url>
    <email>{xml_text(SHOP_EMAIL)}</email>
    <picture>{xml_text(SHOP_PICTURE)}</picture>
    <description>{cdata(SHOP_DESCRIPTION)}</description>
    <currencies>
      <currency id="RUR" rate="1"/>
    </currencies>
    <categories>
      <category id="{xml_text(CATEGORY_PARENT_ID)}">{xml_text(CATEGORY_PARENT_NAME)}</category>
      <category id="{xml_text(CATEGORY_ID)}" parentId="{xml_text(CATEGORY_PARENT_ID)}">{xml_text(CATEGORY_NAME)}</category>
    </categories>
    <sets>
      <set id="s-school">
        <name>Курсы по классам и внеклассное чтение</name>
        <url>{SITE}/programmy</url>
      </set>
      <set id="s-early">
        <name>Первые шаги в чтении</name>
        <url>{SITE}/programmy</url>
      </set>
      <set id="s-slow">
        <name>Медленное чтение</name>
        <url>{SITE}/programmy</url>
      </set>
    </sets>
    <offers>
{chr(10).join(offers)}
    </offers>
  </shop>
</yml_catalog>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(body, encoding="utf-8")
    print(f"Wrote {OUT} ({n} offers), categoryId={CATEGORY_ID}")


if __name__ == "__main__":
    main()
