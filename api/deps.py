from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Header, HTTPException, Request

from config.settings import RATE_LIMIT_PER_MINUTE, WEBHOOK_SECRET

_hits: dict[str, list[float]] = defaultdict(list)


def verify_webhook_secret(x_webhook_secret: str | None = Header(default=None)) -> None:
    if not WEBHOOK_SECRET:
        raise HTTPException(500, "WEBHOOK_SECRET не настроен на сервере")
    if x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(401, "Неверный webhook secret")


def rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window = _hits[ip]
    _hits[ip] = [t for t in window if now - t < 60]
    if len(_hits[ip]) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(429, "Слишком много запросов")
    _hits[ip].append(now)
