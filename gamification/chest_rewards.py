"""Сундук сказки: картинки состояний и награды по tale_slug.

Состав сундука (фиксированный, 4 предмета):
  1. Письмо от школы — показывается при открытии, в сокровищницу не сохраняется.
  2. Бонусная страница с заданием — можно скачать и распечатать, сохраняется в сокровищнице.
  3. Сказочная раскраска — можно скачать и распечатать, сохраняется в сокровищнице.
  4. Секретная наклейка — сохраняется в сокровищнице.

Файлы для каждой сказки: static/chest/rewards/{tale_slug}/
  letter.png       — превью письма (или letter.pdf только для просмотра)
  bonus.pdf        — бонусная страница (или bonus.png)
  coloring.pdf     — раскраска (или coloring.png)
  sticker.png      — наклейка
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config.settings import ROOT

CHEST_STATIC = "/static/chest"

CHEST_IMAGES: dict[str, str] = {
    "closed": f"{CHEST_STATIC}/chest-closed.png",
    "opening": f"{CHEST_STATIC}/chest-opening.png",
    "open": f"{CHEST_STATIC}/chest-open.png",
}

LETTER_KIND = "letter"
BONUS_KIND = "bonus"
COLORING_KIND = "coloring"
STICKER_KIND = "sticker"

# kind, label, файлы превью (по приоритету), файлы для скачивания (по приоритету), запасная картинка
CHEST_CONTENTS: list[dict[str, Any]] = [
    {
        "kind": LETTER_KIND,
        "label": "Письмо от школы",
        "description": "Личное письмо от школы — прочитай сразу после открытия сундука",
        "preview_files": ("letter.png", "letter.jpg"),
        "download_files": ("letter.pdf",),
        "fallback_image": "/static/sloviki/slovik-writes.png",
        "downloadable": False,
        "in_treasury": False,
    },
    {
        "kind": BONUS_KIND,
        "label": "Бонусная страница с заданием",
        "description": "Дополнительное задание по сказке — скачай и распечатай",
        "preview_files": ("bonus.png", "bonus.jpg"),
        "download_files": ("bonus.pdf", "bonus.png"),
        "fallback_image": "/static/sloviki/slovik-grows.png",
        "downloadable": True,
        "in_treasury": True,
    },
    {
        "kind": COLORING_KIND,
        "label": "Сказочная раскраска",
        "description": "Раскраска по мотивам сказки — скачай и распечатай",
        "preview_files": ("coloring.png", "coloring.jpg"),
        "download_files": ("coloring.pdf", "coloring.png"),
        "fallback_image": "/static/sloviki/slovik-reads.png",
        "downloadable": True,
        "in_treasury": True,
    },
    {
        "kind": STICKER_KIND,
        "label": "Секретная наклейка",
        "description": "Редкая наклейка из сундука этой сказки",
        "preview_files": ("sticker.png", "sticker.jpg"),
        "download_files": ("sticker.png",),
        "fallback_image": "/static/sloviki/slovik-dreams.png",
        "downloadable": False,
        "in_treasury": True,
    },
]

TREASURY_KINDS = frozenset({BONUS_KIND, COLORING_KIND, STICKER_KIND})

# Состав сундука для отдельных сказок (если задан — вместо CHEST_CONTENTS)
TALE_CHEST_ITEMS: dict[str, list[dict[str, Any]]] = {
    "early-stories-stage1-tale-00": [
        {
            "kind": "creative_1",
            "label": "Дорисуй дом",
            "description": "Задание из сундука пробного урока — скачай и распечатай",
            "preview_files": ("gift-1.jpg", "gift-1.png"),
            "download_files": ("gift-1.pdf", "gift-1.jpg"),
            "download_name": "Читательство Дорисуй дом.pdf",
            "fallback_image": "/static/sloviki/slovik-grows.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_2",
            "label": "Обведи кота",
            "description": "Задание из сундука пробного урока — скачай и распечатай",
            "preview_files": ("gift-2.jpg", "gift-2.png"),
            "download_files": ("gift-2.pdf", "gift-2.jpg"),
            "download_name": "Читательство Обведи кота.pdf",
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_3",
            "label": "Обведи фразу",
            "description": "Задание из сундука пробного урока — скачай и распечатай",
            "preview_files": ("gift-3.jpg", "gift-3.png"),
            "download_files": ("gift-3.pdf", "gift-3.jpg"),
            "download_name": "Читательство Обведи фразу.pdf",
            "fallback_image": "/static/sloviki/slovik-dreams.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_4",
            "label": "Пройди лабиринт",
            "description": "Задание из сундука пробного урока — скачай и распечатай",
            "preview_files": ("gift-4.jpg", "gift-4.png"),
            "download_files": ("gift-4.pdf", "gift-4.jpg"),
            "download_name": "Читательство Пройди лабиринт.pdf",
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
    ],
    "early-letters-stage1-tale-00": [
        {
            "kind": "creative_1",
            "label": "Обведи арбуз",
            "description": "Задание из сундука пробного урока — скачай и распечатай",
            "preview_files": ("gift-1.png", "gift-1.jpg"),
            "download_files": ("gift-1.pdf", "gift-1.png"),
            "download_name": "Читательство Обведи Арбуз.pdf",
            "fallback_image": "/static/sloviki/slovik-grows.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_2",
            "label": "Обведи букву А",
            "description": "Задание из сундука пробного урока — скачай и распечатай",
            "preview_files": ("gift-2.png", "gift-2.jpg"),
            "download_files": ("letter-a.pdf", "gift-2.pdf", "gift-2.png"),
            "download_name": "Читательство Обведи букву А.pdf",
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_3",
            "label": "Пройди лабиринт",
            "description": "Задание из сундука пробного урока — скачай и распечатай",
            "preview_files": ("gift-3.png", "gift-3.jpg"),
            "download_files": ("gift-3.pdf", "gift-3.png"),
            "download_name": "Читательство Пройди лабиринт.pdf",
            "fallback_image": "/static/sloviki/slovik-dreams.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_4",
            "label": "Раскрась Словика",
            "description": "Задание из сундука пробного урока — скачай и распечатай",
            "preview_files": ("gift-4.png", "gift-4.jpg"),
            "download_files": ("gift-4.pdf", "gift-4.png"),
            "download_name": "Читательство Раскрась Словика.pdf",
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
    ],
    "grade-1-stage1-tale-01": [
        {
            "kind": LETTER_KIND,
            "label": "Письмо от школы",
            "description": "Личное письмо от школы — прочитай сразу после открытия сундука",
            "preview_files": ("letter.png", "letter.jpg"),
            "download_files": ("letter.pdf",),
            "fallback_image": "/static/sloviki/slovik-writes.png",
            "downloadable": False,
            "in_treasury": False,
        },
        {
            "kind": "creative_1",
            "label": "Нарисуй свою лягушку в болоте",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-1.png", "creative-1.jpg"),
            "download_files": ("creative-1.pdf",),
            "fallback_image": "/static/sloviki/slovik-grows.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_2",
            "label": "Раскрась лягушку",
            "description": "Раскраска по сказке — скачай и распечатай",
            "preview_files": ("creative-2.png", "creative-2.jpg"),
            "download_files": ("creative-2.pdf",),
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_3",
            "label": "Обведи стрелу",
            "description": "Задание со стрелой — скачай и распечатай",
            "preview_files": ("creative-3.png", "creative-3.jpg"),
            "download_files": ("creative-3.pdf",),
            "fallback_image": "/static/sloviki/slovik-dreams.png",
            "downloadable": True,
            "in_treasury": True,
        },
    ],
    "grade-2-stage1-tale-01": [
        {
            "kind": LETTER_KIND,
            "label": "Письмо от школы",
            "description": "Личное письмо от школы — прочитай сразу после открытия сундука",
            "preview_files": ("letter.png", "letter.jpg"),
            "download_files": ("letter.pdf",),
            "fallback_image": "/static/sloviki/slovik-writes.png",
            "downloadable": False,
            "in_treasury": False,
        },
        {
            "kind": "creative_1",
            "label": "Нарисуй золотую рыбку",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-1.png", "creative-1.jpg"),
            "download_files": ("creative-1.pdf",),
            "fallback_image": "/static/sloviki/slovik-grows.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_2",
            "label": "Раскрась море спокойным и бурным",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-2.png", "creative-2.jpg"),
            "download_files": ("creative-2.pdf",),
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_3",
            "label": "Сделай комикс: поймал — попросила — отпустил",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-3.png", "creative-3.jpg"),
            "download_files": ("creative-3.pdf",),
            "fallback_image": "/static/sloviki/slovik-dreams.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_4",
            "label": "Нарисуй корыто и 3 добрых желания",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-4.png", "creative-4.jpg"),
            "download_files": ("creative-4.pdf",),
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
    ],
    "extra-6-8-stage1-tale-01": [
        {
            "kind": LETTER_KIND,
            "label": "Письмо от школы",
            "description": "Личное письмо от школы — прочитай сразу после открытия сундука",
            "preview_files": ("letter.png", "letter.jpg"),
            "download_files": ("letter.pdf",),
            "fallback_image": "/static/sloviki/slovik-writes.png",
            "downloadable": False,
            "in_treasury": False,
        },
        {
            "kind": "creative_1",
            "label": "Нарисуй своего плюшевого зайца",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-1.png", "creative-1.jpg"),
            "download_files": ("creative-1.pdf",),
            "fallback_image": "/static/sloviki/slovik-grows.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_2",
            "label": "Сделай комикс: подарок → любовь → чудо",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-2.png", "creative-2.jpg"),
            "download_files": ("creative-2.pdf",),
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_3",
            "label": "Раскрась зайца",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-3.png", "creative-3.jpg"),
            "download_files": ("creative-3.pdf",),
            "fallback_image": "/static/sloviki/slovik-dreams.png",
            "downloadable": True,
            "in_treasury": True,
        },
    ],
    "extra-9-11-stage1-tale-01": [
        {
            "kind": LETTER_KIND,
            "label": "Письмо от школы",
            "description": "Личное письмо от школы — прочитай сразу после открытия сундука",
            "preview_files": ("letter.png", "letter.jpg"),
            "download_files": ("letter.pdf",),
            "fallback_image": "/static/sloviki/slovik-writes.png",
            "downloadable": False,
            "in_treasury": False,
        },
        {
            "kind": "creative_1",
            "label": "Сделай комикс: потоп → театр → роль",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-1.png", "creative-1.jpg"),
            "download_files": ("creative-1.pdf",),
            "fallback_image": "/static/sloviki/slovik-grows.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_2",
            "label": "Нарисуй свой театр",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-2.png", "creative-2.jpg"),
            "download_files": ("creative-2.pdf",),
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_3",
            "label": "Напиши письмо герою",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-3.png", "creative-3.jpg"),
            "download_files": ("creative-3.pdf",),
            "fallback_image": "/static/sloviki/slovik-dreams.png",
            "downloadable": True,
            "in_treasury": True,
        },
    ],
    "grade-3-stage1-tale-01": [
        {
            "kind": LETTER_KIND,
            "label": "Письмо от школы",
            "description": "Личное письмо от школы — прочитай сразу после открытия сундука",
            "preview_files": ("letter.png", "letter.jpg"),
            "download_files": ("letter.pdf",),
            "fallback_image": "/static/sloviki/slovik-writes.png",
            "downloadable": False,
            "in_treasury": False,
        },
        {
            "kind": "creative_1",
            "label": "Сделай комикс: ложь → испытание → правда",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-1.png", "creative-1.jpg"),
            "download_files": ("creative-1.pdf",),
            "fallback_image": "/static/sloviki/slovik-grows.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_2",
            "label": "Напиши письмо Салтану от Гвидона",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-2.png", "creative-2.jpg"),
            "download_files": ("creative-2.pdf",),
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_3",
            "label": "Нарисуй свой остров",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-3.png", "creative-3.jpg"),
            "download_files": ("creative-3.pdf",),
            "fallback_image": "/static/sloviki/slovik-dreams.png",
            "downloadable": True,
            "in_treasury": True,
        },
    ],
    "grade-4-stage1-tale-01": [
        {
            "kind": LETTER_KIND,
            "label": "Письмо от школы",
            "description": "Личное письмо от школы — прочитай сразу после открытия сундука",
            "preview_files": ("letter.png", "letter.jpg"),
            "download_files": ("letter.pdf",),
            "fallback_image": "/static/sloviki/slovik-writes.png",
            "downloadable": False,
            "in_treasury": False,
        },
        {
            "kind": "creative_1",
            "label": "Сделай комикс: чудо → испытание → цена выбора",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-1.png", "creative-1.jpg"),
            "download_files": ("creative-1.pdf",),
            "fallback_image": "/static/sloviki/slovik-grows.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_2",
            "label": "Нарисуй дух горы в двух обликах",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-2.png", "creative-2.jpg"),
            "download_files": ("creative-2.pdf",),
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_3",
            "label": "Напиши свой мини-сказ",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-3.png", "creative-3.jpg"),
            "download_files": ("creative-3.pdf",),
            "fallback_image": "/static/sloviki/slovik-dreams.png",
            "downloadable": True,
            "in_treasury": True,
        },
        {
            "kind": "creative_4",
            "label": "Нарисуй Хозяйку Медной горы",
            "description": "Творческое задание — скачай и распечатай",
            "preview_files": ("creative-4.png", "creative-4.jpg"),
            "download_files": ("creative-4.pdf",),
            "fallback_image": "/static/sloviki/slovik-reads.png",
            "downloadable": True,
            "in_treasury": True,
        },
    ],
}

CHEST_REWARD_SUMMARY = "бонусная страница с заданием и ещё сюрпризы"


def canonical_tale_slug(tale_slug: str) -> str:
    """Приводит slug урока или сказки к ключу папки наград сундука."""
    slug = (tale_slug or "").strip()
    if not slug:
        return ""
    if slug in TALE_CHEST_ITEMS:
        return slug

    from lessons.loader import get_lesson

    lesson = get_lesson(slug)
    if lesson:
        canonical = (lesson.get("tale_slug") or "").strip()
        if canonical:
            return canonical
    return slug


def _rewards_dir(tale_slug: str) -> Path:
    return ROOT / "static" / "chest" / "rewards" / tale_slug


def _first_existing(base: Path, names: tuple[str, ...]) -> Path | None:
    for name in names:
        path = base / name
        if path.is_file():
            return path
    return None


def _static_url(tale_slug: str, filename: str) -> str:
    return f"/static/chest/rewards/{tale_slug}/{filename}"


def _build_item(entry: dict[str, Any], tale_slug: str, tale_title: str) -> dict[str, Any]:
    folder = _rewards_dir(tale_slug)
    preview = _first_existing(folder, entry["preview_files"])
    download = _first_existing(folder, entry["download_files"])

    image_url = (
        _static_url(tale_slug, preview.name)
        if preview
        else entry["fallback_image"]
    )
    download_url = _static_url(tale_slug, download.name) if download else None

    item: dict[str, Any] = {
        "kind": entry["kind"],
        "label": entry["label"],
        "description": entry["description"],
        "image_url": image_url,
        "downloadable": bool(entry["downloadable"] and download_url),
        "in_treasury": bool(entry["in_treasury"]),
        "tale_title": tale_title,
    }
    if download_url:
        item["download_url"] = download_url
        name = (entry.get("download_name") or "").strip()
        if name:
            item["download_name"] = name
    return item


def rewards_for_tale(tale_slug: str, tale_title: str) -> list[dict[str, Any]]:
    """Все предметы сундука для показа при открытии (включая письмо)."""
    slug = canonical_tale_slug((tale_slug or "").strip())
    title = (tale_title or "").strip() or "Сказка недели"
    entries = TALE_CHEST_ITEMS.get(slug) or CHEST_CONTENTS
    return [_build_item(entry, slug, title) for entry in entries]


def items_for_treasury(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Только то, что сохраняем в сокровищнице (без письма и без пустых заглушек Словика)."""
    out: list[dict[str, Any]] = []
    for item in items:
        kind = str(item.get("kind", ""))
        if kind not in TREASURY_KINDS and not kind.startswith("creative_"):
            continue
        image = str(item.get("image_url") or "")
        has_file = bool(item.get("download_url")) or "/static/chest/rewards/" in image
        if not has_file:
            continue
        out.append(item)
    return out


def chest_visual_state(
    *,
    steps_done: int,
    steps_total: int,
    ready: bool,
    claimed: bool,
) -> str:
    if claimed:
        return "claimed"
    if ready:
        return "ready"
    if steps_done > 0:
        return "opening"
    return "closed"


def chest_image_for_state(visual: str) -> str:
    if visual in ("ready", "claimed"):
        return CHEST_IMAGES["open"]
    if visual == "opening":
        return CHEST_IMAGES["opening"]
    return CHEST_IMAGES["closed"]


def reward_summary_text(items: list[dict[str, Any]] | None = None) -> str:
    if items:
        labels = [
            item.get("label", "")
            for item in items
            if item.get("label") and item.get("kind") != LETTER_KIND
        ]
        if labels:
            return ", ".join(labels[:2]).lower() + " и ещё сюрпризы"
    return CHEST_REWARD_SUMMARY
