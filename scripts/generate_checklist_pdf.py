#!/usr/bin/env python3
"""Generate static PDF checklist for quiz emails (Cyrillic via DejaVu, brand style)."""

from __future__ import annotations

import urllib.request
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "quiz-checklist.pdf"
SITE_URL = "https://chitatelstvo.ru"
LOGO_REMOTE = "https://api.chitatelstvo.ru/assets/logo-chitatelstvo-quiz.png"
SIGNOFF = "с теплом, команда Читательства"

BLUE = colors.HexColor("#5B7FA6")
BLUE_PALE = colors.HexColor("#E8F1F8")
LILAC = colors.HexColor("#8F7DA3")
CREAM = colors.HexColor("#F6F4F9")
TEXT = colors.HexColor("#3D5266")
MUTED = colors.HexColor("#6B8499")
BORDER = colors.HexColor("#D4E2EF")

FONT_CANDIDATES = (
    ROOT / "static" / "fonts" / "DejaVuSans.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
)

LOGO_CANDIDATES = (
    ROOT / "static" / "logo-chitatelstvo-quiz.png",
    Path("/var/www/chitatelstvo-assets/logo-chitatelstvo-quiz.png"),
)

ITEMS = [
    "Перечитывает одно и то же место, но не может объяснить, что произошло",
    "Отвечает на вопросы односложно: «не знаю», «нормально»",
    "Путает персонажей или их мотивы",
    "Читает вслух бегло, но не понимает смысл",
    "Не может связать события в одну историю",
    "Пропускает абзацы или «скачет» по тексту",
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


def _find_logo() -> Path | None:
    for path in LOGO_CANDIDATES:
        if path.is_file():
            return path
    dest = ROOT / "static" / "logo-chitatelstvo-quiz.png"
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(LOGO_REMOTE, dest)
        if dest.is_file() and dest.stat().st_size > 0:
            return dest
    except OSError:
        pass
    return None


def _draw_page_frame(canvas, doc) -> None:
    canvas.saveState()
    w, h = A4

    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)

    canvas.setFillColor(colors.white)
    canvas.roundRect(12 * mm, 14 * mm, w - 24 * mm, h - 28 * mm, 10, fill=1, stroke=0)

    canvas.setFillColor(BLUE_PALE)
    canvas.roundRect(12 * mm, h - 52 * mm, w - 24 * mm, 38 * mm, 10, fill=1, stroke=0)

    logo_path = _find_logo()
    if logo_path:
        lw, lh = 28 * mm, 28 * mm
        lx = (w - lw) / 2
        ly = h - 48 * mm
        canvas.drawImage(
            str(logo_path),
            lx,
            ly,
            lw,
            lh,
            mask="auto",
            preserveAspectRatio=True,
        )
        canvas.linkURL(SITE_URL, (lx, ly, lx + lw, ly + lh), relative=0)

    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.6)
    canvas.line(18 * mm, 22 * mm, w - 18 * mm, 22 * mm)

    canvas.setFont(doc.font_name, 8)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(w / 2, 16 * mm, f"chitatelstvo.ru  ·  {SITE_URL}")

    canvas.restoreState()


class ChecklistDoc(SimpleDocTemplate):
    def __init__(self, font_name: str, *args, **kwargs):
        self.font_name = font_name
        super().__init__(*args, **kwargs)

    def handle_pageBegin(self):
        super().handle_pageBegin()
        _draw_page_frame(self.canv, self)


def _item_table(font: str) -> Table:
    rows: list[list] = []
    for index, text in enumerate(ITEMS, start=1):
        rows.append(
            [
                Paragraph(
                    f'<font color="#8F7DA3"><b>{index}</b></font>',
                    ParagraphStyle(
                        "Num",
                        fontName=font,
                        fontSize=11,
                        leading=14,
                        alignment=TA_CENTER,
                    ),
                ),
                Paragraph(
                    text,
                    ParagraphStyle(
                        "ItemText",
                        fontName=font,
                        fontSize=10.5,
                        leading=14,
                        textColor=TEXT,
                        alignment=TA_LEFT,
                    ),
                ),
            ]
        )

    table = Table(rows, colWidths=[10 * mm, 148 * mm], hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, BLUE_PALE]),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("ROUNDEDCORNERS", [4, 4, 4, 4]),
            ]
        )
    )
    return table


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    font = _register_font()

    title_style = ParagraphStyle(
        "Title",
        fontName=font,
        fontSize=17,
        leading=21,
        textColor=BLUE,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    lead_style = ParagraphStyle(
        "Lead",
        fontName=font,
        fontSize=10.5,
        leading=14,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    signoff_style = ParagraphStyle(
        "Signoff",
        fontName=font,
        fontSize=11,
        leading=15,
        textColor=LILAC,
        alignment=TA_CENTER,
        spaceBefore=6,
    )
    link_style = ParagraphStyle(
        "Link",
        fontName=font,
        fontSize=9,
        leading=12,
        textColor=BLUE,
        alignment=TA_CENTER,
        spaceBefore=4,
    )

    story = [
        Spacer(1, 42 * mm),
        Paragraph("10 признаков, что ребёнок не понимает прочитанное", title_style),
        Paragraph("Если заметите 3+ признака — вам будет полезна наша помощь", lead_style),
        HRFlowable(width="88%", thickness=1, color=BORDER, spaceBefore=2, spaceAfter=10),
        _item_table(font),
        Spacer(1, 4 * mm),
        Paragraph(SIGNOFF, signoff_style),
        Paragraph(
            f'<a href="{SITE_URL}" color="#5B7FA6">chitatelstvo.ru</a>',
            link_style,
        ),
    ]

    doc = ChecklistDoc(
        font,
        str(OUT),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=16 * mm,
        bottomMargin=28 * mm,
        title="10 признаков — Читательство",
        author="Читательство",
    )
    doc.build(story)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
