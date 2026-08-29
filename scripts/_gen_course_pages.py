#!/usr/bin/env python3
"""Generate Tilda Zero Block shells with static SEO HTML for course pages."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "docs" / "course-pages"
REDIR = ROOT / "tilda-redirects"
SEO = json.loads((ROOT / "course-seo.json").read_text(encoding="utf-8"))
VER = "20260828c"
API = "https://api.chitatelstvo.ru/assets/course-pages"
SITE = SEO["site"]
ASSETS = SEO["assets"]
ORG = SEO["org"]

# Обложки для og:image (WebP на CDN)
COVER_BY_GROUP = {
    "grade-1": "course-cover-grade-1.webp",
    "grade-2": "course-cover-grade-2.webp",
    "grade-3": "course-cover-grade-3.webp",
    "grade-4": "course-cover-grade-4.webp",
    "extra-6-8": "course-cover-extra-6-8.webp",
    "extra-9-11": "course-cover-extra-9-11.webp",
    "early-letters": "course-cover-letters.webp",
    "early-stories": "course-cover-stories.webp",
    "wind": "course-cover-wind.webp",
    "garden": "course-cover-garden.webp",
    "rus-6-9": "course-cover-rus-6-9.webp",
    "rus-10-12": "course-cover-rus-10-12.webp",
}

DEFAULT_FAQ_FULL = [
    {
        "q": "Когда можно начать?",
        "a": "В любой день. В программе 8 сказок (2 блока по 4). Можно взять одну сказку, блок или всю программу.",
    },
    {
        "q": "Что будет после оплаты?",
        "a": "На email придёт ссылка на личную страницу — там открытые сказки, баллы и прогресс.",
    },
    {
        "q": "Можно ли начать с одной сказки?",
        "a": "Да. Тариф «Разовое» — 799 ₽: одна сказка на платформе. Живые занятия — на тарифе «С преподавателем».",
    },
    {
        "q": "Чем отличаются тарифы?",
        "a": "Индивидуальное — 1 990 ₽ за 4 сказки, свой темп. С преподавателем — 4 990 ₽: та же основа плюс живые встречи в мини-группе.",
    },
]

DEFAULT_FAQ_LITE = [
    {
        "q": "Когда можно начать?",
        "a": "В любой день — уроки открываются на платформе сразу после оплаты или по расписанию модуля.",
    },
    {
        "q": "Что будет после оплаты?",
        "a": "На email придёт ссылка на личную страницу прогресса с доступом к урокам модуля.",
    },
    {
        "q": "Есть ли пробный урок?",
        "a": "У ранних курсов и части программ — да. На главной и на странице курса есть кнопка «Пробный урок бесплатно».",
    },
    {
        "q": "Чем отличаются тарифы?",
        "a": "Разовое — 799 ₽ за один урок. Индивидуальное — 1 990 ₽ за модуль. С преподавателем — 4 990 ₽ с живыми встречами.",
    },
]


def cover_url(group: str) -> str:
    name = COVER_BY_GROUP.get(group, "logo-chitatelstvo.png")
    return f"{ASSETS}/{name}"


def seo_title(data: dict) -> str:
    return data.get("seoTitle") or f"{data['h1']} — {ORG}"


def faq_items(group: str, data: dict) -> list[dict]:
    raw = data.get("faq")
    if raw:
        out = []
        for item in raw:
            if isinstance(item, dict) and item.get("q") and item.get("a"):
                out.append({"q": item["q"], "a": item["a"]})
        if out:
            return out
    if group.startswith("early-") or group in {"wind", "garden", "rus-6-9", "rus-10-12"}:
        return list(DEFAULT_FAQ_LITE)
    return list(DEFAULT_FAQ_FULL)


def offers_for(group: str) -> list[dict]:
    is_early = group.startswith("early-")
    self_label = "8 уроков" if is_early else ("4 урока" if group in {"wind", "garden", "rus-6-9", "rus-10-12"} else "4 сказки")
    return [
        {
            "@type": "Offer",
            "name": "Разовое",
            "price": "799",
            "priceCurrency": "RUB",
            "availability": "https://schema.org/InStock",
            "url": f"{SITE}/#program",
            "category": "1 урок" if is_early or group in {"wind", "garden", "rus-6-9", "rus-10-12"} else "1 сказка",
        },
        {
            "@type": "Offer",
            "name": "Индивидуальное",
            "price": "1990",
            "priceCurrency": "RUB",
            "availability": "https://schema.org/InStock",
            "url": f"{SITE}/#program",
            "category": self_label,
        },
        {
            "@type": "Offer",
            "name": "С преподавателем",
            "price": "4990",
            "priceCurrency": "RUB",
            "availability": "https://schema.org/InStock",
            "url": f"{SITE}/#program",
            "category": f"{self_label} + встречи",
        },
    ]


def json_ld_scripts(group: str, data: dict, url: str) -> str:
    title = seo_title(data)
    faqs = faq_items(group, data)
    course = {
        "@context": "https://schema.org",
        "@type": "Course",
        "name": data["h1"],
        "description": data["description"],
        "provider": {
            "@type": "Organization",
            "name": ORG,
            "url": SITE,
            "email": "info@chitatelstvo.ru",
        },
        "url": url,
        "image": cover_url(group),
        "inLanguage": "ru",
        "isAccessibleForFree": False,
        "audience": {
            "@type": "EducationalAudience",
            "audienceType": data.get("age", ""),
            "educationalRole": "student",
        },
        "offers": offers_for(group),
        "hasCourseInstance": {
            "@type": "CourseInstance",
            "courseMode": "online",
            "courseWorkload": data.get("age", ""),
        },
    }
    faq_page = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {"@type": "Answer", "text": item["a"]},
            }
            for item in faqs
        ],
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Главная", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "Программы", "item": f"{SITE}/programmy"},
            {"@type": "ListItem", "position": 3, "name": data["h1"], "item": url},
        ],
    }
    # title unused in LD but kept for parity with OG
    _ = title
    chunks = []
    for payload in (course, faq_page, breadcrumb):
        chunks.append(
            '<script type="application/ld+json">'
            + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
            + "</script>"
        )
    return "".join(chunks)


def og_and_meta_tags(group: str, data: dict, url: str) -> str:
    title = seo_title(data)
    desc = data["description"]
    image = cover_url(group)
    return "\n".join(
        [
            f'  <title>{esc(title)}</title>',
            f'  <meta name="description" content="{esc(desc)}">',
            f'  <meta name="keywords" content="{esc(data.get("keywords") or "")}">',
            f'  <link rel="canonical" href="{esc(url)}">',
            f'  <meta property="og:type" content="website">',
            f'  <meta property="og:site_name" content="{esc(ORG)}">',
            f'  <meta property="og:locale" content="ru_RU">',
            f'  <meta property="og:title" content="{esc(title)}">',
            f'  <meta property="og:description" content="{esc(desc)}">',
            f'  <meta property="og:url" content="{esc(url)}">',
            f'  <meta property="og:image" content="{esc(image)}">',
            f'  <meta property="og:image:alt" content="{esc(data["h1"])}">',
            f'  <meta name="twitter:card" content="summary_large_image">',
            f'  <meta name="twitter:title" content="{esc(title)}">',
            f'  <meta name="twitter:description" content="{esc(desc)}">',
            f'  <meta name="twitter:image" content="{esc(image)}">',
        ]
    )


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def li_items(items: list) -> str:
    return "".join(f"<li>{esc(x)}</li>" for x in items)


def json_ld_course(data: dict, url: str) -> str:
    """Backward-compatible wrapper — prefer json_ld_scripts. """
    group = data.get("_group") or ""
    return json_ld_scripts(group, data, url)


FIX_JS = (ROOT / "chit-tilda-fix.inline.js").read_text(encoding="utf-8").strip()
FIX_CSS = (ROOT / "chit-tilda-fix.inline.css").read_text(encoding="utf-8").strip()

FULL = [
    ("1-klass.html", "grade-1"),
    ("2-klass.html", "grade-2"),
    ("3-klass.html", "grade-3"),
    ("4-klass.html", "grade-4"),
    ("6-8-let.html", "extra-6-8"),
    ("9-11-let.html", "extra-9-11"),
]

LITE = [
    ("bukvy-ozhivayut.html", "early-letters"),
    ("pervye-istorii.html", "early-stories"),
    ("veter-v-ivah.html", "wind"),
    ("tainstvenny-sad.html", "garden"),
    ("russkie-skazki-6-9.html", "rus-6-9"),
    ("russkie-skazki-10-12.html", "rus-10-12"),
]

TILDA_FIX = (
    "<!-- Читательство · страница курса для Zero Block\n"
    "     Вставить целиком в HTML-элемент Zero Block → Опубликовать.\n"
    "     Ширина артборда: 1200, высота: авто, выравнивание: сверху.\n"
    "     SEO: текст ниже виден поисковикам; после загрузки JS — интерактив.\n"
    "-->\n"
    f"<script>{FIX_JS}</script>\n"
    f'<style id="chit-course-tilda">{FIX_CSS}'
    "#chit-course-root,#chit-course-lite{width:100%!important;max-width:100%!important;"
    "box-sizing:border-box;margin:0;padding:0;font-family:Manrope,Nunito,system-ui,sans-serif;"
    "color:#2E2A38;background:#fff;line-height:1.65;font-size:17px}"
    "#chit-course-root *,#chit-course-lite *,#chit-course-root *::before,#chit-course-lite *::before,"
    "#chit-course-root *::after,#chit-course-lite *::after{box-sizing:border-box}"
    ".tn-atom__html #chit-course-root,.tn-atom__html #chit-course-lite{display:block!important;width:100%!important}"
    "#chit-course-app[hidden],#chit-course-lite-app[hidden],#chit-course-static[hidden]{display:none!important}"
    "</style>\n"
)


def static_footer_full() -> str:
    courses = (
        ("1-klass", "1 класс"),
        ("2-klass", "2 класс"),
        ("3-klass", "3 класс"),
        ("4-klass", "4 класс"),
        ("6-8-let", "Внеклассное 6–8 лет"),
        ("9-11-let", "Внеклассное 9–11 лет"),
        ("bukvy-ozhivayut", "Буквы оживают"),
        ("pervye-istorii", "Первые истории"),
        ("programmy", "Все программы"),
    )
    course_lis = "".join(
        f'<li><a href="{SITE}/{slug}">{esc(label)}</a></li>' for slug, label in courses
    )
    return (
        '<footer class="cc-footer">'
        '<div class="cc-footer__inner">'
        f'<img class="cc-footer__logo" src="{ASSETS}/logo-chitatelstvo.png" alt="{esc(ORG)}" width="256" height="256">'
        f'<p class="cc-footer__warm">С теплом, команда {esc(ORG)}</p>'
        '<nav class="cc-footer__courses" aria-label="Все курсы">'
        '<p class="cc-footer__courses-title">Курсы Читательства</p>'
        f'<ul class="cc-footer__courses-list">{course_lis}</ul>'
        "</nav>"
        '<nav class="cc-footer__legal" aria-label="Юридическая информация">'
        '<a href="https://api.chitatelstvo.ru/legal/politika">Политика</a>'
        '<a href="https://api.chitatelstvo.ru/legal/oferta">Оферта</a>'
        '<a href="https://api.chitatelstvo.ru/legal/rekvizity">Реквизиты</a>'
        "</nav>"
        '<p class="cc-footer__contact">'
        '<a href="mailto:info@chitatelstvo.ru">info@chitatelstvo.ru</a> · '
        f'<a href="{SITE}">chitatelstvo.ru</a>'
        "</p>"
        '<p class="cc-footer__seller">ИП Рощина Ольга Владимировна · ИНН 231150315327</p>'
        f'<p class="cc-footer__copy">© {esc(ORG)}</p>'
        "</div></footer>"
    )


def static_footer_lite() -> str:
    return (
        '<footer class="ccl-footer">'
        '<div class="ccl-footer__inner">'
        f'<img class="ccl-footer__logo" src="{ASSETS}/logo-chitatelstvo.png" alt="{esc(ORG)}" width="180" height="48">'
        f'<p class="ccl-footer__warm">С теплом, команда {esc(ORG)}</p>'
        '<nav class="ccl-footer__legal" aria-label="Юридическая информация">'
        '<a href="https://api.chitatelstvo.ru/legal/politika">Политика</a>'
        '<a href="https://api.chitatelstvo.ru/legal/oferta">Оферта</a>'
        '<a href="https://api.chitatelstvo.ru/legal/rekvizity">Реквизиты</a>'
        "</nav>"
        '<p class="ccl-footer__contact">'
        '<a href="mailto:info@chitatelstvo.ru">info@chitatelstvo.ru</a> · '
        f'<a href="{SITE}">chitatelstvo.ru</a>'
        "</p>"
        '<p class="ccl-footer__seller">ИП Рощина Ольга Владимировна · ИНН 231150315327</p>'
        f'<p class="ccl-footer__copy">© {esc(ORG)}</p>'
        "</div></footer>"
    )


def static_full_html(group: str, data: dict) -> str:
    url = f"{SITE}/{data['slug']}"
    b1 = data["program"]["block1"]
    b2 = data["program"]["block2"]
    return (
        f'<article id="chit-course-static" class="cc-static" itemscope itemtype="https://schema.org/Course">'
        f'<meta itemprop="name" content="{esc(data["h1"])}">'
        f'<meta itemprop="description" content="{esc(data["description"])}">'
        f'<link itemprop="url" href="{esc(url)}">'
        '<header class="cc-header"><div class="cc-header__inner">'
        f'<a class="cc-logo" href="{SITE}"><img src="{ASSETS}/logo-chitatelstvo.png" alt="{esc(ORG)}"></a>'
        '<nav class="cc-nav" aria-label="О школе">'
        f'<a href="{SITE}/#programs">Программы</a>'
        f'<a href="{SITE}/#timeline">О школе</a>'
        f'<a href="{SITE}/#platform">Платформа</a>'
        f'<a href="{SITE}/#proof">Отзывы</a>'
        f'<a href="{SITE}/#lead">Консультация</a>'
        "</nav>"
        '<a class="cc-header-cta" href="#enroll">Записаться</a>'
        "</div></header>"
        '<section class="cc-banner" id="about">'
        '<div class="cc-banner__inner">'
        f'<span class="cc-banner__tag">{esc(data["badge"])}</span> '
        f'<span class="cc-banner__tag cc-banner__tag--ghost">{esc(data["age"])}</span>'
        f'<h1 itemprop="headline">{esc(data["h1"])}</h1>'
        f'<p class="cc-banner__lead">{esc(data["lead"])}</p>'
        f"<p>{esc(data['intro'])}</p>"
        "<p><strong>8 сказок · старт в любой день</strong> · видео и задания на платформе</p>"
        "</div></section>"
        '<section class="cc-section cc-section--pale" id="program-list">'
        '<div class="cc-section__inner">'
        "<h2>8 сказок — что читаем</h2>"
        "<p>Два блока по 4 сказки. Можно начать с любого блока.</p>"
        "<h3>Блок 1 · сказки 1–4</h3>"
        f"<ol>{li_items(b1)}</ol>"
        "<h3>Блок 2 · сказки 5–8</h3>"
        f"<ol>{li_items(b2)}</ol>"
        "</div></section>"
        '<section class="cc-section cc-section--outcome" id="outcome">'
        '<div class="cc-section__inner">'
        f"<h2>{esc(data['outcomeTitle'])}</h2>"
        f"<p>{esc(data['outcomeLead'])}</p>"
        f'<ul class="cc-outcome-list">{li_items(data["outcome"])}</ul>'
        "</div></section>"
        '<section class="cc-section cc-section--white" id="for-whom">'
        '<div class="cc-section__inner">'
        "<h2>Этот курс для вас, если</h2>"
        f"<ul>{li_items(data['forWhom'])}</ul>"
        "</div></section>"
        '<section class="cc-section cc-section--pale" id="tariffs">'
        '<div class="cc-section__inner">'
        "<h2>Тарифы</h2>"
        "<ul>"
        "<li><strong>Разовое</strong> — 799 ₽ · 1 сказка на платформе</li>"
        "<li><strong>Индивидуальное</strong> — 1 990 ₽ · 4 сказки (499 ₽ за сказку)</li>"
        "<li><strong>С преподавателем</strong> — 4 990 ₽ · 4 сказки и живые встречи (1 248 ₽ за сказку)</li>"
        "</ul>"
        "</div></section>"
        '<section class="cc-section cc-section--deep" id="enroll">'
        '<div class="cc-section__inner">'
        "<h2>Записаться на курс</h2>"
        f"<p>Выберите формат и оформите запись на этой странице или на <a href=\"{SITE}/#program\">главной</a>.</p>"
        '<p><a class="cc-btn" href="#enroll">Записаться</a></p>'
        "</div></section>"
        + static_footer_full()
        + "</article>"
        + json_ld_scripts(group, data, url)
    )


def static_lite_html(group: str, data: dict) -> str:
    url = f"{SITE}/{data['slug']}"
    chips = "".join(f'<span class="ccl-chip">{esc(c)}</span>' for c in data.get("chips", []))
    lessons = "".join(
        f'<li><span class="ccl-lesson__n">{i + 1}</span> {esc(t if isinstance(t, str) else t.get("title", ""))}</li>'
        for i, t in enumerate(data.get("lessons", []))
    )
    is_early = group.startswith("early-")
    price = (
        "Разовое — 799 ₽ · самостоятельное прохождение курса — 1 990 ₽ за 8 уроков.<br>С преподавателем — 4 990 ₽."
        if is_early
        else "Разовое — 799 ₽ · самостоятельное прохождение курса — 1 990 ₽ за 4 урока.<br>С преподавателем — 4 990 ₽."
    )
    hero_class = "ccl-hero ccl-hero--brand" if is_early else "ccl-hero"
    parts = [
        f'<article id="chit-course-static" class="ccl-static" itemscope itemtype="https://schema.org/Course">',
        f'<meta itemprop="name" content="{esc(data["h1"])}">',
        f'<meta itemprop="description" content="{esc(data["description"])}">',
        f'<link itemprop="url" href="{esc(url)}">',
        '<header class="ccl-header"><div class="ccl-header__inner">',
        f'<a class="ccl-logo" href="{SITE}"><img src="{ASSETS}/logo-chitatelstvo.png" alt="{esc(ORG)}"></a>',
        '<nav class="ccl-nav" aria-label="Разделы">',
        '<a href="#program">Программа</a>',
        '<a href="#outcome">После курса</a>',
        '<a href="#enroll">Запись</a>',
        "</nav>",
        f'<a class="ccl-header-cta" href="{SITE}/#program">Записаться</a>',
        "</div></header>",
        f'<section class="{hero_class}" id="about">',
    ]
    if is_early:
        parts.append('<div class="ccl-hero__frame"><div class="ccl-hero__pattern" aria-hidden="true"></div>')
    parts.append('<div class="ccl-hero__grid"><div class="ccl-hero__copy">')
    if is_early:
        age = f'<span class="ccl-age">{esc(data["age"])}</span>' if data.get("age") else ""
        parts.append(
            f'<div class="ccl-hero__tags"><span class="ccl-badge">{esc(data["badge"])}</span>'
            f"{age}</div>"
        )
    else:
        age = f' <span class="ccl-age">{esc(data["age"])}</span>' if data.get("age") else ""
        parts.append(
            f'<span class="ccl-badge">{esc(data["badge"])}</span>{age}'
        )
    parts.append(f'<h1 itemprop="headline">{esc(data["h1"])}</h1>')
    if data.get("subtitle"):
        parts.append(f'<p class="ccl-subtitle">{esc(data["subtitle"])}</p>')
    lead = esc(data["lead"]).replace("\n", "<br>")
    parts.append(f'<p class="ccl-lead">{lead}</p>')
    if not is_early:
        parts.append(f'<p class="ccl-intro">{esc(data["intro"])}</p>')
    parts.append(f'<div class="ccl-chips">{chips}</div>')
    parts.append("</div></div>")
    if is_early:
        parts.append("</div>")
    parts.append("</section>")
    if data.get("promise"):
        parts.append(
            f'<section class="ccl-promise"><div class="ccl-promise__inner">'
            f'<p>{esc(data["promise"])}</p></div></section>'
        )
    if data.get("slogan"):
        parts.append(
            f'<section class="ccl-slogan" aria-label="Слоган"><div class="ccl-slogan__inner">'
            f'<p class="ccl-slogan__text">{esc(data["slogan"])}</p></div></section>'
        )
    if data.get("why"):
        parts.append(
            f'<section class="ccl-why" id="why"><div class="ccl-why__inner">'
            f'<h2>{esc(data.get("whyTitle") or "Почему выбирают этот курс")}</h2>'
            f"<ul>{li_items(data['why'])}</ul></div></section>"
        )
    parts.extend(
        [
            '<section class="ccl-program" id="program">',
            '<div class="ccl-program__inner">',
            "<h2>Что будем проходить</h2>",
            f'<ol class="ccl-lessons">{lessons}</ol>',
            "</div></section>",
        ]
    )
    if data.get("childGets") or data.get("parentGets"):
        gets = ['<section class="ccl-gets" id="gets"><div class="ccl-gets__inner">']
        if data.get("childGets"):
            gets.append(
                "<h2>Что получит ребёнок</h2>"
                f"<ul>{li_items(data['childGets'])}</ul>"
            )
        if data.get("parentGets"):
            gets.append(
                "<h2>Что получите вы</h2>"
                f"<ul>{li_items(data['parentGets'])}</ul>"
            )
        gets.append("</div></section>")
        parts.append("".join(gets))
    parts.extend(
        [
            '<section class="ccl-outcome" id="outcome">',
            '<div class="ccl-outcome__inner">',
            f"<h2>{esc(data['outcomeTitle'])}</h2>",
            f'<p class="ccl-outcome__lead">{esc(data["outcomeLead"])}</p>',
            f'<ul class="ccl-outcome__list">{li_items(data["outcome"])}</ul>',
            "</div></section>",
            (
                f'<section class="ccl-enroll ccl-enroll--fares" id="tariffs">'
                f'<div class="ccl-enroll__inner">'
                f"<h2>Выберите формат</h2>"
                f"<p>Форматы этого модуля · 1 990 ₽ — за 8 уроков</p>"
                f'<div class="ccl-fares" role="list">'
                f'<article class="ccl-fare"><h3 class="ccl-fare__name">Разовое</h3>'
                f'<p class="ccl-fare__price">799 ₽</p><p class="ccl-fare__sub">1 урок</p>'
                f'<ul class="ccl-fare__feats"><li class="is-yes">1 урок модуля на платформе</li>'
                f'<li class="is-yes">Квест и задания</li><li class="is-yes">Личная страница прогресса</li>'
                f'<li class="is-no">Модуль из 8 уроков</li><li class="is-no">Живые встречи</li></ul></article>'
                f'<article class="ccl-fare ccl-fare--rec"><span class="ccl-fare__badge">Рекомендуем</span>'
                f'<h3 class="ccl-fare__name">Индивидуальное</h3><p class="ccl-fare__price">1 990 ₽</p>'
                f'<p class="ccl-fare__sub">8 уроков модуля · свой темп</p>'
                f'<ul class="ccl-fare__feats"><li class="is-yes">8 уроков модуля на платформе</li>'
                f'<li class="is-yes">Квест и задания</li><li class="is-yes">Личная страница прогресса</li>'
                f'<li class="is-yes">Модуль целиком</li><li class="is-no">Живые встречи</li></ul></article>'
                f'<article class="ccl-fare"><h3 class="ccl-fare__name">С преподавателем</h3>'
                f'<p class="ccl-fare__price">4 990 ₽</p><p class="ccl-fare__sub">8 уроков модуля + 4 встречи</p>'
                f'<ul class="ccl-fare__feats"><li class="is-yes">8 уроков модуля на платформе</li>'
                f'<li class="is-yes">Квест и задания</li><li class="is-yes">Личная страница прогресса</li>'
                f'<li class="is-yes">Модуль целиком</li><li class="is-yes">Живые встречи</li></ul></article>'
                f"</div>"
                + (
                    f'<p class="ccl-enroll__trial"><a class="ccl-btn ccl-btn--ghost" href="#trial">Пробный урок бесплатно</a></p>'
                    if data.get("trialSlug")
                    else ""
                )
                + f'<div id="enroll" hidden></div></div></section>'
                if is_early
                else (
                    '<section class="ccl-enroll" id="enroll">'
                    '<div class="ccl-enroll__inner">'
                    "<h2>Выберите тариф и запишитесь</h2>"
                    f"<p>{esc(price)}</p>"
                    f'<p><a class="ccl-btn ccl-btn--primary" href="{SITE}/#program">Записаться на курс</a></p>'
                    "</div></section>"
                )
            ),
        ]
    )
    if is_early and data.get("trialSlug"):
        parts.append(
            '<section class="ccl-trial" id="trial">'
            '<div class="ccl-trial__inner">'
            "<h2>Запись на пробный урок</h2>"
            f'<p>Откроем «{esc(data.get("trialTitle") or data["h1"])}». '
            "Заполните форму на странице после загрузки — ссылка придёт на email.</p>"
            "</div></section>"
        )
    if data.get("nextLinks"):
        links = "".join(
            f'<li><a href="{esc(x["href"])}">{esc(x["label"])}</a>'
            f' — {esc(x.get("meta") or "")}</li>'
            for x in data["nextLinks"]
        )
        parts.append(
            f'<section class="ccl-next" id="next"><div class="ccl-next__inner">'
            f'<h2>{esc(data.get("nextTitle") or "Следующий шаг")}</h2>'
            f'<p>{esc(data.get("nextText") or "")}</p>'
            f"<ul>{links}</ul></div></section>"
        )
    parts.append(static_footer_lite())
    parts.append("</article>")
    parts.append(json_ld_scripts(group, data, url))
    return "".join(parts)


def full_shell(group: str) -> str:
    data = SEO["full"][group]
    static = static_full_html(group, data)
    return f"""{TILDA_FIX}<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{API}/chit-course-page.css?v={VER}">
<div id="chit-course-root" class="chit-course-page" data-group="{group}">
{static}
  <div id="chit-course-app" hidden><div id="chit-course"></div></div>
</div>
<script src="https://api.chitatelstvo.ru/static/chit-image-guard.js?v={VER}"></script>
<script src="{API}/chit-course-data.js?v={VER}"></script>
<script src="{API}/chit-course-page.js?v={VER}"></script>
<!-- {esc(data["h1"])} · SEO static + interactive app -->
"""


def lite_shell(group: str) -> str:
    data = SEO["lite"][group]
    static = static_lite_html(group, data)
    return f"""{TILDA_FIX}<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{API}/course-lite.css?v={VER}">
<div id="chit-course-lite" data-group="{group}">
{static}
  <div id="chit-course-lite-app" hidden></div>
</div>
<script src="{API}/course-lite-data.js?v={VER}"></script>
<script src="{API}/course-lite.js?v={VER}"></script>
<!-- {esc(data["h1"])} · SEO static + interactive app -->
"""


def api_full_html(group: str, data: dict) -> str:
    static = static_full_html(group, data)
    url = f"{SITE}/{data['slug']}"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
{og_and_meta_tags(group, data, url)}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="chit-course-page.css?v={VER}">
</head>
<body class="chit-course-page" data-group="{group}">
  <div id="chit-course-root" class="chit-course-page" data-group="{group}">
{static}
    <div id="chit-course-app" hidden><div id="chit-course"></div></div>
  </div>
  <script src="https://api.chitatelstvo.ru/static/chit-image-guard.js?v={VER}"></script>
  <script src="chit-course-data.js?v={VER}"></script>
  <script src="chit-course-page.js?v={VER}"></script>
</body>
</html>
"""


def api_lite_html(group: str, data: dict) -> str:
    static = static_lite_html(group, data)
    url = f"{SITE}/{data['slug']}"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
{og_and_meta_tags(group, data, url)}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="course-lite.css?v={VER}">
</head>
<body data-group="{group}">
  <div id="chit-course-lite" data-group="{group}">
{static}
    <div id="chit-course-lite-app" hidden></div>
  </div>
  <script src="course-lite-data.js?v={VER}"></script>
  <script src="course-lite.js?v={VER}"></script>
</body>
</html>
"""


API_FULL_MAP = {
    "grade-1": "grade-1.html",
    "grade-2": "grade-2.html",
    "grade-3": "grade-3.html",
    "grade-4": "grade-4.html",
    "extra-6-8": "extra-6-8.html",
    "extra-9-11": "extra-9-11.html",
}

LITE_API_MAP = {
    "early-letters": "early-letters.html",
    "early-stories": "early-stories.html",
    "wind": "wind.html",
    "garden": "garden.html",
    "rus-6-9": "rus-6-9.html",
    "rus-10-12": "rus-10-12.html",
}

for fname, group in FULL:
    REDIR.joinpath(fname).write_text(full_shell(group), encoding="utf-8")
    ROOT.joinpath(API_FULL_MAP[group]).write_text(
        api_full_html(group, SEO["full"][group]), encoding="utf-8"
    )

for fname, group in LITE:
    REDIR.joinpath(fname).write_text(lite_shell(group), encoding="utf-8")
    ROOT.joinpath(LITE_API_MAP[group]).write_text(
        api_lite_html(group, SEO["lite"][group]), encoding="utf-8"
    )

REDIR.joinpath("programmy.html").write_text(
    f"""{TILDA_FIX}<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{API}/chit-course-page.css?v={VER}">
<div id="chit-course-root" class="chit-course-page" data-page="hub">
  <article id="chit-course-static" class="cc-static">
    <header class="cc-header"><div class="cc-header__inner">
      <a class="cc-logo" href="{SITE}"><img src="{ASSETS}/logo-chitatelstvo.png" alt="{esc(ORG)}"></a>
      <a class="cc-header-cta" href="{SITE}">На главную</a>
    </div></header>
    <section class="cc-section"><div class="cc-section__inner">
      <h1>Программы Читательства по возрастам</h1>
      <p>Курсы для 1–4 класса, внеклассное чтение, ранние программы и медленное чтение.</p>
      <ul>
        <li><a href="{SITE}/1-klass">1 класс</a></li>
        <li><a href="{SITE}/2-klass">2 класс</a></li>
        <li><a href="{SITE}/3-klass">3 класс</a></li>
        <li><a href="{SITE}/4-klass">4 класс</a></li>
        <li><a href="{SITE}/6-8-let">Внеклассное чтение 6–8 лет</a></li>
        <li><a href="{SITE}/9-11-let">Внеклассное чтение 9–11 лет</a></li>
        <li><a href="{SITE}/bukvy-ozhivayut">Буквы оживают</a></li>
        <li><a href="{SITE}/pervye-istorii">Первые истории</a></li>
        <li><a href="{SITE}/veter-v-ivah">Ветер в ивах</a></li>
        <li><a href="{SITE}/tainstvenny-sad">Таинственный сад</a></li>
        <li><a href="{SITE}/russkie-skazki-6-9">Русские сказки 6–9 лет</a></li>
        <li><a href="{SITE}/russkie-skazki-10-12">Русские сказки 10–12 лет</a></li>
      </ul>
    </div></section>
  </article>
  <div id="chit-course-app" hidden><div id="chit-course"></div></div>
</div>
<script src="{API}/chit-course-data.js?v={VER}"></script>
<script src="{API}/chit-course-page.js?v={VER}"></script>
""",
    encoding="utf-8",
)

readme = f"""# Страницы курсов в Tilda (Zero Block)

**Версия ассетов:** `{VER}`

В каждом файле есть **статический HTML** (для поисковиков и AI) и интерактивная версия (подгружается с CDN).

## Как поставить / обновить страницу

1. **Страницы** → нужная страница
2. **SEO в Tilda** (вне Zero Block): title = заголовок курса, description = из `course-seo.json`
3. **Zero Block** → вставить **весь** файл → артборд высота **авто** → **Опубликовать**

## Заявки «С преподавателем»

Скрытый блок Form с именем **`Жду с преподавателем`**, поля Email + Phone, уведомления на email.

## Когда что обновлять

| Что меняется | Действие |
|--------------|----------|
| Даты, цены в форме | JS на CDN → деплой. Tilda не трогать |
| Тексты курса, программа | `course-seo.json` → `python scripts/_gen_course_pages.py` → вставить HTML в Tilda |
| Версия `?v=` | После деплоя CDN — перегенерировать shells и опубликовать |

Источник SEO-текстов: `docs/course-pages/course-seo.json`
"""
REDIR.joinpath("README.md").write_text(readme, encoding="utf-8")

print(f"Wrote {len(FULL)} full + {len(LITE)} lite Tilda shells with static SEO HTML, v={VER}")
