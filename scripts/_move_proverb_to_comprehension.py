"""Перенести пословицу и «корыто» из meaning в comprehension; убрать q7."""
from __future__ import annotations

import json
from pathlib import Path

PATHS = [
    Path(r"c:\Users\Оля\Documents\Читательство\lessons\catalog\grade-2-self_paced-stage-1-lesson-01.json"),
    Path(r"c:\Users\Оля\Documents\Читательство\lessons\skazka-o-rybake-i-rybke.json"),
]

NEW_Q7 = {
    "id": "q7",
    "type": "single",
    "text": "Какая пословица подходит к сказке «О рыбаке и рыбке»?",
    "hint": "Выбери одну.",
    "options": [
        {"id": "a", "text": "Семь раз отмерь, один раз отрежь."},
        {"id": "b", "text": "Без труда не вытащишь и рыбку из пруда."},
        {"id": "c", "text": "Друзья познаются в беде."},
        {"id": "d", "text": "Делу время, потехе час."},
    ],
    "correct": "b",
}

NEW_Q8 = {
    "id": "q8",
    "type": "single",
    "text": "Что значит выражение «остаться у разбитого корыта»?",
    "hint": "Выбери верное значение.",
    "options": [
        {"id": "a", "text": "получить много подарков"},
        {"id": "b", "text": "стать богатым и знаменитым"},
        {"id": "c", "text": "остаться ни с чем"},
        {"id": "d", "text": "уехать к морю"},
    ],
    "correct": "c",
}


def main() -> None:
    for path in PATHS:
        data = json.loads(path.read_text(encoding="utf-8"))
        comp = data["comprehension_quiz"]["questions"]
        # drop old q7, keep q1–q6, append proverb + expression
        comp = [q for q in comp if q["id"] != "q7"]
        # ensure only q1-q6 remain before append
        comp = [q for q in comp if q["id"] in {"q1", "q2", "q3", "q4", "q5", "q6"}]
        comp.extend([NEW_Q7, NEW_Q8])
        data["comprehension_quiz"]["questions"] = comp
        data["comprehension_quiz"]["pass_score"] = 6

        meaning = data["meaning_quiz"]["questions"]
        meaning = [q for q in meaning if q["id"] not in {"m2", "m3"}]
        # renumber m1, m4..m8 -> m1..m6
        for i, q in enumerate(meaning, start=1):
            q["id"] = f"m{i}"
        data["meaning_quiz"]["questions"] = meaning
        data["meaning_quiz"]["pass_score"] = 4

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(path.name)
        print("  comprehension:", [q["id"] + ": " + q["text"][:40] for q in comp])
        print("  meaning:", [q["id"] + ": " + q["text"][:40] for q in meaning])


if __name__ == "__main__":
    main()
