"""Проверка заполненного СКАЗКИ.csv."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "docs" / "google_sheets" / "СКАЗКИ.csv"


def main() -> None:
    with CSV_PATH.open(encoding="utf-8-sig") as f:
        tales = list(csv.DictReader(f))

    empty = [r for r in tales if not (r.get("Сказка (заполнить)") or "").strip()]
    mismatch = [
        r
        for r in tales
        if (r.get("Сказка (заполнить)") or "").strip()
        != (r.get("Название урока (заполнить)") or "").strip()
    ]

    print(f"Всего строк: {len(tales)}")
    print(f"Пустых сказок: {len(empty)}")
    print(f"Сказка != название урока: {len(mismatch)}")

    by_group: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for r in tales:
        t = (r.get("Сказка (заполнить)") or "").strip()
        by_group[r["Группа"]].append((r["Этап"], r["№ сказки в этапе"], t))

    print("Дубликаты текста в одной группе:")
    found = False
    for group, items in by_group.items():
        seen: dict[str, str] = {}
        for stage, num, text in items:
            if text in seen:
                print(f"  {group}: «{text[:60]}» — {seen[text]} и {stage} №{num}")
                found = True
            seen[text] = f"{stage} №{num}"
    if not found:
        print("  нет")


if __name__ == "__main__":
    main()
