# -*- coding: utf-8 -*-
from pathlib import Path
import shutil

import fitz

SRC = Path(r"C:\Users\Оля\Desktop\ЧИТАТЕЛЬСТВО\Буквы оживают")
DST = Path(__file__).resolve().parents[1] / "static" / "chest" / "rewards" / "early-letters-stage1-tale-00"

ITEMS = [
    ("gift-1", "Арбуз"),
    ("gift-2", "букву"),
    ("gift-3", "лабиринт"),
    ("gift-4", "словик"),
]


def find_pdf(needle: str) -> Path:
    hits = [p for p in SRC.glob("*.pdf") if needle.lower() in p.stem.lower()]
    if len(hits) != 1:
        raise SystemExit(f"Need 1 PDF for {needle!r}, got {[p.name for p in hits]}")
    return hits[0]


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for stem, needle in ITEMS:
        src = find_pdf(needle)
        pdf_dst = DST / f"{stem}.pdf"
        png_dst = DST / f"{stem}.png"
        shutil.copy2(src, pdf_dst)
        doc = fitz.open(src)
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(0.85, 0.85), alpha=False)
        pix.save(png_dst)
        doc.close()
        print(f"{stem}: {src.name} -> {pdf_dst.name} + {png_dst.name} ({png_dst.stat().st_size})")
    print("OK", DST)


if __name__ == "__main__":
    main()
