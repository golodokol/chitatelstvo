import json
from pathlib import Path

paths = [
    Path(r"c:\Users\Оля\Documents\Читательство\lessons\catalog\grade-2-self_paced-stage-1-lesson-01.json"),
    Path(r"c:\Users\Оля\Documents\Читательство\lessons\skazka-o-rybake-i-rybke.json"),
]

for path in paths:
    data = json.loads(path.read_text(encoding="utf-8"))
    qs = data["meaning_quiz"]["questions"]
    by_id = {q["id"]: q for q in qs}

    # Убрать старые m2/m3; на их месте — бывшие m9/m10; дальше m4..m8
    order = ["m1", "m9", "m10", "m4", "m5", "m6", "m7", "m8"]
    new_qs = []
    for i, oid in enumerate(order, start=1):
        q = dict(by_id[oid])
        q["id"] = f"m{i}"
        new_qs.append(q)

    wishes = new_qs[4]  # m5
    wishes["left"] = [
        {"id": "ask1", "text": "первое желание старухи"},
        {"id": "ask2", "text": "второе желание старухи"},
        {"id": "ask3", "text": "третье желание старухи"},
    ]
    wishes["hint"] = "Соедини желания старухи по порядку с тем, что она просила."

    actions = new_qs[5]  # m6
    # слева герои; «старик · 2» → рыбка; справа действие «исполняла желания»
    actions["left"] = [
        {"id": "man1", "text": "старик"},
        {"id": "fish", "text": "рыбка"},
        {"id": "woman", "text": "старуха"},
    ]
    actions["right"] = [
        {"id": "caught", "text": "поймал рыбку"},
        {"id": "granted", "text": "исполняла желания"},
        {"id": "asked", "text": "просила желания"},
    ]
    actions["correct"] = {
        "man1": "caught",
        "fish": "granted",
        "woman": "asked",
    }

    data["meaning_quiz"]["questions"] = new_qs
    data["meaning_quiz"]["pass_score"] = 5
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path.name)
    for q in new_qs:
        print(f"  {q['id']}: {q['text'][:50]}")
    print("  m5 left:", [x["text"] for x in new_qs[4]["left"]])
    print("  m6:", [(x["id"], x["text"]) for x in new_qs[5]["left"]], new_qs[5]["correct"])
