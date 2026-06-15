#!/usr/bin/env python3
import json, urllib.parse, urllib.request
PROJECT = "14447246"
UA = {"User-Agent": "x", "Referer": "https://chitatelstvo.ru/"}
tests = [
    ("ST100", "2379461281", "797131986522", 1490),
    ("T762-1", "2380183631", "797131986522", 1490),
    ("T762-2", "2380172391", "206548598642", 1990),
    ("T762-3", "2380172421", "956231952022", 4990),
]
for label, recid, uid, price in tests:
    cart = [{"name": "Читательство · Разовое", "price": price, "amount": price, "quantity": 1, "uid": uid, "recid": recid}]
    body = urllib.parse.urlencode({
        "c": PROJECT, "recid": recid, "prodamount": price, "amount": price, "total": price,
        "products": json.dumps(cart, ensure_ascii=False),
    }).encode()
    req = urllib.request.Request("https://store.tildaapi.com/api/getpriceproducts", data=body,
        headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
    try:
        raw = urllib.request.urlopen(req, timeout=20).read().decode()
        print(label, recid, "->", raw[:150])
    except Exception as e:
        print(label, "ERR", e)
