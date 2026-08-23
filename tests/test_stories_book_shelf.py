"""Мини-полка книжек «Первые истории» — без оценок, только сбор."""

from types import SimpleNamespace

from gamification.cabinet_ui import (
    STORIES_SHELF_BOOKS,
    _stories_book_shelf,
    build_child_cabinet,
)


def _event(title: str, *, slug: str | None = None):
    payload = {}
    if slug:
        payload["tale_slug"] = slug
    return SimpleNamespace(
        event_type="lesson_complete",
        tale_title=title,
        payload=payload,
    )


def test_shelf_unlocks_home_book_after_intro_complete():
    shelf = _stories_book_shelf([_event("Спаси первую историю")])
    assert shelf["collected"] == 1
    assert shelf["total"] == 8
    assert shelf["slots"][0]["unlocked"] is True
    assert shelf["slots"][0]["book_title"] == "Дома"
    assert shelf["slots"][0]["cover_url"]
    assert all(not s["unlocked"] for s in shelf["slots"][1:])


def test_shelf_unlocks_by_tale_slug():
    shelf = _stories_book_shelf(
        [_event("anything", slug="early-stories-stage1-tale-01")]
    )
    assert shelf["slots"][1]["unlocked"] is True
    assert shelf["slots"][1]["book_title"] == "Кот и коробка"


def test_lesson_four_has_no_shelf_slot():
    slugs = {b["tale_slug"] for b in STORIES_SHELF_BOOKS}
    assert "early-stories-stage1-tale-04" not in slugs
    assert len(STORIES_SHELF_BOOKS) == 8


def test_cabinet_shows_book_shelf_for_early_stories_track():
    tracks = [
        {
            "group_code": "early-stories",
            "group_label": "Первые истории",
            "tariff_code": "trial",
            "lesson_links": [
                {
                    "slug": "early-stories-trial-lesson-01",
                    "tale_slug": "early-stories-stage1-tale-00",
                    "title": "Спаси первую историю",
                    "group_code": "early-stories",
                    "url": "/lesson/x",
                }
            ],
        }
    ]
    cab = build_child_cabinet(
        name="Полина",
        level="Новичок",
        points=2,
        earned_badges=[],
        events=[_event("Спаси первую историю")],
        lesson_links=tracks[0]["lesson_links"],
        tracks=tracks,
        assets_base="https://example.test",
    )
    assert cab["show_book_shelf"] is True
    assert cab["book_shelf"]["collected"] == 1
    assert cab["show_reading_diary"] is False
