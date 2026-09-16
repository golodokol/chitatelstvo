# -*- coding: utf-8 -*-
"""Point homepage HTML at WebP assets + meadow pattern WebP."""
from __future__ import annotations

import re
from pathlib import Path

DIR = Path("docs/tilda-zero-main")
FILES = [
    "glavnaya.html",
    "00-tilda-zero-upload.html",
    "00-tilda-lite.html",
    "_preview-layout.html",
]

REPLACEMENTS = [
    (
        "https://api.chitatelstvo.ru/assets/hero-book-single.png",
        "https://api.chitatelstvo.ru/assets/hero-book-single.webp",
    ),
    (
        "https://api.chitatelstvo.ru/assets/audience-kids.png",
        "https://api.chitatelstvo.ru/assets/audience-kids.webp",
    ),
    (
        "https://api.chitatelstvo.ru/assets/audience-parents.png",
        "https://api.chitatelstvo.ru/assets/audience-parents.webp",
    ),
    (
        "https://api.chitatelstvo.ru/assets/audience-family.png",
        "https://api.chitatelstvo.ru/assets/audience-family.webp",
    ),
    (
        "https://api.chitatelstvo.ru/assets/audience-pace.png",
        "https://api.chitatelstvo.ru/assets/audience-pace.webp",
    ),
    (
        "https://static.tildacdn.com/tild6237-3735-4437-b563-353738363938/pattern-meadow-books.png",
        "https://api.chitatelstvo.ru/assets/pattern-meadow-books.webp",
    ),
    (
        "https://api.chitatelstvo.ru/assets/pattern-meadow-books.png",
        "https://api.chitatelstvo.ru/assets/pattern-meadow-books.webp",
    ),
    (
        "https://api.chitatelstvo.ru/assets/cta-fairy-tale-bg.png",
        "https://api.chitatelstvo.ru/assets/cta-fairy-tale-bg.webp",
    ),
]


def main() -> None:
    for name in FILES:
        p = DIR / name
        t = p.read_text(encoding="utf-8")
        o = t
        for a, b in REPLACEMENTS:
            t = t.replace(a, b)
        # defer Nunito as well (keep preload-ish but non-blocking)
        t = t.replace(
            'href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&amp;display=swap" rel="stylesheet"',
            'href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&amp;display=swap" rel="stylesheet" media="print" onload="this.media=\'all\'"',
        )
        t = t.replace(
            'href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&amp;display=swap" rel="stylesheet" />',
            'href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&amp;display=swap" rel="stylesheet" media="print" onload="this.media=\'all\'" />',
        )
        # hero book: fetchpriority high, decoding async (LCP candidate)
        t = re.sub(
            r'(<img class="book__cover" src="https://api\.chitatelstvo\.ru/assets/hero-book-single\.webp"[^>]*)(>)',
            lambda m: (m.group(1) if "fetchpriority" in m.group(1) else m.group(1) + ' decoding="async" fetchpriority="high"') + m.group(2),
            t,
            count=3,
        )
        if t != o:
            p.write_text(t, encoding="utf-8")
            print("updated", name)
        else:
            print("no change", name)


if __name__ == "__main__":
    main()
