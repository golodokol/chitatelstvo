#!/usr/bin/env python3
import re
import urllib.request

js = urllib.request.urlopen(
    "https://static.tildacdn.com/js/tilda-cart-1.1.min.js",
    timeout=30,
).read().decode("utf-8", "replace")

for term in ["getpriceproducts", "Wrong Products", "tcart__addProduct", "storepartuid", ":::uid=", "out of stock", "нет в наличии"]:
    idx = 0
    n = 0
    while n < 3:
        idx = js.find(term, idx)
        if idx < 0:
            break
        print(f"\n=== {term} #{n+1} @ {idx} ===")
        print(js[max(0, idx - 120) : idx + 280])
        idx += len(term)
        n += 1
