# -*- coding: utf-8 -*-
"""Also overwrite heavy PNGs with smaller re-encodes (same filenames) for live HTML without re-paste."""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "tilda-zero-main" / "_perf-opt"
OUT = SRC / "png-slim"
OUT.mkdir(parents=True, exist_ok=True)
KEY = Path.home() / ".ssh" / "chitatelstvo_deploy"
REMOTE = "root@194.87.201.99:/var/www/chitatelstvo-assets/"


def save_png(im: Image.Image, path: Path) -> None:
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA")
    im.save(path, "PNG", optimize=True, compress_level=9)
    print(f"{path.name:30} {path.stat().st_size/1024:7.1f} KiB {im.size}")


def main() -> None:
    cta = Image.open(SRC / "cta-fairy-tale-bg.png").resize((1440, 960), Image.Resampling.LANCZOS).convert("RGB")
    save_png(cta, OUT / "cta-fairy-tale-bg.png")

    pat = Image.open(SRC / "pattern-meadow-books-tilda.png").resize((420, 420), Image.Resampling.LANCZOS)
    save_png(pat, OUT / "pattern-meadow-books.png")

    for name, box in (
        ("audience-kids.png", (240, 240)),
        ("audience-parents.png", (240, 240)),
        ("audience-family.png", (240, 240)),
        ("audience-pace.png", (240, 240)),
        ("hero-book-single.png", (280, 400)),
    ):
        im = Image.open(SRC / name)
        w, h = im.size
        scale = min(box[0] / w, box[1] / h, 1.0)
        if scale < 1:
            im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
        save_png(im, OUT / name)

    files = list(OUT.glob("*.png"))
    cmd = [
        "scp",
        "-i",
        str(KEY),
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
    ] + [str(f) for f in files] + [REMOTE]
    subprocess.check_call(cmd)
    print("png slim uploaded", len(files))


if __name__ == "__main__":
    main()
