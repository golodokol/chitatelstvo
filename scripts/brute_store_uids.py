#!/usr/bin/env python3
"""Bruteforce Tilda store endpoints for chitatelstvo catalog UIDs."""
import json
import re
import urllib.request

PROJECT = "14447246"
ST100 = "2379461281"
C = PROJECT
UA = {"User-Agent": "chit-brute/1", "Referer": "https://chitatelstvo.ru/"}

# stor path from favicon on site
STOR = "3463-6531-4233-a632-616134353338"

candidates = [
    f"https://static.tildacdn.com/stor{STOR}/products.json",
    f"https://static.tildacdn.com/stor{STOR}/store.json",
    f"https://static.tildacdn.com/stor{STOR}/catalog.json",
    f"https://store.tildacdn.com/stor{STOR}/products.json",
    f"https://forms.tildacdn.com/projs/{PROJECT}/store.json",
    f"https://forms.tildacdn.com/projs/{PROJECT}/products.json",
    f"https://store.tildaapi.com/api/getstore/?projectid={PROJECT}&c={C}",
    f"https://store.tildaapi.com/api/getstore/?projectid={PROJECT}&domain=chitatelstvo.ru&c={C}",
    f"https://store.tildaapi.com/api/getpartstore/?projectid={PROJECT}&c={C}",
    f"https://store.tildaapi.com/api/getstoreparts/?projectid={PROJECT}&c={C}",
    f"https://store.tildaapi.com/api/getproductslist/?recid={ST100}&c={C}&size=100&getparts=true&flag_root=withroot&storepartuid={PROJECT}",
    f"https://store.tildaapi.com/api/getproductslist/?recid={ST100}&c={C}&size=100&getparts=true&flag_root=withroot&storepartuid={STOR.replace('-','')}",
]

for url in candidates:
    print("\n===", url)
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode("utf-8", errors="replace")
        if raw.startswith("{"):
            data = json.loads(raw)
            text = json.dumps(data, ensure_ascii=False)
            if any(x in text for x in ("1490", "4990", "SKU000", "Разовое", "uid")):
                print("MATCH:", text[:5000])
            else:
                print(text[:300])
        else:
            print(raw[:300])
    except Exception as exc:
        print("ERR", exc)

# brute numeric storepartuid near project id
for sid in [PROJECT, ST100, "2378409351", "133375856", STOR.replace("-", "")[:12]]:
    url = f"https://store.tildaapi.com/api/getproductslist/?recid={ST100}&c={C}&size=100&storepartuid={sid}"
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=10).read().decode("utf-8", errors="replace")
        if raw.startswith("{") and "products" in raw:
            print("\n*** HIT", sid, raw[:3000])
    except Exception:
        pass
