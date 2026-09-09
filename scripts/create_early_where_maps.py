"""Create eight "where the hero is now" variants of the Land of Sounds map."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
LETTERS = ROOT / "static" / "early" / "letters"
BASE_PATH = LETTERS / "scene-map-sounds-final.png"

# Lesson pads in lesson order 1–8, fractions of the 1280x720 map.
LESSON_PADS = (
    (0.1609, 0.5681),  # 1 — car / машина
    (0.2070, 0.3694),  # 2 — cave / У
    (0.4422, 0.3694),  # 3 — pond / О
    (0.6523, 0.3889),  # 4 — snake
    (0.7078, 0.6250),  # 5 — pavilion / Р
    (0.5125, 0.6972),  # 6 — bridge / слоги
    (0.6227, 0.9111),  # 7 — glowing spheres
    (0.8734, 0.9333),  # 8 — flower garden
)


def four_point_star(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    outer: int,
    inner: int,
    fill: tuple[int, int, int, int],
) -> None:
    x, y = center
    points = [
        (x, y - outer),
        (x + inner, y - inner),
        (x + outer, y),
        (x + inner, y + inner),
        (x, y + outer),
        (x - inner, y + inner),
        (x - outer, y),
        (x - inner, y - inner),
    ]
    draw.polygon(points, fill=fill)


def add_current_lesson_marker(
    base: Image.Image,
    center: tuple[int, int],
) -> Image.Image:
    width, height = base.size
    x, y = center
    radius_x = round(width * 0.041)
    radius_y = round(height * 0.043)

    # A broad diffused halo keeps the map readable and does not cover the art.
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        (x - radius_x, y - radius_y, x + radius_x, y + radius_y),
        fill=(255, 190, 62, 175),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(max(10, round(width * 0.011))))
    marked = Image.alpha_composite(base, glow)

    accent = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(accent)
    line_width = max(3, round(width * 0.003))
    draw.ellipse(
        (
            x - round(radius_x * 0.69),
            y - round(radius_y * 0.60),
            x + round(radius_x * 0.69),
            y + round(radius_y * 0.60),
        ),
        outline=(239, 159, 42, 220),
        width=line_width,
    )

    # Small hand-painted four-pointed sparks around the current pad.
    spark_specs = (
        (-radius_x, -round(radius_y * 0.65), 8),
        (round(radius_x * 0.93), -round(radius_y * 0.48), 6),
        (-round(radius_x * 0.82), round(radius_y * 0.70), 5),
    )
    for dx, dy, size in spark_specs:
        four_point_star(
            draw,
            (x + dx, y + dy),
            size,
            max(2, size // 3),
            (255, 221, 116, 235),
        )

    # Compact curved terracotta-and-gold arrow, pointing at the active pad.
    start = (x + round(width * 0.043), y - round(height * 0.071))
    control = (x + round(width * 0.017), y - round(height * 0.087))
    end = (x + round(width * 0.012), y - round(height * 0.030))
    curve: list[tuple[int, int]] = []
    for step in range(21):
        t = step / 20
        one_minus_t = 1 - t
        curve.append(
            (
                round(
                    one_minus_t * one_minus_t * start[0]
                    + 2 * one_minus_t * t * control[0]
                    + t * t * end[0]
                ),
                round(
                    one_minus_t * one_minus_t * start[1]
                    + 2 * one_minus_t * t * control[1]
                    + t * t * end[1]
                ),
            )
        )
    draw.line(curve, fill=(157, 91, 45, 210), width=line_width + 4, joint="curve")
    draw.line(curve, fill=(239, 174, 55, 245), width=line_width, joint="curve")

    previous = curve[-2]
    angle = math.atan2(end[1] - previous[1], end[0] - previous[0])
    head_length = round(width * 0.015)
    head_spread = math.radians(34)
    head = [
        end,
        (
            round(end[0] - head_length * math.cos(angle - head_spread)),
            round(end[1] - head_length * math.sin(angle - head_spread)),
        ),
        (
            round(end[0] - head_length * math.cos(angle + head_spread)),
            round(end[1] - head_length * math.sin(angle + head_spread)),
        ),
    ]
    draw.polygon(head, fill=(239, 174, 55, 245))
    draw.line(head + [end], fill=(157, 91, 45, 220), width=max(2, line_width // 2))

    return Image.alpha_composite(marked, accent)


def render() -> list[Path]:
    base = Image.open(BASE_PATH).convert("RGBA")
    width, height = base.size
    outputs: list[Path] = []

    for lesson, (x_ratio, y_ratio) in enumerate(LESSON_PADS, start=1):
        center = (round(width * x_ratio), round(height * y_ratio))
        frame = add_current_lesson_marker(base.copy(), center)

        output = LETTERS / f"scene-map-sounds-where-{lesson:02d}.png"
        frame.convert("RGB").save(output, "PNG", optimize=True)
        outputs.append(output)

    return outputs


if __name__ == "__main__":
    for path in render():
        print(path.relative_to(ROOT))
