#!/usr/bin/env python3
import urllib.request

urls = [
    "https://static.tildacdn.com/tild3564-3933-4463-a134-366463373364/vignette-reading-cor.png",
    "https://static.tildacdn.com/tild3965-6363-4134-b530-653333303262/lesson-step-quiz-tex.PNG",
    "https://static.tildacdn.com/tild3961-3361-4433-b232-316233356634/lesson-step-quiz-mea.PNG",
    "https://static.tildacdn.com/tild3864-6436-4237-b730-346663656565/lesson-step-creative.PNG",
    "https://static.tildacdn.com/tild6561-6235-4235-a331-303663316662/hero-book-full.png",
    "https://static.tildacdn.com/tild3364-3963-4332-a336-633664353637/programs-shelf-strip.PNG",
    "https://static.tildacdn.com/tild6433-3763-4463-b933-363439656234/lesson-step-video.PNG",
    "https://static.tildacdn.com/tild3734-3262-4633-b265-613764366233/lesson-step-retell.PNG",
]

for url in urls:
    try:
        r = urllib.request.urlopen(url, timeout=30)
        size = int(r.headers.get("Content-Length", 0))
        name = url.rsplit("/", 1)[-1]
        print(f"{size//1024:4d} KB  {name}")
    except Exception as e:
        print(f"FAIL  {url}: {e}")
