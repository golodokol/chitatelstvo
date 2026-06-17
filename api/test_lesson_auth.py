"""Доступ к приватной тестовой странице урока."""

from __future__ import annotations

import hmac

from config.settings import TEST_LESSON_SECRET


def test_lesson_enabled() -> bool:
    return bool(TEST_LESSON_SECRET)


def verify_test_lesson_key(key: str | None) -> bool:
    if not key or not TEST_LESSON_SECRET:
        return False
    return hmac.compare_digest(key, TEST_LESSON_SECRET)
