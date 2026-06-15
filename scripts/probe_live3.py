#!/usr/bin/env python3
import re
import urllib.request

req = urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "x"})
html = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", errors="replace")

print("=== block types ===")
for rec, typ in re.findall(r'id="(rec\d+)"[^>]*data-record-type="(\d+)"', html):
    print(f"  rec{rec} type={typ}")

idx = html.find("Разовое")
if idx >= 0:
    print("\n=== around Разовое ===")
    print(html[max(0, idx - 400) : idx + 600])

idx = html.find("t706")
if idx >= 0:
    chunk = html[idx : idx + 20000]
    print("\n=== t706 field markers ===")
    for pat in [r'data-field-name="([^"]+)"', r'name="([^"]+)"', r'data-field-type="([^"]+)"']:
        found = list(dict.fromkeys(re.findall(pat, chunk)))[:20]
        if found:
            print(pat, found)
