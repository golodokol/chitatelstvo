# -*- coding: utf-8 -*-
"""Оптимизация тяжёлых early-ассетов: меньше пикселей, чёткость на retina сохраняется.

- Буквы с альфой → PNG (resize + optimize)
- Непрозрачные сцены / позы Словика → JPEG q90 (рядом .jpg, исходный .png удаляется)
"""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def resize_max(im: Image.Image, max_edge: int) -> Image.Image:
    w, h = im.size
    edge = max(w, h)
    if edge <= max_edge:
        return im
    scale = max_edge / float(edge)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    return im.resize((nw, nh), Image.Resampling.LANCZOS)


def save_png(path: Path, im: Image.Image) -> int:
    if im.mode not in ("RGBA", "RGB", "LA", "L"):
        im = im.convert("RGBA")
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True, compress_level=9)
    data = buf.getvalue()
    path.write_bytes(data)
    return len(data)


def save_jpeg(path: Path, im: Image.Image, *, quality: int = 90) -> int:
    buf = io.BytesIO()
    im.convert("RGB").save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
    data = buf.getvalue()
    path.write_bytes(data)
    return len(data)


def main() -> None:
    # (path, max_edge, mode)  mode: png | jpg_from_png | jpg
    jobs: list[tuple[Path, int, str]] = [
        (ROOT / "static/early/letters/letter-a-hero.png", 1100, "png"),
        (ROOT / "static/early/letters/letter-a-piece-left.png", 900, "png"),
        (ROOT / "static/early/letters/letter-a-piece-right.png", 900, "png"),
        (ROOT / "static/early/letters/letter-a-piece-bar.png", 900, "png"),
        (ROOT / "static/early/letters/scene-gate-slovik.png", 1400, "jpg_from_png"),
        (ROOT / "static/early/letters/scene-missing.jpg", 1400, "jpg"),
        (ROOT / "static/early/letters/scene-sparks.jpg", 1400, "jpg"),
        (ROOT / "static/early/letters/scene-invite.jpg", 1400, "jpg"),
        (ROOT / "static/early/letters/scene-gate.jpg", 1400, "jpg"),
        (ROOT / "static/early/stories/scene-path-empty.png", 1600, "jpg_from_png"),
        (ROOT / "static/early/stories/scene-night-sleep-2.PNG", 1600, "jpg_from_png"),
    ]
    for p in sorted((ROOT / "static/early/slovik").glob("*.png")):
        jobs.append((p, 800, "jpg_from_png"))
    # уже сконвертированные jpg-позы (повторный прогон)
    for p in sorted((ROOT / "static/early/slovik").glob("*.jpg")):
        jobs.append((p, 800, "jpg"))

    total_b = total_a = 0
    for path, max_edge, mode in jobs:
        if not path.is_file():
            continue
        before = path.stat().st_size
        im = Image.open(path)
        im.load()
        im = resize_max(im, max_edge)

        if mode == "png":
            after = save_png(path, im if im.mode == "RGBA" else im.convert("RGBA"))
            out = path
        elif mode == "jpg_from_png":
            out = path.with_suffix(".jpg")
            after = save_jpeg(out, im, quality=90)
            if out.resolve() != path.resolve() and path.exists():
                path.unlink()
        else:
            after = save_jpeg(path, im, quality=90)
            out = path

        # не раздуваем
        if after > before and out == path:
            # откат смысла нет без оригинала — просто печатаем
            pass
        total_b += before
        total_a += after
        print(f"{out.relative_to(ROOT)}: {before // 1024}KB -> {after // 1024}KB")

    print(f"TOTAL: {total_b // 1024}KB -> {total_a // 1024}KB")


if __name__ == "__main__":
    main()
