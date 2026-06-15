#!/usr/bin/env python3
"""Generate static PDF checklist for quiz emails (Cyrillic via DejaVu)."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "quiz-checklist.pdf"
SIGNOFF = "с теплом, команда Читательства"

FONT_CANDIDATES = (
    ROOT / "static" / "fonts" / "DejaVuSans.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
)

ITEMS = [
    "Перечитывает одно и то же место, но не может объяснить, что произошло",
    "Отвечает на вопросы односложно: «не знаю», «нормально»",
    "Путает персонажей или их мотивы",
    "Читает вслух бегло, но не понимает смысл",
    "Не может связать события в одну историю",
    "Пропускает абзацы или «скакает» по тексту",
    "Путает фантазию и факты из текста",
    "Избегает книг с большим количеством текста",
    "Раздражается, когда просят пересказать",
    "Не может ответить «почему герой так поступил»",
]


def _find_font() -> Path:
    for path in FONT_CANDIDATES:
        if path.is_file():
            return path
    raise FileNotFoundError(
        "Не найден DejaVuSans.ttf. Установите fonts-dejavu-core или положите шрифт в static/fonts/."
    )


def _register_font() -> str:
    font_path = _find_font()
    name = "DejaVuSans"
    if name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(name, str(font_path)))
    return name


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    font = _register_font()

    title_style = ParagraphStyle(
        "Title",
        fontName=font,
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#5B7FA6"),
        alignment=1,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        fontName=font,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#5B7FA6"),
        alignment=1,
        spaceAfter=10,
    )
    lead_style = ParagraphStyle(
        "Lead",
        fontName=font,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#6B8499"),
        alignment=1,
        spaceAfter=16,
    )
    item_style = ParagraphStyle(
        "Item",
        fontName=font,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#3D5266"),
        leftIndent=8,
        spaceAfter=8,
    )
    signoff_style = ParagraphStyle(
        "Signoff",
        fontName=font,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#8F7DA3"),
        alignment=1,
        spaceBefore=18,
    )

    story = [
        Paragraph("Читательство", title_style),
        Paragraph("10 признаков, что ребёнок не понимает прочитанное", subtitle_style),
        Paragraph("Если заметите 3+ признака — вам будет полезна наша помощь", lead_style),
        Spacer(1, 4 * mm),
    ]
    for index, text in enumerate(ITEMS, start=1):
        story.append(Paragraph(f"{index}. {text}", item_style))
    story.append(Paragraph(SIGNOFF, signoff_style))

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="10 признаков — Читательство",
        author="Читательство",
    )
    doc.build(story)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
