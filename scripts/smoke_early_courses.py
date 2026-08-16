# -*- coding: utf-8 -*-
"""Smoke checks for early courses catalog (no DB)."""
from __future__ import annotations

from datetime import date

from catalog.loader import get_module, load_modules
from lessons.loader import get_lesson, list_module_lessons


def main() -> None:
    assert len(load_modules()) >= 25
    for mid, n in ((20, 1), (21, 8), (22, 8), (23, 1), (24, 8), (25, 8)):
        lessons = list_module_lessons(mid, active_only=False)
        assert len(lessons) == n, (mid, len(lessons), n)
        assert get_module(mid)

    for slug in (
        "early-letters-trial-lesson-01",
        "early-stories-trial-lesson-01",
    ):
        lesson = get_lesson(slug)
        assert lesson, slug
        assert lesson.get("active") is True
        assert lesson.get("stations")
        assert lesson.get("lesson_format") == "quest"

    assert get_lesson("early-letters-self_paced-stage-1-lesson-01")
    assert get_lesson("early-letters-with_teacher-stage-1-lesson-08")
    assert get_lesson("early-stories-self_paced-stage-1-lesson-04")
    assert get_lesson("early-stories-with_teacher-stage-1-lesson-08")

    # Schedule: Tue/Thu starting 1 Sep 2026
    from lessons.access import early_lesson_opens_on

    expected = [
        date(2026, 9, 1),
        date(2026, 9, 3),
        date(2026, 9, 8),
        date(2026, 9, 10),
        date(2026, 9, 15),
        date(2026, 9, 17),
        date(2026, 9, 22),
        date(2026, 9, 24),
    ]
    for i, d in enumerate(expected, start=1):
        assert early_lesson_opens_on(i) == d, (i, early_lesson_opens_on(i), d)

    print("SMOKE OK: early catalog + Tue/Thu schedule")


if __name__ == "__main__":
    main()
