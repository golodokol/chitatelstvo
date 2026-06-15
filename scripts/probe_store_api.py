#!/usr/bin/env python3
"""Try all known Tilda store API endpoints for chitatelstvo project."""
import json
import re
import urllib.request

PROJECT = "14447246"
PAGE = "133375856"
ST100 = "2379461281"
ZERO = "2378409351"

URLS = [
    f"https://store.tildaapi.com/api/getproductslist/?recid={ST100}&size=100&getparts=true",
    f"https://store.tildaapi.com/api/getproductslist/?recid={ST100}&size=100&getparts=true&flag_root=withroot",
    f"https://store.tildaapi.com/api/getproductslist/?pageid={PAGE}&size=100&getparts=true",
    f"https://store.tildaapi.com/api/getproductslist/?projectid={PROJECT}&size=100",
    f"https://store.tildaapi.com/api/getstoreparts/?projectid={PROJECT}",
    f"https://store.tildaapi.com/api/getstoreparts/?recid={ST100}",
    f"https://store.tildaapi.com/api/getpartstore/?projectid={PROJECT}",
    f"https://store.tildaapi.com/api/getpartstore/?recid={ST100}",
]

UA = {"User-Agent": "chit-store-probe/1"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


html = get("https://chitatelstvo.ru/")
print("=== IDs in homepage HTML ===")
for pat in [
    r"storepartuid[=:\"']([a-f0-9]+)",
    r'data-store-part-uid="([a-f0-9]+)"',
    r'"partuid"\s*:\s*(\d+)',
    r'"productuid"\s*:\s*(\d+)',
    r'"uid"\s*:\s*(\d{6,})',
    r"productuid[=:\"'](\d+)",
]:
    found = set(re.findall(pat, html, re.I))
    if found:
        print(pat[:40], found)

print("\n=== tcart / products in scripts ===")
for m in re.finditer(r"productuid[^0-9]{0,3}(\d{8,})", html):
    print(" productuid", m.group(1))
for m in re.finditer(r"storepartuid[^a-f0-9]{0,3}([a-f0-9]{8,})", html, re.I):
    print(" storepartuid", m.group(1))

print("\n=== API probes ===")
partuids = set()
for url in URLS:
    print("\n---", url)
    try:
        raw = get(url)
        print(raw[:1500])
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                for k in ("parts", "storeparts", "products", "partlist"):
                    if k in data:
                        print("KEY", k, "len", len(data[k]) if isinstance(data[k], list) else data[k])
                for p in data.get("parts") or data.get("storeparts") or []:
                    uid = p.get("uid") or p.get("partuid")
                    if uid:
                        partuids.add(str(uid))
        except json.JSONDecodeError:
            pass
    except Exception as e:
        print("ERR", e)

if partuids:
    print("\n=== Try partuids ===")
    for sid in partuids:
        url = f"https://store.tildaapi.com/api/getproductslist/?recid={ST100}&storepartuid={sid}&size=100"
        print("\n", url)
        try:
            print(get(url)[:2000])
        except Exception as e:
            print("ERR", e)
