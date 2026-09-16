# -*- coding: utf-8 -*-
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
data = (root / "docs/course-pages/course-lite-data.js").read_text(encoding="utf-8")
# Better chest visual from school presentation assets mirrored on CDN static if present;
# fall back stays lesson-step-creative. Prefer absolute presentation URL via api assets copy.
old = "https://api.chitatelstvo.ru/assets/lesson-step-creative.png"
# Only replace the chest reward image (second occurrence in rewards blocks is creative step too).
# Patch rewards chest specifically by unique surrounding text.
chest_url = "https://api.chitatelstvo.ru/assets/lesson-step-creative.png"
# Use gamify badge as alternate? Keep creative for chest text about creative task — OK.

# Verify embed JSON has lessons
for name in ("veter-v-ivah.html", "tainstvenny-sad.html"):
    t = (root / "docs/course-pages/tilda-redirects" / name).read_text(encoding="utf-8")
    checks = {
        "aboutBook": "aboutBook" in t,
        "lessonSteps": "lessonSteps" in t,
        "rewards": '"rewards"' in t or "rewardsTitle" in t,
        "ccl-step css": ".ccl-step" in t,
        "inline activate": "activateLiteApp" in t,
    }
    print(name, checks)
    # extract lesson titles from embed
    m = re.search(r'"lessons"\s*:\s*\[(.*?)\]', t, re.S)
    if m:
        titles = re.findall(r'"title"\s*:\s*"([^"]+)"', m.group(1))
        print("  lessons:", titles)

# chit-zero
z = (root / "docs/tilda-zero-main/chit-zero.js").read_text(encoding="utf-8")
print("chit-zero wind label:", "Жители берега реки" in z)
print("chit-zero garden label:", "Знакомство с Мэри" in z)
print("chit-zero old:", "Знакомство с книгой" in z and "wind" in z)
