#!/usr/bin/env python3
import re, urllib.request
html = urllib.request.urlopen(urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent":"x"}), timeout=30).read().decode("utf-8","replace")
for m in re.finditer(r"t_store_oneProduct_init\([^;]{0,600}\)", html):
    s = m.group(0)
    if "797131986522" in s or "206548598642" in s or "956231952022" in s:
        print(s[:600])
        print("---")
