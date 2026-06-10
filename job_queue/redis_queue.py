"""Простая очередь задач на Redis — масштабируется добавлением worker-ов."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import redis

from config.settings import QUEUE_KEY, REDIS_URL

logger = logging.getLogger(__name__)


def _client() -> redis.Redis:
    # socket_timeout=None — иначе blpop падает с TimeoutError при ожидании задач
    return redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_timeout=None,
        socket_connect_timeout=5,
    )


def enqueue(job_type: str, payload: dict[str, Any]) -> str:
    job_id = str(uuid.uuid4())
    job = {"id": job_id, "type": job_type, "payload": payload}
    _client().rpush(QUEUE_KEY, json.dumps(job, ensure_ascii=False))
    logger.info("Задача в очереди: %s (%s)", job_type, job_id)
    return job_id


def dequeue(timeout: int = 5) -> dict[str, Any] | None:
    item = _client().blpop(QUEUE_KEY, timeout=timeout)
    if not item:
        return None
    _, raw = item
    return json.loads(raw)


def queue_length() -> int:
    return int(_client().llen(QUEUE_KEY))
