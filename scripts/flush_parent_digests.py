#!/usr/bin/env python3
"""Сводка писем родителям: не чаще 1 раза в день (МСК).

Запуск (cron каждые 30 мин):
  cd /root/chitatelstvo && docker compose exec -T api python scripts/flush_parent_digests.py

Или через очередь worker:
  enqueue flush_progress_digests
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from worker.processor import process_flush_progress_digests  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("flush_parent_digests")


def main() -> None:
    force = "--force" in sys.argv
    sent = process_flush_progress_digests(force=force)
    logger.info("Отправлено сводок: %s", sent)


if __name__ == "__main__":
    main()
