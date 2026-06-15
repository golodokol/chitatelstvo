#!/usr/bin/env python3
"""Try multiple getpriceproducts payload shapes."""
import json
import urllib.parse
import urllib.request

PROJECT = "14447246"
ST100 = "2379461281"
UA = {"User-Agent": "chit-price/1", "Referer": "https://chitatelstvo.ru/"}

TITLE = "Читательство · С преподавателем"
PRICE = 4990
UID = "956231952022"
SKU = "SKU0003"


def try_payload(label, products, extra=None):
    data = {
        "c": PROJECT,
        "recid": ST100,
        "prodamount": PRICE,
        "amount": PRICE,
        "total": PRICE,
        "products": json.dumps(products, ensure_ascii=False),
    }
    if extra:
        data.update(extra)
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        "https://store.tildaapi.com/api/getpriceproducts",
        data=body,
        headers={**UA, "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        raw = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace")
        print(f"{label}: {raw[:200]}")
    except Exception as exc:
        print(f"{label}: ERR {exc}")


base = {"name": TITLE, "price": PRICE, "amount": PRICE, "quantity": 1, "recid": ST100}

try_payload("name only", [base])
try_payload("name+sku", [{**base, "sku": SKU}])
try_payload("name+uid", [{**base, "uid": UID}])
try_payload("name+uid+sku", [{**base, "uid": UID, "sku": SKU}])
try_payload("short name", [{**base, "name": "С преподавателем"}])
try_payload("no dot name", [{**base, "name": "Читательство С преподавателем"}])

# full cart object as Tilda sends
cart = {
    "prodamount": PRICE,
    "discount": 0,
    "products": [{**base, "uid": UID, "sku": SKU, "lid": UID}],
    "amount": PRICE,
    "total": PRICE,
    "updated": 1718380800,
}
body = urllib.parse.urlencode({"c": PROJECT, "recid": ST100, **{k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in {
    "prodamount": PRICE, "amount": PRICE, "total": PRICE,
    "products": cart["products"],
}.items()}}).encode()
req = urllib.request.Request(
    "https://store.tildaapi.com/api/getpriceproducts",
    data=body,
    headers={**UA, "Content-Type": "application/x-www-form-urlencoded"},
)
try:
    print("with lid:", urllib.request.urlopen(req, timeout=25).read().decode()[:200])
except Exception as e:
    print("with lid ERR", e)

# try storepartuid variants
for sid in [PROJECT, ST100, "133375856", "2378409351"]:
    try_payload(f"uid+storepartuid={sid}", [{**base, "uid": UID, "sku": SKU}], {"storepartuid": sid})
