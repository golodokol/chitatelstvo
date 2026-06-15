#!/usr/bin/env python3
import json
import re
import urllib.request

html = urllib.request.urlopen(
    urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "check/3"}),
    timeout=30,
).read().decode("utf-8", "replace")

# all product-like JSON fragments
for m in re.finditer(r'"title"\s*:\s*"([^"]{3,80})"', html):
    t = m.group(1)
    if "итат" in t or "азов" in t or "ндив" in t or "1490" in t or "1990" in t or "4990" in t:
        print("title:", t)

for m in re.finditer(r'"price"\s*:\s*"?(\\d+(?:\\.\\d+)?)"?', html):
    print("price:", m.group(1))

# tcart products in inline scripts
for m in re.finditer(r"products\s*[:=]\s*(\[[\s\S]{0,5000}?\])", html):
    chunk = m.group(1)[:500]
    print("products chunk:", chunk[:300])

# storepart in any form
for pat in [r"storepartuid[^a-f0-9]{0,5}([a-f0-9]{8,})", r"partuid[^0-9]{0,5}(\\d{8,})", r"productuid[^0-9]{0,5}(\\d{8,})"]:
    found = re.findall(pat, html, re.I)
    if found:
        print(pat, found[:5])

# search wrong-name variants
variants = [
    "Читательство · Разовое",
    "Читательство - Разовое",
    "Читательство – Разовое",
    "Читательство • Разовое",
    "Разовое",
]
print("\nname variants in HTML:")
for v in variants:
    print(f"  {repr(v)}: {v in html}")
