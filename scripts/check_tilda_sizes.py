#!/usr/bin/env python3
import urllib.request

checks = [
    ("GL12 hero-book-full", "https://static.tildacdn.com/tild3463-6531-4233-a632-616134353338/hero-book-full.png"),
    ("live hero-book-full", "https://static.tildacdn.com/tild3835-6438-4433-b036-333936663637/hero-book-full.png"),
    ("GL12 vignette", "https://static.tildacdn.com/tild3463-6531-4233-a632-616134353338/vignette-reading-corner.png"),
    ("live vignette", "https://static.tildacdn.com/tild3233-3362-4337-b331-633436343466/vignette-reading-cor.png"),
    ("GL12 lesson-video", "https://static.tildacdn.com/tild3463-6531-4233-a632-616134353338/lesson-step-video.png"),
    ("live lesson-video", "https://static.tildacdn.com/tild3932-6565-4461-b665-633831356432/lesson-step-video.png"),
    ("GL12 programs-shelf", "https://static.tildacdn.com/tild3463-6531-4233-a632-616134353338/programs-shelf-strip.png"),
    ("live programs-shelf", "https://static.tildacdn.com/tild6430-3038-4439-b730-326364336631/programs-shelf-strip.png"),
]

for label, url in checks:
    try:
        r = urllib.request.urlopen(url, timeout=30)
        size = int(r.headers.get("Content-Length", 0))
        print(f"{size//1024:4d} KB  {label}")
    except Exception as e:
        print(f" FAIL  {label}: {e}")
