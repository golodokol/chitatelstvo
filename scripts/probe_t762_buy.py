#!/usr/bin/env python3
import re, urllib.request
html = urllib.request.urlopen(urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent":"x"}), timeout=30).read().decode("utf-8","replace")
idx = html.find("rec2380172341")
chunk = html[idx:idx+35000]
for pat in ["t762__btn", "addtocart", "order", "buy", "cart", "js-store", "t-store", "onclick", "data-product"]:
    matches = [(m.start(), chunk[max(0,m.start()-30):m.start()+80]) for m in re.finditer(pat, chunk, re.I)]
    if matches:
        print(f"\n=== {pat} ({len(matches)}) ===")
        for _, snip in matches[:4]:
            print(" ", snip.replace("\n", " ")[:120])
