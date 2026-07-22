"""Audit lesson cover coverage."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lessons.covers import _load_registry, cover_url_for_lesson

catalog = ROOT / "lessons" / "catalog"
seen: set[tuple[int, str]] = set()
missing: list[dict] = []
ok: list[dict] = []

for path in sorted(catalog.glob("*.json")):
    data = json.loads(path.read_text(encoding="utf-8"))
    title = data.get("title") or data.get("tale_title") or ""
    if not title or "разовое" in title.lower():
        continue
    week = int(data.get("module_week") or 0)
    key = (week, title.casefold())
    if key in seen:
        continue
    seen.add(key)
    url = cover_url_for_lesson(week, title)
    row = {"week": week, "title": title, "slug": path.stem, "url": url}
    (ok if url else missing).append(row)

print(f"registry entries: {len(_load_registry())}")
print(f"unique tales with cover: {len(ok)}")
print(f"unique tales missing cover: {len(missing)}")
print("---MISSING---")
for row in missing:
    print(f"W{row['week']}: {row['title']} ({row['slug']})")

out = ROOT / "data" / "_covers_status.json"
out.write_text(
    json.dumps({"ok": ok, "missing": missing}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
