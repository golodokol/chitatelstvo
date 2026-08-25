# -*- coding: utf-8 -*-
"""Reorder early-letters lessons 01/02/03 to O → U → M (was M → U → O)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "lessons" / "catalog"


def patch_meta(data: dict, kind: str, num: int) -> dict:
    n = f"{num:02d}"
    data["slug"] = f"early-letters-{kind}-stage-1-lesson-{n}"
    data["lesson_number"] = num
    data["tale_number"] = num
    data["tale_slug"] = f"early-letters-stage1-tale-{n}"
    data["module_week"] = num
    return data


def reorder_kind(kind: str) -> None:
    paths = [ROOT / f"early-letters-{kind}-stage-1-lesson-{i:02d}.json" for i in (1, 2, 3)]
    lessons = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
    # old: 0=M, 1=U, 2=O  →  new: O, U, M
    titles = [x.get("title") for x in lessons]
    print(kind, "before:", titles)
    reordered = [lessons[2], lessons[1], lessons[0]]
    for i, data in enumerate(reordered, start=1):
        patch_meta(data, kind, i)
        paths[i - 1].write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(kind, "after:", [x.get("title") for x in reordered])


def main() -> None:
    for kind in ("self_paced", "with_teacher"):
        reorder_kind(kind)


if __name__ == "__main__":
    main()
