#!/usr/bin/env python3
"""Deep probe of live homepage after ST205 setup."""
import json
import re
import urllib.parse
import urllib.request

URL = "https://chitatelstvo.ru/"
PROJECT = "14447246"
ST100 = "2379461281"
UA = {"User-Agent": "chit-st205-probe/1", "Referer": URL}

html = urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=30).read().decode(
    "utf-8", errors="replace"
)

print("=== Asset versions ===")
print(re.findall(r"chit-zero\.(js|css)\?v=[^\"']+", html))

print("\n=== All block types on page ===")
blocks = re.findall(r'id="rec(\d+)"[^>]*data-record-type="(\d+)"', html)
type_names = {"205": "ST205", "706": "ST100", "396": "Zero", "331": "T123", "215": "ST015"}
for rec, typ in blocks:
    print(f"  rec{rec}  type={typ} ({type_names.get(typ, '?')})")
print(f"Total blocks: {len(blocks)}")

print("\n=== ST205 / store markers ===")
print("data-record-type=205:", html.count('data-record-type="205"'))
print("js-product cards:", len(re.findall(r'class="[^"]*js-product', html)))
print("data-product-uid:", re.findall(r'data-product-uid="(\d+)"', html))
print("storepartuid:", set(re.findall(r'storepartuid[=:"\']([a-f0-9]+)', html, re.I)))
print("data-store-part-uid:", re.findall(r'data-store-part-uid="([^"]+)"', html))

for title in ["Разовое", "Индивидуальное", "преподавателем", "1490", "4990"]:
    print(f"  '{title}' in html: {title in html}")

# ST205 block excerpts
for m in re.finditer(r'id="rec(\d+)"[^>]*data-record-type="205"', html):
    rec = m.group(1)
    start = m.start()
    chunk = html[start : start + 2500]
    print(f"\n=== ST205 rec{rec} excerpt ===")
    for pat in ["data-product-uid", "data-product-lid", "data-product-part-uid", "797131986522", "956231952022"]:
        if pat in chunk:
            idx = chunk.find(pat)
            print(" ", pat, "->", chunk[max(0, idx - 40) : idx + 80])

# getproductslist with storepartuid from ST205 if found
partuids = set(re.findall(r'data-product-part-uid="([^"]+)"', html))
partuids |= set(re.findall(r'storepartuid[=:"\']([a-f0-9]+)', html, re.I))
for sid in partuids:
    api = f"https://store.tildaapi.com/api/getproductslist/?recid={ST100}&c={PROJECT}&size=100&storepartuid={sid}"
    print(f"\n=== getproductslist storepartuid={sid} ===")
    try:
        raw = urllib.request.urlopen(urllib.request.Request(api, headers=UA), timeout=20).read().decode()
        print(raw[:1500])
    except Exception as exc:
        print("ERR", exc)

# getpriceproducts with uid if on page
uids = re.findall(r'data-product-uid="(\d+)"', html) or [
    "797131986522",
    "206548598642",
    "956231952022",
]
for uid in uids[:3]:
    cart = [{"name": "test", "price": 4990, "amount": 4990, "quantity": 1, "uid": uid, "recid": ST100}]
    body = urllib.parse.urlencode(
        {
            "c": PROJECT,
            "recid": ST100,
            "prodamount": 4990,
            "amount": 4990,
            "total": 4990,
            "products": json.dumps(cart, ensure_ascii=False),
        }
    ).encode()
    req = urllib.request.Request(
        "https://store.tildaapi.com/api/getpriceproducts",
        data=body,
        headers={**UA, "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        raw = urllib.request.urlopen(req, timeout=20).read().decode()
        print(f"\ngetpriceproducts uid={uid}: {raw[:200]}")
    except Exception as exc:
        print(f"\ngetpriceproducts uid={uid}: ERR {exc}")
