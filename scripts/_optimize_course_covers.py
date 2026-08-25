#!/usr/bin/env python3
"""Compress course covers to small WebP + baseline JPEG for mobile browsers."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("NEED_PIL")
    sys.exit(2)

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
MAX_W = 720
WEBP_Q = 62
JPEG_Q = 68

names = [
    "course-cover-letters",
    "course-cover-stories",
    "course-cover-letters-intro",
    "course-cover-stories-intro",
    "course-cover-grade-1",
    "course-cover-grade-2",
    "course-cover-grade-3",
    "course-cover-grade-4",
    "course-cover-extra-6-8",
    "course-cover-extra-9-11",
    "course-cover-wind",
    "course-cover-garden",
    "course-cover-rus-6-9",
    "course-cover-rus-10-12",
]


def convert_one(src: Path) -> None:
    im = Image.open(src)
    im = im.convert("RGB")
    w, h = im.size
    if w > MAX_W:
        nh = int(round(h * (MAX_W / w)))
        im = im.resize((MAX_W, nh), Image.Resampling.LANCZOS)
    stem = src.stem
    webp = src.with_name(stem + ".webp")
    jpg = src.with_name(stem + ".jpg")
    # Write optimized files (overwrite jpg with baseline)
    im.save(webp, "WEBP", quality=WEBP_Q, method=6)
    im.save(jpg, "JPEG", quality=JPEG_Q, optimize=True, progressive=False)
    print(f"{stem}: {w}x{h} -> {im.size[0]}x{im.size[1]}  "
          f"webp={webp.stat().st_size} jpg={jpg.stat().st_size}")


def main() -> None:
    for name in names:
        src = ROOT / f"{name}.jpg"
        if not src.is_file():
            # try webp-only later
            alt = ROOT / f"{name}.webp"
            if alt.is_file():
                continue
            print(f"skip missing {name}")
            continue
        convert_one(src)


if __name__ == "__main__":
    main()
