#!/usr/bin/env python3
"""Отправка отложенных писем основателя (09:00–18:00 МСК).

Cron каждые 15 мин:
  cd /root/chitatelstvo && docker compose exec -T api python scripts/send_due_founder_letters.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.founder_letter_queue import process_due_founder_letters  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("send_due_founder_letters")


def main() -> None:
    force = "--force" in sys.argv
    sent = process_due_founder_letters(force=force)
    logger.info("Отправлено писем основателя: %s", sent)


if __name__ == "__main__":
    main()
