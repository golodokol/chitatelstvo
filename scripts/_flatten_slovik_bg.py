"""Paint a solid cream around Slovik: keep the character, flatten the rest."""
from __future__ import annotations

import struct
import zlib
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "static" / "early" / "slovik"
FILL = (245, 237, 226, 255)
DILATE = 12


def decode(path: Path):
    data = path.read_bytes()
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
    w, h, bit, color, *_ = struct.unpack(">IIBBBBB", ihdr[:13])
    if bit != 8 or color != 6:
        raise ValueError(f"{path.name}: need RGBA")
    raw = zlib.decompress(idat)
    stride = w * 4
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
                row[x] = (row[x] + (row[x - 4] if x >= 4 else 0)) & 255
        elif ft == 2:
            for x in range(stride):
                row[x] = (row[x] + prev[x]) & 255
        elif ft == 3:
            for x in range(stride):
                left = row[x - 4] if x >= 4 else 0
                row[x] = (row[x] + ((left + prev[x]) // 2)) & 255
        elif ft == 4:
            for x in range(stride):
                a = row[x - 4] if x >= 4 else 0
                b = prev[x]
                c = prev[x - 4] if x >= 4 else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                row[x] = (row[x] + pr) & 255
        rows.append(row)
        prev = row
    return w, h, rows


def write(path: Path, w: int, h: int, rows: list[bytearray]) -> None:
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


def is_character(r: int, g: int, b: int, a: int) -> bool:
    if a < 40:
        return False
    # blue body / antennae / eyes
    if b > r + 12 and b > 70 and (r + g + b) < 420:
        return True
    # dark linework
    if max(r, g, b) < 90 and a > 80:
        return True
    # purple star: magenta, not the pale blue-lavender halo
    if b > 110 and r > 80 and g < 105 and b > g + 30:
        return True
    # orange/red book or clasp (redder than paper-yellow)
    if r > 155 and (r - g) > 50 and g < 165 and (r - b) > 50:
        return True
    return False


def flatten(path: Path) -> str:
    w, h, rows = decode(path)
    keep = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int, int]] = deque()
    seeds = 0
    for y in range(h):
        for x in range(w):
            i = x * 4
            if is_character(rows[y][i], rows[y][i + 1], rows[y][i + 2], rows[y][i + 3]):
                keep[y][x] = True
                q.append((x, y, 0))
                seeds += 1

    while q:
        x, y, d = q.popleft()
        if d >= DILATE:
            continue
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and not keep[ny][nx]:
                keep[ny][nx] = True
                q.append((nx, ny, d + 1))

    painted = 0
    for y in range(h):
        for x in range(w):
            i = x * 4
            r, g, b, a = rows[y][i], rows[y][i + 1], rows[y][i + 2], rows[y][i + 3]
            paper = r > 210 and g > 170 and b < 210 and (r + g) > 2 * b + 20
            if keep[y][x] and not paper:
                rows[y][i + 3] = 255
                continue
            rows[y][i] = FILL[0]
            rows[y][i + 1] = FILL[1]
            rows[y][i + 2] = FILL[2]
            rows[y][i + 3] = 255
            painted += 1

    write(path, w, h, rows)
    return f"seeds={seeds} painted={painted}"


def main() -> None:
    for p in sorted(FOLDER.glob("*.png")):
        print(f"{flatten(p):<32} {p.name}")


if __name__ == "__main__":
    main()
