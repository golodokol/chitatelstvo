"""JWT-сессии для входа родителя (email + OTP)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt

from config.settings import JWT_SECRET, JWT_TTL_SECONDS


class AuthError(Exception):
    """Невалидный или просроченный токен."""


def _require_secret() -> str:
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET не настроен")
    return JWT_SECRET


def create_access_token(*, family_id: uuid.UUID, email: str) -> tuple[str, int]:
    secret = _require_secret()
    now = datetime.now(timezone.utc)
    expires_in = JWT_TTL_SECONDS
    payload = {
        "sub": email.strip().lower(),
        "family_id": str(family_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in)).timestamp()),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token, expires_in


def decode_access_token(token: str) -> dict:
    secret = _require_secret()
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Сессия истекла") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError("Неверный токен") from exc
    if payload.get("type") != "access":
        raise AuthError("Неверный тип токена")
    return payload
