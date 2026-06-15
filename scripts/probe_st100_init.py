#!/usr/bin/env python3
"""Extract ST100 init and cart config from live homepage."""
import re
import urllib.request

req = urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "chit/1"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="replace")

i = html.find("rec2379461281")
if i >= 0:
    chunk = html[i : i + 25000]
    for pat in [
        r"tcart__init\([^)]+\)",
        r"storepartuid[^;]{0,80}",
        r"t706[^\"]{0,40}",
        r"formservices",
    ]:
        for m in re.finditer(pat, chunk):
            print(m.group(0)[:200])
            print("---")

print("\nStudio Headphones count:", html.count("Studio Headphones"))
