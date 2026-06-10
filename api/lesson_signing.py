"""Подписанные ссылки на урок — защита автоматических событий."""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid

from config.settings import LESSON_LINK_TTL_SECONDS, LESSON_SIGNING_SECRET, PUBLIC_BASE_URL


def _secret() -> bytes:
    if not LESSON_SIGNING_SECRET:
        raise RuntimeError("LESSON_SIGNING_SECRET не настроен")
    return LESSON_SIGNING_SECRET.encode("utf-8")


def sign_lesson_access(child_id: str | uuid.UUID, slug: str, exp: int | None = None) -> tuple[int, str]:
    if exp is None:
        exp = int(time.time()) + LESSON_LINK_TTL_SECONDS
    cid = str(child_id)
    msg = f"{cid}:{slug}:{exp}"
    sig = hmac.new(_secret(), msg.encode("utf-8"), hashlib.sha256).hexdigest()
    return exp, sig


def verify_lesson_access(child_id: str | uuid.UUID, slug: str, exp: int, sig: str) -> bool:
    if int(time.time()) > int(exp):
        return False
    expected = sign_lesson_access(child_id, slug, exp)[1]
    return hmac.compare_digest(expected, sig)


def build_lesson_url(child_id: str | uuid.UUID, slug: str) -> str:
    exp, sig = sign_lesson_access(child_id, slug)
    cid = str(child_id)
    return f"{PUBLIC_BASE_URL}/lesson/{slug}?child={cid}&exp={exp}&sig={sig}"
