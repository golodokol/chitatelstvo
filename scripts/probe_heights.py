#!/usr/bin/env python3
import re, urllib.request
html = urllib.request.urlopen(
    urllib.request.Request("https://chitatelstvo.ru/", headers={"User-Agent": "x"}),
    timeout=30,
).read().decode("utf-8", errors="replace")

idx = html.find("rec2378409351")
chunk = html[idx:idx+80000]

# all height rules in zero block styles
heights = re.findall(r"height:(\d+)px", chunk)
print("height values in zero block CSS:", sorted(set(heights), key=int))
print("max height rule:", max(int(h) for h in heights) if heights else "?")

# tn-elem rules
print("\n=== tn-elem height rules ===")
for m in re.finditer(r"(\#rec2378409351[^\{]+\{[^}]*height:[^}]+\})", chunk):
    s = m.group(1)
    if "9500" in s or "1200" in s:
        print(s[:200])

# blocks in page
for tag in ['enroll-panel','program-picker','tariff-pick','final-cta','site-footer','feedback-tab','preview-strip','benefits','for-whom']:
    print(f"{tag}: {tag in html}")

# chit-main approximate size
start = html.find('id="chit-main"')
end = html.find('<script src="https://api.chitatelstvo.ru/assets/chit-zero.js', start)
print(f"\nchit-main HTML size: {end-start if end>start else '?'} chars")

# media queries in t396 for elem width
print("\n=== width rules at breakpoints ===")
for m in re.finditer(r"@media[^{]+\{[^}]*width:(\d+)px", chunk):
    print(" ", m.group(0)[:120])
