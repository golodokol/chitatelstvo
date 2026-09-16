# -*- coding: utf-8 -*-
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CP = ROOT / "docs" / "course-pages"
KEY = Path.home() / ".ssh" / "chitatelstvo_deploy"
VER = "20260916j"

subprocess.check_call(["python", str(ROOT / "scripts" / "_gen_course_pages.py")], cwd=str(ROOT))

# bump local wind/garden html if gen didn't cover all refs
for p in CP.rglob("*.html"):
    t = p.read_text(encoding="utf-8")
    t2 = re.sub(r"course-lite\.(css|js|data\.js)\?v=[^\"'&\s]+", rf"course-lite.\1?v={VER}", t)
    if t2 != t:
        p.write_text(t2, encoding="utf-8")

cmd = [
    "scp",
    "-i",
    str(KEY),
    "-o",
    "BatchMode=yes",
    "-o",
    "StrictHostKeyChecking=accept-new",
    str(CP / "course-lite.css"),
    str(CP / "course-lite.js"),
    str(CP / "course-lite-data.js"),
    f"root@194.87.201.99:/var/www/chitatelstvo-assets/course-pages/",
]
subprocess.check_call(cmd)
print("uploaded accordion fix", VER)
