#!/usr/bin/env python3
import re
import sys
import urllib.request
from pathlib import Path

LIVE = Path(__file__).resolve().parent / "live.html"
URL = "https://chitatelstvo.ru/"

if LIVE.exists() and "--fetch" not in sys.argv:
    html = LIVE.read_text(encoding="utf-8", errors="replace")
else:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    LIVE.write_text(html, encoding="utf-8")

urls = sorted(set(re.findall(r"https://static\.tildacdn\.com/[^\s\"'<>]+", html)))
print("total_tilda_urls", len(urls))

# GL12 / gallery blocks
for pat in [r"t-gallery", r"data-record-type=\"12\"", r"GL12", r"t-slds"]:
    if re.search(pat, html, re.I):
        print("found", pat)

print("\n--- by filename ---")
names = [
    "hero-book-full",
    "hero-book-single",
    "hero-book-block",
    "vignette",
    "programs-shelf",
    "lesson-step",
    "logo-chitatelstvo",
    "cta-fairy",
    "pattern-meadow",
    "photo.png",
    "audience-",
    "gamify-",
    "founder-",
]
for u in urls:
    if any(n in u for n in names):
        print(u)

# unique bases
bases = sorted({re.match(r"(https://static\.tildacdn\.com/tild[^/]+/)", u).group(1) for u in urls if re.match(r"https://static\.tildacdn\.com/tild", u)})
print("\n--- bases ---")
for b in bases:
    print(b)
