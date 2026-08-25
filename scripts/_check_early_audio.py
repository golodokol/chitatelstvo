#!/usr/bin/env python3
"""Compare early trial audio IDs vs files on disk."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
audio_dir = root / "static" / "early" / "audio"

on_disk = {}
for f in audio_dir.iterdir():
    if f.name == ".gitkeep":
        continue
    stem = f.stem.lower()
    on_disk.setdefault(stem, []).append(f.name)

ids = set()


def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in (
                "audio",
                "sound",
                "success_audio",
                "fail_audio",
                "result_sound",
                "prompt_audio",
                "word_audio",
            ) and isinstance(v, str) and v and not v.startswith("http") and "/" not in v:
                ids.add(v)
            elif k.endswith("_audio") and isinstance(v, str) and v:
                ids.add(v)
            elif k == "sounds" and isinstance(v, dict):
                for vv in v.values():
                    ids.add(vv)
            else:
                walk(v)
    elif isinstance(o, list):
        for x in o:
            walk(x)


for jf in [
    root / "lessons/catalog/early-letters-trial-lesson-01.json",
    root / "lessons/catalog/early-stories-trial-lesson-01.json",
]:
    walk(json.loads(jf.read_text(encoding="utf-8")))

letters_react = [
    "vo-ok",
    "vo-yes",
    "vo-good",
    "vo-found",
    "vo-spark",
    "vo-try",
    "vo-more",
    "vo-wrong",
]
stories_react = ["ph-vo-" + x.split("-", 1)[1] for x in letters_react]

print("=== FROM JSON ===")
missing_json = []
for i in sorted(ids):
    ok = i.lower() in on_disk
    status = "OK" if ok else "MISSING"
    print(f"{status:7} {i}")
    if not ok:
        missing_json.append(i)

print("\n=== LETTERS REACTIONS ===")
missing_lr = []
for i in letters_react:
    ok = i.lower() in on_disk
    status = "OK" if ok else "MISSING"
    print(f"{status:7} {i}")
    if not ok:
        missing_lr.append(i)

print("\n=== STORIES REACTIONS (ph-vo-*) ===")
missing_sr = []
for i in stories_react:
    ok = i.lower() in on_disk
    alt = i.replace("ph-vo-", "vo-")
    alt_ok = alt.lower() in on_disk
    note = f" (есть {alt})" if not ok and alt_ok else ""
    status = "OK" if ok else "MISSING"
    print(f"{status:7} {i}{note}")
    if not ok:
        missing_sr.append(i)

print("\n=== EXTRA ON DISK (not in JSON/reactions) ===")
known = {x.lower() for x in ids} | {x.lower() for x in letters_react + stories_react}
for stem in sorted(on_disk):
    if stem not in known:
        print("EXTRA ", on_disk[stem])

print("\n=== EXTENSION CASE ===")
for stem, names in sorted(on_disk.items()):
    exts = [n.rsplit(".", 1)[-1] for n in names]
    if any(e != e.lower() for e in exts):
        print(f"{stem}: {names}")

print("\nSUMMARY")
print("JSON missing:", missing_json or "none")
print("Letters reactions missing:", missing_lr or "none")
print("Stories reactions missing:", missing_sr or "none")
