#!/usr/bin/env python3
"""Full diagnostic of chitatelstvo.ru homepage."""
import json
import re
import urllib.parse
import urllib.request

URL = "https://chitatelstvo.ru/"
PROJECT = "14447246"
ST100 = "2379461281"
UA = {"User-Agent": "chit-diag/2", "Referer": URL}

html = urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=30).read().decode(
    "utf-8", errors="replace"
)

print("=== Assets ===")
for m in re.finditer(r"chit-zero\.(css|js)\?v=([^\"']+)", html):
    print(f"  {m.group(1)} v={m.group(2)}")

print("\n=== Blocks ===")
for rec, typ in re.findall(r'id="rec(\d+)"[^>]*data-record-type="(\d+)"', html):
    print(f"  rec{rec} type={typ}")

print("\n=== Store products on page ===")
for m in re.finditer(
    r'data-product-gen-uid="(\d+)"[^>]*>|data-product-gen-uid="(\d+)"', html
):
    uid = m.group(1) or m.group(2)
    start = max(0, m.start() - 200)
    chunk = html[start : m.start() + 800]
    name = re.search(r'js-product-name[^>]*>([^<]+)', chunk)
    price = re.search(r'js-store-prod-price-val[^>]*>([^<]+)', chunk)
    sku = re.search(r'js-product-sku[^>]*>([^<]+)', chunk)
    print(f"  uid={uid} name={name.group(1).strip() if name else '?'} price={price.group(1).strip() if price else '?'} sku={sku.group(1).strip() if sku else '?'}")

print("\n=== CSS hide rule on server ===")
css_url = re.search(r'chit-zero\.css\?v=([^"\']+)', html)
if css_url:
    v = css_url.group(1)
    css = urllib.request.urlopen(
        urllib.request.Request(f"https://api.chitatelstvo.ru/assets/chit-zero.css?v={v}", headers=UA),
        timeout=20,
    ).read().decode("utf-8", errors="replace")
    print("  has hide rule:", "data-record-type=\"762\"" in css and "left: -99999px" in css)
else:
    print("  chit-zero.css not linked")

print("\n=== JS on server ===")
js_url = re.search(r'chit-zero\.js\?v=([^"\']+)', html)
if js_url:
    js = urllib.request.urlopen(
        urllib.request.Request(f"https://api.chitatelstvo.ru/assets/chit-zero.js?v={js_url.group(1)}", headers=UA),
        timeout=20,
    ).read().decode("utf-8", errors="replace")
    for fn in ["triggerStoreBuy", "findStoreProductCard", "chitValidateCatalogPayment", "data-record-type=\"762\""]:
        print(f"  {fn}: {fn in js}")

print("\n=== getpriceproducts ===")
for uid, price in [
    ("797131986522", 1490),
    ("206548598642", 1990),
    ("956231952022", 4990),
]:
    cart = [{"name": "x", "price": price, "amount": price, "quantity": 1, "uid": uid, "recid": ST100}]
    body = urllib.parse.urlencode(
        {
            "c": PROJECT,
            "recid": ST100,
            "prodamount": price,
            "amount": price,
            "total": price,
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
        print(f"  uid {uid}: {raw[:120]}")
    except Exception as e:
        print(f"  uid {uid}: ERR {e}")

# t_store init on 762 blocks
print("\n=== t_store_oneProduct_init ===")
for m in re.finditer(r"t_store_oneProduct_init\([^)]{0,400}\)", html):
    s = m.group(0)
    if "797131986522" in s or "956231952022" in s or "previewmode" in s:
        print(" ", s[:350])
