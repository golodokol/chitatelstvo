#!/usr/bin/env python3
"""Inspect live chitatelstvo.ru homepage for store/ST100 markers."""
import re
import urllib.request

URL = "https://chitatelstvo.ru/"

req = urllib.request.Request(URL, headers={"User-Agent": "chitatelstvo-probe/1.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    html = resp.read().decode("utf-8", errors="replace")

print("=== chit-zero asset ===")
print(re.findall(r"chit-zero\.(js|css)\?v=[^\"']+", html))

print("\n=== ST100 rec2379461281 present ===")
print("rec2379461281" in html)

for pat in [
    r"storepartuid[=:\"']([a-f0-9]+)",
    r'data-store-part-uid="([a-f0-9]+)"',
    r"data-payment-system=\"([^\"]+)\"",
    r"data-formactiontype=\"([^\"]+)\"",
    r"t706__cartdata[^>]*>([^<]*)",
]:
    m = re.search(pat, html, re.I)
    print(f"{pat[:40]}... -> {m.group(1) if m else 'NOT FOUND'}")

print("\n=== ST100 block excerpt ===")
idx = html.find("rec2379461281")
if idx >= 0:
    print(html[idx : idx + 4000])
else:
    print("block not found")

print("\n=== Product title search ===")
for title in [
    "Читательство · Разовое",
    "Читательство · Индивидуальное",
    "Читательство · С преподавателем",
    "SKU0001",
    "1490",
]:
    print(f"  {title!r}: {title in html}")
