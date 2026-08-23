from __future__ import annotations

import uuid

from api.lesson_signing import lesson_slug_from_path, sign_quest_next_paths, verify_lesson_access


def test_lesson_slug_from_path():
    assert lesson_slug_from_path("/lesson/early-stories-trial-lesson-01") == "early-stories-trial-lesson-01"
    assert lesson_slug_from_path("https://api.chitatelstvo.ru/lesson/tsarevna-lyagushka?x=1") == "tsarevna-lyagushka"
    assert lesson_slug_from_path("https://chitatelstvo.ru/pervye-istorii") is None


def test_sign_quest_next_paths(monkeypatch):
    child_id = uuid.uuid4()
    lesson = {
        "stations": [
            {
                "id": "reward",
                "next_paths": [
                    {
                        "cta": "Первые истории — вводный урок",
                        "slug": "early-stories-trial-lesson-01",
                    }
                ],
            }
        ]
    }
    sign_quest_next_paths(lesson, child_id)
    url = lesson["stations"][0]["next_paths"][0]["url"]
    assert url.startswith("https://")
    assert "/lesson/early-stories-trial-lesson-01?" in url
    assert f"child={child_id}" in url
    assert "exp=" in url and "sig=" in url
    assert verify_lesson_access(child_id, "early-stories-trial-lesson-01", int(url.split("exp=")[1].split("&")[0]), url.split("sig=")[1])
