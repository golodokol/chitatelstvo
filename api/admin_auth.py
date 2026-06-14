from __future__ import annotations

import hashlib
import hmac

from fastapi import HTTPException, Request, Response

from config.settings import ADMIN_PASSWORD, PUBLIC_BASE_URL, WEBHOOK_SECRET

ADMIN_COOKIE = "chitatelstvo_admin"
ADMIN_COOKIE_MAX_AGE = 60 * 60 * 24 * 7


def admin_enabled() -> bool:
    return bool(ADMIN_PASSWORD)


def _signing_key() -> bytes:
    secret = ADMIN_PASSWORD or WEBHOOK_SECRET
    return secret.encode("utf-8")


def make_admin_token() -> str:
    return hmac.new(_signing_key(), b"admin", hashlib.sha256).hexdigest()


def verify_admin_token(token: str | None) -> bool:
    if not token or not admin_enabled():
        return False
    expected = make_admin_token()
    return hmac.compare_digest(token, expected)


def is_admin(request: Request) -> bool:
    return verify_admin_token(request.cookies.get(ADMIN_COOKIE))


def require_admin(request: Request) -> None:
    if not admin_enabled():
        raise HTTPException(503, "Админ-панель не настроена: задайте ADMIN_PASSWORD в .env")
    if not is_admin(request):
        raise HTTPException(401, "Требуется вход")


def set_admin_cookie(response: Response) -> None:
    response.set_cookie(
        ADMIN_COOKIE,
        make_admin_token(),
        max_age=ADMIN_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=PUBLIC_BASE_URL.startswith("https://"),
    )


def clear_admin_cookie(response: Response) -> None:
    response.delete_cookie(ADMIN_COOKIE)
