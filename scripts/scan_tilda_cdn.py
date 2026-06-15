#!/usr/bin/env python3
"""Scan Tilda CDN/static endpoints for store product UIDs."""
import json
import re
import urllib.request

PROJECT = "14447246"
PAGE = "133375856"
ST100 = "2379461281"
UA = {"User-Agent": "chit-cdn-scan/1"}

URLS = [
    f"https://static.tildacdn.com/ws/project{PROJECT}/",
    f"https://static.tildacdn.com/ws/page{PAGE}/",
    f"https://neo.tildacdn.com/js/tilda-store-{PROJECT}.min.js",
    f"https://neo.tildacdn.com/js/tilda-catalog-{PROJECT}.min.js",
    f"https://forms.tildacdn.com/projs/{PROJECT}/pages/{PAGE}/",
    f"https://store.tildaapi.com/api/getproductslist/?recid={ST100}&c={PROJECT}&size=100&getparts=true&slice=1",
]

for url in URLS:
    print("\n===", url)
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read().decode("utf-8", errors="replace")
        if any(x in data for x in ("1490", "4990", "SKU000", "Разовое", "productuid", "storepartuid")):
            print("INTERESTING:", data[:4000])
        else:
            print(data[:400])
        uids = set(re.findall(r"\d{12}", data))
        if uids:
            print("12-digit nums:", list(uids)[:20])
    except Exception as exc:
        print("ERR", exc)

# fetch page html and all script srcs
html = urllib.request.urlopen(
    urllib.request.Request("https://chitatelstvo.ru/", headers=UA), timeout=30
).read().decode("utf-8", errors="replace")
scripts = re.findall(r'src="(https://[^"]+)"', html)
for s in scripts:
    if any(k in s for k in ("store", "catalog", "cart", "706", "205", "tilda")):
        print("\nscript:", s)
        try:
            body = urllib.request.urlopen(urllib.request.Request(s, headers=UA), timeout=15).read().decode("utf-8", errors="replace")
            if "1490" in body or "productuid" in body.lower() or "storepartuid" in body.lower():
                print(body[:3000])
        except Exception as exc:
            print("  ERR", exc)

recs = re.findall(r'id="rec(\d+)"[^>]*data-record-type="(\d+)"', html)
print("\nrecord blocks:", recs)
