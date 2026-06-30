#!/usr/bin/env python3
"""Генерация SVG-контуров лепестков эмоциометра под иллюстрацию.

У каждого лепестка свои углы у внутреннего и внешнего края — границы на рисунке
не радиальные и секторы неравномерные (особенно Интерес и Удивление).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "static" / "emotion_wheel_petals.json"

CX, CY = 500, 500
RI, RO = 92, 482


def p(deg: float, r: float) -> list[float]:
    rad = math.radians(deg - 90)
    return [round(CX + r * math.cos(rad), 1), round(CY + r * math.sin(rad), 1)]


def lerp_angle(a0: float, a1: float, t: float) -> float:
    return a0 + (a1 - a0) * t


def petal_path(
    a0_in: float,
    a1_in: float,
    a0_out: float,
    a1_out: float,
    *,
    ri: float = RI,
    ro: float = RO,
    outer_n: int = 15,
    inner_n: int = 5,
) -> str:
    """Контур: левая граница → дуга снаружи → правая граница → дуга у центра."""
    pts: list[list[float]] = [p(a0_in, ri)]

    for i in range(1, 4):
        t = i / 3
        ang = lerp_angle(a0_in, a0_out, t)
        r = ri + (ro - ri) * t * 0.35
        pts.append(p(ang, r))

    for i in range(outer_n):
        t = i / (outer_n - 1)
        ang = lerp_angle(a0_out, a1_out, t)
        bulge = 1.8 * math.sin(math.pi * t)
        pts.append(p(ang, ro + bulge))

    for i in range(1, 4):
        t = 1 - i / 3
        ang = lerp_angle(a1_in, a1_out, t)
        r = ri + (ro - ri) * t * 0.35
        pts.append(p(ang, r))

    for i in range(1, inner_n):
        t = i / inner_n
        ang = lerp_angle(a1_in, a0_in, t)
        pts.append(p(ang, ri - 1.5))

    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for x, y in pts[1:]:
        d += f" L {x:.1f} {y:.1f}"
    return d + " Z"


# Углы по часовой от верха (0° = Радость вверху).
# a0_in/a1_in — у белого круга в центре, a0_out/a1_out — у внешнего ободка.
SPECS: list[tuple[str, float, float, float, float, int]] = [
    ("joy", -21, 13, -23, 17, 13),
    ("interest", 13, 44, 17, 52, 17),
    ("surprise", 44, 78, 52, 87, 17),
    ("sadness", 78, 111, 80, 113, 13),
    ("fear", 111, 143, 112, 144, 13),
    ("anger", 143, 175, 144, 176, 13),
    ("resentment", 175, 207, 176, 208, 13),
    ("tired", 207, 239, 208, 240, 13),
    ("pride", 239, 271, 240, 272, 13),
    ("calm", 271, 339, 272, 341, 13),
]


def main() -> None:
    out = {
        name: petal_path(a0_in, a1_in, a0_out, a1_out, outer_n=n)
        for name, a0_in, a1_in, a0_out, a1_out, n in SPECS
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
