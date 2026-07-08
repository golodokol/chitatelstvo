from datetime import date, timedelta

from gamification.streak_badges import consecutive_activity_days


def test_consecutive_activity_days_three_in_row():
    today = date(2026, 7, 8)
    dates = {today, today - timedelta(days=1), today - timedelta(days=2)}
    assert consecutive_activity_days(dates, ending=today) == 3


def test_consecutive_activity_days_broken_streak():
    today = date(2026, 7, 8)
    dates = {today, today - timedelta(days=2)}
    assert consecutive_activity_days(dates, ending=today) == 1
