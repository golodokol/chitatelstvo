"""Flood-fill background removal for all early PNGs (letters, stories, slovik).

Strategy:
- Sample the background colour from the 3×3 corner pixels.
- Flood-fill from every edge pixel that is "background-like" and set its alpha to 0.
- For pixels on the boundary of the fill region, soften the edge slightly.
- Skip PNGs where corners are already transparent (alpha == 0).
- Only works on 8-bit RGBA (colour type 6).
"""
from __future__ import annotations

import struct
import zlib
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = [
    ROOT / "static" / "early" / "letters",
    ROOT / "static" / "early" / "stories",
    ROOT / "static" / "early" / "slovik",
]

# ── PNG decode / encode ──────────────────────────────────────────────────────

def _decode_rgba_png(path: Path):
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
    if bit != 8 or color != 6:
        raise ValueError(f"need 8-bit RGBA (color 6), got bit={bit} color={color}")

    raw = zlib.decompress(idat)
    stride = w * 4
    rows: list[bytearray] = []
    i = 0
    prev = bytearray(stride)
    for _ in range(h):
        ft = raw[i]; i += 1
        row = bytearray(raw[i : i + stride]); i += stride
        if ft == 1:
            for x in range(stride):
                row[x] = (row[x] + (row[x - 4] if x >= 4 else 0)) & 255
        elif ft == 2:
            for x in range(stride):
                row[x] = (row[x] + prev[x]) & 255
        elif ft == 3:
            for x in range(stride):
                row[x] = (row[x] + ((( row[x - 4] if x >= 4 else 0) + prev[x]) // 2)) & 255
        elif ft == 4:
            for x in range(stride):
                a = row[x - 4] if x >= 4 else 0
                b = prev[x]
                c = prev[x - 4] if x >= 4 else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                row[x] = (row[x] + pr) & 255
        rows.append(row); prev = row
    return w, h, rows


def _write_rgba_png(path: Path, w: int, h: int, rows: list[bytearray]) -> None:
    raw = bytearray()
    for row in rows:
        raw.append(0)
        raw.extend(row)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)

    def _chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    out = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(out)


# ── background detection ─────────────────────────────────────────────────────

def _sample_bg(rows: list[bytearray], w: int, h: int) -> tuple[int, int, int]:
    """Average the 3×3 pixels in each corner to get the background colour."""
    samples: list[tuple[int, int, int]] = []
    for y in range(min(3, h)):
        for x in range(min(3, w)):
            i = x * 4
            samples.append((rows[y][i], rows[y][i + 1], rows[y][i + 2]))
    for y in range(max(0, h - 3), h):
        for x in range(min(3, w)):
            i = x * 4
            samples.append((rows[y][i], rows[y][i + 1], rows[y][i + 2]))
    for y in range(min(3, h)):
        for x in range(max(0, w - 3), w):
            i = x * 4
            samples.append((rows[y][i], rows[y][i + 1], rows[y][i + 2]))
    for y in range(max(0, h - 3), h):
        for x in range(max(0, w - 3), w):
            i = x * 4
            samples.append((rows[y][i], rows[y][i + 1], rows[y][i + 2]))
    n = len(samples)
    return (
        sum(s[0] for s in samples) // n,
        sum(s[1] for s in samples) // n,
        sum(s[2] for s in samples) // n,
    )


def _is_bg(r: int, g: int, b: int, bg: tuple[int, int, int], tol: int = 38) -> bool:
    """Return True if pixel is close enough to bg colour (Euclidean in RGB)."""
    dist = ((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2) ** 0.5
    if dist > tol:
        return False
    # Reject pixels that are clearly warm/saturated (part of an icon).
    chroma = max(r, g, b) - min(r, g, b)
    warm = (r + g) / 2 - b
    if warm > 28 and chroma > 18:
        return False
    return True


# ── flood fill + edge softening ──────────────────────────────────────────────

def _knockout(path: Path) -> str:
    try:
        w, h, rows = _decode_rgba_png(path)
    except Exception as exc:
        return f"SKIP ({exc})"

    # Skip files whose corners are already transparent.
    corner_alphas = [
        rows[0][3], rows[0][(w - 1) * 4 + 3],
        rows[h - 1][3], rows[h - 1][(w - 1) * 4 + 3],
    ]
    if all(a == 0 for a in corner_alphas):
        return "already transparent"

    bg = _sample_bg(rows, w, h)

    # Flood fill from every edge pixel.
    visited = [[False] * w for _ in range(h)]
    bg_set: set[tuple[int, int]] = set()
    q: deque[tuple[int, int]] = deque()

    def _seed(x: int, y: int) -> None:
        if not visited[y][x]:
            visited[y][x] = True
            q.append((x, y))

    for x in range(w):
        _seed(x, 0); _seed(x, h - 1)
    for y in range(h):
        _seed(0, y); _seed(w - 1, y)

    while q:
        x, y = q.popleft()
        i = x * 4
        r, g, b = rows[y][i], rows[y][i + 1], rows[y][i + 2]
        if not _is_bg(r, g, b, bg):
            continue
        bg_set.add((x, y))
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                visited[ny][nx] = True
                q.append((nx, ny))

    # Write alpha.
    for y in range(h):
        row = rows[y]
        for x in range(w):
            i = x * 4
            if (x, y) in bg_set:
                row[i] = row[i + 1] = row[i + 2] = 0
                row[i + 3] = 0
                continue
            # Soften pixels adjacent to the erased area.
            near = sum(
                1 for nx, ny in (
                    (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
                    (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1),
                )
                if (nx, ny) in bg_set
            )
            if near:
                row[i + 3] = max(0, int(row[i + 3] * (1 - 0.1 * near)))

    _write_rgba_png(path, w, h, rows)
    trans = sum(1 for y in range(h) for x in range(w) if rows[y][x * 4 + 3] == 0)
    return f"bg={bg} trans={trans}/{w * h}"


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    total = 0
    for folder in FOLDERS:
        pngs = sorted(folder.glob("*.png"))
        for p in pngs:
            result = _knockout(p)
            print(f"{result:<55} {p.parent.name}/{p.name}")
            total += 1
    print(f"\nDone: {total} files processed.")


if __name__ == "__main__":
    main()
