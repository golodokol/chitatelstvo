from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LESSONS_DIR = Path(__file__).resolve().parent
LESSONS_CATALOG_DIR = LESSONS_DIR / "catalog"


def _iter_lesson_files() -> list[Path]:
    paths = sorted(LESSONS_DIR.glob("*.json"))
    if LESSONS_CATALOG_DIR.is_dir():
        paths.extend(sorted(LESSONS_CATALOG_DIR.glob("*.json")))
    return paths


def list_lessons(*, active_only: bool = True) -> list[dict[str, Any]]:
    """Все уроки (legacy + catalog). Для страницы прогресса — list_lessons_for_child."""
    items = []
    for path in _iter_lesson_files():
        if path.name.endswith(".example.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if active_only and not data.get("active", True):
            continue
        items.append(_lesson_list_item(data))
    return sorted(items, key=lambda x: x.get("module_week", 1))


def list_legacy_lessons() -> list[dict[str, Any]]:
    """Уроки без module_id (пилот kolobok)."""
    items = []
    for path in sorted(LESSONS_DIR.glob("*.json")):
        if path.name.endswith(".example.json"):
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("module_id") is not None:
            continue
        if not data.get("active", True):
            continue
        items.append(_lesson_list_item(data))
    return sorted(items, key=lambda x: x.get("module_week", 1))


def list_module_lessons(module_id: int, *, active_only: bool = False) -> list[dict[str, Any]]:
    items = []
    if not LESSONS_CATALOG_DIR.is_dir():
        return items
    for path in sorted(LESSONS_CATALOG_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("module_id") != module_id:
            continue
        if active_only and not data.get("active", True):
            continue
        items.append(_lesson_list_item(data, full=data))
    return sorted(items, key=lambda x: (x.get("module_week", 1), x.get("slug", "")))


def _lesson_list_item(data: dict[str, Any], *, full: bool = False) -> dict[str, Any]:
    item = {
        "slug": data["slug"],
        "title": data["title"],
        "module_week": data.get("module_week", 1),
        "active": data.get("active", True),
        "module_id": data.get("module_id"),
        "group_code": data.get("group_code"),
        "tariff_code": data.get("tariff_code"),
        "stage_label": data.get("stage_label"),
        "stage": data.get("stage"),
    }
    if full:
        item["video"] = data.get("video")
    return item


def list_lessons_legacy() -> list[dict[str, Any]]:
    """Список уроков без catalog/ — для обратной совместимости пилота."""
    items = []
    for path in sorted(LESSONS_DIR.glob("*.json")):
        if path.name.endswith(".example.json"):
            continue
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
    for base in (LESSONS_DIR, LESSONS_CATALOG_DIR):
        path = base / f"{slug}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


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
