#!/usr/bin/env python3
"""Shift course dates: stage-1 start 29 Jun→6 Jul, stage-2 start 20 Jul→27 Jul."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Order: longer / more specific strings first where it matters.
REPLACES = [
    ("Старт курса 29 июня", "Старт курса 6 июля"),
    ("Старт 20 июля", "Старт 27 июля"),
    ("этап 29 июня", "этап 6 июля"),
    ("этап 20 июля", "этап 27 июля"),
    ("29 июня = 1", "6 июля = 1"),
    ("20 июля = 2", "27 июля = 2"),
    ("29 июня или 20 июля", "6 июля или 27 июля"),
    ("29 июня и 20 июля", "6 июля и 27 июля"),
    ("29 июня или", "6 июля или"),
    ("с 20 июля", "с 27 июля"),
    ("22 июня или 20 июля", "6 июля или 27 июля"),
    ("старт 22 июня или 20 июля", "старт 6 июля или 27 июля"),
    ("29 июня", "6 июля"),
    ("20 июля", "27 июля"),
    ("2026-06-29", "2026-07-06"),
    ("2 июля 2026", "9 июля 2026"),
    ("lessons: ['29 июня', '6 июля', '13 июля', '20 июля']", "lessons: ['6 июля', '13 июля', '20 июля', '27 июля']"),
    ("meetings: ['2 июля', '9 июля', '16 июля', '23 июля']", "meetings: ['9 июля', '16 июля', '23 июля', '30 июля']"),
    ("lessons: ['20 июля', '27 июля', '3 августа', '10 августа']", "lessons: ['27 июля', '3 августа', '10 августа', '17 августа']"),
    ("meetings: ['23 июля', '30 июля', '6 августа', '13 августа']", "meetings: ['30 июля', '6 августа', '13 августа', '20 августа']"),
]

FILES = [
    ROOT / "docs/tilda-zero-main/00-tilda-lite.html",
    ROOT / "docs/tilda-zero-main/01-html.txt",
    ROOT / "docs/tilda-zero-main/03-js.txt",
    ROOT / "docs/tilda-zero-main/ST100_SETUP.md",
    ROOT / "docs/zapis_preview.html",
    ROOT / "docs/tilda_zero_zapis.html",
    ROOT / "docs/TILDA_ZAPIS_PROGRAMS.md",
    ROOT / "docs/TILDA_PAGE_UNIFIED.md",
    ROOT / "templates/legal/oferta.html",
    ROOT / "docs/tilda-zero-main/00-all-in-one.html",
    ROOT / "docs/tilda-zero-main/chit-zero.src.js",
    ROOT / "docs/tilda-zero-main/chit-zero.js",
]

for path in FILES:
    if not path.exists():
        print("skip", path)
        continue
    text = path.read_text(encoding="utf-8")
    orig = text
    for old, new in REPLACES:
        text = text.replace(old, new)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        print("updated", path.relative_to(ROOT))
    else:
        print("unchanged", path.relative_to(ROOT))
