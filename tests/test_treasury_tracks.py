"""Сокровищница при нескольких модулях и сказках."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from gamification.cabinet_ui import _build_track_section, _treasury_for_track


@dataclass
class FakeClaim:
    tale_slug: str
    tale_title: str = "Сказка"
    claimed_at: datetime | None = None
    items: list[dict[str, Any]] = field(default_factory=list)


def test_treasury_for_track_includes_all_claimed_tales_in_module():
    claims = [
        FakeClaim("grade-1-stage1-tale-01", "Царевна лягушка"),
        FakeClaim("grade-1-stage1-tale-02", "Колобок"),
    ]
    lesson_links = [
        {"slug": "lesson-01", "tale_slug": "grade-1-stage1-tale-01", "title": "Царевна лягушка"},
        {"slug": "lesson-02", "tale_slug": "grade-1-stage1-tale-02", "title": "Колобок"},
    ]
    rows = _treasury_for_track(claims, lesson_links)
    tale_slugs = {row["tale_slug"] for row in rows}
    assert "grade-1-stage1-tale-01" in tale_slugs
    assert "grade-1-stage1-tale-02" in tale_slugs


def test_treasury_for_track_keeps_rewards_when_current_lesson_is_next_tale():
    claims = [FakeClaim("grade-1-stage1-tale-01", "Царевна лягушка")]
    lesson_links = [
        {"slug": "lesson-01", "tale_slug": "grade-1-stage1-tale-01", "title": "Царевна лягушка", "url": "/l1"},
        {"slug": "lesson-02", "tale_slug": "grade-1-stage1-tale-02", "title": "Колобок", "url": "/l2"},
    ]
    track = {
        "group_code": "grade-1",
        "group_label": "1 класс",
        "module_title": "Self-paced",
        "module_id": 1,
        "lesson_links": lesson_links,
    }
    section = _build_track_section(
        track=track,
        events=[],
        claims=claims,
        points=0,
        assets_base="https://example.test",
    )
    assert section["treasury"]
    assert any(row["tale_slug"] == "grade-1-stage1-tale-01" for row in section["treasury"])


def test_treasury_for_track_excludes_other_modules():
    claims = [
        FakeClaim("grade-1-stage1-tale-01", "Царевна лягушка"),
        FakeClaim("grade-2-stage1-tale-01", "Репка"),
    ]
    lesson_links = [
        {"slug": "lesson-01", "tale_slug": "grade-1-stage1-tale-01", "title": "Царевна лягушка"},
    ]
    rows = _treasury_for_track(claims, lesson_links)
    assert rows
    assert all(row["tale_slug"] == "grade-1-stage1-tale-01" for row in rows)
