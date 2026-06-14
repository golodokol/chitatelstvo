#!/usr/bin/env python3
"""Export zapis_preview.html → docs/tilda-zero-main/ for Tilda Zero Block."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "zapis_preview.html"
OUT = ROOT / "docs" / "tilda-zero-main"
IMG_BASE = "https://api.chitatelstvo.ru/assets/"


def extract_between(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i)
    return text[i + len(start) : j]


def scope_css(css: str) -> str:
    css = re.sub(r"\bhtml\b\s*\{", "#chit-main {", css)
    css = re.sub(r"\bbody\b\s*\{", "#chit-main {", css)
    if not css.strip().startswith("#chit-main"):
        css = f"#chit-main {{\n  font-family: 'Nunito', system-ui, sans-serif;\n  color: var(--text);\n  line-height: 1.6;\n  font-size: 17px;\n}}\n" + css
    return css


def fix_images(content: str) -> str:
    content = content.replace("images/", IMG_BASE)
    content = content.replace("pattern-meadow-books.PNG", "pattern-meadow-books.png")
    return content


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    css = extract_between(text, "<style>", "</style>")
    body = extract_between(text, "<body>", "</body>")
    js = extract_between(text, "<script>", "</script>")

    body = re.sub(r'<div class="preview-strip">.*?</div>\s*', "", body, flags=re.S)
    body = re.sub(r"<script>.*?</script>\s*", "", body, flags=re.S)

    css = scope_css(css)
    css = fix_images(css)
    body = fix_images(body)

    html = (
        "<!-- Читательство · главная · вкладка HTML Zero Block -->\n"
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800'
        "&family=Literata:ital,wght@0,400;0,600;1,400&family=Caveat:wght@600;700&display=swap\" "
        'rel="stylesheet">\n'
        '<div id="chit-main">\n'
        + body.strip()
        + "\n</div>\n"
    )

    js = (
        f'window.CHIT_IMG_BASE = "{IMG_BASE}";\n'
        "document.addEventListener('DOMContentLoaded', function() {\n"
        + js.strip()
        + "\n});\n"
    )

    all_in_one = (
        "<!-- Читательство · единый файл для HTML-элемента Zero Block -->\n"
        "<!-- Вставить целиком в один HTML-элемент (кнопка </> внизу) -->\n"
        + html.replace(
            "<!-- Читательство · главная · вкладка HTML Zero Block -->\n", ""
        ).strip()
        + "\n<style>\n"
        + css.replace("/* Читательство · вкладка CSS Zero Block */\n", "").strip()
        + "\n</style>\n<script>\n"
        + js.replace("/* Читательство · вкладка JS Zero Block */\n", "").strip()
        + "\n</script>\n"
    )

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "00-all-in-one.html").write_text(all_in_one, encoding="utf-8")
    (OUT / "01-html.txt").write_text(html, encoding="utf-8")
    (OUT / "02-css.txt").write_text(
        "/* Читательство · вкладка CSS Zero Block */\n" + css,
        encoding="utf-8",
    )
    (OUT / "03-js.txt").write_text(
        "/* Читательство · вкладка JS Zero Block */\n" + js,
        encoding="utf-8",
    )

    install = f"""# Главная Tilda — Zero Block (быстрая установка)

Картинки уже на сервере: `{IMG_BASE}`

## 1. Tilda — главная страница

1. Удалите/скройте старые блоки
2. **Добавить блок** → **Zero Block** (T123)
3. Ширина **1200px**, высота **авто**

## 2. Вставить код (Ctrl+A → Ctrl+C → Ctrl+V)

| Вкладка | Файл |
|---------|------|
| **HTML** | `01-html.txt` |
| **CSS** | `02-css.txt` |
| **JS** | `03-js.txt` |

Сохранить → **Опубликовать**.

## 3. Шрифты

Сайт → Настройки → Шрифты: **Nunito**, **Literata**, **Caveat**

## 4. ST100 + оплата + webhook (обязательно!)

См. **`ST100_SETUP.md`** — поля формы, webhook, все 18 модулей.

Без ST100 регистрация и оплата **не работают** — Zero Block только выбирает программу.
"""
    (OUT / "INSTALL.md").write_text(install, encoding="utf-8")
    print(f"OK: {OUT}")
    print(f"HTML {len(html)} CSS {len(css)} JS {len(js)}")


if __name__ == "__main__":
    main()
