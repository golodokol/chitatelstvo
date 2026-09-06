#!/usr/bin/env python3
"""Собрать единый HTML для вставки в Zero Block на Tilda."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs" / "tilda-zero-main"
VERSION = "20260905a"

CHIT_QUIZ_LOADER = (
    '<script id="chit-quiz-loader">(function(){if(window.__chitTrialLoaderBound)return;window.__chitTrialLoaderBound=1;'
    'var A="https://api.chitatelstvo.ru/assets/",V="__VERSION__",busy=0,done=0,q=[],last=0;'
    'function run(){while(q.length)q.shift()();}'
    'function rememberTrial(el){if(!el||!el.getAttribute)return;var slug=el.getAttribute("data-trial-slug");if(!slug)return;'
    'try{var age=el.getAttribute("data-trial-age")||"",quiz=el.getAttribute("data-quiz")||"";'
    'sessionStorage.setItem("chit_trial",JSON.stringify({age:age,slug:slug,title:el.getAttribute("data-trial-title")||"",quiz:quiz}));'
    'var hint=age==="4-6"?"5":(age==="5-7"?"6":(age==="6-8"?"7":(age==="9-11"?"10":"")));'
    'if(hint)sessionStorage.setItem("chit_trial_age_hint",hint);}catch(err){}}'
    'function openReady(el){if(window.chitQuizOpenWithEl){window.chitQuizOpenWithEl(el);return;}'
    'if(window.chitQuizOpen)window.chitQuizOpen();}'
    'function appendJs(){if(document.querySelector(\'script[src*="chit-quiz.js"]\'))return;'
    'var s=document.createElement("script");s.src=A+"chit-quiz.js?v="+V;'
    's.onload=function(){done=1;busy=0;run();};s.onerror=function(){busy=0;};document.head.appendChild(s);}'
    'window.chitLoadQuiz=function(cb){if(done){if(cb)cb();return;}if(cb)q.push(cb);if(busy)return;busy=1;'
    'if(!document.querySelector(\'link[href*="chit-quiz.css"]\')){var c=document.createElement("link");'
    'c.rel="stylesheet";c.href=A+"chit-quiz.css?v="+V;document.head.appendChild(c);}'
    'appendJs();setTimeout(function(){if(!done)appendJs();},2000);};'
    'function openTrial(el,e){if(!el)return;var now=Date.now();if(now-last<450)return;last=now;'
    'if(e){e.preventDefault();e.stopPropagation();}rememberTrial(el);'
    'if(done&&window.chitQuizOpen){openReady(el);return;}'
    'window.chitLoadQuiz(function(){openReady(el);});}'
    'function trialTarget(e){return e.target&&e.target.closest?e.target.closest(\'[href="#quiz"], [href="/quiz"], [href$="/quiz"], a[href*="/quiz"], [data-qz-open], .course-card__btn--trial\'):null;}'
    'document.addEventListener("click",function(e){var t=trialTarget(e);if(t)openTrial(t,e);},true);'
    'document.addEventListener("touchend",function(e){var t=trialTarget(e);if(t)openTrial(t,e);},{capture:true,passive:false});'
    'if(location.hash==="#quiz")window.chitLoadQuiz();' +
    'try{if(sessionStorage.getItem("chit_open_quiz")==="1"){sessionStorage.removeItem("chit_open_quiz");window.chitLoadQuiz(function(){if(window.chitQuizOpen)window.chitQuizOpen();});}}catch(err){}' +
    '})();</script>'
).replace("__VERSION__", VERSION)

CHIT_QZ_CLOSE = (
    '<style id="chit-qz-close">'
    '#qz-modal .qz-modal__close{position:absolute!important;top:16px!important;right:36px!important;left:auto!important;'
    'display:flex!important;align-items:center!important;justify-content:center!important;'
    'width:36px!important;height:36px!important;padding:0!important;border:none!important;'
    'border-radius:50%!important;background:#fff!important;color:#4A6D94!important;'
    'box-shadow:0 2px 10px rgba(61,82,102,.15)!important;font-size:0!important;line-height:0!important;'
    'transform:none!important;margin:0!important;z-index:3!important}'
    '#qz-modal .qz-modal__close:hover{background:#EDF2F9!important;transform:none!important}'
    '#qz-modal .qz-modal__close-icon{position:relative!important;display:block!important;width:14px!important;height:14px!important}'
    '#qz-modal .qz-modal__close-icon::before,#qz-modal .qz-modal__close-icon::after{content:\'\'!important;'
    'position:absolute!important;top:50%!important;left:50%!important;width:14px!important;height:2px!important;'
    'background:currentColor!important;border-radius:1px!important}'
    '#qz-modal .qz-modal__close-icon::before{transform:translate(-50%,-50%) rotate(45deg)!important}'
    '#qz-modal .qz-modal__close-icon::after{transform:translate(-50%,-50%) rotate(-45deg)!important}'
    '#qz-modal .qz-progress__meta{padding-right:0!important}'
    '#qz-modal .qz-modal__dialog .qz-card{padding:44px 16px 20px!important;width:100%!important;max-width:none!important;box-sizing:border-box!important}'
    '#qz-modal .qz-modal__dialog .qz-options,#qz-modal .qz-modal__dialog .qz-option{width:100%!important;max-width:100%!important;box-sizing:border-box!important}'
    '#qz-modal .qz-modal__dialog .qz-nav{width:100%!important;max-width:100%!important;box-sizing:border-box!important;'
    'display:flex!important;flex-wrap:nowrap!important;gap:10px!important;align-items:stretch!important}'
    '#qz-modal .qz-modal__dialog .qz-nav .qz-btn{width:auto!important;max-width:none!important;box-sizing:border-box!important}'
    '#qz-modal .qz-modal__dialog .qz-nav .qz-btn--back{flex:0 0 auto!important;min-width:96px!important}'
    '#qz-modal .qz-modal__dialog .qz-nav .qz-btn--next{flex:1 1 auto!important;min-width:0!important}'
    '@media(max-width:720px){#qz-modal{padding:8px!important}#qz-modal .qz-modal__dialog{max-width:100%!important;width:100%!important}'
    '#qz-modal .qz-modal__close{top:10px!important;right:10px!important}'
    '#qz-modal .qz-modal__dialog .qz-card{padding:42px 16px 18px!important;border-radius:16px!important}}'
    '</style>'
)

CHIT_QZ_LAUNCHER = (
    '<style id="chit-qz-launcher-critical">'
    '#chit-main .qz-launcher{position:fixed;bottom:0;left:24px;z-index:199;'
    'display:inline-flex;align-items:center;gap:8px;padding:12px 20px 14px;'
    'border-radius:14px 14px 0 0;background:var(--accent);color:#fff!important;-webkit-text-fill-color:#fff;'
    'text-decoration:none;font-family:Nunito,system-ui,sans-serif;font-size:14px;font-weight:800;'
    'box-shadow:0 -4px 24px rgba(143,125,163,.35);transition:background .2s,transform .15s}'
    '#chit-main a.qz-launcher,#chit-main a.qz-launcher:visited,#chit-main a.qz-launcher:hover,#chit-main a.qz-launcher:active'
    '{color:#fff!important;-webkit-text-fill-color:#fff;text-decoration:none}'
    '#chit-main .qz-launcher:hover{background:#7a6a8f;transform:translateY(-2px)}'
    '#chit-main .qz-launcher__icon,#chit-main .qz-launcher__text{color:#fff!important;-webkit-text-fill-color:#fff}'
    '#chit-main .qz-launcher__icon{font-size:18px;line-height:1}'
    '@media(max-width:720px){#chit-main{padding-bottom:calc(72px + env(safe-area-inset-bottom))!important}'
    '#chit-main .qz-launcher{left:0;right:50%;justify-content:center;border-radius:0;'
    'padding:12px 10px max(14px,env(safe-area-inset-bottom));font-size:13px;line-height:1.2;'
    'white-space:nowrap;box-shadow:none;border-right:1px solid rgba(255,255,255,.28)}'
    'body.qz-modal-open #chit-main .qz-launcher{display:none!important}}'
    '@media(max-width:380px){#chit-main .qz-launcher{font-size:12px}}'
    '</style>'
)
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
    '#chit-main.is-with-teacher-stage1-closed #chit-stages [data-stage="1"],'
    '#chit-main:has(#chit-tariffs .pick-card[data-tariff="with_teacher"].is-active) #chit-stages [data-stage="1"]'
    '{display:none!important;visibility:hidden!important;pointer-events:none!important;'
    'position:absolute!important;width:0!important;height:0!important;overflow:hidden!important;'
    'margin:0!important;padding:0!important;border:0!important}'
    '</style>'
)

CHIT_FARE_MODAL_CRITICAL = (
    '<style id="chit-fare-modal-critical">'
    '.fare-modal:not(.is-open){position:fixed!important;inset:0!important;z-index:10050!important;'
    'display:flex!important;align-items:center!important;justify-content:center!important;'
    'opacity:0!important;visibility:hidden!important;pointer-events:none!important}'
    '.fare-modal.is-open{opacity:1!important;visibility:visible!important;pointer-events:auto!important}'
    '</style>'
)

CHIT_HERO_PREMIUM = (
    '<style id="chit-hero-premium">'
    '#chit-main .hero--premium .hero__grid{display:grid!important;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr)!important;'
    'column-gap:clamp(36px,5vw,72px)!important;row-gap:10px!important;align-items:stretch!important;'
    'max-width:1120px;width:100%!important;margin:0 auto}'
    '#chit-main .hero--premium .hero__badge--hero-top{grid-column:1/-1!important;grid-row:1!important;'
    'justify-self:center!important;text-align:center!important;background:transparent!important;border:none!important;'
    'box-shadow:none!important;padding:0!important;margin:0 0 14px!important;max-width:none!important;width:100%!important;gap:8px!important}'
    '#chit-main .hero--premium .hero__badge-line--sub{font-size:15px!important;line-height:1.45!important;font-weight:600!important;color:#6B8499!important}'
    '#chit-main .hero--premium .hero__badge-line--title em{font-size:clamp(36px,4.6vw,46px)!important;letter-spacing:.05em!important;line-height:1.1!important;font-weight:800!important;color:#8F7DA3!important;font-style:normal!important}'
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
    '#chit-main .hero--premium .hero__badge--hero-top{grid-column:1!important;grid-row:1!important;'
    'margin:0 0 26px!important}'
    '#chit-main .hero--premium .hero__content{grid-column:1!important;grid-row:2!important;align-items:center!important;'
    'justify-content:flex-start!important;text-align:center!important}'
    '#chit-main .hero--premium .hero__visual{grid-column:1!important;grid-row:3!important;justify-content:flex-start!important}'
    '#chit-main .hero--premium .hero__actions{flex-direction:column!important;align-items:stretch!important}'
    '#chit-main .hero--premium .hero__actions .btn{width:100%!important}'
    '#chit-main .hero--premium .hero__cta-note,#chit-main .hero--premium .hero__visual-gift{margin-top:12px!important;padding-top:0!important}'
    '#chit-main .hero--premium .hero__badge-line--sub{font-size:14px!important}'
    '#chit-main .hero--premium .hero__badge-line--title em{font-size:clamp(28px,7.5vw,34px)!important;letter-spacing:.04em!important}'
    '#chit-main .hero--premium h1{margin-top:4px!important}'
    '}'
    '</style>'
)


CHIT_QZ_CRITICAL = (
    '<style id="chit-qz-critical">'
    '#qz-modal{display:none!important;position:fixed!important;inset:0!important;z-index:10050!important;'
    'align-items:center!important;justify-content:center!important;padding:16px!important;box-sizing:border-box!important}'
    '#qz-modal.is-open{display:flex!important}'
    '#qz-modal .qz-modal__backdrop{position:absolute!important;inset:0!important;background:rgba(26,38,58,.55)!important}'
    '#qz-modal .qz-modal__dialog{position:relative!important;z-index:1!important;width:100%!important;'
    'max-width:600px!important;max-height:calc(100vh - 32px)!important;overflow:hidden!important;box-sizing:border-box!important}'
    '@media(max-width:720px){#qz-modal{padding:8px!important}#qz-modal .qz-modal__dialog{max-width:100%!important}}'
    '#chit-quiz .qz-step{display:none!important}#chit-quiz .qz-step.is-active{display:block!important}'
    'body.qz-modal-open{overflow:hidden!important}'
    '</style>'
)

CHIT_GAMIFY_PATH = (
    '<style id="chit-gamify-path">'
    '#chit-main .gamify__path-wrap{display:flex!important;justify-content:center!important;'
    'align-items:center!important;width:100%!important;margin:0 auto 20px!important;'
    'padding:0 16px!important;box-sizing:border-box!important}'
    '#chit-main .gamify__path-note{display:block!important;width:100%!important;max-width:640px!important;'
    'margin:0 auto!important;padding:0!important;text-align:center!important;font-size:15px!important;'
    'line-height:1.55!important;color:#6B8499!important}'
    '#chit-main #rewards .gamify__subtitle{text-align:center!important;width:100%!important;'
    'margin-left:auto!important;margin-right:auto!important}'
    '@media(max-width:720px){'
    '#allrecords #chit-main .gamify-levels,#chit-main .gamify-levels{'
    'display:flex!important;flex-wrap:wrap!important;justify-content:center!important;'
    'align-items:flex-start!important;gap:18px 10px!important;width:100%!important;max-width:100%!important;'
    'padding:0 12px!important;margin:0 auto 36px!important;box-sizing:border-box!important}'
    '#allrecords #chit-main .gamify-levels::before,#chit-main .gamify-levels::before{display:none!important}'
    '#allrecords #chit-main .gamify-levels__arrow,#chit-main .gamify-levels__arrow{display:none!important}'
    '#allrecords #chit-main .gamify-levels .gamify-item,#chit-main .gamify-levels .gamify-item{'
    'flex:0 0 calc(33.333% - 10px)!important;min-width:96px!important;max-width:118px!important;'
    'width:auto!important;gap:8px!important;overflow:visible!important}'
    '#allrecords #chit-main .gamify-levels .gamify-item__img,#chit-main .gamify-levels .gamify-item__img{'
    'width:72px!important;height:72px!important;min-width:72px!important;min-height:72px!important;'
    'margin:0 auto!important;overflow:visible!important}'
    '#allrecords #chit-main .gamify-levels .gamify-item__img img,#chit-main .gamify-levels .gamify-item__img img{'
    'transform:none!important}'
    '#allrecords #chit-main .gamify-levels .gamify-item__name,#chit-main .gamify-levels .gamify-item__name{'
    'font-size:12px!important;max-width:100%!important;min-height:0!important;line-height:1.25!important;'
    'padding:0 2px!important;white-space:normal!important;text-align:center!important;'
    'writing-mode:horizontal-tb!important;hyphens:none!important;word-break:normal!important;'
    'overflow-wrap:normal!important;overflow:visible!important}'
    '}'
    '@media(max-width:400px){'
    '#allrecords #chit-main .gamify-levels .gamify-item,#chit-main .gamify-levels .gamify-item{'
    'flex:0 0 calc(50% - 8px)!important;min-width:120px!important;max-width:150px!important}'
    '#allrecords #chit-main .gamify-levels .gamify-item__img,#chit-main .gamify-levels .gamify-item__img{'
    'width:68px!important;height:68px!important;min-width:68px!important;min-height:68px!important}'
    '}'
    '</style>'
)


def patch_head_styles(head: str) -> str:
    head = re.sub(r'<style id="chit-btn-fix">[^<]+</style>', CHIT_BTN_FIX, head)
    head = re.sub(r'<style id="chit-hero-premium">[\s\S]*?</style>', CHIT_HERO_PREMIUM, head)
    head = head.replace(
        '.hero__badge--hero-top{margin-top:0!important;margin-bottom:14px!important}',
        '.hero__badge--hero-top{margin-top:0!important;margin-bottom:26px!important}',
    )
    head = re.sub(r'<style id="chit-qz-launcher-critical">[\s\S]*?</style>', CHIT_QZ_LAUNCHER, head)
    head = re.sub(r'<style id="chit-qz-critical">[\s\S]*?</style>', CHIT_QZ_CRITICAL, head)
    head = re.sub(r'<style id="chit-qz-close">[\s\S]*?</style>', CHIT_QZ_CLOSE, head)
    head = re.sub(r'<style id="chit-fare-modal-critical">[\s\S]*?</style>', CHIT_FARE_MODAL_CRITICAL, head)
    if 'chit-fare-modal-critical' not in head:
        head = head.replace(CHIT_QZ_CLOSE, CHIT_QZ_CLOSE + CHIT_FARE_MODAL_CRITICAL, 1)
    head = re.sub(r'<style id="chit-gamify-path">[\s\S]*?</style>', CHIT_GAMIFY_PATH, head)
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
        f"<!-- CHIT VERSION {VERSION} · evergreen школа, программы по возрастам -->\n"
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
    return (
        '<script>window.CHIT_QUIZ_AUTO={enabled:false};</script>\n'
        + CHIT_QUIZ_LOADER
        + f'\n<script defer src="https://api.chitatelstvo.ru/assets/chit-zero.js?v={VERSION}"></script>'
    )


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
