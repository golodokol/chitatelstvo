#!/usr/bin/env python3
import re
import sys
import urllib.request
from pathlib import Path

LIVE = Path(__file__).resolve().parent / "live.html"

if "--fetch" in sys.argv:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    LIVE.write_text(html, encoding="utf-8")
else:
    html = LIVE.read_text(encoding="utf-8", errors="replace")

versions = sorted(set(re.findall(r"20260622[acd]", html)))
print("versions_on_site:", versions)

expected = [
    "tild6561-6235-4235-a331-303663316662/hero-book-full.png",
    "tild3564-3933-4463-a134-366463373364/vignette-reading-cor.png",
    "tild6433-3763-4463-b933-363439656234/lesson-step-video.PNG",
    "tild3965-6363-4134-b530-653333303262/lesson-step-quiz-tex.PNG",
    "tild3961-3361-4433-b232-316233356634/lesson-step-quiz-mea.PNG",
    "tild3864-6436-4237-b730-346663656565/lesson-step-creative.PNG",
    "tild3734-3262-4633-b265-613764366233/lesson-step-retell.PNG",
    "tild3364-3963-4332-a336-633664353637/programs-shelf-strip.PNG",
]

found = set(re.findall(r"https://static\.tildacdn\.com/[^\s\"'<>]+", html))

print("\n--- new compressed urls ---")
ok = 0
for key in expected:
    hits = [u for u in found if key in u]
    if hits:
        ok += 1
        print("OK ", hits[0])
    else:
        print("MISS", key)

print(f"\nnew_urls_ok: {ok}/{len(expected)}")

old = [
    "tild3835-6438-4433-b036-333936663637/hero-book-full",
    "tild3233-3362-4337-b331-633436343466/vignette-reading-cor",
    "tild6430-3038-4439-b730-326364336631/programs-shelf-strip",
    "tild3932-6565-4461-b665-633831356432/lesson-step-video",
]
print("\n--- old heavy urls still present? ---")
for key in old:
    hits = [u for u in found if key in u]
    print(("YES " if hits else "no "), key)

api_imgs = [u for u in found if "api.chitatelstvo.ru/assets/" in u and u.endswith((".png", ".PNG", ".jpg"))]
print("\napi_image_urls:", len(api_imgs))
for u in api_imgs:
    print(u)

js = re.findall(r"chit-zero\.js\?v=([^\"'\s]+)", html)
print("\nchit-zero.js versions:", sorted(set(js)))

css = re.findall(r"chit-zero\.css\?v=([^\"'\s]+)", html)
print("chit-zero.css versions:", sorted(set(css)))
