# -*- coding: utf-8 -*-
"""Optimize homepage images to WebP without visible quality loss."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

SRC = Path("docs/tilda-zero-main/_perf-opt")
OUT = Path("docs/tilda-zero-main")  # also copy into assets folder for upload
ASSETS_OUT = Path("docs/tilda-zero-main/_perf-opt/out")
ASSETS_OUT.mkdir(parents=True, exist_ok=True)


def save_webp(im: Image.Image, path: Path, quality: int = 85) -> None:
    im = im.convert("RGBA") if im.mode in ("P", "LA") else im.convert("RGB") if im.mode != "RGBA" else im
    # Prefer RGB for photos (smaller); keep RGBA only if needed
    if im.mode == "RGBA":
        # flatten if mostly opaque
        alpha = im.getchannel("A")
        if alpha.getextrema()[0] >= 250:
            bg = Image.new("RGB", im.size, (255, 252, 248))
            bg.paste(im, mask=alpha)
            im = bg
        else:
            pass
    elif im.mode != "RGB":
        im = im.convert("RGB")
    im.save(path, "WEBP", quality=quality, method=6)
    print(f"{path.name:32} {path.stat().st_size/1024:7.1f} KiB  {im.size[0]}x{im.size[1]}")


def resize_max(im: Image.Image, max_w: int, max_h: int | None = None) -> Image.Image:
    w, h = im.size
    max_h = max_h or 10_000
    scale = min(max_w / w, max_h / h, 1.0)
    if scale >= 0.999:
        return im
    nw, nh = int(w * scale), int(h * scale)
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def main() -> None:
    # CTA background: full-bleed cover — 1920 wide is enough for retina desktops
    cta = Image.open(SRC / "cta-fairy-tale-bg.png")
    print("cta src", cta.size, f"{(SRC / 'cta-fairy-tale-bg.png').stat().st_size/1024:.0f} KiB")
    cta = resize_max(cta, 1920, 1280)
    save_webp(cta, ASSETS_OUT / "cta-fairy-tale-bg.webp", quality=82)
    # mobile variant
    cta_m = resize_max(Image.open(SRC / "cta-fairy-tale-bg.png"), 960, 1200)
    save_webp(cta_m, ASSETS_OUT / "cta-fairy-tale-bg-m.webp", quality=80)

    # Icons shown ~80–120px CSS, with scale up to 1.48 → ~180px; use 240 for retina
    for name in ("audience-kids.png", "audience-parents.png"):
        im = Image.open(SRC / name)
        print(name, "src", im.size)
        im = resize_max(im, 240, 240)
        save_webp(im, ASSETS_OUT / name.replace(".png", ".webp"), quality=86)

    # Hero book covers ~124x180 CSS → 2x = 248x360
    book = Image.open(SRC / "hero-book-single.png")
    print("book src", book.size)
    book = resize_max(book, 280, 400)
    save_webp(book, ASSETS_OUT / "hero-book-single.webp", quality=86)

    # Also fetch other audience icons if present later — skip
    print("DONE ->", ASSETS_OUT)


if __name__ == "__main__":
    main()
