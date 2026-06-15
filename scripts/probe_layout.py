#!/usr/bin/env python3
"""Diagnose chitatelstvo.ru layout issues."""
import json
import re
import urllib.request

URL = "https://chitatelstvo.ru/"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "layout-check/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace"), dict(resp.headers)


html, hdrs = fetch(URL)
print("=== Page ===")
print("content-length:", hdrs.get("Content-Length", "?"))
print("page size:", len(html))

# Zero blocks count
zero_blocks = re.findall(r'id="rec(\d+)"[^>]*data-record-type="396"', html)
print("\n=== Zero blocks (396) ===")
print("count:", len(zero_blocks), "recids:", zero_blocks)

# chit-main count
print("chit-main count:", html.count('id="chit-main"'))
print("chit-zero.css refs:", len(re.findall(r"chit-zero\.css", html)))
print("chit-zero.js refs:", len(re.findall(r"chit-zero\.js", html)))

for m in re.finditer(r'(https?://[^"\']+chit-zero\.(css|js)\?v=[^"\']+)', html):
    print("  asset:", m.group(1))

# Artboard settings for zero block
print("\n=== Zero block artboard (rec2378409351) ===")
idx = html.find("rec2378409351")
if idx >= 0:
    chunk = html[idx:idx+15000]
    for pat in [
        r'data-artboard-screens="([^"]+)"',
        r'data-artboard-height="(\d+)"',
        r'data-artboard-valign="([^"]+)"',
        r'data-artboard-upscale="([^"]+)"',
        r'height:(\d+)px;background-color',
    ]:
        m = re.search(pat, chunk)
        print(f"  {pat[:35]}: {m.group(1) if m else 'NOT FOUND'}")

    # HTML element sizes per breakpoint in t396
    elems = re.findall(
        r'data-field-top-value="(\d+)"[^>]*data-field-left-value="(\d+)"[^>]*data-field-width-value="(\d+)"[^>]*data-field-height-value="(\d+)"',
        chunk,
    )
    print("  t396 field boxes (top,left,width,height):", elems[:8])

# Tilda scale script presence
print("\n=== Tilda scale/autoscale ===")
print("t396_initialScale in page:", "t396_initialScale" in html)
print("tn_scale in page:", "tn_scale" in html)

# Check assets HTTP
print("\n=== Asset HTTP status ===")
assets = re.findall(r'https://api\.chitatelstvo\.ru/assets/[^"\']+', html)
seen = set()
for a in sorted(set(assets)):
    if a in seen:
        continue
    seen.add(a)
    try:
        req = urllib.request.Request(a, headers={"User-Agent": "layout-check/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"  {r.status} {r.headers.get('Content-Type','?')[:40]} {len(r.read())}b {a[:90]}")
    except Exception as e:
        print(f"  FAIL {a[:90]} -> {e}")

# ST100 visible on page?
print("\n=== ST100 cart icon ===")
print("t706 cart block:", "rec2379461281" in html)
print("t706__carticon in html:", "t706__carticon" in html)

# Potential layout killers
print("\n=== Red flags ===")
if html.count('id="chit-main"') > 1:
    print("  DUPLICATE chit-main!")
if len(zero_blocks) > 1:
    print("  MULTIPLE zero blocks!")
if html.count("chit-zero.css") > 1:
    print("  DUPLICATE css links!")
if "100vw" in html and "chit-main" in html:
    # check if in inline styles from tilda
    pass
# artboard height
m = re.search(r'rec2378409351[^>]+', html)
ah = re.search(r'height:(\d+)px;background-color:#ffffff', html)
if ah:
    h = int(ah.group(1))
    print(f"  artboard CSS height: {h}px")
    if h > 50000:
        print("  WARNING: artboard height very large")

# fonts
print("\n=== External fonts ===")
for u in ["fonts.googleapis.com", "fonts.gstatic.com"]:
    print(f"  {u}:", u in html)
