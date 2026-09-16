# -*- coding: utf-8 -*-
"""Upload perf-optimized homepage assets to CDN."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "docs" / "tilda-zero-main"
OUT = DIR / "_perf-opt" / "out"
KEY = Path.home() / ".ssh" / "chitatelstvo_deploy"
HOST = "194.87.201.99"
REMOTE = f"root@{HOST}:/var/www/chitatelstvo-assets/"
NEW = "20260916p"

WEBPS = [
    "cta-fairy-tale-bg.webp",
    "cta-fairy-tale-bg-m.webp",
    "pattern-meadow-books.webp",
    "hero-book-single.webp",
    "audience-kids.webp",
    "audience-parents.webp",
    "audience-family.webp",
    "audience-pace.webp",
]


def prepare() -> list[Path]:
    files: list[Path] = []
    for name in WEBPS:
        src = OUT / name
        if not src.is_file():
            raise SystemExit(f"missing {src}")
        dest = DIR / name
        shutil.copy2(src, dest)
        files.append(dest)
        print("asset", name, f"{src.stat().st_size/1024:.1f} KiB")

    # Serve minified CSS on CDN (keep readable source as chit-zero.css in repo,
    # but upload min as the live file).
    mini = OUT / "chit-zero.min.css"
    if not mini.is_file():
        raise SystemExit("missing min css")
    files.append(mini)
    files.append(DIR / "chit-zero.js")
    return files


def bump_html() -> None:
    for name in (
        "glavnaya.html",
        "00-tilda-zero-upload.html",
        "00-tilda-lite.html",
        "_preview-layout.html",
    ):
        p = DIR / name
        t = p.read_text(encoding="utf-8")
        t2 = re.sub(r"chit-zero\.js\?v=[^\"'&]+", f"chit-zero.js?v={NEW}", t)
        t2 = re.sub(r"chit-zero\.css\?v=[^\"'&]+", f"chit-zero.css?v={NEW}", t2)
        t2 = re.sub(r'(V=")[^"]+(")', rf"\g<1>{NEW}\2", t2)
        if t2 != t:
            p.write_text(t2, encoding="utf-8")
            print("bumped", name)


def bump_src_v() -> None:
    src = DIR / "chit-zero.src.js"
    t = src.read_text(encoding="utf-8")
    t2 = re.sub(r"var V = '[^']+'", f"var V = '{NEW}'", t, count=1)
    if t2 != t:
        src.write_text(t2, encoding="utf-8")
        print("src V", NEW)


def upload(files: list[Path]) -> None:
    # Rename min css to chit-zero.css on remote via scp temp name then ssh mv? 
    # Simpler: copy min to a temp local name chit-zero.css.upload
    upload_css = OUT / "chit-zero.css"
    shutil.copy2(OUT / "chit-zero.min.css", upload_css)
    payload = [f for f in files if f.name != "chit-zero.min.css"] + [upload_css]
    cmd = [
        "scp",
        "-i",
        str(KEY),
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ] + [str(f) for f in payload] + [REMOTE]
    print("scp", len(payload), "files")
    subprocess.check_call(cmd)
    print("cdn uploaded")


def main() -> None:
    bump_src_v()
    # rebuild zero after V bump
    subprocess.check_call(["python", str(ROOT / "scripts" / "_rebuild_zero.py")], cwd=str(ROOT))
    bump_html()
    files = prepare()
    upload(files)
    print("DONE", NEW)


if __name__ == "__main__":
    main()
