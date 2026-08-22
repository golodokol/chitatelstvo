#!/usr/bin/env python3
"""Проверка станций shape_rebus: каждая фигурка в шифре есть в ключе, пары уникальны."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "lessons" / "catalog"


def check_station(path: Path, station: dict) -> list[str]:
    errors: list[str] = []
    sid = station.get("id") or station.get("title") or "?"
    legend = station.get("legend") or []
    by_pair: dict[str, str] = {}
    by_letter: dict[str, dict] = {}
    for i, item in enumerate(legend):
        shape = (item or {}).get("shape")
        tone = (item or {}).get("tone")
        letter = (item or {}).get("letter")
        if not shape or not tone or not letter:
            errors.append(f"{path.name}:{sid}: legend[{i}] incomplete")
            continue
        pair = f"{shape}|{tone}"
        if pair in by_pair:
            errors.append(
                f"{path.name}:{sid}: duplicate figure {pair} for {by_pair[pair]!r} and {letter!r}"
            )
        by_pair[pair] = letter
        if letter in by_letter:
            errors.append(f"{path.name}:{sid}: letter {letter!r} twice in legend")
        by_letter[letter] = item

    rounds = station.get("rounds") or [station]
    for ri, rnd in enumerate(rounds):
        for ti, tok in enumerate(rnd.get("cipher") or []):
            letter = (tok or {}).get("letter")
            if letter and letter in by_letter:
                continue
            pair = f"{(tok or {}).get('shape')}|{(tok or {}).get('tone')}"
            if pair not in by_pair:
                errors.append(
                    f"{path.name}:{sid}: round {ri + 1} token {ti + 1} {pair} not in legend"
                )
            elif letter and by_pair[pair] != letter:
                errors.append(
                    f"{path.name}:{sid}: round {ri + 1} token {ti + 1} letter "
                    f"{letter!r} != legend {by_pair[pair]!r}"
                )
    return errors


def main() -> int:
    errors: list[str] = []
    for path in sorted(CATALOG.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for station in data.get("stations") or []:
            if station.get("kind") != "shape_rebus":
                continue
            errors.extend(check_station(path, station))
    if errors:
        print("SHAPE REBUS ERRORS:")
        for err in errors:
            print(" -", err)
        return 1
    print("OK: all shape_rebus stations consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
