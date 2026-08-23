"""Convert letter-a-hero.png (RGB) to RGBA and knock out checkerboard backdrop."""
from __future__ import annotations

import struct
import zlib
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "static" / "early" / "letters" / "letter-a-hero.png"


def _decode_png(path: Path):
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"not a PNG: {path}"
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
    w, h, bit, color, _c, _f, _i = struct.unpack(">IIBBBBB", ihdr[:13])
    if bit != 8 or color not in (2, 6):
        raise ValueError(f"need 8-bit RGB/RGBA, got bit={bit} color={color}")
    bpp = 4 if color == 6 else 3
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows: list[bytearray] = []
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
                row[x] = (row[x] + (((row[x - bpp] if x >= bpp else 0) + prev[x]) // 2)) & 255
        elif ft == 4:
            for x in range(stride):
                a = row[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                row[x] = (row[x] + pr) & 255
        rows.append(row)
        prev = row
    return w, h, rows, color


def _to_rgba(rows: list[bytearray], w: int) -> list[bytearray]:
    out: list[bytearray] = []
    for row in rows:
        if len(row) == w * 4:
            out.append(bytearray(row))
            continue
        rgba = bytearray(w * 4)
        for x in range(w):
            j = x * 3
            k = x * 4
            rgba[k : k + 3] = row[j : j + 3]
            rgba[k + 3] = 255
        out.append(rgba)
    return out


def _is_backdrop(r: int, g: int, b: int) -> bool:
    chroma = max(r, g, b) - min(r, g, b)
    if chroma > 24:
        return False
    if min(r, g, b) < 168:
        return False
    return True


def _write_rgba_png(path: Path, w: int, h: int, rows: list[bytearray]) -> None:
    raw = bytearray()
    for row in rows:
        raw.append(0)
        raw.extend(row)

    def _chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    out = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(out)


def main() -> None:
    w, h, rows, color = _decode_png(TARGET)
    rows = _to_rgba(rows, w)
    visited = [[False] * w for _ in range(h)]
    bg: set[tuple[int, int]] = set()
    q: deque[tuple[int, int]] = deque()

    def seed(x: int, y: int) -> None:
        if not visited[y][x]:
            visited[y][x] = True
            q.append((x, y))

    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(h):
        seed(0, y)
        seed(w - 1, y)

    while q:
        x, y = q.popleft()
        i = x * 4
        r, g, b = rows[y][i], rows[y][i + 1], rows[y][i + 2]
        if not _is_backdrop(r, g, b):
            continue
        bg.add((x, y))
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                visited[ny][nx] = True
                q.append((nx, ny))

    for x, y in bg:
        i = x * 4
        rows[y][i : i + 4] = bytes(4)

    for y in range(h):
        row = rows[y]
        for x in range(w):
            if (x, y) in bg:
                continue
            i = x * 4
            near = sum(
                1
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                if (nx, ny) in bg
            )
            if near:
                row[i + 3] = max(0, int(row[i + 3] * (1 - 0.12 * near)))

    _write_rgba_png(TARGET, w, h, rows)
    print(f"color={color} removed={len(bg)}/{w * h} -> {TARGET}")


if __name__ == "__main__":
    main()
