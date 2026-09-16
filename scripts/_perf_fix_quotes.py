# -*- coding: utf-8 -*-
from pathlib import Path

DIR = Path("docs/tilda-zero-main")
for name in ("glavnaya.html", "00-tilda-zero-upload.html", "00-tilda-lite.html", "_preview-layout.html"):
    p = DIR / name
    t = p.read_text(encoding="utf-8")
    t2 = t.replace(r"this.media=\'all\'", "this.media='all'")
    t2 = t2.replace(r"this.media=\\'all\\'", "this.media='all'")
    if t2 != t:
        p.write_text(t2, encoding="utf-8")
        print("fixed", name)
    i = t2.find("Nunito")
    print(name, repr(t2[i : i + 130]))
