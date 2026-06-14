#!/usr/bin/env python3
import re, urllib.request
html = urllib.request.urlopen(urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent":"x"}), timeout=30).read().decode("utf-8","replace")
for rec in ["2380172341", "2380172391", "2380172421"]:
    idx = html.find("rec" + rec)
    chunk = html[idx:idx + 25000]
    links = re.findall(r'href="(#order[^"]+)"', chunk)
    print("rec", rec)
    print("  order links:", links[:5])
    for m in re.finditer(r"js-store-prod-price-val[^>]*>([^<]+)", chunk):
        print("  price:", m.group(1).strip())
    sku = re.search(r"js-product-sku[^>]*>([^<]+)", chunk)
    if sku:
        print("  sku:", sku.group(1).strip())
