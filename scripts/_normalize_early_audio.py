"""Rename static/early/audio/*.MP3 → *.mp3 for Linux-friendly paths."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "static" / "early" / "audio"

for path in sorted(ROOT.glob("*.MP3")):
    target = path.with_suffix(".mp3")
    if target.exists() and target.resolve() != path.resolve():
        print("SKIP exists", target.name)
        continue
    tmp = path.with_name(path.stem + ".__renaming.mp3")
    path.rename(tmp)
    tmp.rename(target)
    print("OK", target.name)
