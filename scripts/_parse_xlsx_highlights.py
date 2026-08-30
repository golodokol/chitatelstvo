"""Parse yellow-highlighted cells from edited xlsx tables."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
BASE = Path(__file__).resolve().parents[1] / "docs" / "email-templates"
OUT = BASE / "_parsed-highlights.txt"

YELLOW_RGB = {
    "FFFFEB9C",
    "FFFFCC99",
    "FFFFFFCC",
    "FFFFC000",
    "FFFFFF00",
    "FFFF99",
    "FFD966",
    "FFF2CC",
    "FFC000",
    "FFC6EFCE",
    "FFFFC7CE",
}


def col_sort(col: str) -> tuple[int, str]:
    return (len(col), col)


def parse_xlsx(path: Path) -> tuple[dict[str, str], list[dict], dict[int, dict[str, str]]]:
    with zipfile.ZipFile(path) as z:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall(".//m:si", NS):
                shared.append("".join(n.text or "" for n in si.findall(".//m:t", NS)))

        styles = ET.fromstring(z.read("xl/styles.xml"))
        fills: list[str] = []
        for fill in styles.findall(".//m:fill", NS):
            fg = fill.find(".//m:fgColor", NS)
            if fg is not None:
                rgb = fg.get("rgb")
                theme = fg.get("theme")
                fills.append((rgb or f"theme:{theme}").upper())
            else:
                fills.append("")

        xfs = styles.findall(".//m:cellXfs/m:xf", NS)
        style_to_fill = [fills[int(xf.get("fillId", 0))] for xf in xfs]

        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        header: dict[str, str] = {}
        highlighted: list[dict] = []
        all_rows: dict[int, dict[str, str]] = {}

        for cell in sheet.findall(".//m:c", NS):
            ref = cell.get("r", "")
            col_match = re.match(r"([A-Z]+)", ref)
            row_match = re.match(r"[A-Z]+(\d+)", ref)
            if not col_match or not row_match:
                continue
            col = col_match.group(1)
            row = int(row_match.group(1))
            style = int(cell.get("s", 0))
            fill = style_to_fill[style] if style < len(style_to_fill) else ""

            value_elem = cell.find("m:v", NS)
            inline = cell.find("m:is", NS)
            if cell.get("t") == "s" and value_elem is not None:
                value = shared[int(value_elem.text)]
            elif value_elem is not None:
                value = value_elem.text or ""
            elif inline is not None:
                value = "".join(n.text or "" for n in inline.findall(".//m:t", NS))
            else:
                value = ""

            all_rows.setdefault(row, {})[col] = value
            if row == 1:
                header[col] = value

            fill_up = fill.upper()
            is_yellow = fill_up in YELLOW_RGB or fill_up.startswith("THEME:4") or fill_up.startswith("THEME:5")
            if is_yellow and (value.strip() or row > 1):
                highlighted.append(
                    {
                        "ref": ref,
                        "row": row,
                        "col": col,
                        "header": header.get(col, col),
                        "fill": fill,
                        "value": value,
                    }
                )

    return header, highlighted, all_rows


def main() -> None:
    lines: list[str] = []
    for fname in ("recommendation-rules.xlsx", "founder-trial-letter-placeholders.xlsx"):
        path = BASE / fname
        lines.append("=" * 60)
        lines.append(fname)
        header, highlighted, all_rows = parse_xlsx(path)
        lines.append("HIGHLIGHTED CELLS:")
        if highlighted:
            for item in highlighted:
                lines.append(
                    f"  {item['ref']} [{item['header']}]: {item['value']} (fill={item['fill']})"
                )
        else:
            lines.append("  (none detected)")

        lines.append("ALL DATA ROWS:")
        for row_num in sorted(all_rows):
            if row_num == 1:
                continue
            cols = sorted(all_rows[row_num].keys(), key=col_sort)
            parts = [
                f"{header.get(c, c)}={all_rows[row_num].get(c, '')}"
                for c in cols
                if all_rows[row_num].get(c, "")
            ]
            if parts:
                lines.append(f"  row {row_num}: " + " || ".join(parts))
        lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"written {OUT}")


if __name__ == "__main__":
    main()
