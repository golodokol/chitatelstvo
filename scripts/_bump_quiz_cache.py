# -*- coding: utf-8 -*-
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
files = [
    ROOT / "docs/tilda-zero-main/glavnaya.html",
    ROOT / "docs/tilda-zero-main/00-tilda-zero-upload.html",
    ROOT / "docs/tilda-zero-main/00-tilda-lite.html",
    ROOT / "docs/tilda-zero-main/_preview-layout.html",
    ROOT / "docs/tilda-zero-main/00-tilda-lite-tildacdn.html",
]
NEW = "20260916a"
for p in files:
    if not p.exists():
        print("missing", p)
        continue
    t = p.read_text(encoding="utf-8")
    o = t
    t = re.sub(r"chit-zero\.js\?v=[^\"'&]+", f"chit-zero.js?v={NEW}", t)
    t = re.sub(r'(V=")[^"]+(")', rf"\g<1>{NEW}\2", t)
    t = re.sub(r"(V=')[^']+(')", rf"\g<1>{NEW}\2", t)
    if t != o:
        p.write_text(t, encoding="utf-8")
        print("bumped", p.name)
    else:
        print(
            "ok",
            p.name,
            "zero",
            f"chit-zero.js?v={NEW}" in t,
            "V",
            NEW in t,
        )
