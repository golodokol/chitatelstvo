"""Prepare generated lesson PNGs for direct use in the early-course UI."""

from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
LETTERS = ROOT / "static" / "early" / "letters"
STORIES = ROOT / "static" / "early" / "stories"

LETTER_PNGS = [
    "ui-star-board.png",
    "bush-green.png",
    "pebble-hero.png",
    "letter-m-hero.png",
    "letter-m-small.png",
    "letter-u-hero.png",
    "letter-u-small.png",
    "letter-o-hero.png",
    "letter-o-small.png",
    "letter-s-hero.png",
    "letter-s-small.png",
    "sun-smile.png",
    "snake-hiss.png",
    "wind-howl.png",
    "bear-wise.png",
    "som-fish.png",
    "box-square.png",
    "slot-white.png",
    "tile-word.png",
    "badge-silver.png",
]

STORY_PNGS = [
    "ui-reward-books.png",
    "slovik-screen.png",
    "box-closed.png",
    "box-empty.png",
    "box-ball.png",
    "cat-happy.png",
    "window-frame.png",
    "ball-under-chair.png",
    "ball-on-sofa.png",
    "cat-run.png",
    "cat-catch.png",
]


def remove_background(path: Path) -> None:
    """Remove generated white/black/checkerboard backgrounds.

    Generated cutouts use achromatic backgrounds, while the illustrated objects
    are colored. Border sampling also handles the fake gray checkerboard that
    some generations bake into the RGB image.
    """
    image = Image.open(path).convert("RGB")
    width, height = image.size
    edge = max(8, min(width, height) // 80)
    border_pixels = (
        list(image.crop((0, 0, width, edge)).getdata())
        + list(image.crop((0, height - edge, width, height)).getdata())
        + list(image.crop((0, 0, edge, height)).getdata())
        + list(image.crop((width - edge, 0, width, height)).getdata())
    )
    counts = [0] * 256
    for red, green, blue in border_pixels:
        if max(red, green, blue) - min(red, green, blue) <= 10:
            counts[round((red + green + blue) / 3)] += 1
    minimum_count = max(20, len(border_pixels) // 200)
    levels = [level for level, count in enumerate(counts) if count >= minimum_count]
    if not levels:
        levels = [255]

    red, green, blue = image.split()
    maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    minimum = ImageChops.darker(ImageChops.darker(red, green), blue)
    saturation = ImageChops.subtract(maximum, minimum)
    low_saturation = saturation.point(lambda value: 255 if value <= 11 else 0)
    luminance = ImageOps.grayscale(image)
    level_lut = [
        255 if any(abs(value - level) <= 5 for level in levels) else 0
        for value in range(256)
    ]
    near_border_level = luminance.point(level_lut)
    background = ImageChops.multiply(low_saturation, near_border_level)
    alpha_image = ImageOps.invert(background).filter(ImageFilter.GaussianBlur(0.55))
    result = image.convert("RGBA")
    result.putalpha(alpha_image)
    result.save(path, "PNG", optimize=True)


def masked_piece(source: Image.Image, polygon: list[tuple[int, int]], target: Path) -> None:
    mask = Image.new("L", source.size, 0)
    ImageDraw.Draw(mask).polygon(polygon, fill=255)
    alpha = Image.composite(source.getchannel("A"), Image.new("L", source.size, 0), mask)
    piece = source.copy()
    piece.putalpha(alpha)
    piece.save(target, "PNG", optimize=True)


def make_puzzle_parts() -> None:
    letter_m = Image.open(LETTERS / "letter-m-hero.png").convert("RGBA")
    width, height = letter_m.size
    left_x = int(width * 0.39)
    right_x = int(width * 0.63)
    masked_piece(
        letter_m,
        [(0, 0), (left_x, 0), (left_x, height), (0, height)],
        LETTERS / "m-part-left.png",
    )
    masked_piece(
        letter_m,
        [(right_x, 0), (width, 0), (width, height), (right_x, height)],
        LETTERS / "m-part-right.png",
    )
    masked_piece(
        letter_m,
        [(left_x, 0), (right_x, 0), (right_x, height), (left_x, height)],
        LETTERS / "m-part-bar.png",
    )

    letter_o = Image.open(LETTERS / "letter-o-hero.png").convert("RGBA")
    width, height = letter_o.size
    overlap = int(height * 0.04)
    masked_piece(
        letter_o,
        [(0, 0), (width, 0), (width, height // 2 + overlap), (0, height // 2 + overlap)],
        LETTERS / "o-part-arc.png",
    )


def make_named_reuse_files() -> None:
    shutil.copy2(LETTERS / "cup.png", LETTERS / "round-cup.png")
    shutil.copy2(LETTERS / "ball.png", LETTERS / "round-ball.png")
    shutil.copy2(LETTERS / "sun-smile.png", STORIES / "sun-clear.png")


def main() -> None:
    for directory, names in ((LETTERS, LETTER_PNGS), (STORIES, STORY_PNGS)):
        for name in names:
            path = directory / name
            remove_background(path)
            print(f"transparent: {path.relative_to(ROOT)}")
    make_puzzle_parts()
    make_named_reuse_files()
    print("created: static/early/letters/m-part-left.png")
    print("created: static/early/letters/m-part-right.png")
    print("created: static/early/letters/m-part-bar.png")
    print("created: static/early/letters/o-part-arc.png")
    print("created named reuse files: round-cup.png, round-ball.png, sun-clear.png")


if __name__ == "__main__":
    main()
