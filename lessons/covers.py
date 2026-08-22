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
    r"^[Уу]рок\s+(\d+)\s*[-–—]?\s*(.+)\.(png|jpe?g|webp)$",
    re.IGNORECASE,
)

EARLY_ASSETS_VERSION = "20260822n"

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
    # Этап 2 (module_week 5–8)
    "по щучьему велению": ("по щучьему велению",),
    "филипок": ("филипок",),
    "сказка о молодильных яблоках": ("молодильных яблоках", "волшебное кольцо"),
    "приключения тома сойера": ("тома сойера", "том сойер"),
    "невероятные приключения кролика эдварда": ("кролика эдварда", "эдвард"),
    "сказка о мертвой царевне": ("мёртвой царевне", "мертвой царевне"),
    "незнайка на луне": ("незнайка",),
    "серебряный рубль": ("серебряный рубль",),
    "белый бим, черное ухо": ("белый бим", "бим"),
    "тутта карлссон": ("тутта карлссон",),
    "чудесное путешествие нильса с дикими гусями": (
        "чудесное путешествие нильса",
        "нильса с дикими гусями",
    ),
    "принцесса на горошине": ("принцесса на горошине", "горошине"),
    "рикки-тикки-тави": ("рикки-тикки",),
    "аленький цветочек": ("аленький цветочек",),
    "пеппи длинный чулок": ("пеппи",),
    "полианна": ("полианна",),
    "карлик нос": ("карлик нос",),
    "аля, кляксич и буква а": ("аля, кляксич", "кляксич"),
    "маленькая баба-яга": ("бабая-яга", "баба-яга"),
    "маленькая баьа-яга": ("бабая-яга",),
    "маленькая бабая-яга": ("бабая-яга",),
    "королевство кривых зеркал": ("кривых зеркал",),
    "путешествия гулливера": ("гулливер",),
    "чарли и шоколадная фабрика": ("чарли",),
    "калиф аист": ("калиф-аист", "калиф аист"),
    "маленький мук": ("маленький мук",),
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


# Имя в static/lesson-covers → (module_week, hint для docs/images)
STAGED_UPLOAD_HINTS: dict[str, tuple[int, str]] = {
    "по щучьему велению": (5, "По щучьему велению"),
    "филипок": (5, "Филипок"),
    "сказка о молодильных яблоках": (5, "Сказка о молодильных яблоках"),
    "приключения тома сойера": (5, "Приключения Тома Сойера"),
    "невероятные приключения кролика эдварда": (
        5,
        "Невероятные приключения кролика Эдварда",
    ),
    "чудесное путешествие нильса с дикими гусями": (
        5,
        "Чудесное путешествие Нильса с дикими гусями",
    ),
    "сказка о мертвой царевне": (6, "Сказка о мертвой Царевне"),
    "незнайка на луне": (6, "Незнайка на Луне"),
    "серебряный рубль": (6, "Серебряный рубль"),
    "белый бим, черное ухо": (6, "Белый Бим, Чёрное Ухо"),
    "тутта карлссон": (6, "Тутта Карлссон"),
    "чудесное путешествие нильса 2 часть": (
        6,
        "Чудесное путешествие Нильса 2 часть",
    ),
    "принцесса на горошине": (7, "Принцесса на горошине"),
    "рикки-тикки-тави": (7, "Рикки-Тикки-Тави"),
    "аленький цветочек": (7, "Аленький цветочек"),
    "пеппи длинный чулок": (7, "Пеппи Длинный чулок"),
    "полианна": (7, "Полианна"),
    "карлик нос": (7, "Карлик Нос"),
    "аля, кляксич и буква а": (8, "Аля, Кляксич и буква А"),
    "маленькая баба-яга": (8, "Маленькая Баба-Яга"),
    "королевство кривых зеркал": (8, "Королевство кривых зеркал"),
    "путешествия гулливера": (8, "Путешествия Гулливера"),
    "чарли и шоколадная фабрика": (8, "Чарли и шоколадная фабрика"),
    "калиф аист": (8, "Калиф Аист"),
    "маленький мук": (8, "Маленький мук"),
}


def _resolve_staged_upload(hint: str, file_week: int) -> tuple[int, str] | None:
    norm = _normalize(hint)
    if norm in STAGED_UPLOAD_HINTS:
        return STAGED_UPLOAD_HINTS[norm]
    if "нильс" in norm and file_week == 6:
        return STAGED_UPLOAD_HINTS["чудесное путешествие нильса 2 часть"]
    if "нильс" in norm and file_week == 1:
        return STAGED_UPLOAD_HINTS["чудесное путешествие нильса с дикими гусями"]
    if "баба" in norm or "бaба" in norm:
        return STAGED_UPLOAD_HINTS["маленькая баба-яга"]
    if norm.startswith("аля") or "кляксич" in norm:
        return STAGED_UPLOAD_HINTS["аля, кляксич и буква а"]
    return None


def import_labeled_covers_from_static() -> list[str]:
    """Переносит «Урок N — …» из static/lesson-covers в docs/images и синхронизирует."""
    COVER_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    imported: list[str] = []
    for path in sorted(COVER_STATIC_DIR.iterdir()):
        if not path.is_file() or path.name.startswith("urok-"):
            continue
        match = COVER_FILENAME_RE.match(path.name)
        if not match:
            continue
        file_week = int(match.group(1))
        hint_raw = match.group(2).strip()
        resolved = _resolve_staged_upload(hint_raw, file_week)
        if not resolved:
            continue
        module_week, hint = resolved
        dest_name = f"Урок {module_week} {hint}{path.suffix.lower()}"
        dest = COVER_SOURCE_DIR / dest_name
        shutil.copy2(path, dest)
        imported.append(f"{path.name} → {dest_name}")
        path.unlink()
    if imported:
        _load_registry.cache_clear()
        _load_registry()
    return imported


def enrich_lesson_link(link: dict) -> dict:
    """Добавляет cover_url и cover_state в словарь урока для шаблона."""
    week = link.get("module_week")
    title = link.get("title") or ""
    cover = cover_url_for_lesson(week, title)
    if not cover:
        group = str(link.get("group_code") or "")
        early_covers = {
            "early-letters": "course-cover-letters.jpg",
            "early-stories": "course-cover-stories.jpg",
        }
        filename = early_covers.get(group)
        if filename:
            from config.settings import PUBLIC_BASE_URL

            cover = f"{PUBLIC_BASE_URL.rstrip('/')}/assets/{filename}?v={EARLY_ASSETS_VERSION}"
    link["cover_url"] = cover
    link["cover_state"] = lesson_cover_state(
        url=link.get("url"),
        unlocked=bool(link.get("unlocked")),
        ready=bool(link.get("ready", True)),
    )
    return link
