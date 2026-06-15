#!/usr/bin/env python3
import re, urllib.request
html = urllib.request.urlopen(urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent":"x"}), timeout=30).read().decode("utf-8","replace")
for rec in ["2380183631", "2380172391", "2380172421"]:
    idx = html.find("rec" + rec)
    if idx < 0:
        print(rec, "missing")
        continue
    chunk = html[idx:idx+12000]
    name = re.search(r'js-product-name[^>]*>([^<]+)', chunk)
    price = re.search(r'js-store-prod-price-val[^>]*>([^<]+)', chunk)
    style_h = re.search(r'id="rec' + rec + r'"[^>]*style="([^"]*)"', chunk[:200])
    artboard_h = re.search(r't762[^"]*"[^>]*style="[^"]*height:\s*(\d+)', chunk)
    print(f"\nrec{rec}")
    print("  name:", name.group(1).strip() if name else "?")
    print("  price:", price.group(1).strip() if price else "?")
    print("  rec style:", style_h.group(1) if style_h else "?")
    # block total height hints
    for m in re.finditer(r'height:(\d+)px', chunk[:3000]):
        print("  height px:", m.group(1))
