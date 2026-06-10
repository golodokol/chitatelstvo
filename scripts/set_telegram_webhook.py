#!/usr/bin/env python3
"""Регистрирует webhook Telegram-бота на ваш API."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib import parse, request

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import PUBLIC_BASE_URL, TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET


def main() -> int:
    if not TELEGRAM_BOT_TOKEN:
        print("Задайте TELEGRAM_BOT_TOKEN в .env")
        return 1

    webhook_url = f"{PUBLIC_BASE_URL}/telegram/webhook"
    payload: dict = {"url": webhook_url, "allowed_updates": ["message", "edited_message"]}
    if TELEGRAM_WEBHOOK_SECRET:
        payload["secret_token"] = TELEGRAM_WEBHOOK_SECRET

    api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(api, data=data, headers={"Content-Type": "application/json"}, method="POST")

    with request.urlopen(req, timeout=20) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("ok"):
        print(f"\nWebhook установлен: {webhook_url}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
