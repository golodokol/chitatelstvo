from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

LESSONS_DIR = Path(__file__).resolve().parent
LESSONS_CATALOG_DIR = LESSONS_DIR / "catalog"
PROJECT_ROOT = LESSONS_DIR.parent
EMOTION_PETAL_PATHS_FILE = PROJECT_ROOT / "static" / "emotion_wheel_petals.json"


def _load_emotion_petal_paths() -> dict[str, str]:
    if not EMOTION_PETAL_PATHS_FILE.is_file():
        return {}
    return json.loads(EMOTION_PETAL_PATHS_FILE.read_text(encoding="utf-8"))


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


def quiz_for_client(quiz: dict[str, Any], *, shuffle_options: bool = True) -> dict[str, Any]:
    """Вопросы без правильных ответов — только для браузера."""
    questions = []
    for q in quiz.get("questions", []):
        options = list(q.get("options", []))
        if shuffle_options and len(options) > 1:
            random.shuffle(options)
        questions.append(
            {
                "id": q["id"],
                "text": q["text"],
                "options": options,
            }
        )
    return {
        "title": quiz.get("title", ""),
        "pass_score": int(quiz.get("pass_score", len(questions))),
        "questions": questions,
    }


def score_quiz(quiz: dict[str, Any], answers: dict[str, str]) -> tuple[int, int]:
    total = len(quiz.get("questions", []))
    correct = 0
    for q in quiz.get("questions", []):
        if answers.get(q["id"]) == q.get("correct"):
            correct += 1
    return correct, total


def quiz_answer_results(quiz: dict[str, Any], answers: dict[str, str]) -> list[dict[str, Any]]:
    """По каждому вопросу — верно ли; при ошибке id правильного варианта."""
    items: list[dict[str, Any]] = []
    for q in quiz.get("questions", []):
        qid = q["id"]
        picked = answers.get(qid)
        correct_id = q.get("correct")
        ok = picked == correct_id
        item: dict[str, Any] = {"id": qid, "ok": ok}
        if not ok and correct_id:
            item["correct_option"] = correct_id
        items.append(item)
    return items


EMOTION_WHEEL_IMAGE = "/static/images/emotion-wheel.png?v=10"

# Порядок — по часовой стрелке с верхнего лепестка (как на иллюстрации).
EMOTION_WHEEL: list[dict[str, str]] = [
    {"id": "joy", "label": "Радость", "color": "#8EC4E8"},
    {"id": "interest", "label": "Интерес", "color": "#C8B8E4"},
    {"id": "surprise", "label": "Удивление", "color": "#9A84BC"},
    {"id": "sadness", "label": "Грусть", "color": "#8FAAC8"},
    {"id": "fear", "label": "Страх", "color": "#6E94BE"},
    {"id": "anger", "label": "Злость", "color": "#7A7098"},
    {"id": "resentment", "label": "Обида", "color": "#C4B0D8"},
    {"id": "tired", "label": "Усталость", "color": "#8AB4D8"},
    {"id": "pride", "label": "Гордость", "color": "#F2E4A8"},
    {"id": "calm", "label": "Спокойствие", "color": "#B8DCE8"},
]


def emotion_quiz_for_client(quiz: dict[str, Any]) -> dict[str, Any]:
    """Вопрос эмоциометра без правильных ответов."""
    q = quiz.get("question") or {}
    return {
        "title": quiz.get("title", "Эмоции героя"),
        "character": quiz.get("character", ""),
        "emotions": EMOTION_WHEEL,
        "wheel_image": EMOTION_WHEEL_IMAGE,
        "wheel_petals": _load_emotion_petal_paths(),
        "question": {
            "id": q["id"],
            "text": q["text"],
            "pick": int(q.get("pick", 1)),
        },
        "feedback_ok": quiz.get("feedback_ok", ""),
        "feedback_retry": quiz.get("feedback_retry", ""),
    }


def score_emotion_quiz(quiz: dict[str, Any], answers: dict[str, list[str]]) -> bool:
    """Точное совпадение набора эмоций с правильным ответом."""
    q = quiz.get("question") or {}
    qid = q.get("id")
    if not qid:
        return False
    picked = set(answers.get(qid) or [])
    correct = set(q.get("correct") or [])
    expected_pick = int(q.get("pick", len(correct)))
    return picked == correct and len(picked) == expected_pick
