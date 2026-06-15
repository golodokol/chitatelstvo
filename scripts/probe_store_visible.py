#!/usr/bin/env python3
import re
import urllib.request

req = urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")

print("assets", re.findall(r"chit-zero\.(js|css)\?v=([^\"']+)", html))
for label in ["Разовое", "Индивидуальное", "SKU0001", "Оплатить", "t-store", "data-record-type"]:
    print(label, html.count(label) if label.startswith(("data", "t-")) else (label in html))

# find rec blocks
blocks = re.findall(r'id="(rec\d+)"[^>]*data-record-type="(\d+)"', html)
print("blocks", len(blocks), blocks[:15])

for m in re.finditer(r"SKU0001", html):
    print("\n=== SKU0001 context ===")
    print(html[max(0, m.start() - 300) : m.start() + 500])
    break

for m in re.finditer(r"Оплатить", html):
    print("\n=== Оплатить context ===")
    print(html[max(0, m.start() - 200) : m.start() + 200])
    break
