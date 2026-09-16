# -*- coding: utf-8 -*-
from pathlib import Path
import re

DIR = Path("docs/tilda-zero-main")
NEW = "20260916p"

for name in ("glavnaya.html", "00-tilda-zero-upload.html", "00-tilda-lite.html", "_preview-layout.html"):
    p = DIR / name
    t = p.read_text(encoding="utf-8")
    # fix duplicated media/onload on Nunito
    t = re.sub(
        r'(family=Nunito:wght@400;600;700;800&amp;display=swap" rel="stylesheet")(?: media="print" onload="this\.media=\'all\'")+(/?)',
        r'\1 media="print" onload="this.media=\'all\'"\2',
        t,
    )
    # fix broken book img tags
    t = re.sub(
        r'<img class="book__cover" src="https://api\.chitatelstvo\.ru/assets/hero-book-single\.webp"[^>]*>',
        '<img class="book__cover" src="https://api.chitatelstvo.ru/assets/hero-book-single.webp" alt="" width="108" height="156" decoding="async" fetchpriority="high" onerror="this.remove()" />',
        t,
    )
    # bump css versions
    t = re.sub(r"chit-zero\.css\?v=[^\"'&\s]+", f"chit-zero.css?v={NEW}", t)
    t = re.sub(r"chit-zero\.js\?v=[^\"'&\s]+", f"chit-zero.js?v={NEW}", t)
    t = re.sub(r'(V=")[^"]+(")', rf"\g<1>{NEW}\2", t)
    p.write_text(t, encoding="utf-8")
    print("fixed", name)
    # sanity
    assert 'media="print" onload="this.media=\'all\'" media="print"' not in t
    assert 'onerror="this.remove()" / decoding' not in t
    print("  css v", NEW in t)
