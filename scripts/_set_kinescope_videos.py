#!/usr/bin/env python3
"""Set Kinescope video IDs on lesson JSON files."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "lessons"

UPDATES: list[tuple[list[str], str, str]] = [
    (["опасное лето"], "fuDHSoEgHwZtSt57eraez5", "Опасное лето"),
    (
        ["рассказы из азбуки", "азбуки л.н", "азбуки л. н"],
        "xg3UwRJ8sK8umeFk4s3FFX",
        "Азбука Толстого",
    ),
    (
        ["потерянном времени", "потерянного времени"],
        "vECX6CeQAsg8XnfGHb4in2",
        "Потерянное время",
    ),
    (["храброго зайца"], "d8E6ijvZtDmyL1fJEbnpcL", "Храбрый заяц"),
    (["уральские сказы"], "ihGn4iANXwTcEXPvmN6rzb", "Уральские сказы"),
    (["рыбаке и рыбке", "рыбаке и рыбк"], "aupzRUw6Dp2mtfV1MGxD1o", "Рыбак и рыбка"),
]

# Явные slug’и (включая with_teacher-заготовки без полного контента)
SLUG_IDS: dict[str, str] = {
    "opasnoe-leto": "fuDHSoEgHwZtSt57eraez5",
    "extra-9-11-self_paced-stage-1-lesson-01": "fuDHSoEgHwZtSt57eraez5",
    "extra-9-11-with_teacher-stage-1-lesson-01": "fuDHSoEgHwZtSt57eraez5",
    "grade-1-self_paced-stage-1-lesson-02": "xg3UwRJ8sK8umeFk4s3FFX",
    "grade-1-with_teacher-stage-1-lesson-02": "xg3UwRJ8sK8umeFk4s3FFX",
    "grade-4-self_paced-stage-1-lesson-02": "vECX6CeQAsg8XnfGHb4in2",
    "grade-4-with_teacher-stage-1-lesson-02": "vECX6CeQAsg8XnfGHb4in2",
    "skazka-o-poteryannom-vremeni": "vECX6CeQAsg8XnfGHb4in2",
    "grade-3-self_paced-stage-1-lesson-02": "d8E6ijvZtDmyL1fJEbnpcL",
    "grade-3-with_teacher-stage-1-lesson-02": "d8E6ijvZtDmyL1fJEbnpcL",
    "grade-4-self_paced-stage-1-lesson-01": "ihGn4iANXwTcEXPvmN6rzb",
    "grade-4-with_teacher-stage-1-lesson-01": "ihGn4iANXwTcEXPvmN6rzb",
    "uralskie-skazy": "ihGn4iANXwTcEXPvmN6rzb",
    "grade-2-self_paced-stage-1-lesson-01": "aupzRUw6Dp2mtfV1MGxD1o",
    "grade-2-with_teacher-stage-1-lesson-01": "aupzRUw6Dp2mtfV1MGxD1o",
    "skazka-o-rybake-i-rybke": "aupzRUw6Dp2mtfV1MGxD1o",
}


def _apply_id(data: dict, vid: str, label: str) -> str | None:
    video = data.get("video")
    if not isinstance(video, dict):
        data["video"] = {
            "type": "kinescope",
            "id": vid,
            "title": (data.get("tale_title") or data.get("title") or label)[:80],
            "duration_min": "8-15",
            "pass_condition": "просмотр >= 50%",
        }
        return ""
    old = video.get("id") or ""
    if old == vid:
        return None
    video["id"] = vid
    video["type"] = "kinescope"
    return old


def main() -> None:
    changed: list[tuple[str, str, str, str]] = []
    for path in sorted(ROOT.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        slug = str(data.get("slug") or path.stem)
        applied = False
        if slug in SLUG_IDS:
            old = _apply_id(data, SLUG_IDS[slug], slug)
            if old is not None:
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                changed.append((path.as_posix(), slug, old, SLUG_IDS[slug]))
            applied = True
        if applied:
            continue

        title = f"{data.get('title') or ''} {data.get('tale_title') or ''}".lower()
        if not title.strip():
            continue
        for needles, vid, label in UPDATES:
            if not any(n in title for n in needles):
                continue
            if vid == "xg3UwRJ8sK8umeFk4s3FFX" and "филипок" in title:
                continue
            if not isinstance(data.get("video"), dict) and not (
                data.get("emotion_quiz") or data.get("comprehension_quiz")
            ):
                break
            old = _apply_id(data, vid, label)
            if old is not None:
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                changed.append((path.as_posix(), label, old, vid))
            break

    print(f"updated {len(changed)}")
    for path, label, old, vid in changed:
        print(f"{path} | {label} | {old!r} -> {vid}")


if __name__ == "__main__":
    main()
