from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LESSONS_DIR = Path(__file__).resolve().parent


def list_lessons() -> list[dict[str, Any]]:
    items = []
    for path in sorted(LESSONS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        items.append(
            {
                "slug": data["slug"],
                "title": data["title"],
                "module_week": data.get("module_week", 1),
            }
        )
    return sorted(items, key=lambda x: x.get("module_week", 1))


def get_lesson(slug: str) -> dict[str, Any] | None:
    path = LESSONS_DIR / f"{slug}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def quiz_for_client(quiz: dict[str, Any]) -> dict[str, Any]:
    """Вопросы без правильных ответов — только для браузера."""
    questions = []
    for q in quiz.get("questions", []):
        questions.append(
            {
                "id": q["id"],
                "text": q["text"],
                "options": q["options"],
            }
        )
    return {
        "title": quiz.get("title", ""),
        "questions": questions,
    }


def score_quiz(quiz: dict[str, Any], answers: dict[str, str]) -> tuple[int, int]:
    total = len(quiz.get("questions", []))
    correct = 0
    for q in quiz.get("questions", []):
        if answers.get(q["id"]) == q.get("correct"):
            correct += 1
    return correct, total
