"""OTP-коды для входа по email — хранение в Redis."""

from __future__ import annotations

import hashlib
import logging
import secrets

import redis

from config.settings import (
    JWT_SECRET,
    OTP_MAX_SENDS_PER_HOUR,
    OTP_MAX_VERIFY_ATTEMPTS,
    OTP_TTL_SECONDS,
    REDIS_URL,
    WEBHOOK_SECRET,
)
from db import repository as repo
from db.models import Child, Family
from notifications.email_templates import SUBJECT_OTP, build_otp_message
from notifications.email_channel import send_email
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_OTP_PREFIX = "auth:otp:"
_SEND_PREFIX = "auth:otp:send:"
_VERIFY_PREFIX = "auth:otp:verify:"


def _redis() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=5)


def _pepper() -> str:
    return JWT_SECRET or WEBHOOK_SECRET or "dev-insecure-pepper"


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _otp_key(email: str) -> str:
    return f"{_OTP_PREFIX}{_normalize_email(email)}"


def _hash_code(email: str, code: str) -> str:
    msg = f"{_normalize_email(email)}:{code}:{_pepper()}"
    return hashlib.sha256(msg.encode("utf-8")).hexdigest()


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _can_send(email: str) -> bool:
    key = f"{_SEND_PREFIX}{_normalize_email(email)}"
    client = _redis()
    count = client.incr(key)
    if count == 1:
        client.expire(key, 3600)
    return int(count) <= OTP_MAX_SENDS_PER_HOUR


def _register_failed_verify(email: str) -> bool:
    """True если лимит попыток не превышен."""
    key = f"{_VERIFY_PREFIX}{_normalize_email(email)}"
    client = _redis()
    count = client.incr(key)
    if count == 1:
        client.expire(key, OTP_TTL_SECONDS)
    return int(count) <= OTP_MAX_VERIFY_ATTEMPTS


def _clear_failed_verify(email: str) -> None:
    _redis().delete(f"{_VERIFY_PREFIX}{_normalize_email(email)}")


def _store_code(email: str, code: str) -> None:
    client = _redis()
    client.setex(_otp_key(email), OTP_TTL_SECONDS, _hash_code(email, code))


def _check_code(email: str, code: str) -> bool:
    stored = _redis().get(_otp_key(email))
    if not stored:
        return False
    candidate = _hash_code(email, code.strip())
    return secrets.compare_digest(stored, candidate)


def _clear_code(email: str) -> None:
    _redis().delete(_otp_key(email))


def request_login_otp(db: Session, email: str) -> bool:
    """Отправить OTP, если семья с таким email есть. Возвращает, было ли письмо."""
    normalized = _normalize_email(email)
    if not _can_send(normalized):
        raise ValueError("rate_limit_send")

    family = repo.get_primary_family_for_email(db, normalized)
    if not family:
        logger.info("OTP request: email не найден (%s)", normalized)
        return False

    code = _generate_code()
    _store_code(normalized, code)
    body = build_otp_message(code=code, ttl_minutes=max(1, OTP_TTL_SECONDS // 60))
    try:
        send_email(
            to=normalized,
            subject=SUBJECT_OTP,
            body=body,
        )
    except Exception as exc:
        _clear_code(normalized)
        logger.exception("OTP email failed: %s", normalized)
        raise RuntimeError("SMTP send failed") from exc
    logger.info("OTP отправлен: %s", normalized)
    return True


def verify_login_otp(db: Session, email: str, code: str) -> tuple[Family, list[Child]]:
    normalized = _normalize_email(email)
    if not _register_failed_verify(normalized):
        raise ValueError("rate_limit_verify")

    if not _check_code(normalized, code):
        raise ValueError("invalid_code")

    family = repo.get_primary_family_for_email(db, normalized)
    if not family:
        raise ValueError("invalid_code")

    _clear_code(normalized)
    _clear_failed_verify(normalized)
    family = repo.get_family_by_id(db, family.id) or family
    children = repo.list_children_for_family(db, family.id)
    return family, children
