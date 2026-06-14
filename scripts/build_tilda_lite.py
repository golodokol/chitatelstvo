#!/usr/bin/env python3
"""Build lite Zero Block paste + static CSS/JS on API."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs" / "tilda-zero-main"
VERSION = "20260609t"
API = "https://api.chitatelstvo.ru/assets"


def strip_header(text: str) -> str:
    return re.sub(r"^/\*[^*\n]*\*/\r?\n", "", text, count=1).strip()


def main() -> None:
    css = strip_header((DIR / "02-css.txt").read_text(encoding="utf-8"))
    js = strip_header((DIR / "03-js.txt").read_text(encoding="utf-8"))
    html_lines = (DIR / "01-html.txt").read_text(encoding="utf-8").splitlines()
    # skip first comment line; keep fonts + body
    body = "\n".join(html_lines[1:]).strip()

    (DIR / "chit-zero.css").write_text(css + "\n", encoding="utf-8")
    (DIR / "chit-zero.js").write_text(js + "\n", encoding="utf-8")

    lite = f"""<!-- Читательство · lite (CSS/JS грузятся с API, вставлять целиком) -->
{body.split('<div id="chit-main">', 1)[0].strip()}
<link rel="stylesheet" href="{API}/chit-zero.css?v={VERSION}">
<div id="chit-main">{body.split('<div id="chit-main">', 1)[1]}
<script src="{API}/chit-zero.js?v={VERSION}"></script>
"""
    # fix duplicate chit-main wrapper if split wrong
    if lite.count('id="chit-main"') > 1:
        fonts = "\n".join(
            line
            for line in html_lines[1:4]
            if line.strip().startswith("<link")
        )
        inner = "\n".join(html_lines[4:]).strip()
        lite = f"""<!-- Читательство · lite (CSS/JS грузятся с API, вставлять целиком) -->
{fonts}
<link rel="stylesheet" href="{API}/chit-zero.css?v={VERSION}">
{inner}
<script src="{API}/chit-zero.js?v={VERSION}"></script>
"""

    (DIR / "00-tilda-lite.html").write_text(lite, encoding="utf-8")
    print(f"chit-zero.css: {(DIR / 'chit-zero.css').stat().st_size} bytes")
    print(f"chit-zero.js: {(DIR / 'chit-zero.js').stat().st_size} bytes")
    print(f"00-tilda-lite.html: {(DIR / '00-tilda-lite.html').stat().st_size} bytes")


if __name__ == "__main__":
    main()
