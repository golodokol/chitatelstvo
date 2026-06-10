"""Какие события автоматизирует плеер, какие — только вручную."""

AUTO_LESSON_PLAYER = frozenset(
    {
        "lesson_complete",
        "comprehension",
        "meaning_analysis",
    }
)

MANUAL_MARK_ONLY = frozenset(
    {
        "creative_task",
        "live_meeting",
    }
)
