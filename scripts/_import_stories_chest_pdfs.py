# -*- coding: utf-8 -*-
"""Обновить PDF и превью сундука «Первые истории» из папки на рабочем столе."""
from __future__ import annotations

import shutil
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\Оля\Desktop\ЧИТАТЕЛЬСТВО\Первая история\Вводный")
DST = ROOT / "static" / "chest" / "rewards" / "early-stories-stage1-tale-00"

ITEMS = [
    ("gift-1", "дорисуй дом"),
    ("gift-2", "обведи кота"),
    ("gift-3", "обведи фразу"),
    ("gift-4", "пройди лабиринт"),
    ("gift-5", "раскрась словика"),
]


def find_pdf(needle: str) -> Path:
    hits = [p for p in SRC.glob("*.pdf") if needle in p.stem.lower().replace("ё", "е")]
    if len(hits) != 1:
        raise SystemExit(f"Need 1 PDF for {needle!r}, got {[p.name for p in hits]}")
    return hits[0]


def render_previews(pdf: Path, stem: str) -> None:
    doc = fitz.open(pdf)
    page = doc[0]
    zoom = min(720 / page.rect.width, 2.0)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    png = DST / f"{stem}.png"
    jpg = DST / f"{stem}.jpg"
    pix.save(str(png))
    jpg.write_bytes(pix.tobytes("jpeg"))
    doc.close()
    print(f"  preview {png.name} ({png.stat().st_size // 1024} KB), {jpg.name}")


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"Source folder not found: {SRC}")
    DST.mkdir(parents=True, exist_ok=True)
    for stem, needle in ITEMS:
        src = find_pdf(needle)
        pdf_dst = DST / f"{stem}.pdf"
        shutil.copy2(src, pdf_dst)
        print(f"{stem}: {src.name} -> {pdf_dst.name}")
        render_previews(pdf_dst, stem)
    print("OK", DST)


if __name__ == "__main__":
    main()
