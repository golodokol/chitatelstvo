# -*- coding: utf-8 -*-
from pathlib import Path
from PIL import Image

SRC = Path("docs/tilda-zero-main/_perf-opt")
OUT = SRC / "out"


def save_webp(im: Image.Image, path: Path, quality: int = 82) -> None:
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
    if im.mode == "RGBA":
        a = im.getchannel("A")
        if a.getextrema()[0] >= 250:
            bg = Image.new("RGB", im.size, (246, 244, 249))
            bg.paste(im, mask=a)
            im = bg
    im.save(path, "WEBP", quality=quality, method=6)
    print(f"{path.name:36} {path.stat().st_size/1024:7.1f} KiB  {im.size}")


# Prefer smaller Tilda source for pattern if available
pat_path = SRC / "pattern-meadow-books-tilda.png"
if not pat_path.exists():
    pat_path = SRC / "pattern-meadow-books.png"
pat = Image.open(pat_path)
print("pattern src", pat.size, pat_path.name, pat_path.stat().st_size / 1024)
# tile used at background-size 420px — keep ~840 for 2x
w, h = pat.size
scale = min(840 / w, 840 / h, 1.0)
if scale < 1:
    pat = pat.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
save_webp(pat, OUT / "pattern-meadow-books.webp", quality=78)

for name in ("audience-family.png", "audience-pace.png"):
    im = Image.open(SRC / name)
    print(name, im.size)
    w, h = im.size
    scale = min(240 / w, 240 / h, 1.0)
    if scale < 1:
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    save_webp(im, OUT / name.replace(".png", ".webp"), quality=86)

# Re-compress CTA a bit more aggressively for desktop (~still sharp)
cta = Image.open(SRC / "cta-fairy-tale-bg.png")
cta = cta.resize((1440, 960), Image.Resampling.LANCZOS)
save_webp(cta, OUT / "cta-fairy-tale-bg.webp", quality=78)
print("re-done cta")
