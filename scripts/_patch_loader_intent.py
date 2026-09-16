# -*- coding: utf-8 -*-
from pathlib import Path
import re

DIR = Path(__file__).resolve().parents[1] / "docs" / "tilda-zero-main"
OLD = "var now=Date.now();if(now-last<=449)return;last=now;"
NEW = 'var now=Date.now();if(now-last<=449)return;last=now;try{window.__chitQuizUserIntent=now;}catch(err){}'

for name in (
    "glavnaya.html",
    "00-tilda-zero-upload.html",
    "00-tilda-lite.html",
    "_preview-layout.html",
):
    p = DIR / name
    t = p.read_text(encoding="utf-8")
    if "__chitQuizUserIntent" in t:
        print("already", name)
        continue
    if OLD in t:
        p.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
        print("patched", name)
    else:
        # find nearby
        i = t.find("now-last<450")
        print("missing pattern", name, "idx", i, repr(t[i - 40 : i + 80] if i >= 0 else ""))
