# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CP = ROOT / "docs" / "course-pages"
KEY = Path.home() / ".ssh" / "chitatelstvo_deploy"
files = [
    CP / "course-lite.css",
    CP / "course-lite.js",
    CP / "course-lite-data.js",
]
cmd = [
    "scp",
    "-i",
    str(KEY),
    "-o",
    "BatchMode=yes",
    "-o",
    "StrictHostKeyChecking=accept-new",
] + [str(f) for f in files] + [
    "root@194.87.201.99:/var/www/chitatelstvo-assets/course-pages/"
]
subprocess.check_call(cmd)
print("cdn ok", [f.name for f in files])
