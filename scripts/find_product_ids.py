#!/usr/bin/env python3
"""Find Tilda catalog Product IDs for chitatelstvo."""
import json
import re
import urllib.parse
import urllib.request

PROJECT = "14447246"
PAGE = "133375856"
ST100 = "2379461281"
DOMAIN = "chitatelstvo.ru"
SKUS = ["SKU0001-2", "SKU0002", "SKU0003"]
TITLES = [
    "Читательство · Разовое",
    "Читательство · Индивидуальное",
    "Читательство · С преподавателем",
]

UA = {"User-Agent": "chit-product-id/1"}


def get(url, headers=None):
    h = dict(UA)
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def try_json(url):
    try:
        return json.loads(get(url))
    except Exception as e:
        return {"error": str(e), "url": url}


html = get(f"https://{DOMAIN}/")
formskey = re.search(r'data-tilda-formskey="([^"]+)"', html)
project = re.search(r'data-tilda-project-id="([^"]+)"', html)
print("formskey:", formskey.group(1) if formskey else "?")
print("project:", project.group(1) if project else "?")

# scan HTML for numeric product uids near titles/prices
print("\n=== UIDs in HTML ===")
for m in re.finditer(r'"uid"\s*:\s*"?(\d{8,})"?', html):
    print(" uid:", m.group(1))
for m in re.finditer(r'productuid[=:"\'](\d+)', html, re.I):
    print(" productuid:", m.group(1))

# try store API variants
candidates = [
    f"https://store.tildaapi.com/api/getproductslist/?projectid={PROJECT}&size=100&slice=1&c={PROJECT}",
    f"https://store.tildaapi.com/api/getproductslist/?projectid={PROJECT}&size=100",
    f"https://store.tildaapi.com/api/getproductslist/?projectid={PROJECT}&size=100&getparts=true&c={PROJECT}",
    f"https://store.tildaapi.com/api/getproductslist/?projectid={PROJECT}&size=100&getparts=true",
    f"https://store.tildaapi.com/api/getproductslist/?pageid={PAGE}&c={PROJECT}&size=100&getparts=true",
    f"https://store.tildaapi.com/api/getproductslist/?pageid={PAGE}&size=100&getparts=true",
    f"https://store.tildaapi.com/api/getproductslist/?recid={ST100}&c={PROJECT}&size=100&getparts=true",
    f"https://store.tildaapi.com/api/getproducts/?projectid={PROJECT}&size=100",
    f"https://store.tildaapi.com/api/getproducts/?projectid={PROJECT}",
    f"https://forms.tildacdn.com/projs/{PROJECT}/store/products.json",
    f"https://store.tildaapi.com/api/getstore/?projectid={PROJECT}&domain={DOMAIN}",
    f"https://store.tildaapi.com/api/getstore/?projectid={PROJECT}&domain=www.{DOMAIN}",
]

for url in candidates:
    print("\n---", url)
    data = try_json(url)
    if isinstance(data, dict) and data.get("error"):
        print(data["error"][:200])
        continue
    text = json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data
    if any(t in text for t in ("Разовое", "1490", "SKU0001")):
        print("MATCH:", text[:3000])
    elif isinstance(data, dict) and data.get("products"):
        for p in data["products"][:10]:
            print(" ", p.get("title"), p.get("price"), "uid=", p.get("uid", p.get("productuid")))
    else:
        print(text[:400])

# try by SKU / external id
for sku in SKUS:
    for base in [
        f"https://store.tildaapi.com/api/getproducts/?projectid={PROJECT}&sku={urllib.parse.quote(sku)}",
        f"https://store.tildaapi.com/api/getproducts/?projectid={PROJECT}&externalid={urllib.parse.quote(sku)}",
    ]:
        print("\n--- SKU probe", sku, base)
        print(get(base)[:500])

# tilda cc store export
for url in [
    f"https://tilda.cc/projects/getstore/?projectid={PROJECT}",
    f"https://tilda.ws/projects/getstore/?projectid={PROJECT}",
]:
    print("\n---", url)
    try:
        print(get(url)[:300])
    except Exception as e:
        print("ERR", e)
