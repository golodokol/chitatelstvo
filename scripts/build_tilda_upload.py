#!/usr/bin/env python3
"""Собрать единый HTML для вставки в Zero Block на Tilda."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs" / "tilda-zero-main"
VERSION = "20260708s"
API = "https://api.chitatelstvo.ru/assets"
OUT = DIR / "00-tilda-zero-upload.html"
LITE = DIR / "00-tilda-lite.html"


def strip_html_comments(text: str) -> str:
    lines = text.splitlines()
    while lines and lines[0].strip().startswith("<!--"):
        lines.pop(0)
    return "\n".join(lines).strip()


def read_head_boilerplate() -> str:
    """Критичные inline-стили и preload из lite-шаблона."""
    lite = LITE.read_text(encoding="utf-8")
    m = re.search(r"^(.*?)(<div id=\"chit-main\">)", lite, re.S)
    if not m:
        raise RuntimeError("Cannot find chit-main in 00-tilda-lite.html")
    head = m.group(1)
    # Убрать старые комментарии версии
    head = re.sub(r"<!--[\s\S]*?-->\s*", "", head, count=0)
    head = head.lstrip()
    head = re.sub(r"chit-zero\.css\?v=[^\"']+", f"chit-zero.css?v={VERSION}", head)
    head = re.sub(r"chit-zero\.js\?v=[^\"']+", f"chit-zero.js?v={VERSION}", head)
    head = re.sub(r'V="[^"]+"', f'V="{VERSION}"', head)
    return (
        f"<!-- CHIT VERSION {VERSION} · даты 6/27 июля, без поля «Как присылать новости», промокоды -->\n"
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
    lite = LITE.read_text(encoding="utf-8")
    m = re.search(r"(<script>window\.CHIT_QUIZ_AUTO[\s\S]*?</script>\s*<script defer src=\"[^\"]+chit-zero\.js[^\"]+\"></script>)", lite)
    if not m:
        raise RuntimeError("Cannot find footer scripts in lite template")
    footer = m.group(1)
    footer = re.sub(r"chit-zero\.js\?v=[^\"']+", f"chit-zero.js?v={VERSION}", footer)
    footer = re.sub(r'V="[^"]+"', f'V="{VERSION}"', footer)
    return footer


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
