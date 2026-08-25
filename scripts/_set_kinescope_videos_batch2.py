#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "lessons"

SLUG_IDS: dict[str, str] = {
    "grade-3-self_paced-stage-1-lesson-01": "4ezcjsTcDZGTev6svMGPNr",
    "grade-3-with_teacher-stage-1-lesson-01": "4ezcjsTcDZGTev6svMGPNr",
    "skazka-o-tsare-saltane": "4ezcjsTcDZGTev6svMGPNr",
    "extra-6-8-self_paced-stage-1-lesson-01": "vCghXsnvsBgYNtiXfD9AL5",
    "extra-6-8-with_teacher-stage-1-lesson-01": "vCghXsnvsBgYNtiXfD9AL5",
    "plyushevyy-zayats": "vCghXsnvsBgYNtiXfD9AL5",
    "grade-2-self_paced-stage-1-lesson-02": "uasVh1RsE4Wsp6u2spweRv",
    "grade-2-with_teacher-stage-1-lesson-02": "uasVh1RsE4Wsp6u2spweRv",
    "extra-6-8-self_paced-stage-1-lesson-02": "itbXyEoSvzYG3uP7hzAUfB",
    "extra-6-8-with_teacher-stage-1-lesson-02": "itbXyEoSvzYG3uP7hzAUfB",
}

TITLE_IDS: list[tuple[list[str], str, str]] = [
    (["царе салтане"], "4ezcjsTcDZGTev6svMGPNr", "Салтан"),
    (["плюшевый заяц"], "vCghXsnvsBgYNtiXfD9AL5", "Плюшевый заяц"),
    (["цветик-семицветик", "цветик семицветик"], "uasVh1RsE4Wsp6u2spweRv", "Цветик"),
    (["муми-тролль и комета", "муми тролль и комета"], "itbXyEoSvzYG3uP7hzAUfB", "Комета"),
]


def apply_id(data: dict, vid: str, label: str) -> str | None:
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
        if slug in SLUG_IDS:
            old = apply_id(data, SLUG_IDS[slug], slug)
            if old is not None:
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                changed.append((path.as_posix(), slug, old, SLUG_IDS[slug]))
            continue

        title = f"{data.get('title') or ''} {data.get('tale_title') or ''}".lower()
        for needles, vid, label in TITLE_IDS:
            if not any(n in title for n in needles):
                continue
            if not isinstance(data.get("video"), dict) and not (
                data.get("emotion_quiz") or data.get("comprehension_quiz")
            ):
                break
            old = apply_id(data, vid, label)
            if old is not None:
                path.write_text(
                    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                changed.append((path.as_posix(), label, old, vid))
            break

    print(f"updated {len(changed)}")
    for row in changed:
        print(f"{row[0]} | {row[1]} | {row[2]!r} -> {row[3]}")


if __name__ == "__main__":
    main()
