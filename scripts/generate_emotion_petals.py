#!/usr/bin/env python3
"""Генерация SVG-контуров лепестков эмоциометра под иллюстрацию."""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "static" / "emotion_wheel_petals.json"

CX, CY = 500, 500


def p(deg: float, r: float) -> list[float]:
    rad = math.radians(deg - 90)
    return [round(CX + r * math.cos(rad), 1), round(CY + r * math.sin(rad), 1)]


def petal_path(a0: float, a1: float, ri: float = 84, ro: float = 490, outer_n: int = 13) -> str:
    w = a1 - a0
    pts = [p(a0, ri)]
    for i in range(outer_n):
        t = i / (outer_n - 1)
        ang = a0 + w * t
        bulge = 2.0 * math.sin(math.pi * t)
        pts.append(p(ang, ro + bulge))
    pts.append(p(a1, ri))
    for t in (0.75, 0.5, 0.25):
        pts.append(p(a0 + w * t, ri - 2.5))
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for x, y in pts[1:]:
        d += f" L {x:.1f} {y:.1f}"
    return d + " Z"


# Границы лепестков по часовой стрелке от верха (градусы).
SPECS: list[tuple[str, float, float, int]] = [
    ("joy", -19, 17, 11),
    ("interest", 17, 49, 15),
    ("surprise", 49, 83, 15),
    ("sadness", 83, 115, 11),
    ("fear", 115, 147, 11),
    ("anger", 147, 179, 11),
    ("resentment", 179, 211, 11),
    ("tired", 211, 243, 11),
    ("pride", 243, 275, 11),
    ("calm", 275, 341, 11),
]


def main() -> None:
    out = {name: petal_path(a0, a1, outer_n=n) for name, a0, a1, n in SPECS}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
