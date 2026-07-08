"""Какие события автоматизирует плеер, какие — только вручную."""

AUTO_LESSON_PLAYER = frozenset(
    {
        "video_unlock",
        "lesson_complete",
        "emotion_quiz",
        "comprehension",
        "meaning_analysis",
        "retelling",
    }
)

MANUAL_MARK_ONLY = frozenset(
    {
        "creative_task",
        "live_meeting",
    }
)

AUTO_SYSTEM_EVENTS = frozenset(
    {
        "streak_3",
        "streak_5",
    }
)
