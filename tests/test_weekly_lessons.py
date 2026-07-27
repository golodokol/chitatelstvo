"""Блок «Сказка этой недели» / «Будет доступно позже» на личной странице."""

from __future__ import annotations

from gamification.cabinet_ui import _weekly_lessons


def _lesson(
    *,
    week: int,
    title: str,
    url: str | None = None,
    unlocked: bool = False,
) -> dict:
    return {
        "title": title,
        "module_week": week,
        "week_in_stage": week,
        "url": url,
        "unlocked": unlocked,
    }


def test_weekly_lessons_prefers_playable_lesson_over_grandfathered_soon_week():
    """Ранний доступ: неделя 2 unlocked, но без url — в шапке остаётся сказка 1."""
    links = [
        _lesson(week=1, title="Царевна лягушка", url="/lesson/1", unlocked=True),
        _lesson(week=2, title="Рассказы из Азбуки", unlocked=True),
        _lesson(week=3, title="Носов", unlocked=False),
    ]
    weekly, label = _weekly_lessons(links)
    assert label == "Сказка этой недели"
    assert len(weekly) == 1
    assert weekly[0]["title"] == "Царевна лягушка"
    assert weekly[0]["module_week"] == 1


def test_weekly_lessons_open_label_for_playable():
    links = [
        _lesson(week=1, title="Сказка 1", url="/lesson/1", unlocked=True),
        _lesson(week=2, title="Сказка 2", url="/lesson/2", unlocked=True),
    ]
    weekly, label = _weekly_lessons(links)
    assert label == "Сказки этой недели"
    assert {w["module_week"] for w in weekly} == {1, 2}


def test_weekly_lessons_closed_label():
    links = [
        _lesson(week=1, title="По щучьему велению", unlocked=False),
    ]
    weekly, label = _weekly_lessons(links)
    assert label == "Будет доступно позже"
    assert len(weekly) == 1
    assert weekly[0]["title"] == "По щучьему велению"
