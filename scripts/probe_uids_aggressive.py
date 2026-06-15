#!/usr/bin/env python3
"""Try getproductsbyuid and getpriceproducts with SKU/external id."""
import json
import urllib.parse
import urllib.request

PROJECT = "14447246"
ST100 = "2379461281"
C = PROJECT
UA = {"User-Agent": "chit-uid-probe/1", "Referer": "https://chitatelstvo.ru/"}

PRODUCTS = [
    ("single", "SKU0001-2", "Читательство · Разовое", 1490),
    ("self_paced", "SKU0002", "Читательство · Индивидуальное", 1990),
    ("with_teacher", "SKU0003", "Читательство · С преподавателем", 4990),
]


def post(url, data):
    if isinstance(data, dict):
        body = urllib.parse.urlencode(data).encode()
    else:
        body = data
    req = urllib.request.Request(url, data=body, headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


def post_json(url, obj):
    body = json.dumps(obj).encode()
    req = urllib.request.Request(url, data=body, headers={**UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


# getpriceproducts with cart-like payload
cart = {
    "prodamount": 4990,
    "discount": 0,
    "products": [
        {"name": t, "price": p, "amount": p, "quantity": 1, "recid": ST100, "sku": s}
        for _, s, t, p in PRODUCTS
    ],
    "amount": 4990,
    "total": 4990,
    "updated": 1718380800,
}
for url in [
    "https://store.tildaapi.com/api/getpriceproducts",
    "https://store.tildacdn.com/api/getpriceproducts",
]:
    print("=== POST", url)
    try:
        raw = post(url, {"c": C, "recid": ST100, "data": json.dumps(cart)})
        print(raw[:2000])
    except Exception as exc:
        print("form ERR", exc)
    try:
        raw = post_json(url + f"?c={C}", cart)
        print(raw[:2000])
    except Exception as exc:
        print("json ERR", exc)

# try getproductsbyuid with sku as uid (long shot)
for key, sku, title, price in PRODUCTS:
    payload = {"productsuid": sku, "c": C}
    print("\n--- getproductsbyuid sku", sku)
    try:
        print(post("https://store.tildaapi.com/api/getproductsbyuid", payload)[:500])
    except Exception as exc:
        print("ERR", exc)

# YML/feed common paths
for url in [
    f"https://store.tilda.cc/connectors/commerceml/?projectid={PROJECT}",
    f"https://{PROJECT}.tilda.ws/store/yml.xml",
    f"https://chitatelstvo.ru/store/yml.xml",
    f"https://chitatelstvo.ru/yml.xml",
    f"https://store.tildaapi.com/api/getproductslist/?projectid={PROJECT}&size=100&storepartuid=1",
]:
    print("\n---", url)
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()[:1500].decode("utf-8", errors="replace")
            if any(x in data for x in ("1490", "4990", "SKU000", "uid", "Разовое")):
                print("MATCH:", data)
            else:
                print(data[:300])
    except Exception as exc:
        print("ERR", exc)
