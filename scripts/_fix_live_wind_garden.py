# -*- coding: utf-8 -*-
"""Make wind/garden pages show lesson steps + gallery reliably.

1) Deploy course-lite-* to CDN (live pages using CDN pick up content immediately)
2) Put steps/gallery into static HTML (visible even if JS fails)
3) Rebuild smaller Tilda pastes (CDN CSS/JS + embed JSON, not 97KB inline)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CP = ROOT / "docs" / "course-pages"
SEO_PATH = CP / "course-seo.json"
DATA_PATH = CP / "course-lite-data.js"
GEN = ROOT / "scripts" / "_gen_course_pages.py"
PUB = CP / "tilda-publish"
REDIR = CP / "tilda-redirects"
KEY = Path.home() / ".ssh" / "chitatelstvo_deploy"
HOST = "194.87.201.99"
USER = "root"
REMOTE_ASSETS = "/var/www/chitatelstvo-assets"
REMOTE_CP = f"{REMOTE_ASSETS}/course-pages"


def load_courses() -> dict:
    code = (
        "const fs=require('fs');const vm=require('vm');"
        "const ctx={window:{}};vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),ctx);"
        "process.stdout.write(JSON.stringify(ctx.window.CHIT_COURSE_LITE.courses));"
    )
    out = subprocess.check_output(["node", "-e", code, str(DATA_PATH)], text=True, encoding="utf-8")
    return json.loads(out)


def sync_seo(courses: dict) -> dict:
    seo = json.loads(SEO_PATH.read_text(encoding="utf-8"))
    for key in ("wind", "garden"):
        c = courses[key]
        block = seo["lite"][key]
        block["lessons"] = [
            (x["title"] if isinstance(x, dict) else x) for x in (c.get("lessons") or [])
        ]
        for field in (
            "lead",
            "intro",
            "aboutBook",
            "aboutAuthor",
            "aboutBookTitle",
            "aboutAuthorTitle",
            "lessonStepsTitle",
            "lessonStepsLead",
            "rewardsTitle",
            "rewardsLead",
            "galleryTitle",
        ):
            if c.get(field):
                block[field] = c[field]
        block["lessonSteps"] = c.get("lessonSteps") or []
        block["rewards"] = c.get("rewards") or []
        block["gallery"] = c.get("gallery") or []
        block["cover"] = c.get("cover") or block.get("cover")
    SEO_PATH.write_text(json.dumps(seo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("seo synced with lessonSteps/gallery")
    return seo


def patch_generator_static() -> None:
    text = GEN.read_text(encoding="utf-8")
    # Replace lite_shell to CDN mode (smaller paste)
    old_shell = '''def lite_shell(group: str) -> str:
    data = SEO["lite"][group]
    static = static_lite_html(group, data)
    override = lite_course_override_script(group)
    css, js = lite_inline_assets()
    # Данные и логика встроены; CDN-ссылки — запасной путь
    return f"""{TILDA_FIX}<style>
@import url("https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap");
{css}
</style>
<div id="chit-course-lite" data-group="{group}">
{static}
  <div id="chit-course-lite-app" hidden></div>
</div>
<script src="{API}/course-lite-data.js?v={VER}"></script>
{override}<script>
{js}
</script>
<!-- {esc(data["h1"])} · SEO static + interactive app v={VER} -->
"""
'''
    new_shell = '''def lite_shell(group: str) -> str:
    data = SEO["lite"][group]
    static = static_lite_html(group, data)
    override = lite_course_override_script(group)
    # Компактная вставка: CSS/JS с CDN (после scp), данные курса — embed.
    # Статика уже содержит «внутри урока» и галерею — видно даже без JS.
    return f"""{TILDA_FIX}<style>
@import url("https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap");
@import url("{API}/course-lite.css?v={VER}");
</style>
<div id="chit-course-lite" data-group="{group}">
{static}
  <div id="chit-course-lite-app" hidden></div>
</div>
<script src="{API}/course-lite-data.js?v={VER}"></script>
{override}<script src="{API}/course-lite.js?v={VER}"></script>
<!-- {esc(data["h1"])} · SEO static + interactive app v={VER} -->
"""
'''
    if old_shell in text:
        text = text.replace(old_shell, new_shell)
        print("lite_shell -> CDN mode")
    elif "CDN CSS/JS" in text or "course-lite.css?v={VER}" in text and "lite_inline_assets()" not in text.split("def lite_shell")[1][:800]:
        print("lite_shell already CDN-ish")
    else:
        # Force replace by marker
        if "def lite_shell(group: str) -> str:" in text and "lite_inline_assets()" in text:
            start = text.index("def lite_shell(group: str) -> str:")
            end = text.index("\ndef api_full_html", start)
            text = text[:start] + new_shell + text[end:]
            print("lite_shell force-replaced")
        else:
            print("WARN: could not patch lite_shell")

    marker = '    parts.append("".join(about))\n    parts.extend(\n        [\n            \'<section class="ccl-program" id="program">\','
    if "id=\"inside-lesson\"" in text:
        print("static steps already present")
    else:
        insert = '''    parts.append("".join(about))
    # Внутри урока / награды / галерея — в статике, чтобы было видно без JS
    if data.get("lessonSteps"):
        steps = []
        for i, step in enumerate(data["lessonSteps"], 1):
            img = step.get("image") or ""
            img_html = (
                f'<img class="ccl-step__img" src="{esc(img)}" alt="" width="320" height="200" loading="lazy" />'
                if img else ""
            )
            steps.append(
                f'<article class="ccl-step is-active">'
                f'<span class="ccl-step__n">{i}</span>{img_html}'
                f'<strong class="ccl-step__title">{esc(step.get("title", ""))}</strong>'
                f'<span class="ccl-step__text">{esc(step.get("text", ""))}</span>'
                f"</article>"
            )
        parts.append(
            f'<section class="ccl-steps" id="inside-lesson"><div class="ccl-steps__inner">'
            f'<p class="ccl-chapter"><em>внутри урока</em></p>'
            f'<h2>{esc(data.get("lessonStepsTitle") or "Внутри урока")}</h2>'
            + (f'<p class="ccl-steps__lead">{esc(data["lessonStepsLead"])}</p>' if data.get("lessonStepsLead") else "")
            + f'<div class="ccl-steps__track">{"".join(steps)}</div></div></section>'
        )
    if data.get("rewards"):
        cards = []
        for r in data["rewards"]:
            img = r.get("image") or ""
            img_html = (
                f'<img class="ccl-reward__img" src="{esc(img)}" alt="{esc(r.get("title", ""))}" width="240" height="240" loading="lazy" />'
                if img else ""
            )
            cards.append(
                f'<article class="ccl-reward">{img_html}'
                f'<h3>{esc(r.get("title", ""))}</h3><p>{esc(r.get("text", ""))}</p></article>'
            )
        parts.append(
            f'<section class="ccl-rewards" id="rewards"><div class="ccl-rewards__inner">'
            f'<p class="ccl-chapter"><em>награды</em></p>'
            f'<h2>{esc(data.get("rewardsTitle") or "Награды на пути")}</h2>'
            + (f'<p class="ccl-rewards__lead">{esc(data["rewardsLead"])}</p>' if data.get("rewardsLead") else "")
            + f'<div class="ccl-rewards__grid">{"".join(cards)}</div></div></section>'
        )
    if data.get("gallery"):
        figs = []
        for g in data["gallery"]:
            src = g.get("src") or ""
            figs.append(
                f'<figure class="ccl-gallery__item">'
                f'<img src="{esc(src)}" alt="{esc(g.get("alt", ""))}" width="640" height="400" loading="lazy" />'
                + (f'<figcaption>{esc(g["caption"])}</figcaption>' if g.get("caption") else "")
                + "</figure>"
            )
        grid_class = "ccl-gallery__grid ccl-gallery__grid--rich" if len(data["gallery"]) > 4 else "ccl-gallery__grid"
        parts.append(
            f'<section class="ccl-gallery" id="look"><div class="ccl-gallery__inner">'
            f'<p class="ccl-chapter"><em>из уроков</em></p>'
            f'<h2>{esc(data.get("galleryTitle") or "Как выглядит урок изнутри")}</h2>'
            f'<div class="{grid_class}">{"".join(figs)}</div></div></section>'
        )
    parts.extend(
        [
            '<section class="ccl-program" id="program">','''
        if marker not in text:
            raise SystemExit("marker for static insert not found")
        text = text.replace(marker, insert)
        print("static lessonSteps/rewards/gallery inserted")

    # bump version
    text = text.replace('VER = "20260915f"', 'VER = "20260915g"')
    text = text.replace('VER = "20260915e"', 'VER = "20260915g"')
    GEN.write_text(text, encoding="utf-8")
    print("generator patched")


def scp_cdn() -> None:
    if not KEY.is_file():
        raise SystemExit(f"missing ssh key: {KEY}")
    ssh = [
        "ssh", "-i", str(KEY), "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new",
        f"{USER}@{HOST}",
    ]
    scp = [
        "scp", "-i", str(KEY), "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new",
    ]
    subprocess.check_call(ssh + [f"mkdir -p {REMOTE_CP} {REMOTE_ASSETS}/lesson-ui"])
    files = [
        CP / "course-lite-data.js",
        CP / "course-lite.js",
        CP / "course-lite.css",
    ]
    subprocess.check_call(scp + [str(f) for f in files] + [f"{USER}@{HOST}:{REMOTE_CP}/"])
    # also lesson-ui if present
    ui = CP.parent / "images" / "lesson-ui"
    if not ui.is_dir():
        ui = ROOT / "docs" / "images" / "lesson-ui"
    if ui.is_dir():
        imgs = [str(p) for p in sorted(ui.glob("*")) if p.is_file()]
        if imgs:
            subprocess.check_call(scp + imgs + [f"{USER}@{HOST}:{REMOTE_ASSETS}/lesson-ui/"])
    print("CDN uploaded")


def rebuild() -> None:
    subprocess.check_call([sys.executable, str(GEN)], cwd=str(ROOT))
    PUB.mkdir(parents=True, exist_ok=True)
    for slug in ("veter-v-ivah", "tainstvenny-sad"):
        shutil.copyfile(REDIR / f"{slug}.html", PUB / f"{slug}.html")
    v = (PUB / "veter-v-ivah.html").read_text(encoding="utf-8")
    assert "Внутри урока" in v
    assert "lesson-ui/01-reading.png" in v
    assert "Дорожная история" in v
    assert "course-lite.js" in v
    assert "activateLiteApp" not in v  # not inlined
    print("publish OK", (PUB / "veter-v-ivah.html").stat().st_size)


def verify_cdn() -> None:
    import urllib.request
    for url in (
        "https://api.chitatelstvo.ru/assets/course-pages/course-lite-data.js",
        "https://api.chitatelstvo.ru/assets/course-pages/course-lite.js",
        "https://api.chitatelstvo.ru/assets/lesson-ui/01-reading.png",
    ):
        with urllib.request.urlopen(url, timeout=20) as r:
            body = r.read(2000)
            print(r.status, url, "bytes", len(body))
            if url.endswith("course-lite-data.js"):
                assert b"lessonSteps" in body or b"lesson-ui" in body
                print("  CDN data has lesson content")


def main() -> None:
    courses = load_courses()
    sync_seo(courses)
    patch_generator_static()
    scp_cdn()
    rebuild()
    verify_cdn()
    print("DONE — re-paste tilda-publish HTML OR hard-refresh live if CDN scripts already on page")


if __name__ == "__main__":
    main()
