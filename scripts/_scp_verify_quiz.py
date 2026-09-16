# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "docs" / "tilda-zero-main"
KEY = Path.home() / ".ssh" / "chitatelstvo_deploy"
HOST = "194.87.201.99"
USER = "root"

files = [DIR / "chit-quiz.js", DIR / "chit-zero.js"]
scp = [
    "scp",
    "-i",
    str(KEY),
    "-o",
    "BatchMode=yes",
    "-o",
    "StrictHostKeyChecking=accept-new",
] + [str(f) for f in files] + [f"{USER}@{HOST}:/var/www/chitatelstvo-assets/"]
print("local", {f.name: f.stat().st_size for f in files})
subprocess.check_call(scp)
ssh = [
    "ssh",
    "-i",
    str(KEY),
    "-o",
    "BatchMode=yes",
    "-o",
    "StrictHostKeyChecking=accept-new",
    f"{USER}@{HOST}",
    "ls -l /var/www/chitatelstvo-assets/chit-quiz.js /var/www/chitatelstvo-assets/chit-zero.js; grep -c hasQuizIntent /var/www/chitatelstvo-assets/chit-quiz.js; grep -c chit_open_quiz /var/www/chitatelstvo-assets/chit-zero.js",
]
subprocess.check_call(ssh)
print("remote ok")
