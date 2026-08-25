"""Cut cream/gray square background from spark PNGs, keep the flame shape."""
from __future__ import annotations

import struct
import zlib
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "static/early/letters/spark.png",
    ROOT / "static/early/stories/spark.png",
]


def decode_png(path: Path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"not a png: {path}")
    pos = 8
    idat = b""
    ihdr = None
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
    w, h, bit, color, _comp, _filt, _inter = struct.unpack(">IIBBBBB", ihdr[:13])
    if bit != 8 or color != 6:
        raise ValueError(f"need 8-bit RGBA, got bit={bit} color={color} in {path}")
    raw = zlib.decompress(idat)
    bpp = 4
    stride = w * bpp
    rows = []
    i = 0
    prev = bytearray(stride)
    for _y in range(h):
        ft = raw[i]
        i += 1
        row = bytearray(raw[i : i + stride])
        i += stride
        if ft == 1:
            for x in range(stride):
                left = row[x - bpp] if x >= bpp else 0
                row[x] = (row[x] + left) & 255
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
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                row[x] = (row[x] + pr) & 255
        rows.append(row)
        prev = row
    return w, h, rows


def write_png(path: Path, w: int, h: int, rows):
    raw = bytearray()
    for row in rows:
        raw.append(0)
        raw.extend(row)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)

    def chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    out = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(out)


def sample_bg(rows, w, h):
    samples = []
    for y in (0, 1, 2, h - 1, h - 2, h - 3):
        for x in (0, 1, 2, w - 1, w - 2, w - 3):
            i = x * 4
            samples.append(tuple(rows[y][i : i + 3]))
    return tuple(sum(c[k] for c in samples) // len(samples) for k in range(3))


def is_background(r, g, b, bg):
    dist = ((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2) ** 0.5
    chroma = max(r, g, b) - min(r, g, b)
    warm = (r + g) / 2 - b
    if warm > 26 and chroma > 16:
        return False
    if r > 230 and g > 170 and b < 170 and (r - b) > 40:
        return False
    if dist < 38:
        return True
    if chroma < 20 and min(r, g, b) > 205:
        return True
    return False


def knockout(path: Path):
    w, h, rows = decode_png(path)
    bg = sample_bg(rows, w, h)
    mark = [[False] * w for _ in range(h)]
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            q.append((x, y))
            mark[y][x] = True
    for y in range(h):
        for x in (0, w - 1):
            q.append((x, y))
            mark[y][x] = True
    bg_set = set()
    while q:
        x, y = q.popleft()
        i = x * 4
        r, g, b = rows[y][i], rows[y][i + 1], rows[y][i + 2]
        if not is_background(r, g, b, bg):
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
            near = 0
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
                           (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1)):
                if (nx, ny) in bg_set:
                    near += 1
            if near:
                a = row[i + 3]
                row[i + 3] = max(0, int(a * (1 - 0.12 * near)))

    write_png(path, w, h, rows)
    trans = sum(1 for y in range(h) for x in range(w) if rows[y][x * 4 + 3] == 0)
    print(f"{path.name}: bg={bg} transparent={trans}/{w*h} kept={w*h-trans}")


if __name__ == "__main__":
    for f in FILES:
        knockout(f)
