"""Подписанные ссылки на видео в Yandex Object Storage."""

from __future__ import annotations

import hashlib
import hmac
import logging
from datetime import datetime, timezone
from urllib.parse import quote

from config.settings import (
    YANDEX_BUCKET,
    YANDEX_ENDPOINT,
    YANDEX_PRESIGN_TTL,
    YANDEX_PUBLIC_BASE,
    YANDEX_SECRET_KEY,
    YANDEX_ACCESS_KEY,
)

logger = logging.getLogger(__name__)


def _configured() -> bool:
    return bool(YANDEX_ACCESS_KEY and YANDEX_SECRET_KEY and YANDEX_BUCKET)


def public_object_url(object_key: str) -> str:
    """Публичный URL (бакет с анонимным чтением)."""
    if YANDEX_PUBLIC_BASE:
        base = YANDEX_PUBLIC_BASE.rstrip("/")
        return f"{base}/{quote(object_key.lstrip('/'))}"
    endpoint = YANDEX_ENDPOINT.rstrip("/")
    bucket = YANDEX_BUCKET
    return f"{endpoint}/{bucket}/{quote(object_key.lstrip('/'))}"


def presigned_object_url(object_key: str, expires: int | None = None) -> str | None:
    """
    Подписанный GET URL для приватного бакета (AWS Signature V2, совместимо с Yandex S3).
    """
    if not _configured():
        return None

    ttl = expires or YANDEX_PRESIGN_TTL
    key = object_key.lstrip("/")
    expires_ts = int(datetime.now(timezone.utc).timestamp()) + ttl

    resource = f"/{YANDEX_BUCKET}/{key}"
    string_to_sign = f"GET\n\n\n{expires_ts}\n{resource}"
    signature = hmac.new(
        YANDEX_SECRET_KEY.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        hashlib.sha1,
    ).hexdigest()

    endpoint = YANDEX_ENDPOINT.rstrip("/")
    return (
        f"{endpoint}/{YANDEX_BUCKET}/{quote(key)}"
        f"?AWSAccessKeyId={quote(YANDEX_ACCESS_KEY)}"
        f"&Expires={expires_ts}"
        f"&Signature={quote(signature)}"
    )


def resolve_video_src(video: dict) -> str | None:
    """
    Возвращает URL для воспроизведения.
    - src: готовый URL
    - object_key: публичный или presigned URL
    """
    if video.get("src"):
        return str(video["src"])

    object_key = video.get("object_key")
    if not object_key:
        return None

    if video.get("presign") or not video.get("public"):
        signed = presigned_object_url(object_key)
        if signed:
            return signed
        logger.warning("Не удалось подписать URL Yandex, пробуем публичный")

    return public_object_url(object_key)
