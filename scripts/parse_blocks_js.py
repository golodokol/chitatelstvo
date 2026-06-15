#!/usr/bin/env python3
import re
import urllib.request

url = "https://static.tildacdn.com/ws/project14447246/tilda-blocks-page133375856.min.js?t=1781470497"
t = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "x"}), timeout=30).read().decode("utf-8", "replace")
print("len", len(t))
for pat in ["1490", "1990", "4990", "SKU000", "storepartuid", "productuid", "Разовое", "Индивидуальное", "преподавателем", "797131986522", "956231952022"]:
    if pat in t:
        idx = t.find(pat)
        print(f"\n=== {pat} @ {idx} ===")
        print(t[max(0, idx - 80) : idx + 120])

# all 12-digit numbers near prices
for m in re.finditer(r"\d{12}", t):
    num = m.group(0)
    ctx = t[m.start() - 30 : m.end() + 30]
    if any(x in ctx for x in ("149", "199", "499", "SKU", "store", "prod")):
        print("12dig", num, ctx[:80])
