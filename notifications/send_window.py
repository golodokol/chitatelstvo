"""Окно отправки писем от основателя (МСК)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

MSK = ZoneInfo("Europe/Moscow")

# Письма от Ольги — только 09:00–18:00 по Москве (18:00 уже не отправляем).
FOUNDER_SEND_HOUR_START = 9
FOUNDER_SEND_HOUR_END = 18


def is_founder_send_window(now_msk: datetime | None = None) -> bool:
    now = now_msk or datetime.now(MSK)
    if now.tzinfo is None:
        now = now.replace(tzinfo=MSK)
    else:
        now = now.astimezone(MSK)
    return FOUNDER_SEND_HOUR_START <= now.hour < FOUNDER_SEND_HOUR_END


def next_founder_send_time(now: datetime | None = None) -> datetime:
    """UTC-aware: сейчас или ближайшее 09:00 МСК, если вне окна."""
    now_utc = now or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    now_msk = now_utc.astimezone(MSK)

    if is_founder_send_window(now_msk):
        return now_utc

    day = now_msk.date()
    if now_msk.hour < FOUNDER_SEND_HOUR_START:
        target_msk = datetime(
            day.year,
            day.month,
            day.day,
            FOUNDER_SEND_HOUR_START,
            0,
            0,
            tzinfo=MSK,
        )
    else:
        next_day = day + timedelta(days=1)
        target_msk = datetime(
            next_day.year,
            next_day.month,
            next_day.day,
            FOUNDER_SEND_HOUR_START,
            0,
            0,
            tzinfo=MSK,
        )
    return target_msk.astimezone(timezone.utc)
