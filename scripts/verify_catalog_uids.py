#!/usr/bin/env python3
"""Verify Tilda getpriceproducts accepts our catalog UIDs."""
import json
import urllib.parse
import urllib.request

PROJECT = "14447246"
ST100 = "2379461281"
PRODUCTS = [
    ("single", "797131986522", "Читательство · Разовое", 1490, "SKU0001-2"),
    ("self_paced", "206548598642", "Читательство · Индивидуальное", 1990, "SKU0002"),
    ("with_teacher", "956231952022", "Читательство · С преподавателем", 4990, "SKU0003"),
]

def post_price(product):
    key, uid, title, price, sku = product
    cart = {
        "prodamount": price,
        "discount": 0,
        "products": [{
            "name": title,
            "price": price,
            "amount": price,
            "quantity": 1,
            "uid": uid,
            "sku": sku,
            "recid": ST100,
        }],
        "amount": price,
        "total": price,
        "updated": 1718380800,
    }
    body = urllib.parse.urlencode({
        "c": PROJECT,
        "recid": ST100,
        "prodamount": price,
        "amount": price,
        "total": price,
        "products": json.dumps(cart["products"], ensure_ascii=False),
    }).encode()
    req = urllib.request.Request(
        "https://store.tildaapi.com/api/getpriceproducts",
        data=body,
        headers={"User-Agent": "chit-verify/1", "Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


for p in PRODUCTS:
    print("\n===", p[0], p[1])
    try:
        raw = post_price(p)
        print(raw[:800])
    except Exception as exc:
        print("ERR", exc)

# getproductsbyuid
for key, uid, title, price, sku in PRODUCTS:
    body = urllib.parse.urlencode({"productsuid": uid, "c": PROJECT}).encode()
    req = urllib.request.Request(
        "https://store.tildaapi.com/api/getproductsbyuid",
        data=body,
        headers={"User-Agent": "chit-verify/1", "Content-Type": "application/x-www-form-urlencoded"},
    )
    print("\n--- getproductsbyuid", uid)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            print(r.read().decode("utf-8", errors="replace")[:500])
    except Exception as exc:
        print("ERR", exc)
