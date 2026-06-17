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

CHEST_REWARD_SUMMARY = (
    "письмо от школы, бонусная страница с заданием, "
    "сказочная раскраска и секретная наклейка"
)


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
    return item


def rewards_for_tale(tale_slug: str, tale_title: str) -> list[dict[str, Any]]:
    """Все предметы сундука для показа при открытии (включая письмо)."""
    slug = (tale_slug or "").strip()
    title = (tale_title or "").strip() or "Сказка недели"
    return [_build_item(entry, slug, title) for entry in CHEST_CONTENTS]


def items_for_treasury(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Только то, что сохраняем в сокровищнице (без письма от школы)."""
    return [item for item in items if item.get("kind") in TREASURY_KINDS]


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
        labels = [item.get("label", "") for item in items if item.get("label")]
        if labels:
            return ", ".join(labels[:2]).lower() + " и ещё сюрпризы"
    return CHEST_REWARD_SUMMARY
