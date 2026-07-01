#!/usr/bin/env python3
"""SVG-контуры лепестков: дуговые секторы с калибровкой под PNG."""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "static" / "emotion_wheel_petals.json"

# Калибровка под emotion-wheel.png (viewBox 0 0 1000 1000)
CX, CY = 501.0, 497.0
RI, RO = 80.0, 486.0


def pt(deg: float, r: float) -> tuple[float, float]:
    rad = math.radians(deg - 90)
    return CX + r * math.cos(rad), CY + r * math.sin(rad)


def wedge_path(a0: float, a1: float) -> str:
    """Симметричный клин от a0 до a1 (градусы по часовой от верха)."""
    span = a1 - a0
    large = 1 if span > 180 else 0
    x1i, y1i = pt(a0, RI)
    x1o, y1o = pt(a0, RO)
    x2o, y2o = pt(a1, RO)
    x2i, y2i = pt(a1, RI)
    return (
        f"M {x1i:.1f} {y1i:.1f}"
        f" L {x1o:.1f} {y1o:.1f}"
        f" A {RO:.1f} {RO:.1f} 0 {large} 1 {x2o:.1f} {y2o:.1f}"
        f" L {x2i:.1f} {y2i:.1f}"
        f" A {RI:.1f} {RI:.1f} 0 {large} 0 {x1i:.1f} {y1i:.1f}"
        f" Z"
    )


def wedge_path_asym(a0_in: float, a1_in: float, a0_out: float, a1_out: float) -> str:
    """Клин с разными углами у центра и у края (границы на рисунке не радиальные)."""
    span_out = a1_out - a0_out
    large = 1 if span_out > 180 else 0
    x0i, y0i = pt(a0_in, RI)
    x0o, y0o = pt(a0_out, RO)
    x1o, y1o = pt(a1_out, RO)
    x1i, y1i = pt(a1_in, RI)
    return (
        f"M {x0i:.1f} {y0i:.1f}"
        f" L {x0o:.1f} {y0o:.1f}"
        f" A {RO:.1f} {RO:.1f} 0 {large} 1 {x1o:.1f} {y1o:.1f}"
        f" L {x1i:.1f} {y1i:.1f}"
        f" A {RI:.1f} {RI:.1f} 0 {large} 0 {x0i:.1f} {y0i:.1f}"
        f" Z"
    )


# Симметричные лепестки (не трогаем).
SYMMETRIC: list[tuple[str, float, float]] = [
    ("joy", -24.5, 11.5),
    ("interest", 11.5, 49.0),
    ("surprise", 49.0, 86.5),
    ("sadness", 86.5, 128.0),
    ("fear", 128.0, 162.0),
    ("anger", 162.0, 196.0),
    ("resentment", 196.0, 236.0),
]

# Усталость / гордость / спокойствие — сдвиг по часовой, разные углы у центра и края.
# (a0_in, a1_in, a0_out, a1_out)
ASYMMETRIC: list[tuple[str, float, float, float, float]] = [
    ("tired", 236.0, 270.0, 252.0, 288.0),
    ("pride", 270.0, 306.0, 288.0, 320.0),
    ("calm", 306.0, 332.0, 320.0, 335.5),
]


def main() -> None:
    out: dict[str, str] = {}
    for name, a0, a1 in SYMMETRIC:
        out[name] = wedge_path(a0, a1)
    for name, a0_in, a1_in, a0_out, a1_out in ASYMMETRIC:
        out[name] = wedge_path_asym(a0_in, a1_in, a0_out, a1_out)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
