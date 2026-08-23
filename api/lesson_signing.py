"""Подписанные ссылки на урок — защита автоматических событий."""

from __future__ import annotations

import hashlib
import hmac
import re
import time
import uuid
from typing import Any

from config.settings import LESSON_LINK_TTL_SECONDS, LESSON_SIGNING_SECRET, PUBLIC_BASE_URL

_LESSON_PATH_RE = re.compile(r"/lesson/([^/?#]+)")


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


def lesson_slug_from_path(url: str) -> str | None:
    match = _LESSON_PATH_RE.search((url or "").strip())
    return match.group(1) if match else None


def sign_quest_next_paths(lesson: dict[str, Any], child_id: str | uuid.UUID) -> None:
    """Replace /lesson/{slug} paths in reward next_paths with signed URLs."""
    stations = lesson.get("stations") or []
    for station in stations:
        paths = station.get("next_paths")
        if not paths:
            continue
        signed: list[dict[str, Any]] = []
        for item in paths:
            if not isinstance(item, dict):
                continue
            row = dict(item)
            slug = str(row.get("slug") or "").strip() or lesson_slug_from_path(str(row.get("url") or ""))
            if slug:
                row["url"] = build_lesson_url(child_id, slug)
            signed.append(row)
        station["next_paths"] = signed
