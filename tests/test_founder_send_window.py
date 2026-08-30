from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from notifications.send_window import (
    FOUNDER_SEND_HOUR_END,
    FOUNDER_SEND_HOUR_START,
    is_founder_send_window,
    next_founder_send_time,
)

MSK = ZoneInfo("Europe/Moscow")


def test_inside_window_at_noon_msk() -> None:
    noon = datetime(2026, 8, 30, 12, 0, tzinfo=MSK)
    assert is_founder_send_window(noon) is True


def test_outside_window_late_evening_msk() -> None:
    evening = datetime(2026, 8, 30, 19, 30, tzinfo=MSK)
    assert is_founder_send_window(evening) is False


def test_next_send_same_morning_before_nine() -> None:
    early = datetime(2026, 8, 30, 6, 0, tzinfo=MSK).astimezone(timezone.utc)
    nxt = next_founder_send_time(early).astimezone(MSK)
    assert nxt.hour == FOUNDER_SEND_HOUR_START
    assert nxt.date().day == 30


def test_next_send_next_day_after_eighteen() -> None:
    late = datetime(2026, 8, 30, 20, 0, tzinfo=MSK).astimezone(timezone.utc)
    nxt = next_founder_send_time(late).astimezone(MSK)
    assert nxt.hour == FOUNDER_SEND_HOUR_START
    assert nxt.date().day == 31


def test_boundary_eighteen_is_outside() -> None:
    at_end = datetime(2026, 8, 30, FOUNDER_SEND_HOUR_END, 0, tzinfo=MSK)
    assert is_founder_send_window(at_end) is False
