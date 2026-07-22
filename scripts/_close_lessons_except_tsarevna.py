"""Закрыть все уроки кроме Царевны-лягушки (legacy + grade-1 self_paced)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "lessons"
KEEP = {"tsarevna-lyagushka", "grade-1-self_paced-stage-1-lesson-01"}
SKIP_NAMES = {"kolobok.yandex.example.json"}


def main() -> None:
    closed: list[str] = []
    for path in sorted(list(ROOT.glob("*.json")) + list((ROOT / "catalog").glob("*.json"))):
        if path.name in SKIP_NAMES:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        slug = data.get("slug") or path.stem
        if slug in KEEP:
            if data.get("active") is not True:
                data["active"] = True
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print("kept/open", slug)
            else:
                print("keep", slug)
            continue
        if data.get("active", True) is False:
            continue
        data["active"] = False
        if "status" in data and data["status"] not in ("черновик",):
            data["status"] = "черновик"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        closed.append(slug)
        print("closed", slug)
    print("total closed", len(closed))


if __name__ == "__main__":
    main()
