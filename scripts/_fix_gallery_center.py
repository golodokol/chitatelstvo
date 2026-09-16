# -*- coding: utf-8 -*-
"""Remove wind/garden gallery, bump VER, rebuild publish HTML."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CP = ROOT / "docs" / "course-pages"
SEO = CP / "course-seo.json"
GEN = ROOT / "scripts" / "_gen_course_pages.py"
NEW_VER = "20260916i"


def strip_gallery_seo() -> None:
    data = json.loads(SEO.read_text(encoding="utf-8"))
    lite = data["lite"]
    for key in ("wind", "garden"):
        lite[key].pop("gallery", None)
        lite[key].pop("galleryTitle", None)
        print("seo stripped", key)
    SEO.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bump_ver() -> None:
    text = GEN.read_text(encoding="utf-8")
    text2 = re.sub(r'VER = "[^"]+"', f'VER = "{NEW_VER}"', text, count=1)
    if text2 == text:
        raise SystemExit("VER not found")
    GEN.write_text(text2, encoding="utf-8")
    print("VER", NEW_VER)


def rebuild() -> None:
    subprocess.check_call(["python", str(GEN)], cwd=str(ROOT))


def main() -> None:
    strip_gallery_seo()
    bump_ver()
    rebuild()
    for slug in ("veter-v-ivah.html", "tainstvenny-sad.html"):
        for folder in ("tilda-publish", "tilda-redirects"):
            p = CP / folder / slug
            t = p.read_text(encoding="utf-8")
            print(slug, folder, "has_gallery", "ccl-gallery" in t, "has_ver", NEW_VER in t)


if __name__ == "__main__":
    main()
