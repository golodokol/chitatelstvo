#!/usr/bin/env python3
"""Flatten quiz logo onto white background (remove black matte)."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image


def flatten_on_white(src: Path, dst: Path) -> None:
    im = Image.open(src).convert("RGBA")
    cleaned: list[tuple[int, int, int, int]] = []
    for r, g, b, a in im.getdata():
        if a > 200 and r + g + b < 45:
            cleaned.append((255, 255, 255, 0))
        else:
            cleaned.append((r, g, b, a))
    im.putdata(cleaned)
    out = Image.new("RGB", im.size, (255, 255, 255))
    out.paste(im, mask=im.split()[3])
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst, "PNG", optimize=True)
    print(f"saved {dst} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/logo-src.png")
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("/var/www/chitatelstvo-assets/logo-chitatelstvo-quiz.png")
    flatten_on_white(source, target)
