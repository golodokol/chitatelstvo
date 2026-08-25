# -*- coding: utf-8 -*-
"""Убрать белый квадрат у пробных бейджей и сжать до ~360px RGBA."""
from __future__ import annotations

import struct
import zlib
from collections import deque
from pathlib import Path

# deque used in knockout flood-fill

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "docs" / "images"
FILES = [
    "gamify-badge-spark-hunter.png",
    "gamify-badge-chest-keeper.png",
    "gamify-badge-syllable-master.png",
    "gamify-badge-letter-m.png",
    "gamify-badge-word-book.png",
    "gamify-badge-slovik-friend.png",
]
TARGET = 360


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png(path: Path) -> tuple[int, int, list[bytearray]]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not png: {path}")
    pos = 8
    ihdr = None
    idat = b""
    while pos < len(data):
        ln = struct.unpack(">I", data[pos : pos + 4])[0]
        typ = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + ln]
        pos += 12 + ln
        if typ == b"IHDR":
            ihdr = chunk
        elif typ == b"IDAT":
            idat += chunk
        elif typ == b"IEND":
            break
    assert ihdr is not None
    w, h, bit, color, _c, _f, _i = struct.unpack(">IIBBBBB", ihdr[:13])
    if bit != 8 or color not in (2, 6):
        raise ValueError(f"need 8-bit RGB/RGBA, got bit={bit} color={color} in {path.name}")
    bpp = 3 if color == 2 else 4
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows_src: list[bytearray] = []
    i = 0
    prev = bytearray(stride)
    for _ in range(h):
        ft = raw[i]
        i += 1
        row = bytearray(raw[i : i + stride])
        i += stride
        if ft == 1:
            for x in range(stride):
                row[x] = (row[x] + (row[x - bpp] if x >= bpp else 0)) & 255
        elif ft == 2:
            for x in range(stride):
                row[x] = (row[x] + prev[x]) & 255
        elif ft == 3:
            for x in range(stride):
                left = row[x - bpp] if x >= bpp else 0
                row[x] = (row[x] + ((left + prev[x]) // 2)) & 255
        elif ft == 4:
            for x in range(stride):
                a = row[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                row[x] = (row[x] + _paeth(a, b, c)) & 255
        rows_src.append(row)
        prev = row

    rows: list[bytearray] = []
    for row in rows_src:
        if color == 6:
            rows.append(bytearray(row))
            continue
        out = bytearray(w * 4)
        for x in range(w):
            out[x * 4] = row[x * 3]
            out[x * 4 + 1] = row[x * 3 + 1]
            out[x * 4 + 2] = row[x * 3 + 2]
            out[x * 4 + 3] = 255
        rows.append(out)
    return w, h, rows


def write_png(path: Path, w: int, h: int, rows: list[bytearray]) -> None:
    raw = bytearray()
    for row in rows:
        raw.append(0)
        raw.extend(row)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)

    def chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def sample_bg(rows: list[bytearray], w: int, h: int) -> tuple[int, int, int]:
    samples: list[tuple[int, int, int]] = []
    for y in (0, 1, 2, h - 1, h - 2, h - 3):
        for x in (0, 1, 2, w - 1, w - 2, w - 3):
            if 0 <= y < h and 0 <= x < w:
                i = x * 4
                samples.append((rows[y][i], rows[y][i + 1], rows[y][i + 2]))
    n = len(samples) or 1
    return tuple(sum(c[k] for c in samples) // n for k in range(3))  # type: ignore[return-value]


def is_bg(r: int, g: int, b: int, bg: tuple[int, int, int]) -> bool:
    dist = ((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2) ** 0.5
    chroma = max(r, g, b) - min(r, g, b)
    # почти белый / фон карточки
    if min(r, g, b) > 235 and chroma < 18:
        return True
    if dist < 42 and chroma < 28:
        return True
    if dist < 28:
        return True
    return False


def knockout(rows: list[bytearray], w: int, h: int) -> tuple[int, int, int]:
    bg = sample_bg(rows, w, h)
    mark = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            q.append((x, y))
            mark[y][x] = True
    for y in range(h):
        for x in (0, w - 1):
            if not mark[y][x]:
                q.append((x, y))
                mark[y][x] = True
    bg_set: set[tuple[int, int]] = set()
    while q:
        x, y = q.popleft()
        i = x * 4
        r, g, b = rows[y][i], rows[y][i + 1], rows[y][i + 2]
        if not is_bg(r, g, b, bg):
            continue
        bg_set.add((x, y))
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and not mark[ny][nx]:
                mark[ny][nx] = True
                q.append((nx, ny))
    for y in range(h):
        row = rows[y]
        for x in range(w):
            i = x * 4
            if (x, y) in bg_set:
                row[i] = row[i + 1] = row[i + 2] = 0
                row[i + 3] = 0
                continue
            near = sum(
                1
                for nx, ny in (
                    (x - 1, y),
                    (x + 1, y),
                    (x, y - 1),
                    (x, y + 1),
                    (x - 1, y - 1),
                    (x + 1, y - 1),
                    (x - 1, y + 1),
                    (x + 1, y + 1),
                )
                if (nx, ny) in bg_set
            )
            if near:
                row[i + 3] = max(0, int(row[i + 3] * (1 - 0.12 * near)))
    return bg


def downscale(rows: list[bytearray], w: int, h: int, target: int) -> tuple[int, int, list[bytearray]]:
    if max(w, h) <= target:
        return w, h, rows
    scale = max(w, h) / target
    nw, nh = max(1, int(round(w / scale))), max(1, int(round(h / scale)))
    out: list[bytearray] = []
    for y in range(nh):
        row = bytearray(nw * 4)
        sy0 = int(y * h / nh)
        sy1 = max(sy0 + 1, int((y + 1) * h / nh))
        for x in range(nw):
            sx0 = int(x * w / nw)
            sx1 = max(sx0 + 1, int((x + 1) * w / nw))
            tr = tg = tb = ta = cnt = 0
            for sy in range(sy0, sy1):
                src = rows[sy]
                for sx in range(sx0, sx1):
                    i = sx * 4
                    a = src[i + 3]
                    if a == 0:
                        continue
                    tr += src[i] * a
                    tg += src[i + 1] * a
                    tb += src[i + 2] * a
                    ta += a
                    cnt += 1
            o = x * 4
            if ta == 0:
                row[o : o + 4] = b"\x00\x00\x00\x00"
            else:
                row[o] = tr // ta
                row[o + 1] = tg // ta
                row[o + 2] = tb // ta
                row[o + 3] = min(255, ta // max(1, cnt))
        out.append(row)
    return nw, nh, out


def main() -> None:
    for name in FILES:
        path = IMAGES / name
        if not path.is_file():
            print("missing", name)
            continue
        w, h, rows = decode_png(path)
        bg = knockout(rows, w, h)
        w2, h2, rows2 = downscale(rows, w, h, TARGET)
        write_png(path, w2, h2, rows2)
        trans = sum(1 for row in rows2 for x in range(w2) if row[x * 4 + 3] == 0)
        print(f"{name}: {w}x{h} -> {w2}x{h2} bg={bg} transparent={trans}/{w2*h2} size={path.stat().st_size}")


if __name__ == "__main__":
    main()
