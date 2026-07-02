"""Обложки уроков: скан docs/images и привязка по «Урок N …»."""

from __future__ import annotations

import hashlib
import re
import shutil
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from config.settings import ROOT

COVER_SOURCE_DIR = ROOT / "docs" / "images"
COVER_STATIC_DIR = ROOT / "static" / "lesson-covers"
STATIC_URL_PREFIX = "/static/lesson-covers"

COVER_FILENAME_RE = re.compile(
    r"^[Уу]рок\s+(\d+)\s+(.+)\.(png|jpe?g|webp)$",
    re.IGNORECASE,
)

# Подсказка из имени файла → фрагменты в title урока
HINT_ALIASES: dict[str, tuple[str, ...]] = {
    "царевна лягушка": ("царевна лягушка",),
    "сказка о царе салтане": ("царе салтане", "салтан"),
    "сказка о золотой рыбке": ("рыбаке и рыбке", "золотой рыбк", "золотая рыбка"),
    "малахитовая шкатулка": ("малахитовая", "уральские сказы", "бажов"),
    "остров сальткрока": ("сальткрок", "острове сальткрока", "сальткрока"),
    "вафельное сердце": ("вафельное сердце",),
    "опасное лето": ("опасное лето",),
    "рони дочь разбойника": ("рони", "дочь разбойника"),
    "рассказы азбука толстой": ("рассказы из азбуки", "азбуки", "толстой"),
    "носов шляпа": ("рассказы н. носова", "носов", "шляпа"),
    "как муравьишка домой спешил": ("как муравьишка домой", "муравьишка", "раки зимуют"),
    "медвежонок паддингтон": ("медвежонка паддингтона", "паддингтон", "приключения медвежонка"),
}


def _normalize(text: str) -> str:
    raw = unicodedata.normalize("NFKC", text or "")
    raw = raw.replace("ё", "е").lower().strip()
    return re.sub(r"\s+", " ", raw)


def _slugify_hint(week: int, hint: str) -> str:
    digest = hashlib.md5(_normalize(hint).encode("utf-8")).hexdigest()[:10]
    return f"urok-{week}-{digest}"


def _hint_keywords(hint: str) -> tuple[str, ...]:
    norm = _normalize(hint)
    extra = HINT_ALIASES.get(norm, ())
    return (norm, *extra)


def _title_matches(hint: str, title: str) -> bool:
    title_n = _normalize(title)
    for key in _hint_keywords(hint):
        if key and key in title_n:
            return True
    return False


@dataclass(frozen=True)
class CoverEntry:
    week: int
    hint: str
    static_name: str

    @property
    def url(self) -> str:
        return f"{STATIC_URL_PREFIX}/{self.static_name}"


def _sync_cover_file(source: Path, week: int, hint: str) -> str:
    COVER_STATIC_DIR.mkdir(parents=True, exist_ok=True)
    ext = source.suffix.lower()
    static_name = f"{_slugify_hint(week, hint)}{ext}"
    dest = COVER_STATIC_DIR / static_name
    if not dest.exists() or source.stat().st_mtime > dest.stat().st_mtime:
        shutil.copy2(source, dest)
    return static_name


@lru_cache(maxsize=1)
def _load_registry() -> tuple[CoverEntry, ...]:
    if not COVER_SOURCE_DIR.is_dir():
        return ()

    entries: list[CoverEntry] = []
    for path in sorted(COVER_SOURCE_DIR.iterdir()):
        if not path.is_file():
            continue
        match = COVER_FILENAME_RE.match(path.name)
        if not match:
            continue
        week = int(match.group(1))
        hint = match.group(2).strip()
        static_name = _sync_cover_file(path, week, hint)
        entries.append(CoverEntry(week=week, hint=hint, static_name=static_name))
    return tuple(entries)


def cover_url_for_lesson(module_week: int | None, title: str | None) -> str | None:
    """URL обложки или None, если файла «Урок N …» нет."""
    if not module_week or not title:
        return None
    for entry in _load_registry():
        if entry.week == module_week and _title_matches(entry.hint, title):
            return entry.url
    return None


def lesson_cover_state(*, url: str | None, unlocked: bool, ready: bool) -> str:
    if url:
        return "open"
    if unlocked and ready:
        return "soon"
    if unlocked:
        return "soon"
    return "locked"


def enrich_lesson_link(link: dict) -> dict:
    """Добавляет cover_url и cover_state в словарь урока для шаблона."""
    week = link.get("module_week")
    title = link.get("title") or ""
    link["cover_url"] = cover_url_for_lesson(week, title)
    link["cover_state"] = lesson_cover_state(
        url=link.get("url"),
        unlocked=bool(link.get("unlocked")),
        ready=bool(link.get("ready", True)),
    )
    return link
