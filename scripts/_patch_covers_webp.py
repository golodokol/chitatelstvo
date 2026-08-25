#!/usr/bin/env python3
"""Point course covers to WebP and hide broken img overlays."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "docs" / "tilda-zero-main"
VER = "20260823u"
ASSET = "https://api.chitatelstvo.ru/assets"


def to_webp(url: str) -> str:
    url = re.sub(r"course-cover-([a-z0-9\-]+)\.jpe?g", r"course-cover-\1.webp", url, flags=re.I)
    url = re.sub(r"(\.webp)(?:\?v=[^\"')\s]+)?", rf"\1?v={VER}", url)
    return url


def patch_text(text: str) -> str:
    text = re.sub(
        r"https://api\.chitatelstvo\.ru/assets/course-cover-([a-z0-9\-]+)\.jpe?g(?:\?v=[^\"')\s]+)?",
        rf"{ASSET}/course-cover-\1.webp?v={VER}",
        text,
        flags=re.I,
    )
    return text


def main() -> None:
    for name in ("chit-zero.css", "02-css.txt", "chit-zero.src.js", "01-html.txt"):
        path = DIR / name
        if not path.is_file():
            continue
        old = path.read_text(encoding="utf-8")
        new = patch_text(old)
        path.write_text(new, encoding="utf-8")
        print(name, "changed" if new != old else "same")

    # Prefer CSS background only — hide img overlays that break layout in Yandex
    css_path = DIR / "chit-zero.css"
    css = css_path.read_text(encoding="utf-8")
    marker = "#chit-main .course-card__media img[data-chit-img-failed]"
    hide_rule = """#chit-main .course-card__media img {
  /* Yandex/Safari: broken <img> leaves white hole over CSS cover */
  display: none !important;
}
"""
    if "Yandex/Safari: broken" not in css:
        # replace the visible img block with hide
        css = re.sub(
            r"#chit-main \.course-card__media img \{[^}]+\}",
            hide_rule.rstrip(),
            css,
            count=1,
        )
        # keep failed attr rule harmless
        css_path.write_text(css, encoding="utf-8")
        (DIR / "02-css.txt").write_text(css, encoding="utf-8")
        print("css img hide applied")

    # JS: only set background, do not inject/update img
    src = DIR / "chit-zero.src.js"
    js = src.read_text(encoding="utf-8")
    old_block = """      var img = media.querySelector('img');
      if (!img) {
        img = document.createElement('img');
        img.alt = '';
        img.width = 800;
        img.height = 500;
        media.appendChild(img);
      }
      img.loading = 'eager';
      img.setAttribute('decoding', 'async');
      if (img.getAttribute('src') !== item[1]) img.src = item[1];
      img.style.objectPosition = earlyCover ? 'center center' : '';
      if (img.complete && img.naturalWidth === 0) chitHideBrokenImage(img);
    });
    chitForceLoadImages();
  })();"""
    new_block = """      media.querySelectorAll('img').forEach(function(img) {
        img.style.setProperty('display', 'none', 'important');
        img.setAttribute('aria-hidden', 'true');
      });
    });
  })();"""
    if old_block in js:
        js = js.replace(old_block, new_block, 1)
        src.write_text(js, encoding="utf-8")
        print("js covers: background-only")
    else:
        print("js block not found — check manually")

    bp = ROOT / "scripts" / "build_tilda_upload.py"
    bp.write_text(
        re.sub(r'VERSION = "[^"]+"', f'VERSION = "{VER}"', bp.read_text(encoding="utf-8"), count=1),
        encoding="utf-8",
    )
    print("version", VER)


if __name__ == "__main__":
    main()
