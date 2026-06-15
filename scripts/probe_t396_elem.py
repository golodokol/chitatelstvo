#!/usr/bin/env python3
import re, urllib.request
html = urllib.request.urlopen(
    urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "x"}),
    timeout=30,
).read().decode("utf-8", errors="replace")

idx = html.find("rec2378409351")
chunk = html[idx:idx+25000]

# find HTML elem tn-elem blocks
print("=== tn-elem html elements ===")
for m in re.finditer(r'<div class="tn-elem[^"]*"[^>]*data-elem-type="html"[^>]*>', chunk):
    print(m.group(0)[:500])

# breakpoint-specific attrs
print("\n=== elem attrs (left/top/width/height/res/axis) ===")
for m in re.finditer(r'data-field-(left|top|width|height|axisy|container)-value="([^"]*)"', chunk):
    pass
attrs = re.findall(r'data-field-([a-z]+)-value="([^"]*)"', chunk)
from collections import defaultdict
by = defaultdict(list)
for k,v in attrs:
    by[k].append(v)
for k in sorted(by.keys()):
    print(k, ":", by[k][:12])

# inline styles on artboard
m = re.search(r'\.t396__artboard \{([^}]+)\}', chunk)
print("\nartboard inline css:", m.group(1)[:300] if m else "?")

# check for duplicate HTML blocks in zero
print("tn-atom__html count in zero block:", chunk.count("tn-atom__html"))
print("chit-main in chunk:", chunk.count("chit-main"))

# ST100 cart icon style visible?
st = html.find("rec2379461281")
print("\nST100 carticon style:", re.search(r't706__carticon" style="([^"]*)"', html[st:st+5000]))

# page total height estimate from chit-main sections
sections = re.findall(r'<section[^>]+id="([^"]+)"', html)
print("\nsections:", sections[:20], "...", len(sections))
