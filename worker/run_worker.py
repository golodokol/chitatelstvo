#!/usr/bin/env python3
"""Worker: обрабатывает очередь Redis (можно запускать несколько экземпляров)."""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from job_queue.redis_queue import dequeue  # noqa: E402
from worker.processor import process_event, process_send_notification  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("worker")

HANDLERS = {
    "process_event": lambda p: process_event(p["event_id"]),
    "send_notification": lambda p: process_send_notification(p["notification_id"]),
}


def main() -> None:
    logger.info("Worker запущен. Ожидание задач...")
    while True:
        try:
            job = dequeue(timeout=5)
        except Exception as exc:
            logger.exception("Ошибка Redis, повтор через 5 с: %s", exc)
            time.sleep(5)
            continue
        if not job:
            continue
        job_type = job.get("type")
        payload = job.get("payload", {})
        handler = HANDLERS.get(job_type)
        if not handler:
            logger.error("Неизвестный тип задачи: %s", job_type)
            continue
        logger.info("Обработка: %s (%s)", job_type, job.get("id"))
        try:
            handler(payload)
        except Exception:
            logger.exception("Ошибка обработки задачи %s", job_type)


if __name__ == "__main__":
    main()
