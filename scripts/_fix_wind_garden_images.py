# -*- coding: utf-8 -*-
"""Fix wind/garden images + Дорожная история; upload lesson UI assets; rebuild publish pack."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "course-pages" / "course-lite-data.js"
SEO = ROOT / "docs" / "course-pages" / "course-seo.json"
PUB = ROOT / "docs" / "course-pages" / "tilda-publish"
REDIR = ROOT / "docs" / "course-pages" / "tilda-redirects"
IMG_OUT = ROOT / "docs" / "images" / "lesson-ui"
A = "https://api.chitatelstvo.ru/assets"
S = "https://api.chitatelstvo.ru/static"

LESSON_UI = {
    "01-reading.png": ROOT / "docs/presentations/lesson/01-reading.png",
    "02-quiz.png": ROOT / "docs/presentations/lesson/02-quiz.png",
    "03-emotions.png": ROOT / "docs/presentations/lesson/03-emotions.png",
    "04-proverbs.png": ROOT / "docs/presentations/lesson/04-proverbs.png",
    "05-tasks.png": ROOT / "docs/presentations/lesson/05-tasks.png",
    "06-retell-saltan.png": ROOT / "docs/presentations/lesson/06-retell-saltan.png",
    "07-retell-frog.png": ROOT / "docs/presentations/lesson/07-retell-frog.png",
    "08-chest-reward.png": ROOT / "docs/presentations/lesson/08-chest-reward.png",
    "09-letter.png": ROOT / "docs/presentations/lesson/09-letter.png",
    "10-trough.png": ROOT / "docs/presentations/lesson/10-trough.png",
    "11-sea.png": ROOT / "docs/presentations/lesson/11-sea.png",
    "12-sloviki.png": ROOT / "docs/presentations/lesson/12-sloviki.png",
    "cabinet-week-map.png": ROOT / "docs/presentations/cabinet/02-week-map.png",
    "cabinet-trophies.png": ROOT / "docs/presentations/cabinet/03-trophies.png",
    "cabinet-lesson.png": ROOT / "docs/presentations/cabinet/04-lesson.png",
    "cabinet-treasury.png": ROOT / "docs/presentations/cabinet/06-treasury.png",
}


def u(name: str) -> str:
    return f"{A}/lesson-ui/{name}"


SHARED_STEPS = [
    {
        "title": "Текст / видео",
        "text": "Короткий фрагмент книги или видео — вход в историю.",
        "image": u("01-reading.png"),
    },
    {
        "title": "Понимание сюжета",
        "text": "Вопросы: кто герой, чего хочет, что случилось.",
        "image": u("02-quiz.png"),
    },
    {
        "title": "Смысл и эмоции",
        "text": "Замечаем чувства героя, выбор и настроение текста.",
        "image": u("03-emotions.png"),
    },
    {
        "title": "Творчество",
        "text": "Задание дома: нарисовать, написать, сыграть сцену.",
        "image": u("05-tasks.png"),
    },
    {
        "title": "Пересказ",
        "text": "Коротко своими словами — о чём история и что важно.",
        "image": u("07-retell-frog.png"),
    },
]

SHARED_REWARDS = [
    {
        "title": "Словики",
        "text": "За ответы начисляются баллы-Словики — сразу видно прогресс.",
        "image": u("12-sloviki.png"),
    },
    {
        "title": "Сундук после урока",
        "text": "В финале открывается волшебный сундук с творческим заданием.",
        "image": u("08-chest-reward.png"),
    },
    {
        "title": "Путь героя",
        "text": "На личной странице растут уровни, бейджи и карта открытых уроков.",
        "image": u("cabinet-trophies.png"),
    },
]

SHARED_GALLERY = [
    {"src": u("04-proverbs.png"), "alt": "Язык и образы", "caption": "Язык и образы"},
    {"src": u("09-letter.png"), "alt": "Письмо герою", "caption": "Письмо герою"},
    {"src": u("10-trough.png"), "alt": "Творческий лист", "caption": "Творческий лист"},
    {"src": u("11-sea.png"), "alt": "Сцена из урока", "caption": "Сцена из урока"},
    {"src": u("cabinet-week-map.png"), "alt": "Карта недели", "caption": "Личная страница"},
    {"src": u("cabinet-lesson.png"), "alt": "Урок на платформе", "caption": "Кабинет урока"},
]


def copy_images() -> None:
    IMG_OUT.mkdir(parents=True, exist_ok=True)
    for name, src in LESSON_UI.items():
        if not src.is_file():
            raise SystemExit(f"missing image: {src}")
        dst = IMG_OUT / name
        shutil.copyfile(src, dst)
        print("copied", name, dst.stat().st_size)


def patch_course_object(obj: dict, *, is_wind: bool) -> None:
    obj["cover"] = f"{A}/course-cover-{'wind' if is_wind else 'garden'}.webp"
    obj["lessonSteps"] = SHARED_STEPS
    obj["rewards"] = SHARED_REWARDS
    obj["gallery"] = SHARED_GALLERY
    obj["galleryTitle"] = "Ещё кадры с платформы"
    obj["lessonStepsTitle"] = "Внутри урока"
    obj["lessonStepsLead"] = (
        "Короткая сессия 10–25 минут. Сначала работа с текстом — потом награда."
    )
    obj["rewardsTitle"] = "Награды на пути"
    obj["rewardsLead"] = (
        "После заданий — Словики. После урока — сундук. "
        "На личной странице виден весь путь героя."
    )
    if is_wind:
        lessons = obj.get("lessons") or []
        for item in lessons:
            title = item.get("title") if isinstance(item, dict) else item
            if title and "Дородн" in str(title):
                if isinstance(item, dict):
                    item["title"] = "Дорожная история"
                else:
                    # shouldn't happen
                    pass
        # ensure exact titles
        if lessons and isinstance(lessons[1], dict):
            lessons[1]["title"] = "Дорожная история"


def patch_data_js() -> None:
    # Prefer running via node extract/replace for wind/garden blocks using JSON rewrite
    text = DATA.read_text(encoding="utf-8")
    text = text.replace("Дородная история", "Дорожная история")
    # Absolute covers
    text = text.replace(
        '"cover": "course-cover-wind.jpg"',
        f'"cover": "{A}/course-cover-wind.webp"',
    )
    text = text.replace(
        '"cover": "course-cover-garden.jpg"',
        f'"cover": "{A}/course-cover-garden.webp"',
    )
    DATA.write_text(text, encoding="utf-8")

    # Rewrite steps/rewards/gallery via node for safety
    script = r"""
const fs=require('fs');
const path=process.argv[1];
const steps=JSON.parse(process.argv[2]);
const rewards=JSON.parse(process.argv[3]);
const gallery=JSON.parse(process.argv[4]);
const vm=require('vm');
const code=fs.readFileSync(path,'utf8');
const ctx={window:{}};
vm.runInNewContext(code,ctx);
const courses=ctx.window.CHIT_COURSE_LITE.courses;
for (const key of ['wind','garden']) {
  const c=courses[key];
  c.lessonSteps=steps;
  c.rewards=rewards;
  c.gallery=gallery;
  c.galleryTitle='Как выглядит урок изнутри';
  c.lessonStepsTitle='Внутри урока';
  c.lessonStepsLead='Короткая сессия 10–25 минут. Сначала работа с текстом — потом награда.';
  c.rewardsTitle='Награды на пути';
  c.rewardsLead='После заданий — Словики. После урока — сундук. На личной странице виден весь путь героя.';
  if (key==='wind' && Array.isArray(c.lessons)) {
    c.lessons.forEach(l=>{
      if (l && typeof l==='object' && String(l.title||'').includes('Дородн')) l.title='Дорожная история';
      if (l && typeof l==='object' && l.title==='Дородная история') l.title='Дорожная история';
    });
    if (c.lessons[1] && typeof c.lessons[1]==='object') c.lessons[1].title='Дорожная история';
  }
}
// rebuild file preserving header constants
const header = `/* eslint-disable */
window.CHIT_COURSE_LITE = {
  ASSETS: 'https://api.chitatelstvo.ru/assets',
  STATIC: 'https://api.chitatelstvo.ru/static',
  MAIN_URL: 'https://chitatelstvo.ru/#program',
  HOME_URL: 'https://chitatelstvo.ru',
  QUIZ_URL: 'https://chitatelstvo.ru/#quiz',
  courses: `;
fs.writeFileSync(path, header + JSON.stringify(courses, null, 2) + '\n};\n');
console.log('rewrote courses', Object.keys(courses).join(','));
console.log('wind2', courses.wind.lessons[1].title);
console.log('gallery', courses.wind.gallery.length);
"""
    subprocess.check_call(
        [
            "node",
            "-e",
            script,
            str(DATA),
            json.dumps(SHARED_STEPS, ensure_ascii=False),
            json.dumps(SHARED_REWARDS, ensure_ascii=False),
            json.dumps(SHARED_GALLERY, ensure_ascii=False),
        ],
        cwd=str(ROOT),
    )


def patch_seo() -> None:
    seo = json.loads(SEO.read_text(encoding="utf-8"))
    wind = seo["lite"]["wind"]
    lessons = wind.get("lessons") or []
    wind["lessons"] = [
        "Дорожная история" if "Дородн" in str(t) else t for t in lessons
    ]
    if len(wind["lessons"]) >= 2:
        wind["lessons"][1] = "Дорожная история"
    SEO.write_text(json.dumps(seo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def harden_imgurl_and_static() -> None:
    js = ROOT / "docs/course-pages/course-lite.js"
    text = js.read_text(encoding="utf-8")
    old = """  function imgUrl(src) {
    if (!src) return '';
    if (/^https?:\\/\\//i.test(src)) return src;
    if (src.indexOf('/early/') === 0) return (D.STATIC || 'https://api.chitatelstvo.ru/static') + src;
    return D.ASSETS + '/' + src.replace(/^\\//, '');
  }"""
    new = """  function imgUrl(src) {
    if (!src) return '';
    if (/^https?:\\/\\//i.test(src)) return src;
    var assets = (D && D.ASSETS) || 'https://api.chitatelstvo.ru/assets';
    var staticBase = (D && D.STATIC) || 'https://api.chitatelstvo.ru/static';
    if (src.indexOf('/early/') === 0) return staticBase + src;
    if (src.indexOf('/static/') === 0) return 'https://api.chitatelstvo.ru' + src;
    return assets + '/' + String(src).replace(/^\\//, '');
  }"""
    if old in text:
        text = text.replace(old, new)
        js.write_text(text, encoding="utf-8")
        print("hardened imgUrl")
    else:
        print("imgUrl pattern not exact; skip or already patched")


def patch_static_cover() -> None:
    gen = ROOT / "scripts/_gen_course_pages.py"
    text = gen.read_text(encoding="utf-8")
    needle = 'parts.append(f\'<div class="ccl-chips">{chips}</div>\')\n    parts.append("</div></div>")'
    insert = (
        'parts.append(f\'<div class="ccl-chips">{chips}</div>\')\n'
        '    parts.append("</div>")\n'
        '    cover = data.get("cover") or COVER_BY_GROUP.get(group)\n'
        '    if cover:\n'
        '        src = cover if str(cover).startswith("http") else f"{ASSETS}/{cover}"\n'
        '        parts.append(\n'
        '            f\'<div class="ccl-hero__media">'
        f'<img src="{{esc(src)}}" alt="{{esc(data[\'h1\'])}}" width="800" height="500" loading="eager" />'
        "</div>\"\n"
        "        )\n"
        '    parts.append("</div>")'
    )
    # Simpler approach: rewrite a known block carefully via python below
    print("static cover patch handled in ensure_static_cover()")


def ensure_static_cover() -> None:
    gen = ROOT / "scripts/_gen_course_pages.py"
    text = gen.read_text(encoding="utf-8")
    if "ccl-hero__media" in text and "static_lite_html" in text:
        # already may exist in full pages; check lite
        if "cover = data.get(\"cover\")" in text or "hero cover for lite" in text:
            print("static cover already present")
            return
    marker = '    parts.append(f\'<div class="ccl-chips">{chips}</div>\')\n    if not is_early:\n        parts.append(\n            \'<div class="ccl-actions">\'\n'
    # Find closing of hero copy more reliably
    old = '''    parts.append(f'<div class="ccl-chips">{chips}</div>')
    parts.append("</div></div>")
    if is_early:
        parts.append("</div>")
    parts.append("</section>")'''
    new = '''    parts.append(f'<div class="ccl-chips">{chips}</div>')
    parts.append("</div>")
    # hero cover for lite (absolute URL so images show even before JS)
    cover_name = data.get("cover") or COVER_BY_GROUP.get(group, "")
    if cover_name:
        cover_src = cover_name if str(cover_name).startswith("http") else f"{ASSETS}/{cover_name}"
        parts.append(
            f'<div class="ccl-hero__media"><img src="{esc(cover_src)}" alt="{esc(data["h1"])}" '
            f'width="800" height="500" loading="eager" /></div>'
        )
    parts.append("</div>")
    if is_early:
        parts.append("</div>")
    parts.append("</section>")'''
    if old not in text:
        raise SystemExit("static_lite_html hero close block not found")
    gen.write_text(text.replace(old, new), encoding="utf-8")
    print("patched static_lite_html cover")


def scp_images() -> None:
    host = "194.87.201.99"
    user = "root"
    key = Path.home() / ".ssh" / "chitatelstvo_deploy"
    remote_dir = "/var/www/chitatelstvo-assets/lesson-ui"
    if not key.is_file():
        print("no ssh key — skip scp; images stay in docs/images/lesson-ui for deploy")
        return
    ssh = [
        "ssh",
        "-i",
        str(key),
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"{user}@{host}",
    ]
    try:
        subprocess.check_call(ssh + [f"mkdir -p {remote_dir}"])
        scp = [
            "scp",
            "-i",
            str(key),
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=accept-new",
            "-r",
        ]
        # copy files into remote dir
        files = [str(p) for p in sorted(IMG_OUT.glob("*")) if p.is_file()]
        subprocess.check_call(scp + files + [f"{user}@{host}:{remote_dir}/"])
        print("scp OK", len(files), "files ->", remote_dir)
    except Exception as e:
        print("scp failed:", e)


def rebuild() -> None:
    subprocess.check_call([sys.executable, str(ROOT / "scripts/_gen_course_pages.py")], cwd=str(ROOT))
    PUB.mkdir(parents=True, exist_ok=True)
    for slug in ("veter-v-ivah", "tainstvenny-sad"):
        shutil.copyfile(REDIR / f"{slug}.html", PUB / f"{slug}.html")
        print("publish", slug)


def main() -> None:
    copy_images()
    patch_data_js()
    patch_seo()
    harden_imgurl_and_static()
    ensure_static_cover()
    scp_images()
    rebuild()
    # verify
    t = (PUB / "veter-v-ivah.html").read_text(encoding="utf-8")
    assert "Дорожная история" in t
    assert "Дородная" not in t
    assert "lesson-ui/01-reading.png" in t
    assert "course-cover-wind.webp" in t
    print("VERIFY OK")


if __name__ == "__main__":
    main()
