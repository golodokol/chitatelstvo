#!/usr/bin/env python3
"""Generate Expo icon/splash from brand Slovik artwork."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "static" / "early" / "slovik" / "main.jpg"
OUT = ROOT / "mobile" / "assets"
BG = "#F6F4F9"


def _hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _fit_square(im: Image.Image, size: int, pad: float = 0.08) -> Image.Image:
    bg = Image.new("RGBA", (size, size), _hex_rgb(BG) + (255,))
    w, h = im.size
    inner = int(size * (1 - pad * 2))
    scale = min(inner / w, inner / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (size - nw) // 2
    y = (size - nh) // 2
    bg.paste(resized, (x, y), resized if resized.mode == "RGBA" else None)
    return bg.convert("RGB")


def _splash(im: Image.Image, w: int = 1284, h: int = 2778) -> Image.Image:
    canvas = Image.new("RGB", (w, h), _hex_rgb(BG))
    src = im.convert("RGBA")
    max_w, max_h = int(w * 0.72), int(h * 0.38)
    scale = min(max_w / src.width, max_h / src.height)
    nw, nh = int(src.width * scale), int(src.height * scale)
    resized = src.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (w - nw) // 2
    y = int(h * 0.28)
    canvas.paste(resized, (x, y), resized)
    draw = ImageDraw.Draw(canvas)
    tag = "Читательство"
    draw.text((w // 2 - len(tag) * 5, y + nh + 48), tag, fill=_hex_rgb("#5B7FA6"))
    return canvas


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Source image missing: {SRC}")
    OUT.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert("RGBA")
    icon = _fit_square(src, 1024, pad=0.06)
    adaptive = _fit_square(src, 1024, pad=0.14)
    splash_center = _fit_square(src, 512, pad=0.04)
    splash = _splash(src)
    icon.save(OUT / "icon.png", optimize=True)
    adaptive.save(OUT / "adaptive-icon.png", optimize=True)
    splash_center.save(OUT / "splash-icon.png", optimize=True)
    splash.save(OUT / "splash.png", optimize=True)
    print(f"Wrote assets to {OUT}")


if __name__ == "__main__":
    main()
