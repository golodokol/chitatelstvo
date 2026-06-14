#!/usr/bin/env python3
"""Deep check of Tilda catalog for Chitatelstvo."""
from __future__ import annotations

import json
import re
import urllib.request

URL = "https://chitatelstvo.ru/"
ST100_RECID = "2379461281"
PROJECT_ID = "14447246"
EXPECTED = [
    ("Читательство · Разовое", 1490),
    ("Читательство · Индивидуальное", 1990),
    ("Читательство · С преподавателем", 4990),
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "chitatelstvo-check/2.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_json(url: str):
    try:
        return json.loads(fetch(url))
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc), "url": url}


def norm_price(val) -> int | None:
    if val is None:
        return None
    s = str(val).replace(" ", "").replace(",", ".")
    try:
        return int(float(s))
    except ValueError:
        return None


def main() -> None:
    html = fetch(URL)

    store_ids = set(re.findall(r"storepartuid[=:\"']([a-f0-9]+)", html, re.I))
    store_ids |= set(re.findall(r'data-store-part-uid="([a-f0-9]+)"', html))
    store_ids |= set(re.findall(r'"partuid"\s*:\s*(\d+)', html))

    print("storepartuid in homepage HTML:", store_ids or "none")

    api_products: list[dict] = []
    tried: list[str] = []

    candidates = list(store_ids)
    candidates.append("")  # try without part uid

    for sid in candidates:
        urls = [
            f"https://store.tildaapi.com/api/getproductslist/?recid={ST100_RECID}&size=100&storepartuid={sid}" if sid else None,
            f"https://store.tildaapi.com/api/getproducts/?storepartuid={sid}&recid={ST100_RECID}" if sid else None,
            f"https://store.tildaapi.com/api/getproductslist/?recid={ST100_RECID}&size=100&getparts=true",
        ]
        for api_url in urls:
            if not api_url or api_url in tried:
                continue
            tried.append(api_url)
            data = fetch_json(api_url)
            if isinstance(data, dict) and data.get("products"):
                api_products.extend(data["products"])
            elif isinstance(data, list):
                api_products.extend(data)

    # dedupe by uid
    seen = set()
    unique = []
    for p in api_products:
        uid = p.get("uid") or p.get("productuid")
        if uid in seen:
            continue
        seen.add(uid)
        unique.append(p)
    api_products = unique

    # titles in HTML (any variant with middle dot / dash)
    print("\n=== Similar titles in homepage HTML ===")
    for m in re.finditer(r"Читательство[^<\n\"]{0,60}", html):
        t = m.group(0).strip()
        if any(k in t for k in ("Разовое", "Индивидуальное", "преподавателем", "1490", "1990", "4990")):
            print(" ", repr(t))

    print("\n=== Expected products ===")
    for title, price in EXPECTED:
        api_match = next(
            (
                p
                for p in api_products
                if str(p.get("title", "")).strip() == title and norm_price(p.get("price")) == price
            ),
            None,
        )
        html_match = title in html
        status = "OK" if api_match or html_match else "MISSING"
        print(f"  [{status}] {title} — {price} RUB")

    if api_products:
        print("\n=== All products from Tilda store API ===")
        for p in api_products:
            print(
                f"  - {p.get('title')} — {p.get('price')} RUB (uid={p.get('uid', p.get('productuid', '?'))})"
            )
    else:
        print("\n=== Tilda store API returned 0 products ===")
        print("Catalog exists in editor but may not be linked to ST100/homepage yet.")
        print("Check: Catalog -> 3 services published + ST100 uses same catalog.")


if __name__ == "__main__":
    main()
