"""Какие события автоматизирует плеер, какие — только вручную."""

AUTO_LESSON_PLAYER = frozenset(
    {
        "video_unlock",
        "lesson_complete",
        "emotion_quiz",
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
