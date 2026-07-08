#!/usr/bin/env python3
"""Тестовое письмо мониторинга через SMTP приложения (docker api)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from notifications.email_channel import send_email  # noqa: E402


def main() -> int:
    to = os.getenv("MONITOR_ALERT_EMAIL", "info@chitatelstvo.ru").split(",")[0].strip()
    body = (
        "Тестовое письмо мониторинга Читательства.\n\n"
        "Если вы видите это сообщение, SMTP и алерты настроены правильно.\n\n"
        "Проверки: API /health, статика, Docker.\n"
        "Письма о сбоях приходят автоматически (каждые 10 минут).\n"
    )
    send_email(to, "Тест: мониторинг Читательства", body)
    print(f"TEST_EMAIL_SENT to {to}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"TEST_EMAIL_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
