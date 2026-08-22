#!/usr/bin/env python3
import urllib.request

urls = [
    ("hero-book-full", "https://static.tildacdn.com/tild6561-6235-4235-a331-303663316662/hero-book-full.png"),
    ("vignette", "https://static.tildacdn.com/tild3564-3933-4463-a134-366463373364/vignette-reading-cor.png"),
    ("programs-shelf", "https://static.tildacdn.com/tild3364-3963-4332-a336-633664353637/programs-shelf-strip.PNG"),
    ("lesson-video", "https://static.tildacdn.com/tild6433-3763-4463-b933-363439656234/lesson-step-video.PNG"),
    ("lesson-retell", "https://static.tildacdn.com/tild3734-3262-4633-b265-613764366233/lesson-step-retell.PNG"),
]

for name, url in urls:
    try:
        r = urllib.request.urlopen(url, timeout=30)
        data = r.read(1024)
        cl = r.headers.get("Content-Length")
        size = int(cl) if cl else len(data)
        # read rest if no content-length
        if not cl:
            rest = r.read()
            size = len(data) + len(rest)
        print(f"{size//1024:4d} KB  {name}")
    except Exception as e:
        print(f"FAIL {name}: {e}")
