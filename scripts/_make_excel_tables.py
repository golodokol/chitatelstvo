"""Write Excel-friendly copies of email template tables (no extra deps)."""
from __future__ import annotations

import csv
import zipfile
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

BASE = Path(__file__).resolve().parents[1] / "docs" / "email-templates"

TABLES = [
    ("recommendation-rules.csv", "recommendation-rules.xlsx", "Правила рекомендаций"),
    ("recommendation-rules.csv", "recommendation-rules-final.xlsx", "Правила рекомендаций"),
    ("email-triggers.csv", "email-triggers.xlsx", "Триггеры писем"),
    (
        "founder-trial-letter-placeholders.csv",
        "founder-trial-letter-placeholders.xlsx",
        "Плейсхолдеры",
    ),
]


def col_letter(index: int) -> str:
    result = ""
    n = index
    while n:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def read_csv_rows(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f, delimiter=";"))


def write_utf16_csv(src: Path, dst: Path) -> None:
    rows = read_csv_rows(src)
    with dst.open("w", encoding="utf-16", newline="") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_ALL)
        writer.writerows(rows)


def build_xlsx(rows: list[list[str]]) -> bytes:
    shared: list[str] = []
    index: dict[str, int] = {}

    def string_index(value: str) -> int:
        if value not in index:
            index[value] = len(shared)
            shared.append(value)
        return index[value]

    for row in rows:
        for cell in row:
            string_index(cell)

    sst_parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        f'count="{sum(len(r) for r in rows)}" uniqueCount="{len(shared)}">',
    ]
    for item in shared:
        sst_parts.append(f"<si><t>{escape(item)}</t></si>")
    sst_parts.append("</sst>")
    shared_strings = "".join(sst_parts)

    sheet_parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
        "<sheetData>",
    ]
    for r_idx, row in enumerate(rows, 1):
        sheet_parts.append(f'<row r="{r_idx}">')
        for c_idx, cell in enumerate(row, 1):
            ref = f"{col_letter(c_idx)}{r_idx}"
            si = string_index(cell)
            sheet_parts.append(f'<c r="{ref}" t="s"><v>{si}</v></c>')
        sheet_parts.append("</row>")
    sheet_parts.extend(["</sheetData>", "</worksheet>"])
    sheet_xml = "".join(sheet_parts)

    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets>'
        "</workbook>"
    )
    workbook_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" '
        'Target="sharedStrings.xml"/>'
        "</Relationships>"
    )
    root_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        "</Relationships>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/sharedStrings.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
        "</Types>"
    )

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
        zf.writestr("xl/sharedStrings.xml", shared_strings)
    return buf.getvalue()


def main() -> None:
    for csv_name, xlsx_name, _title in TABLES:
        src = BASE / csv_name
        rows = read_csv_rows(src)
        write_utf16_csv(src, BASE / csv_name.replace(".csv", "-excel.csv"))
        xlsx_path = BASE / xlsx_name
        try:
            xlsx_path.write_bytes(build_xlsx(rows))
            print(f"ok: {xlsx_name}")
        except PermissionError:
            alt = BASE / xlsx_name.replace(".xlsx", "-new.xlsx")
            alt.write_bytes(build_xlsx(rows))
            print(f"locked {xlsx_name} -> wrote {alt.name}")


if __name__ == "__main__":
    main()
