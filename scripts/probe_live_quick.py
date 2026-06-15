#!/usr/bin/env python3
import re
import urllib.request

req = urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "chit/1"})
html = urllib.request.urlopen(req).read().decode("utf-8", errors="replace")

for m in re.findall(r"chit-zero\.(css|js)\?v=([^\"']+)", html):
    print("asset", m)

for rid in ["rec2380183631", "rec2380172391", "rec2380172421"]:
    i = html.find('id="' + rid + '"')
    if i < 0:
        print(rid, "NOT FOUND")
        continue
    chunk = html[i : i + 12000]
    print(
        rid,
        "Studio=" + str("Studio Headphones" in chunk),
        "preview=" + str("previewmode" in chunk),
        "genuid=" + str("data-product-gen-uid" in chunk),
    )
