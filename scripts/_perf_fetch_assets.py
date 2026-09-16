# -*- coding: utf-8 -*-
"""Download heavy homepage assets, measure sizes, check for webp."""
import urllib.request
from pathlib import Path

ASSETS = [
    "cta-fairy-tale-bg.png",
    "cta-fairy-tale-bg.webp",
    "audience-kids.png",
    "audience-kids.webp",
    "audience-parents.png",
    "audience-parents.webp",
    "hero-book-single.png",
    "hero-book-single.webp",
    "chit-zero.css",
]
OUT = Path("docs/tilda-zero-main/_perf-opt")
OUT.mkdir(parents=True, exist_ok=True)
base = "https://api.chitatelstvo.ru/assets/"

for name in ASSETS:
    url = base + name + "?nocache=perf1"
    dest = OUT / name
    try:
        data = urllib.request.urlopen(url, timeout=60).read()
        dest.write_bytes(data)
        print(f"OK {name:30} {len(data)/1024:8.1f} KiB")
    except Exception as e:
        print(f"MISS {name:30} {e}")
