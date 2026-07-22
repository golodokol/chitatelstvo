"""One-off: map uploaded lesson covers and sync to project convention."""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lessons.covers import (  # noqa: E402
    COVER_SOURCE_DIR,
    COVER_STATIC_DIR,
    _load_registry,
    _slugify_hint,
    _title_matches,
    cover_url_for_lesson,
)

UPLOAD_RE = re.compile(
    r"^[Уу]рок\s+(\d+)\s*[-–—]?\s*(.+)\.(png|jpe?g|webp)$",
    re.IGNORECASE,
)

HINT_OVERRIDES: dict[str, str] = {
    "Маленькая Баьа-Яга": "Маленькая Бабая-Яга",
}


def load_lessons():
    catalog = ROOT / "lessons" / "catalog"
    lessons = []
    for path in sorted(catalog.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        title = data.get("title") or data.get("tale_title") or ""
        if not title or "разовое" in title.lower():
            continue
        lessons.append(
            {
                "slug": path.stem,
                "title": title,
                "week": int(data.get("module_week") or 0),
            }
        )
    return lessons


def score_match(lesson: dict, file_week: int) -> int:
    week = lesson["week"]
    week_in_stage = week if week <= 4 else week - 4
    score = 0
    if week == file_week:
        score += 10
    if week_in_stage == file_week:
        score += 5
    return score


def map_uploads(lessons: list[dict]) -> tuple[list[dict], list[tuple]]:
    results: list[dict] = []
    unmatched: list[tuple] = []

    for path in sorted(COVER_STATIC_DIR.iterdir()):
        if not path.is_file() or path.name.startswith("urok-"):
            continue
        match = UPLOAD_RE.match(path.name)
        if not match:
            unmatched.append(("bad_name", path.name))
            continue

        file_week = int(match.group(1))
        hint = HINT_OVERRIDES.get(match.group(2).strip(), match.group(2).strip())
        candidates = [l for l in lessons if _title_matches(hint, l["title"])]
        if not candidates:
            unmatched.append(("no_lesson", path.name, hint))
            continue

        candidates.sort(key=lambda l: score_match(l, file_week), reverse=True)
        best = candidates[0]
        module_week = best["week"]
        static_name = f"{_slugify_hint(module_week, hint)}{path.suffix.lower()}"
        source_name = f"Урок {module_week} {hint}{path.suffix.lower()}"

        results.append(
            {
                "orig": path.name,
                "renamed": static_name,
                "source_name": source_name,
                "hint": hint,
                "file_week": file_week,
                "module_week": module_week,
                "slug": best["slug"],
                "title": best["title"],
                "match_count": len(candidates),
            }
        )

    return results, unmatched


def apply_sync(results: list[dict], dry_run: bool = False) -> None:
    COVER_SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    COVER_STATIC_DIR.mkdir(parents=True, exist_ok=True)

    for item in results:
        src = COVER_STATIC_DIR / item["orig"]
        source_dest = COVER_SOURCE_DIR / item["source_name"]
        static_dest = COVER_STATIC_DIR / item["renamed"]

        if dry_run:
            continue

        shutil.copy2(src, source_dest)
        shutil.copy2(src, static_dest)
        if src.name != item["renamed"]:
            src.unlink(missing_ok=True)


def unique_tales(lessons: list[dict]) -> list[dict]:
    seen: set[tuple[int, str]] = set()
    unique: list[dict] = []
    for lesson in lessons:
        key = (lesson["week"], lesson["title"].casefold())
        if key in seen:
            continue
        seen.add(key)
        unique.append(lesson)
    return unique


def missing_covers(lessons: list[dict]) -> list[dict]:
    _load_registry.cache_clear()
    missing = []
    for lesson in unique_tales(lessons):
        url = cover_url_for_lesson(lesson["week"], lesson["title"])
        if not url:
            missing.append(lesson)
    return missing


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    lessons = load_lessons()
    results, unmatched = map_uploads(lessons)

    if not dry_run:
        apply_sync(results)

    _load_registry.cache_clear()
    missing = missing_covers(lessons)

    report = {
        "mapped": results,
        "unmatched": unmatched,
        "missing_after": [
            {"week": m["week"], "title": m["title"], "example_slug": m["slug"]}
            for m in missing
        ],
    }
    out = ROOT / "data" / "_cover_mapping.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Mapped: {len(results)}, unmatched uploads: {len(unmatched)}")
    print(f"Lessons still missing covers: {len(missing)}")
    for item in results:
        print(
            f"{item['orig']} -> {item['renamed']} | week {item['module_week']} | {item['slug']}"
        )
    for row in unmatched:
        print("UNMATCHED", row)
    for row in missing:
        print(f"MISSING week {row['week']}: {row['title']} ({row['slug']})")


if __name__ == "__main__":
    main()
