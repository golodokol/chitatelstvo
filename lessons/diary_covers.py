"""Обложки читательского дневника: «Обложки книг для рейтинга (N).PNG»."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from config.settings import ROOT
from lessons.covers import _normalize, cover_url_for_lesson

DIARY_SOURCE_DIR = ROOT / "docs" / "images"
DIARY_STATIC_DIR = ROOT / "static" / "diary-covers"
DIARY_MANIFEST = ROOT / "catalog" / "diary_covers.json"
STATIC_URL_PREFIX = "/static/diary-covers"

DIARY_FILENAME_RE = re.compile(
    r"^Обложки книг для рейтинга \((\d+)\)\.(png|jpe?g|webp)$",
    re.IGNORECASE,
)


def _title_matches(keys: tuple[str, ...], title: str) -> bool:
    title_n = _normalize(title)
    for key in keys:
        if key and key in title_n:
            return True
    return False


def _load_manifest() -> tuple[dict[str, int], dict[str, tuple[str, ...]]]:
    data = json.loads(DIARY_MANIFEST.read_text(encoding="utf-8"))
    by_slug = {str(k): int(v) for k, v in data.get("by_slug", {}).items()}
    title_keys: dict[str, tuple[str, ...]] = {}
    for idx, keys in data.get("title_keys", {}).items():
        title_keys[str(idx)] = tuple(keys)
    return by_slug, title_keys


def _source_by_index() -> dict[int, Path]:
    found: dict[int, Path] = {}
    if not DIARY_SOURCE_DIR.is_dir():
        return found
    for path in DIARY_SOURCE_DIR.iterdir():
        if not path.is_file():
            continue
        match = DIARY_FILENAME_RE.match(path.name)
        if match:
            found[int(match.group(1))] = path
    return found


def _sync_diary_file(source: Path, slug: str) -> str:
    DIARY_STATIC_DIR.mkdir(parents=True, exist_ok=True)
    ext = source.suffix.lower()
    static_name = f"{slug}{ext}"
    dest = DIARY_STATIC_DIR / static_name
    if not dest.exists() or source.stat().st_mtime > dest.stat().st_mtime:
        shutil.copy2(source, dest)
    return static_name


@dataclass(frozen=True)
class DiaryCoverEntry:
    slug: str
    index: int
    static_name: str
    title_keys: tuple[str, ...]

    @property
    def url(self) -> str:
        return f"{STATIC_URL_PREFIX}/{self.static_name}"


@lru_cache(maxsize=1)
def _load_registry() -> tuple[DiaryCoverEntry, ...]:
    by_slug, title_keys = _load_manifest()
    sources = _source_by_index()
    entries: list[DiaryCoverEntry] = []
    for slug, index in sorted(by_slug.items(), key=lambda item: item[1]):
        source = sources.get(index)
        if not source:
            continue
        keys = title_keys.get(str(index), ())
        static_name = _sync_diary_file(source, slug)
        entries.append(
            DiaryCoverEntry(
                slug=slug,
                index=index,
                static_name=static_name,
                title_keys=keys,
            )
        )
    return tuple(entries)


def _registry_by_slug() -> dict[str, DiaryCoverEntry]:
    return {entry.slug: entry for entry in _load_registry()}


def diary_cover_url_for_tale(
    tale_slug: str | None,
    title: str | None,
    *,
    module_week: int | None = None,
) -> str | None:
    """URL обложки дневника или fallback на обложку урока."""
    if tale_slug:
        entry = _registry_by_slug().get(tale_slug)
        if entry:
            return entry.url

    if title:
        for entry in _load_registry():
            if _title_matches(entry.title_keys, title):
                return entry.url

    return cover_url_for_lesson(module_week, title)
