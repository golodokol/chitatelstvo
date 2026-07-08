"""Иконки Словика: счётчик баллов и подсказка шага урока не должны совпадать."""

from gamification.sloviki import (
    POINTS_COUNTER_SLOVIK,
    companion_key,
    slovik_url,
)


class _Ev:
    def __init__(self, event_type: str, tale_title: str = "Сказка"):
        self.event_type = event_type
        self.tale_title = tale_title


def test_points_counter_uses_reward_icon():
    assert POINTS_COUNTER_SLOVIK == "reward"
    assert slovik_url(POINTS_COUNTER_SLOVIK).endswith("slovik-reward.png")


def test_tasks_step_companion_differs_from_points_counter():
    events = [
        _Ev("lesson_complete"),
        _Ev("comprehension"),
        _Ev("meaning_analysis"),
    ]
    lesson = {"url": "/lesson/1", "title": "Сказка"}
    chest = {"ready": False, "pct": 10, "steps_remaining": 1}
    companion = companion_key(events, lesson, chest)
    assert companion == "dreams"
    assert slovik_url(companion) != slovik_url(POINTS_COUNTER_SLOVIK)
