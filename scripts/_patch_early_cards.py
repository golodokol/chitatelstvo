# -*- coding: utf-8 -*-
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "docs" / "tilda-zero-main"
repls = [
    (
        'data-kind="early" data-enroll="lead" data-course-title="Буквы оживают"',
        'data-kind="early" data-enroll="lead" data-group="early-letters" data-trial-slug="early-letters-trial-lesson-01" data-course-title="Буквы оживают"',
    ),
    (
        'data-kind="early" data-enroll="lead" data-course-title="Первые истории"',
        'data-kind="early" data-enroll="lead" data-group="early-stories" data-trial-slug="early-stories-trial-lesson-01" data-course-title="Первые истории"',
    ),
]
for name in ("00-tilda-lite.html", "00-tilda-zero-upload.html", "_preview-layout.html", "01-html.txt"):
    path = root / name
    if not path.exists():
        print("missing", name)
        continue
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in repls:
        if "data-trial-slug" in text and "early-letters" in text and name != "01-html.txt":
            continue
        text = text.replace(old, new)
    # idempotent if already patched
    if "data-trial-slug=\"early-letters-trial-lesson-01\"" not in text:
        text = text.replace(
            'data-kind="early" data-enroll="lead" data-group="early-letters" data-course-title="Буквы оживают"',
            'data-kind="early" data-enroll="lead" data-group="early-letters" data-trial-slug="early-letters-trial-lesson-01" data-course-title="Буквы оживают"',
        )
    if text != original:
        path.write_text(text, encoding="utf-8")
        print("patched", name)
    else:
        print("ok", name)
