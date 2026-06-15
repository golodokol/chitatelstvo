#!/usr/bin/env python3
import re, urllib.request
html = urllib.request.urlopen(urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent":"x"}), timeout=30).read().decode("utf-8","replace")
for term in ["t_store_oneProduct", "previewmode", "797131986522", "storepart", "partuid", "t762__init"]:
    idx = 0
    n = 0
    while n < 3:
        idx = html.find(term, idx)
        if idx < 0: break
        print(f"\n--- {term} @ {idx} ---")
        print(html[idx:idx+400].replace("\n"," "))
        idx += len(term)
        n += 1
