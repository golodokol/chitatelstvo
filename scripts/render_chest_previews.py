"""Render PNG previews from chest reward PDFs (first page)."""

from __future__ import annotations

import argparse
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
REWARDS = ROOT / "static" / "chest" / "rewards"


def render_pdf_preview(pdf_path: Path, png_path: Path, *, max_width: int = 480) -> None:
    doc = fitz.open(pdf_path)
    page = doc[0]
    zoom = min(max_width / page.rect.width, 2.0)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    pix.save(str(png_path))
    doc.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Render chest PDF previews to PNG")
    parser.add_argument("tale_slug", nargs="?", default="grade-1-stage1-tale-01")
    parser.add_argument("--max-width", type=int, default=480)
    args = parser.parse_args()

    folder = REWARDS / args.tale_slug
    if not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}")

    for pdf in sorted(folder.glob("creative-*.pdf")):
        png = pdf.with_suffix(".png")
        render_pdf_preview(pdf, png, max_width=args.max_width)
        print(f"{png.relative_to(ROOT)} ({png.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
