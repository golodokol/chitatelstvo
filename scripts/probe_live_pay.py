#!/usr/bin/env python3
"""Probe live homepage for cart/catalog/payment state."""
import re
import urllib.request

req = urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "chit-probe/1"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")

print("=== asset versions ===")
for m in re.findall(r"chit-zero\.(css|js)\?v=([^\"']+)", html):
    print(m)

print("\n=== ST100 ===")
print("ST100 present:", "rec2379461281" in html)
print("tinkoff:", "tinkoff" in html.lower())

print("\n=== catalog blocks ===")
for rt in ("762", "205"):
    print(f"type {rt}:", html.count(f'data-record-type="{rt}"'))

print("\n=== product names in HTML ===")
for pat in [
    r"Читательство[^<\"]{0,40}",
    r"Studio Headphones",
    r"previewmode:'yes'",
    r"previewmode:'no'",
    r"data-product-gen-uid=\"(\d+)\"",
]:
    found = re.findall(pat, html)
    if found:
        print(pat[:35], "->", list(dict.fromkeys(found))[:8])

print("\n=== storepartuid ===")
for pat in [r"storepartuid[=:\"']([a-f0-9]+)", r'data-store-part-uid="([^"]+)"']:
    f = set(re.findall(pat, html, re.I))
    if f:
        print(pat, f)
