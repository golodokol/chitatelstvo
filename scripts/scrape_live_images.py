#!/usr/bin/env python3
import re
import urllib.request

URL = "https://chitatelstvo.ru/"
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")

print("html_len", len(html))
print("versions", sorted(set(re.findall(r"20260622[ab]", html))))
print("zero_block", "rec2378409351" in html)

imgs = sorted(set(re.findall(r"https://(?:static\.tildacdn\.com|api\.chitatelstvo\.ru)[^\s\"'<>]+", html)))
print("img_count", len(imgs))

keys = [
    "hero-book",
    "vignette",
    "programs-shelf",
    "lesson-step",
    "gallery",
    "photo",
    "cta-fairy",
    "logo-chit",
    "pattern-meadow",
    "t-gallery",
]

print("\n--- relevant urls ---")
for u in imgs:
    if any(k in u for k in keys):
        print(u)

print("\n--- api assets ---")
for u in imgs:
    if "api.chitatelstvo.ru" in u:
        print(u)

print("\n--- gallery blocks ---")
for m in re.finditer(r"t-gallery|t-slds|gl12", html, re.I):
    start = max(0, m.start() - 80)
    print(html[start : m.start() + 120].replace("\n", " ")[:200])
