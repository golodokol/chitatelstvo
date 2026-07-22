#!/usr/bin/env python3
"""Собрать единый HTML для вставки в Zero Block на Tilda."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs" / "tilda-zero-main"
VERSION = "20260717d"
API = "https://api.chitatelstvo.ru/assets"
OUT = DIR / "00-tilda-zero-upload.html"
LITE = DIR / "00-tilda-lite.html"


def strip_html_comments(text: str) -> str:
    lines = text.splitlines()
    while lines and lines[0].strip().startswith("<!--"):
        lines.pop(0)
    return "\n".join(lines).strip()


CHIT_BTN_FIX = (
    '<style id="chit-btn-fix">'
    '#allrecords #chit-main a.btn,#allrecords #chit-main .btn,#allrecords #chit-main .btn--pay'
    '{color:#fff!important;-webkit-text-fill-color:#fff!important}'
    '#allrecords #chit-main a.btn--outline,#allrecords #chit-main .btn--outline,#allrecords #chit-main a.btn.btn--outline'
    '{color:var(--blue)!important;-webkit-text-fill-color:var(--blue)!important;background:transparent!important;border:2px solid #C5D9ED!important}'
    '#allrecords #chit-main .pill.is-active{color:#fff!important;-webkit-text-fill-color:#fff!important}'
    '</style>'
)

CHIT_HERO_PREMIUM = (
    '<style id="chit-hero-premium">'
    '#chit-main .hero--premium .hero__grid{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr)!important;'
    'column-gap:clamp(36px,5vw,72px)!important;row-gap:10px!important;align-items:stretch!important;'
    'max-width:1120px;width:100%!important;margin:0 auto}'
    '#chit-main .hero--premium .hero__badge--hero-top{grid-column:1/-1!important;grid-row:1!important;'
    'justify-self:center!important;text-align:center!important;background:transparent!important;border:none!important;'
    'box-shadow:none!important;padding:0!important;margin:0 0 10px!important;max-width:none!important;width:100%!important;gap:6px!important}'
    '#chit-main .hero--premium .hero__badge-line--sub{font-size:15px!important;line-height:1.45!important;font-weight:600!important;color:#6B8499!important}'
    '#chit-main .hero--premium .hero__badge-line--title em{font-size:18px!important;letter-spacing:.08em!important;font-weight:800!important;color:#8F7DA3!important;font-style:normal!important}'
    '#chit-main .hero--premium .hero__content{grid-column:1!important;grid-row:2!important;display:flex!important;'
    'flex-direction:column!important;align-items:flex-start!important;justify-content:center!important;align-self:stretch!important}'
    '#chit-main .hero--premium .hero__visual{grid-column:2!important;grid-row:2!important;display:flex!important;'
    'flex-direction:column!important;justify-content:center!important;align-self:stretch!important}'
    '#chit-main .hero--premium .hero__cta{max-width:none!important;width:100%!important}'
    '#chit-main .hero--premium .hero__actions{display:flex!important;flex-direction:row!important;flex-wrap:wrap!important;'
    'align-items:center!important;justify-content:flex-start!important;gap:12px!important;width:100%!important}'
    '#chit-main .hero--premium .hero__actions .btn{width:auto!important;flex:0 1 auto!important;white-space:nowrap!important}'
    '#chit-main .hero--premium .btn--hero{width:auto!important;max-width:none!important}'
    '#chit-main .hero--premium .hero__actions .btn--outline{padding:14px 22px!important;font-size:16px!important}'
    '#chit-main .hero--premium .hero__cta-note{margin-top:0!important;padding-top:0!important}'
    '#chit-main .hero--premium .hero__visual-gift{margin-top:14px!important;padding-top:0!important;align-self:center!important}'
    '@media(max-width:960px){'
    '#chit-main .hero--premium .hero__grid{grid-template-columns:1fr!important}'
    '#chit-main .hero--premium .hero__badge--hero-top{grid-column:1!important;grid-row:1!important}'
    '#chit-main .hero--premium .hero__content{grid-column:1!important;grid-row:2!important;align-items:center!important;'
    'justify-content:flex-start!important;text-align:center!important}'
    '#chit-main .hero--premium .hero__visual{grid-column:1!important;grid-row:3!important;justify-content:flex-start!important}'
    '#chit-main .hero--premium .hero__actions{flex-direction:column!important;align-items:stretch!important}'
    '#chit-main .hero--premium .hero__actions .btn{width:100%!important}'
    '#chit-main .hero--premium .hero__cta-note,#chit-main .hero--premium .hero__visual-gift{margin-top:12px!important;padding-top:0!important}'
    '#chit-main .hero--premium .hero__badge-line--sub{font-size:14px!important}'
    '#chit-main .hero--premium .hero__badge-line--title em{font-size:16px!important}'
    '}'
    '</style>'
)


def patch_head_styles(head: str) -> str:
    head = re.sub(r'<style id="chit-btn-fix">[^<]+</style>', CHIT_BTN_FIX, head)
    head = re.sub(r'<style id="chit-hero-premium">[\s\S]*?</style>', CHIT_HERO_PREMIUM, head)
    head = head.replace(
        '#chit-main .btn{display:inline-flex;align-items:center;justify-content:center;padding:14px 28px;border-radius:12px;background:var(--blue);color:#fff;font-weight:700;text-decoration:none;border:none;cursor:pointer}',
        '#chit-main .btn{display:inline-flex;align-items:center;justify-content:center;padding:14px 28px;border-radius:12px;font-weight:700;text-decoration:none;cursor:pointer}'
        '#chit-main .btn:not(.btn--outline){background:var(--blue);color:#fff;border:none}'
        '#chit-main .btn--outline{background:transparent;color:var(--blue);border:2px solid #C5D9ED;-webkit-text-fill-color:var(--blue)}',
    )
    return head


def read_head_boilerplate() -> str:
    """Критичные inline-стили и preload из актуального upload/lite."""
    src = OUT if OUT.is_file() else LITE
    text = src.read_text(encoding="utf-8")
    m = re.search(r"^(.*?)(<div id=\"chit-main\">)", text, re.S)
    if not m:
        raise RuntimeError(f"Cannot find chit-main in {src.name}")
    head = m.group(1)
    # Убрать HTML-комментарии в начале (версия перезапишется)
    head = re.sub(r"<!--[\s\S]*?-->\s*", "", head, count=0)
    head = head.lstrip()
    head = re.sub(r"chit-zero\.css\?v=[^\"']+", f"chit-zero.css?v={VERSION}", head)
    head = re.sub(r"chit-zero\.js\?v=[^\"']+", f"chit-zero.js?v={VERSION}", head)
    head = re.sub(r'V="[^"]+"', f'V="{VERSION}"', head)
    head = patch_head_styles(head)
    return (
        f"<!-- CHIT VERSION {VERSION} · даты 15 июля / 10 августа, пояснения в карточках формата -->\n"
        + head.rstrip()
        + "\n"
    )


def read_body_from_html_txt() -> str:
    raw = (DIR / "01-html.txt").read_text(encoding="utf-8")
    raw = strip_html_comments(raw)
    if '<div id="chit-main">' not in raw:
        raise RuntimeError("01-html.txt missing chit-main")
    body = raw.split('<div id="chit-main">', 1)[1]
    # Телефон вместо Telegram — как на текущей странице оплаты
    body = body.replace(
        '<label for="chit_parent_telegram">Telegram</label>\n'
        '            <input type="text" id="chit_parent_telegram" name="parent_telegram" placeholder="@username">',
        '<label for="chit_parent_telegram">Телефон</label>\n'
        '            <input type="tel" id="chit_parent_telegram" name="parent_telegram" autocomplete="tel">',
        1,
    )
    return "<div id=\"chit-main\">" + body


def read_footer_scripts() -> str:
    # Берём футер из актуального upload (lite может быть устаревшим)
    for src in (OUT, LITE):
        if not src.is_file():
            continue
        text = src.read_text(encoding="utf-8")
        m = re.search(
            r"(<script>window\.CHIT_QUIZ_AUTO[\s\S]*?</script>\s*"
            r"(?:<script id=\"chit-quiz-loader\">[\s\S]*?</script>\s*)?"
            r"<script defer src=\"[^\"]+chit-zero\.js[^\"]+\"></script>)",
            text,
        )
        if not m:
            m = re.search(
                r"(<script>window\.CHIT_QUIZ_AUTO[\s\S]*?</script>\s*"
                r"<script defer src=\"[^\"]+chit-zero\.js[^\"]+\"></script>)",
                text,
            )
        if m:
            footer = m.group(1)
            footer = re.sub(r"chit-zero\.js\?v=[^\"']+", f"chit-zero.js?v={VERSION}", footer)
            footer = re.sub(r'V="[^"]+"', f'V="{VERSION}"', footer)
            return footer
    raise RuntimeError("Cannot find footer scripts in upload/lite template")


def build_css_js_assets() -> None:
    css = re.sub(
        r"^/\*[^*\n]*\*/\r?\n",
        "",
        (DIR / "02-css.txt").read_text(encoding="utf-8"),
        count=1,
    ).strip()
    (DIR / "chit-zero.css").write_text(css + "\n", encoding="utf-8")

    src = DIR / "chit-zero.src.js"
    out = DIR / "chit-zero.js"
    subprocess.run(
        f'npx --yes terser "{src}" -c -m -o "{out}"',
        cwd=ROOT,
        check=True,
        shell=True,
    )


def main() -> None:
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)}
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_chit_schedule.py")], cwd=ROOT, check=True, env=env)
    build_css_js_assets()

    content = f"""<!-- Читательство · единый файл для HTML-элемента Zero Block ({VERSION})
     Вставить целиком: Tilda → Zero Block → двойной клик по элементу </> → Ctrl+A → вставить → Опубликовать
     CSS и JS грузятся с {API} (нужен деплой на сервер).

     ВАЖНО ПРО ПРОМОКОД (скидку считает Tilda, не наш сервер):
     1) Настройки сайта → Платёжные системы → Промокоды — создать код (напр. ALFACHILDREN).
     2) Блок ST100 на главной И на /oplata → Настройки блока → включить переключатель «Промокоды» → Опубликовать.
        Без этого кнопка «Записаться» покажет полную цену, скидка в корзине не применится.
     3) В ST100: скрытое поле promo_code (Hidden) для webhook — значение пустое, подставит Zero Block.
     Не дублируйте видимое поле «Промокод» в ST100. Проверка: ввести код → сумма на кнопке должна уменьшиться.
     Подробно: docs/tilda-zero-main/ST100_SETUP.md
-->
{read_head_boilerplate()}{read_body_from_html_txt()}
{read_footer_scripts()}
"""
    OUT.write_text(content, encoding="utf-8")
    LITE.write_text(content.replace(
        "00-tilda-zero-upload.html",
        "00-tilda-lite.html",
    ), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")
    print(f"Updated {LITE.relative_to(ROOT)}")
    print(f"Assets version: {VERSION}")


if __name__ == "__main__":
    main()
