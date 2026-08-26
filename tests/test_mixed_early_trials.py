"""Смешанный кабинет: кнопки на оба пробных early-урока."""

from __future__ import annotations

from gamification.cabinet_ui import build_child_cabinet


def test_mixed_cabinet_shows_both_trial_buttons(monkeypatch):
    monkeypatch.setattr(
        "api.lesson_signing.build_lesson_url",
        lambda child_id, slug: f"/lesson/{slug}?child={child_id}",
    )
    tracks = [
        {
            "group_code": "early-letters",
            "group_label": "Буквы оживают",
            "tariff_code": "early",
            "lesson_links": [],
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
                    "url": "/lesson/tale",
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
        lesson_links=tracks[1]["lesson_links"],
        tracks=tracks,
        assets_base="https://example.test",
        child_id="11111111-1111-1111-1111-111111111111",
    )
    assert cab["cabinet_mode"] == "full"
    hint = cab["path_hint"]
    assert hint is not None
    assert hint["title"] == "Пробные уроки"
    ctas = [c["cta"] for c in hint["cards"]]
    assert "Буквы оживают — вводный урок" in ctas
    assert "Первые истории — вводный урок" in ctas
    urls = [c["url"] for c in hint["cards"]]
    assert any("early-letters-trial-lesson-01" in u for u in urls)
    assert any("early-stories-trial-lesson-01" in u for u in urls)


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
