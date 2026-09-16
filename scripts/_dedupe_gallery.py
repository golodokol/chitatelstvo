# -*- coding: utf-8 -*-
"""Remove gallery images that already appear in lessonSteps / rewards."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CP = ROOT / "docs" / "course-pages"
DATA = CP / "course-lite-data.js"
SEO = CP / "course-seo.json"
PUB = CP / "tilda-publish"
REDIR = CP / "tilda-redirects"
KEY = Path.home() / ".ssh" / "chitatelstvo_deploy"

# Only images NOT used in «Внутри урока» (01,02,03,05,07) or «Награды» (08,12,cabinet-trophies)
GALLERY = [
    {
        "src": "https://api.chitatelstvo.ru/assets/lesson-ui/04-proverbs.png",
        "alt": "Язык и образы",
        "caption": "Язык и образы",
    },
    {
        "src": "https://api.chitatelstvo.ru/assets/lesson-ui/09-letter.png",
        "alt": "Письмо герою",
        "caption": "Письмо герою",
    },
    {
        "src": "https://api.chitatelstvo.ru/assets/lesson-ui/10-trough.png",
        "alt": "Творческий лист",
        "caption": "Творческий лист",
    },
    {
        "src": "https://api.chitatelstvo.ru/assets/lesson-ui/11-sea.png",
        "alt": "Сцена из урока",
        "caption": "Сцена из урока",
    },
    {
        "src": "https://api.chitatelstvo.ru/assets/lesson-ui/cabinet-week-map.png",
        "alt": "Карта недели",
        "caption": "Личная страница",
    },
    {
        "src": "https://api.chitatelstvo.ru/assets/lesson-ui/cabinet-lesson.png",
        "alt": "Урок на платформе",
        "caption": "Кабинет урока",
    },
]
TITLE = "Ещё кадры с платформы"


def patch_data() -> None:
    node = r"""
const fs=require('fs'); const vm=require('vm');
const path=process.argv[1];
const gallery=JSON.parse(process.argv[2]);
const title=process.argv[3];
const ctx={window:{}};
vm.runInNewContext(fs.readFileSync(path,'utf8'),ctx);
const courses=ctx.window.CHIT_COURSE_LITE.courses;
for (const key of ['wind','garden']) {
  courses[key].gallery = gallery;
  courses[key].galleryTitle = title;
}
const header = [
  '/* eslint-disable */',
  'window.CHIT_COURSE_LITE = {',
  "  ASSETS: 'https://api.chitatelstvo.ru/assets',",
  "  STATIC: 'https://api.chitatelstvo.ru/static',",
  "  MAIN_URL: 'https://chitatelstvo.ru/#program',",
  "  HOME_URL: 'https://chitatelstvo.ru',",
  "  QUIZ_URL: 'https://chitatelstvo.ru/#quiz',",
  '  courses: '
].join('\n');
fs.writeFileSync(path, header + JSON.stringify(courses, null, 2) + '\n};\n');
console.log('gallery', courses.wind.gallery.length, courses.garden.gallery.length);
"""
    subprocess.check_call(
        ["node", "-e", node, str(DATA), json.dumps(GALLERY, ensure_ascii=False), TITLE],
        cwd=str(ROOT),
    )


def patch_seo() -> None:
    seo = json.loads(SEO.read_text(encoding="utf-8"))
    for key in ("wind", "garden"):
        seo["lite"][key]["gallery"] = GALLERY
        seo["lite"][key]["galleryTitle"] = TITLE
    SEO.write_text(json.dumps(seo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bump_ver() -> None:
    gen = ROOT / "scripts" / "_gen_course_pages.py"
    text = gen.read_text(encoding="utf-8")
    text2 = text.replace('VER = "20260915g"', 'VER = "20260915h"')
    if text2 == text:
        text2 = text.replace('VER = "20260915f"', 'VER = "20260915h"')
    gen.write_text(text2, encoding="utf-8")


def rebuild() -> None:
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / "_gen_course_pages.py")], cwd=str(ROOT))
    PUB.mkdir(parents=True, exist_ok=True)
    for slug in ("veter-v-ivah", "tainstvenny-sad"):
        shutil.copyfile(REDIR / f"{slug}.html", PUB / f"{slug}.html")
        t = (PUB / f"{slug}.html").read_text(encoding="utf-8")
        assert "01-reading.png" in t  # still in steps
        assert t.count("01-reading.png") == 1 or t.count("01-reading.png") <= 2  # embed+static ok, not 3+
        # gallery should not repeat chest/sloviki from rewards
        # allow once in rewards section + maybe embed
        assert "Ещё кадры с платформы" in t
        assert "04-proverbs.png" in t
        print(slug, "ok", (PUB / f"{slug}.html").stat().st_size)


def scp_cdn() -> None:
    if not KEY.is_file():
        print("no ssh key, skip scp")
        return
    host = "194.87.201.99"
    user = "root"
    remote = f"{user}@{host}:/var/www/chitatelstvo-assets/course-pages/"
    scp = [
        "scp",
        "-i",
        str(KEY),
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        str(DATA),
        str(CP / "course-lite.js"),
        str(CP / "course-lite.css"),
        remote,
    ]
    subprocess.check_call(scp)
    print("cdn updated")


def main() -> None:
    patch_data()
    patch_seo()
    bump_ver()
    rebuild()
    scp_cdn()
    print("DONE")


if __name__ == "__main__":
    main()
