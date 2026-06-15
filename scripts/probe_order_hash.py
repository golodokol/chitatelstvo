#!/usr/bin/env python3
"""Probe Tilda cart APIs and order-hash resolution."""
import json
import re
import urllib.parse
import urllib.request

PROJECT = "14447246"
ST100 = "2379461281"
C = PROJECT
UA = {"User-Agent": "chit-probe/1", "Referer": "https://chitatelstvo.ru/"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


def post_json(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


# Download cart JS snippet around order parsing
js = get("https://static.tildacdn.com/js/tilda-cart-1.1.min.js")
idx = js.find("#order:")
print("=== order hash parser context ===")
print(js[idx : idx + 2500])

# Try getpriceproducts with SKUs / titles
skus = ["SKU0001-2", "SKU0002", "SKU0003"]
titles = [
    "Читательство · Разовое",
    "Читательство · Индивидуальное",
    "Читательство · С преподавателем",
]
for sku in skus:
    for field in ["sku", "externalid", "productsuid"]:
        url = "https://store.tildaapi.com/api/getpriceproducts"
        try:
            raw = post_json(url, {field: sku, "c": C, "recid": ST100})
            if "error" not in raw.lower()[:50] and len(raw) > 20:
                print(f"\ngetpriceproducts {field}={sku}:", raw[:500])
        except Exception as exc:
            print(f"getpriceproducts {field}={sku}: ERR {exc}")

# Brute common storepartuid patterns from project id
candidates = [
    PROJECT,
    ST100,
    "2378409351",
    "133375856",
]
# also try stor path from static CDN
html = get("https://chitatelstvo.ru/")
for m in re.findall(r"stor\d+-\d+-\d+-\d+-\d+", html):
    candidates.append(m.replace("stor", "").replace("-", "")[:12])

seen = set()
for sid in candidates:
    if sid in seen:
        continue
    seen.add(sid)
    url = f"https://store.tildaapi.com/api/getproductslist/?recid={ST100}&c={C}&size=100&storepartuid={sid}"
    try:
        raw = get(url)
        if raw.startswith("{"):
            data = json.loads(raw)
            if data.get("products"):
                print(f"\n*** FOUND storepartuid={sid} ***")
                for p in data["products"]:
                    print(p.get("title"), p.get("price"), "uid=", p.get("uid"), "sku=", p.get("sku"), "ext=", p.get("externalid"))
    except Exception:
        pass
