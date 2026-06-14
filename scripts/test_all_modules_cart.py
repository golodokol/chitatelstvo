#!/usr/bin/env python3
"""Verify module mapping + Tilda getpriceproducts for all 3 tariffs."""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request

PROJECT = "14447246"
ST100 = "2379461281"
UA = {"User-Agent": "chit-modules/1", "Referer": "https://chitatelstvo.ru/"}

MODULES = {
    "grade-1": {"single": 1, "self_paced": 2, "with_teacher": 3},
    "grade-2": {"single": 4, "self_paced": 5, "with_teacher": 6},
    "grade-3": {"single": 7, "self_paced": 8, "with_teacher": 9},
    "grade-4": {"single": 10, "self_paced": 11, "with_teacher": 12},
    "extra-6-8": {"single": 13, "self_paced": 14, "with_teacher": 15},
    "extra-9-11": {"single": 16, "self_paced": 17, "with_teacher": 18},
}

PRODUCTS = {
    "single": {
        "title": "Читательство · Разовое",
        "price": 1490,
        "uids": ["797131986522", "863983274147"],
        "sku": "SKU0001-2",
    },
    "self_paced": {
        "title": "Читательство · Индивидуальное",
        "price": 1990,
        "uids": ["206548598642", "205285061796"],
        "sku": "SKU0002",
    },
    "with_teacher": {
        "title": "Читательство · С преподавателем",
        "price": 4990,
        "uids": ["956231952022", "776534181255"],
        "sku": "SKU0003",
    },
}


def post_price(uid: str, title: str, price: int, sku: str) -> str:
    cart = [{
        "name": title,
        "price": price,
        "amount": price,
        "quantity": 1,
        "uid": uid,
        "sku": sku,
        "recid": ST100,
    }]
    body = urllib.parse.urlencode({
        "c": PROJECT,
        "recid": ST100,
        "prodamount": price,
        "amount": price,
        "total": price,
        "products": json.dumps(cart, ensure_ascii=False),
    }).encode()
    req = urllib.request.Request(
        "https://store.tildaapi.com/api/getpriceproducts",
        data=body,
        headers={**UA, "Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    print("=== Module IDs (18) ===")
    ids = []
    for group, tariffs in MODULES.items():
        for tariff, mid in tariffs.items():
            ids.append(mid)
            print(f"  module {mid:2d}  {group:12s}  {tariff}")
    assert len(ids) == 18 and len(set(ids)) == 18, "module id collision"
    print("OK: 18 unique module IDs\n")

    print("=== getpriceproducts (payment validation) ===")
    ok = 0
    for tariff, p in PRODUCTS.items():
        for uid in p["uids"]:
            try:
                raw = post_price(uid, p["title"], p["price"], p["sku"])
                status = "OK" if "error" not in raw.lower() else "FAIL"
                if status == "OK":
                    ok += 1
                print(f"  {status}  {tariff:12s}  uid={uid}  ->  {raw[:120]}")
            except Exception as exc:
                print(f"  ERR   {tariff:12s}  uid={uid}  ->  {exc}")

    if ok == 0:
        print("\nFAIL: no UID accepted by Tilda getpriceproducts")
        print("Fix: add 3x ST205 blocks on homepage OR correct Product IDs in catalog export")
        return 1
    print(f"\nOK: {ok} UID(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
