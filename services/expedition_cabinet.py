"""Мини-кабинет Читательской экспедиции: профили, паспорт, доступ, тарифы.

Аккаунт родителя и ребёнка — те же Family/Child, что и в школе.
Прогресс экспедиции хранится отдельно (JSON + таблицы БД при наличии).
Цены тарифов только из data/expedition/tariffs.json.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config.settings import JWT_SECRET, ROOT

STORE = ROOT / "data" / "expedition" / "cabinet"
TARIFFS_PATH = ROOT / "data" / "expedition" / "tariffs.json"
DATA_PATH = ROOT / "static" / "expedition" / "data.json"
SESSIONS = STORE / "sessions"
PROFILES = STORE / "profiles"

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_SLUG = re.compile(r"^[a-z0-9-]{1,80}$")

STAMP_LEVELS = ("marker", "basic", "gold")
FREE_REGISTERED_PER_REGION = 2
START_REGION = "yaroslavskaya-oblast"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_dirs() -> None:
    SESSIONS.mkdir(parents=True, exist_ok=True)
    PROFILES.mkdir(parents=True, exist_ok=True)


def load_catalog() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def load_tariffs() -> dict:
    if not TARIFFS_PATH.exists():
        return {"items": [], "updated_at": None}
    return json.loads(TARIFFS_PATH.read_text(encoding="utf-8"))


def save_tariffs(payload: dict) -> dict:
    payload = dict(payload)
    payload["updated_at"] = datetime.now(timezone.utc).date().isoformat()
    TARIFFS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TARIFFS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def public_tariffs() -> list[dict]:
    data = load_tariffs()
    items = []
    for item in data.get("items") or []:
        if item.get("active") is False:
            continue
        items.append(
            {
                "id": item.get("id"),
                "code": item.get("code"),
                "title": item.get("title"),
                "blurb": item.get("blurb"),
                "price_rub": item.get("price_rub"),
                "period_days": item.get("period_days"),
                "child_profiles": item.get("child_profiles"),
                "audience": item.get("audience") or "parent",
                "materials": item.get("materials") or [],
            }
        )
    return items


def _session_path(token: str) -> Path:
    return SESSIONS / f"{token}.json"


def _profile_path(email: str) -> Path:
    key = hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()[:24]
    return PROFILES / f"{key}.json"


def _hash_password(password: str) -> str:
    pepper = JWT_SECRET or "expedition-dev-pepper"
    return hashlib.sha256(f"{password}:{pepper}".encode("utf-8")).hexdigest()


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def empty_progress() -> dict:
    return {
        "stories": {},
        "regions": {},
        "stamps": {},
        "badges": [],
        "route": "",
        "listened": [],
        "purchases": [],
        "favorite_story": "",
        "favorite_hero": "",
        "last_work": "",
        "next_stop": "",
        "quiz": {},
    }


def load_session(token: str | None) -> dict | None:
    if not token or not re.match(r"^[a-zA-Z0-9_-]{16,80}$", token):
        return None
    return _read_json(_session_path(token))


def load_profile_by_email(email: str) -> dict | None:
    return _read_json(_profile_path(email))


def _new_profile(
    *,
    child_name: str,
    child_age: int | None,
    parent_name: str,
    email: str,
    avatar: str,
    family_id: str | None = None,
    child_id: str | None = None,
) -> dict:
    now = _utcnow()
    return {
        "id": str(uuid.uuid4()),
        "email": email.strip().lower(),
        "parent_name": parent_name.strip(),
        "child_name": child_name.strip(),
        "child_age": child_age,
        "avatar": avatar or "compass",
        "family_id": family_id,
        "child_id": child_id,
        "started_at": now,
        "level": "Старт",
        "consents": {"pd": True, "expedition": True},
        "progress": empty_progress(),
        "updated_at": now,
    }


def register_expedition(
    *,
    child_name: str,
    parent_name: str,
    email: str,
    child_age: int | None = None,
    password: str | None = None,
    avatar: str = "compass",
    consent: bool = False,
    guest_progress: dict | None = None,
) -> dict:
    _ensure_dirs()
    email = (email or "").strip().lower()
    child_name = (child_name or "").strip()
    parent_name = (parent_name or "").strip()
    if not child_name or len(child_name) > 80:
        raise ValueError("child_name")
    if not parent_name or len(parent_name) > 120:
        raise ValueError("parent_name")
    if not _EMAIL.match(email):
        raise ValueError("email")
    if not consent:
        raise ValueError("consent")
    if child_age is not None and (child_age < 4 or child_age > 16):
        raise ValueError("child_age")

    profile = load_profile_by_email(email) or _new_profile(
        child_name=child_name,
        child_age=child_age,
        parent_name=parent_name,
        email=email,
        avatar=avatar,
    )
    profile["child_name"] = child_name
    profile["parent_name"] = parent_name
    profile["child_age"] = child_age
    profile["avatar"] = avatar or profile.get("avatar") or "compass"
    if password:
        if len(password) < 6:
            raise ValueError("password")
        profile["password_hash"] = _hash_password(password)
    if guest_progress:
        profile["progress"] = merge_progress(profile.get("progress") or empty_progress(), guest_progress)
    apply_stamp_rules(profile)
    profile["updated_at"] = _utcnow()
    _write_json(_profile_path(email), profile)

    token = secrets.token_urlsafe(24)
    session = {
        "token": token,
        "email": email,
        "profile_id": profile["id"],
        "created_at": _utcnow(),
        "role": "parent",
    }
    _write_json(_session_path(token), session)
    return {"token": token, "profile": public_profile(profile)}


def login_expedition(*, email: str, password: str | None = None, token: str | None = None) -> dict:
    _ensure_dirs()
    email = (email or "").strip().lower()
    if token:
        session = load_session(token)
        if not session:
            raise ValueError("session")
        profile = load_profile_by_email(session["email"])
        if not profile:
            raise ValueError("session")
        return {"token": token, "profile": public_profile(profile)}
    if not _EMAIL.match(email):
        raise ValueError("email")
    profile = load_profile_by_email(email)
    if not profile:
        raise ValueError("not_found")
    stored = profile.get("password_hash")
    if stored:
        if not password or _hash_password(password) != stored:
            raise ValueError("password")
    new_token = secrets.token_urlsafe(24)
    session = {
        "token": new_token,
        "email": email,
        "profile_id": profile["id"],
        "created_at": _utcnow(),
        "role": "parent",
    }
    _write_json(_session_path(new_token), session)
    return {"token": new_token, "profile": public_profile(profile)}


def merge_progress(base: dict, incoming: dict) -> dict:
    out = empty_progress()
    out.update({k: v for k, v in (base or {}).items() if k in out or k in incoming})
    stories = dict(base.get("stories") or {})
    for slug, rec in (incoming.get("stories") or {}).items():
        if not _SLUG.match(str(slug)):
            continue
        prev = stories.get(slug) or {}
        merged = dict(prev)
        if isinstance(rec, dict):
            merged.update(rec)
        stories[slug] = merged
    out["stories"] = stories
    regions = dict(base.get("regions") or {})
    regions.update(incoming.get("regions") or {})
    out["regions"] = regions
    stamps = dict(base.get("stamps") or {})
    for slug, rec in (incoming.get("stamps") or {}).items():
        if not _SLUG.match(str(slug)):
            continue
        prev = stamps.get(slug) or {}
        if _stamp_rank(rec.get("level") if isinstance(rec, dict) else rec) >= _stamp_rank(prev.get("level")):
            stamps[slug] = rec if isinstance(rec, dict) else {"level": rec}
    out["stamps"] = stamps
    badges = list(dict.fromkeys((base.get("badges") or []) + (incoming.get("badges") or [])))
    out["badges"] = badges
    for key in ("route", "favorite_story", "favorite_hero", "last_work", "next_stop"):
        out[key] = incoming.get(key) or base.get(key) or ""
    listened = list(dict.fromkeys((base.get("listened") or []) + (incoming.get("listened") or [])))
    out["listened"] = listened
    out["purchases"] = list(base.get("purchases") or incoming.get("purchases") or [])
    out["quiz"] = incoming.get("quiz") or base.get("quiz") or {}
    return out


def _stamp_rank(level: Any) -> int:
    try:
        return STAMP_LEVELS.index(str(level))
    except ValueError:
        return -1


def save_progress(token: str, incoming: dict) -> dict:
    session = load_session(token)
    if not session:
        raise ValueError("session")
    profile = load_profile_by_email(session["email"])
    if not profile:
        raise ValueError("session")
    profile["progress"] = merge_progress(profile.get("progress") or empty_progress(), incoming or {})
    apply_stamp_rules(profile)
    profile["updated_at"] = _utcnow()
    _write_json(_profile_path(session["email"]), profile)
    return public_profile(profile)


def apply_stamp_rules(profile: dict) -> None:
    catalog = load_catalog()
    progress = profile.setdefault("progress", empty_progress())
    stories_by_region: dict[str, list[str]] = {}
    for story in catalog.get("stories") or []:
        stories_by_region.setdefault(story["region"], []).append(story["slug"])
    done = {
        slug
        for slug, rec in (progress.get("stories") or {}).items()
        if isinstance(rec, dict) and rec.get("done")
    }
    stamps = progress.setdefault("stamps", {})
    now = _utcnow()
    for region in catalog.get("regions") or []:
        slug = region["slug"]
        region_stories = stories_by_region.get(slug) or []
        finished = [s for s in region_stories if s in done]
        if not finished:
            continue
        count = len(finished)
        if count >= 3:
            level = "gold"
        elif count >= 1:
            level = "basic"
        else:
            level = "marker"
        stamp_meta = region.get("stamp") or {}
        prev = stamps.get(slug) or {}
        if _stamp_rank(level) > _stamp_rank(prev.get("level")):
            stamps[slug] = {
                "level": level,
                "region_name": region.get("name"),
                "poetic_title": stamp_meta.get("poetic_title") or region.get("pin") or region.get("name"),
                "motif": stamp_meta.get("motif") or "",
                "color": stamp_meta.get("color") or "#C6A15B",
                "symbol": stamp_meta.get("symbol") or "",
                "earned_at": now,
            }
        progress.setdefault("regions", {})[slug] = True


def public_profile(profile: dict) -> dict:
    progress = profile.get("progress") or empty_progress()
    done_stories = [
        slug for slug, rec in (progress.get("stories") or {}).items() if isinstance(rec, dict) and rec.get("done")
    ]
    return {
        "id": profile.get("id"),
        "child_name": profile.get("child_name"),
        "child_age": profile.get("child_age"),
        "parent_name": profile.get("parent_name"),
        "email": profile.get("email"),
        "avatar": profile.get("avatar") or "compass",
        "started_at": profile.get("started_at"),
        "level": profile.get("level") or "Старт",
        "open_regions": len(progress.get("regions") or {}),
        "open_stories": len(done_stories),
        "stamps": len(progress.get("stamps") or {}),
        "badges": len(progress.get("badges") or []),
        "progress": progress,
        "access": access_map(profile),
    }


def _has_season_access(progress: dict) -> bool:
    codes = {p.get("code") for p in (progress.get("purchases") or []) if isinstance(p, dict)}
    return bool(codes & {"expedition_subscription", "family_passport", "library_license"})


def _has_route_access(progress: dict, route_slug: str | None, region_slug: str | None) -> bool:
    if _has_season_access(progress):
        return True
    for item in progress.get("purchases") or []:
        if not isinstance(item, dict) or item.get("code") != "route_purchase":
            continue
        if route_slug and route_slug in (item.get("route_slugs") or []):
            return True
        if region_slug and region_slug in (item.get("region_slugs") or []):
            return True
    return False


def story_access(story: dict, profile: dict | None) -> str:
    """Stories are open to try. Saving a passport and stamps needs a registered profile."""
    if story.get("status") == "hidden":
        return "locked"
    flag = story.get("access") or "open"
    if flag == "demo":
        return "demo"
    return "open"


def access_map(profile: dict | None) -> dict[str, str]:
    catalog = load_catalog()
    return {s["slug"]: story_access(s, profile) for s in catalog.get("stories") or []}


def guest_state(guest_progress: dict | None = None) -> dict:
    progress = merge_progress(empty_progress(), guest_progress or {})
    return {
        "signed_in": False,
        "profile": None,
        "tariffs": public_tariffs(),
        "access": access_map(None),
        "progress": progress,
    }


def session_state(token: str | None, guest_progress: dict | None = None) -> dict:
    session = load_session(token) if token else None
    if not session:
        return guest_state(guest_progress)
    profile = load_profile_by_email(session["email"])
    if not profile:
        return guest_state(guest_progress)
    if guest_progress:
        profile["progress"] = merge_progress(profile.get("progress") or empty_progress(), guest_progress)
        profile["updated_at"] = _utcnow()
        _write_json(_profile_path(session["email"]), profile)
    pub = public_profile(profile)
    return {
        "signed_in": True,
        "profile": pub,
        "tariffs": public_tariffs(),
        "access": pub["access"],
        "progress": pub["progress"],
        "token": token,
    }
