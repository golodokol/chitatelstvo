#!/usr/bin/env python3
import re
import urllib.request

html = urllib.request.urlopen(
    urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "x"}),
    timeout=30,
).read().decode("utf-8", "replace")

start = html.find("rec2379461281")
block = html[start : start + 20000]
print("block len", len(block))
for pat in ["storepart", "product", "catalog", "t-store", "cartdata", "payment-system"]:
    print(pat, block.lower().count(pat.lower()))

cm = re.search(r"t706__cartdata[^>]*>(.*?)</", block, re.S)
print("cartdata:", repr(cm.group(1)[:300]) if cm else "none")

rec = re.search(r'<div id="rec2379461281"[^>]*>', html)
print("rec attrs:", rec.group(0) if rec else "?")

for m in re.finditer(r"<input[^>]+>", block):
    inp = m.group(0)
    if "hidden" in inp or "product" in inp.lower():
        print(inp[:250])
