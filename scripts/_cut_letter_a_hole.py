"""Cut the opaque white counter (hole) out of letter-a-hero.png."""
from __future__ import annotations

import importlib.util
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "static" / "early" / "letters" / "letter-a-hero.png"

spec = importlib.util.spec_from_file_location("ko", ROOT / "scripts" / "_knockout_all_early.py")
ko = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ko)


def is_hole(r: int, g: int, b: int, a: int) -> bool:
    if a < 16:
        return False
    # near-white / light gray, almost no chroma
    if min(r, g, b) < 200:
        return False
    if max(r, g, b) - min(r, g, b) > 18:
        return False
    return True


def cut_hole(path: Path) -> str:
    w, h, rows = ko._decode_rgba_png(path)
    sx, sy = w // 2, h // 2
    i = sx * 4
    print("seed", sx, sy, list(rows[sy][i : i + 4]))
    if not is_hole(rows[sy][i], rows[sy][i + 1], rows[sy][i + 2], rows[sy][i + 3]):
        # search nearby for a white seed
        found = None
        for dy in range(-40, 41):
            for dx in range(-40, 41):
                x, y = sx + dx, sy + dy
                if 0 <= x < w and 0 <= y < h:
                    j = x * 4
                    if is_hole(rows[y][j], rows[y][j + 1], rows[y][j + 2], rows[y][j + 3]):
                        found = (x, y)
                        break
            if found:
                break
        if not found:
            return "no white hole seed"
        sx, sy = found

    visited = [[False] * w for _ in range(h)]
    hole: set[tuple[int, int]] = set()
    q: deque[tuple[int, int]] = deque([(sx, sy)])
    visited[sy][sx] = True
    while q:
        x, y = q.popleft()
        j = x * 4
        if not is_hole(rows[y][j], rows[y][j + 1], rows[y][j + 2], rows[y][j + 3]):
            continue
        hole.add((x, y))
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                visited[ny][nx] = True
                q.append((nx, ny))

    if len(hole) < 200:
        return f"too small ({len(hole)})"

    # soften 1px edge: fade alpha of hole pixels that touch non-hole
    for x, y in hole:
        j = x * 4
        rows[y][j + 3] = 0
        rows[y][j] = 0
        rows[y][j + 1] = 0
        rows[y][j + 2] = 0

    # fade neighboring letter pixels slightly so the cut isn't jagged
    for x, y in list(hole):
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in hole:
                j = nx * 4
                a = rows[ny][j + 3]
                if a > 40:
                    rows[ny][j + 3] = int(a * 0.55)

    ko._write_rgba_png(path, w, h, rows)
    return f"cut {len(hole)} px"


print(cut_hole(TARGET))
