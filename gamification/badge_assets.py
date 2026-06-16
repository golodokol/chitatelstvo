"""Бейджи: имена файлов в /assets и синхронизация из docs/images."""

from __future__ import annotations

import shutil
from pathlib import Path

from config.settings import ROOT

IMAGES_DIR = ROOT / "docs" / "images"

# Имя бейджа в каталоге → файл на CDN (/assets/…)
BADGE_ASSET_FILES: dict[str, str] = {
    "Первый шаг": "gamify-badge-first-step.png",
    "Читатель": "gamify-badge-reader.png",
    "Слушатель": "gamify-badge-listener.png",
    "Следопыт": "gamify-badge-tracker.png",
    "Ловец смысла": "gamify-badge-meaning.png",
    "Мастер пересказа": "gamify-badge-retelling.png",
    "Сказочник": "gamify-badge-storyteller.png",
    "Исследователь сказки": "gamify-badge-module-explorer.png",
    "Непрерывная серия": "gamify-badge-streak.png",
}

# Исходники от дизайнера (docs/images)
BADGE_SOURCE_FILES: dict[str, str] = {
    "Первый шаг": "бейдж первый шаг.PNG",
    "Читатель": "бейдж юный читатель.PNG",
    "Слушатель": "бейдж слушатель.PNG",
    "Следопыт": "бейдж следопыт.PNG",
    "Ловец смысла": "бейдж ловец смысла.PNG",
    "Мастер пересказа": "бейдж мастер пересказа.PNG",
    "Сказочник": "бейдж сказочник.PNG",
    "Исследователь сказки": "бейдж исследователь сказки.PNG",
    "Непрерывная серия": "бейдж непрерывная серия.PNG",
}


def _resolve_source(name: str) -> Path | None:
    rel = BADGE_SOURCE_FILES.get(name)
    if not rel:
        return None
    path = IMAGES_DIR / rel
    if path.is_file():
        return path
    # без учёта регистра / homoglyph в «бейдж»
    target = rel.lower()
    for candidate in IMAGES_DIR.iterdir():
        if candidate.is_file() and candidate.name.lower() == target:
            return candidate
    return None


def sync_badge_assets() -> list[str]:
    """Копирует бейджи в docs/images/gamify-badge-*.png. Возвращает список созданных имён."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    synced: list[str] = []
    for badge_name, asset_name in BADGE_ASSET_FILES.items():
        source = _resolve_source(badge_name)
        if not source:
            continue
        dest = IMAGES_DIR / asset_name
        if not dest.exists() or source.stat().st_mtime > dest.stat().st_mtime:
            shutil.copy2(source, dest)
        synced.append(asset_name)
    return synced
