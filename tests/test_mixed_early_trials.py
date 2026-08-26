"""Смешанный кабинет: вводные early-уроки в карточках трека, не отдельным блоком."""

from __future__ import annotations

from gamification.cabinet_ui import build_child_cabinet


def test_mixed_cabinet_injects_intro_as_weekly_lesson(monkeypatch):
    monkeypatch.setattr(
        "api.lesson_signing.build_lesson_url",
        lambda child_id, slug: f"/lesson/{slug}?child={child_id}&sig=x",
    )
    tracks = [
        {
            "group_code": "early-letters",
            "group_label": "Буквы оживают",
            "tariff_code": "early",
            "lesson_links": [
                {
                    "slug": "early-letters-stage1-tale-01",
                    "title": "Мотор на поляне",
                    "group_code": "early-letters",
                    "week_in_stage": 1,
                    "unlocked": False,
                    "opens_on_label": "1 сентября",
                }
            ],
        },
        {
            "group_code": "early-stories",
            "group_label": "Первые истории",
            "tariff_code": "early",
            "lesson_links": [
                {
                    "slug": "early-stories-stage1-tale-01",
                    "title": "Кот и коробка",
                    "group_code": "early-stories",
                    "week_in_stage": 1,
                    "unlocked": False,
                    "opens_on_label": "1 сентября",
                }
            ],
        },
        {
            "group_code": "grade-2",
            "group_label": "Сказки",
            "tariff_code": "full",
            "lesson_links": [
                {
                    "slug": "tsarevna-lyagushka",
                    "title": "Царевна-лягушка",
                    "group_code": "grade-2",
                    "url": "/lesson/tale?sig=1",
                }
            ],
        },
    ]
    cab = build_child_cabinet(
        name="Полина",
        level="Новичок",
        points=0,
        earned_badges=[],
        events=[],
        lesson_links=tracks[2]["lesson_links"],
        tracks=tracks,
        assets_base="https://example.test",
        child_id="11111111-1111-1111-1111-111111111111",
    )
    assert cab["cabinet_mode"] == "full"
    assert cab["path_hint"] is None

    by_group = {t["group_code"]: t for t in cab["tracks"]}
    letters = by_group["early-letters"]["weekly_lessons"]
    stories = by_group["early-stories"]["weekly_lessons"]
    assert letters and letters[0]["headline"] == "Вводный урок"
    assert "early-letters-trial-lesson-01" in (letters[0]["url"] or "")
    assert letters[0]["cover_url"] and "course-cover-letters.jpg" in letters[0]["cover_url"]
    assert stories and stories[0]["headline"] == "Вводный урок"
    assert "early-stories-trial-lesson-01" in (stories[0]["url"] or "")
    assert stories[0]["cover_url"] and "course-cover-stories.jpg" in stories[0]["cover_url"]


def test_fairy_only_cabinet_hides_trial_buttons():
    tracks = [
        {
            "group_code": "grade-2",
            "group_label": "Сказки",
            "tariff_code": "full",
            "lesson_links": [
                {
                    "slug": "tsarevna-lyagushka",
                    "title": "Царевна-лягушка",
                    "group_code": "grade-2",
                    "url": "/lesson/tale",
                }
            ],
        }
    ]
    cab = build_child_cabinet(
        name="Полина",
        level="Новичок",
        points=0,
        earned_badges=[],
        events=[],
        lesson_links=tracks[0]["lesson_links"],
        tracks=tracks,
        assets_base="https://example.test",
        child_id="11111111-1111-1111-1111-111111111111",
    )
    assert cab["cabinet_mode"] == "full"
    assert cab["path_hint"] is None
