# -*- coding: utf-8 -*-
"""Upload quiz/zero assets and bump cache-bust version in homepage HTML."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "docs" / "tilda-zero-main"
KEY = Path.home() / ".ssh" / "chitatelstvo_deploy"
HOST = "194.87.201.99"
USER = "root"
REMOTE = f"{USER}@{HOST}:/var/www/chitatelstvo-assets/"
NEW = "20260916b"

FILES = [
    DIR / "chit-quiz.js",
    DIR / "chit-zero.js",
    DIR / "chit-quiz.css",
    DIR / "chit-zero.css",
]


def bump_html() -> None:
    for name in (
        "glavnaya.html",
        "00-tilda-zero-upload.html",
        "00-tilda-lite.html",
        "_preview-layout.html",
        "00-tilda-lite-tildacdn.html",
    ):
        p = DIR / name
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        o = t
        t = re.sub(r"chit-zero\.js\?v=[^\"'&]+", f"chit-zero.js?v={NEW}", t)
        t = re.sub(r'(V=")[^"]+(")', rf"\g<1>{NEW}\2", t)
        t = re.sub(r"(V=')[^']+(')", rf"\g<1>{NEW}\2", t)
        if t != o:
            p.write_text(t, encoding="utf-8")
            print("bumped", name)
        else:
            print("ok", name)


def rebuild_zero() -> None:
    src = DIR / "chit-zero.src.js"
    out = DIR / "chit-zero.js"
    cmd = f'npx --yes terser "{src}" -c -m -o "{out}"'
    print("terser…")
    subprocess.check_call(cmd, shell=True, cwd=str(ROOT))
    print("zero", out.stat().st_size)


def scp() -> None:
    if not KEY.is_file():
        print("no ssh key, skip scp", KEY)
        return
    scp_cmd = [
        "scp",
        "-i",
        str(KEY),
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ] + [str(f) for f in FILES if f.is_file()] + [REMOTE]
    print("scp", " ".join(str(x) for x in scp_cmd[-5:]))
    subprocess.check_call(scp_cmd)
    print("cdn uploaded")


def main() -> None:
    bump_html()
    rebuild_zero()
    scp()
    print("DONE", NEW)


if __name__ == "__main__":
    main()
