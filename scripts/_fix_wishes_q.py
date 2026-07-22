import json
from pathlib import Path

PATHS = [
    Path(r"c:\Users\Оля\Documents\Читательство\lessons\catalog\grade-2-self_paced-stage-1-lesson-01.json"),
    Path(r"c:\Users\Оля\Documents\Читательство\lessons\skazka-o-rybake-i-rybke.json"),
]

WISHES = {
    "id": "m6",
    "type": "matching",
    "text": "Вспомни порядок желаний старухи.",
    "hint": "Соедини желания по порядку с тем, что она просила.",
    "left": [
        {"id": "ask1", "text": "первое желание старухи"},
        {"id": "ask2", "text": "второе желание старухи"},
        {"id": "ask3", "text": "третье желание старухи"},
    ],
    "right": [
        {"id": "trough", "text": "новое корыто"},
        {"id": "izba", "text": "новую избу"},
        {"id": "noble", "text": "быть столбовою дворянкой"},
    ],
    "correct": {
        "ask1": "trough",
        "ask2": "izba",
        "ask3": "noble",
    },
}

for path in PATHS:
    data = json.loads(path.read_text(encoding="utf-8"))
    qs = data["meaning_quiz"]["questions"]
    # drop old wishes question (m3 or any matching about желани)
    rest = [
        q
        for q in qs
        if not (
            q.get("type") == "matching"
            and (
                "просил" in (q.get("text") or "").lower()
                or "желани" in (q.get("text") or "").lower()
                or "желани" in (q.get("hint") or "").lower()
            )
        )
    ]
    # keep order of remaining, renumber m1.. then append wishes as last
    for i, q in enumerate(rest, start=1):
        q["id"] = f"m{i}"
    WISHES["id"] = f"m{len(rest) + 1}"
    rest.append(dict(WISHES))
    # re-id final
    for i, q in enumerate(rest, start=1):
        q["id"] = f"m{i}"
    data["meaning_quiz"]["questions"] = rest
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path.name)
    for q in rest:
        print(f"  {q['id']}: {q['text']}")
