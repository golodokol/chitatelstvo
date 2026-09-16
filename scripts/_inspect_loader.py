# -*- coding: utf-8 -*-
from pathlib import Path
import re

p = Path("docs/tilda-zero-main/glavnaya.html")
t = p.read_text(encoding="utf-8")
i = t.find("chit-quiz-loader")
chunk = t[i : i + 3500]
# find openTrial-like
for m in re.finditer(r".{0,40}last.{0,80}", chunk):
    s = m.group(0)
    if "Date" in s or "now" in s:
        print(repr(s))
print("---")
j = chunk.find("openTrial")
print("openTrial idx", j)
print(repr(chunk[j : j + 300] if j >= 0 else chunk[chunk.find("last=") : chunk.find("last=") + 400]))
