#!/usr/bin/env python3
import urllib.request
req = urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "x"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")
idx = html.find("Studio Headphones")
print("index", idx)
if idx >= 0:
    print(html[max(0, idx - 500) : idx + 500])
