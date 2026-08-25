from __future__ import annotations

import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "static" / "early"


def decode_rgba_png(path: Path):
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a png")

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
    if ihdr is None:
        raise ValueError("missing IHDR")

    w, h, bit, color, _comp, _filt, _inter = struct.unpack(">IIBBBBB", ihdr[:13])
    if bit != 8 or color != 6:
        raise ValueError(f"need 8-bit RGBA (color type 6), got bit={bit} color={color}")

    raw = zlib.decompress(idat)
    stride = w * 4
    rows = []
    i = 0
    prev = bytearray(stride)
    for _y in range(h):
        ft = raw[i]
        i += 1
        row = bytearray(raw[i : i + stride])
        i += stride

        if ft == 0:
            pass
        elif ft == 1:  # Sub
            for x in range(stride):
                left = row[x - 4] if x >= 4 else 0
                row[x] = (row[x] + left) & 255
        elif ft == 2:  # Up
            for x in range(stride):
                row[x] = (row[x] + prev[x]) & 255
        elif ft == 3:  # Average
            for x in range(stride):
                left = row[x - 4] if x >= 4 else 0
                row[x] = (row[x] + ((left + prev[x]) // 2)) & 255
        elif ft == 4:  # Paeth (approx)
            for x in range(stride):
                a = row[x - 4] if x >= 4 else 0
                b = prev[x]
                c = prev[x - 4] if x >= 4 else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                row[x] = (row[x] + pr) & 255
        else:
            raise ValueError(f"unsupported filter type {ft}")

        rows.append(row)
        prev = row

    return w, h, rows


def corners_alpha(path: Path):
    w, h, rows = decode_rgba_png(path)
    pts = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    return tuple(rows[y][x * 4 + 3] for x, y in pts)


def main():
    pngs = list(ROOT.rglob("*.png"))
    bad = []
    for p in pngs:
        try:
            c = corners_alpha(p)
        except Exception:
            continue
        if any(a != 0 for a in c):
            bad.append((p, c))

    print("checked_pngs:", len(pngs))
    print("non_transparent_corners:", len(bad))
    for p, c in sorted(bad, key=lambda x: sum(x[1]), reverse=True)[:40]:
        print(c, p)


if __name__ == "__main__":
    main()

