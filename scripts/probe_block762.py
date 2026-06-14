#!/usr/bin/env python3
import re
import urllib.request

html = urllib.request.urlopen(
    urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "x"}),
    timeout=30,
).read().decode("utf-8", errors="replace")

for rec in ["2380172341", "2380172391", "2380172421", "2379461281"]:
    idx = html.find(f'rec{rec}')
    if idx < 0:
        print(f"rec{rec} NOT FOUND")
        continue
    chunk = html[idx : idx + 6000]
    print(f"\n{'='*60}\nrec{rec}\n{'='*60}")
    for pat in [
        r'data-record-type="(\d+)"',
        r'data-product-uid="([^"]+)"',
        r'data-product-lid="([^"]+)"',
        r'data-product-part-uid="([^"]+)"',
        r'data-product-gen-uid="([^"]+)"',
        r'storepartuid[=:"\']([^"\']+)',
        r'productuid[=:"\']([^"\']+)',
        r'"uid"\s*:\s*"?(\d+)"?',
        r'797131986522|206548598642|956231952022',
        r'js-product-name[^>]*>([^<]{5,80})',
        r't-store[^"\'\s]{0,40}',
    ]:
        found = re.findall(pat, chunk, re.I)
        if found:
            print(pat[:50], "->", found[:5])

# sample js-product without uid
for m in re.finditer(r'class="[^"]*js-product[^"]*"', html):
    start = max(0, m.start() - 100)
    snippet = html[start : m.start() + 300]
    if "chit-catalog-bridge" in snippet:
        continue
    if "data-product-uid" in snippet:
        print("\nPRODUCT WITH UID:", snippet[:400])
        break
else:
    m = re.search(r'class="[^"]*js-product[^"]*"', html)
    if m:
        print("\nFIRST js-product (no uid?):", html[max(0,m.start()-80):m.start()+400])
