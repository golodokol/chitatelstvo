#!/usr/bin/env python3
import re, urllib.request
h = urllib.request.urlopen(urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent":"x"}), timeout=30).read().decode("utf-8","replace")
for pat in ["tcart", "t706", "addProduct", "storepart", "getproducts", "t-store", "order:"]:
    print(pat, h.count(pat))
# tcart init
m = re.search(r"tcart__init\('(\d+)'[^\)]*\)", h)
print("tcart init:", m.group(0)[:300] if m else "?")
# any script src store
for m in re.finditer(r'src="([^"]*store[^"]*)"', h, re.I):
    print("script", m.group(1)[:120])
# formservices in st100
idx = h.find("form2379461281")
print("st100 chunk services:", re.findall(r'formservices\[\]" value="([^"]+)"', h[idx:idx+8000]))
