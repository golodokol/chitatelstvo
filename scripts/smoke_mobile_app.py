#!/usr/bin/env python3
"""Smoke-тест мобильного API на prod (без OTP — публичные проверки + опционально JWT)."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.getenv("MOBILE_SMOKE_BASE", "https://api.chitatelstvo.ru").rstrip("/")
TOKEN = os.getenv("AUTH_TEST_TOKEN", "").strip()
CHILD_ID = os.getenv("AUTH_TEST_CHILD_ID", "").strip()
LESSON_SLUG = os.getenv("AUTH_TEST_LESSON_SLUG", "early-letters-trial-lesson-01")


class Check:
    def __init__(self) -> None:
        self.failed = 0
        self.passed = 0

    def ok(self, name: str, detail: str = "") -> None:
        self.passed += 1
        suffix = f" — {detail}" if detail else ""
        print(f"  OK  {name}{suffix}")

    def fail(self, name: str, detail: str) -> None:
        self.failed += 1
        print(f"  FAIL {name}: {detail}")


def request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    body: dict | None = None,
    headers: dict | None = None,
) -> tuple[int, dict | str]:
    url = f"{BASE}{path}"
    hdrs = {"Content-Type": "application/json", **(headers or {})}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            if not raw:
                return resp.status, {}
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            body_out = json.loads(raw)
        except json.JSONDecodeError:
            body_out = raw
        return exc.code, body_out


def smoke_public(check: Check) -> None:
    print("\n== Public endpoints ==")
    status, body = request("GET", "/health")
    if status == 200 and isinstance(body, dict) and body.get("status") == "ok":
        check.ok("GET /health", f"queue={body.get('queue_length')}")
    else:
        check.fail("GET /health", f"{status} {body}")

    status, body = request("POST", "/api/v1/auth/otp/request", body={"email": "smoke-not-registered@example.com"})
    if status == 200 and isinstance(body, dict) and body.get("status") == "sent":
        check.ok("POST /api/v1/auth/otp/request", "neutral response")
    else:
        check.fail("POST /api/v1/auth/otp/request", f"{status} {body}")

    status, body = request("GET", "/api/v1/cabinet")
    if status == 401:
        check.ok("GET /api/v1/cabinet without token", "401")
    else:
        check.fail("GET /api/v1/cabinet without token", f"expected 401, got {status}")

    status, body = request("GET", "/api/v1/auth/me")
    if status == 401:
        check.ok("GET /api/v1/auth/me without token", "401")
    else:
        check.fail("GET /api/v1/auth/me without token", f"expected 401, got {status}")

    status, body = request("GET", "/api/v1/cabinet", token="invalid.jwt.token")
    if status == 401:
        check.ok("GET /api/v1/cabinet bad token", "401")
    else:
        check.fail("GET /api/v1/cabinet bad token", f"expected 401, got {status}")

    status, body = request(
        "POST",
        "/api/v1/auth/otp/verify",
        body={"email": "smoke-not-registered@example.com", "code": "000000"},
    )
    if status == 401:
        check.ok("POST /api/v1/auth/otp/verify bad code", "401")
    else:
        check.fail("POST /api/v1/auth/otp/verify bad code", f"expected 401, got {status}")


def smoke_authenticated(check: Check, token: str, child_id: str) -> None:
    print("\n== Authenticated (JWT) ==")
    status, me = request("GET", "/api/v1/auth/me", token=token)
    if status == 200 and isinstance(me, dict) and me.get("email"):
        check.ok("GET /api/v1/auth/me", me.get("email", ""))
    else:
        check.fail("GET /api/v1/auth/me", f"{status} {me}")
        return

    status, cab = request("GET", f"/api/v1/cabinet?child_id={child_id}", token=token)
    if status != 200 or not isinstance(cab, dict):
        check.fail("GET /api/v1/cabinet", f"{status} {cab}")
        return

    children = cab.get("children") or []
    if not children:
        check.fail("GET /api/v1/cabinet", "empty children[]")
        return

    child = children[0]
    cabinet = child.get("cabinet") or {}
    check.ok(
        "GET /api/v1/cabinet",
        f"{child.get('name')} level={cabinet.get('level')} points={cabinet.get('points')}",
    )

    tracks = cabinet.get("tracks") or []
    if tracks:
        check.ok("cabinet.tracks", f"{len(tracks)} track(s)")
    elif cabinet.get("chest") or cabinet.get("weekly_lessons"):
        check.ok("cabinet legacy layout", "chest/weekly present")

    continue_url = cabinet.get("continue_url")
    if continue_url:
        check.ok("cabinet.continue_url", continue_url[:72] + ("…" if len(continue_url) > 72 else ""))
    else:
        check.ok("cabinet.continue_url", "none (all done or locked)")

    parent = cabinet.get("parent")
    if parent or cab.get("parent_guide"):
        check.ok("parent block", "present")
    else:
        check.fail("parent block", "missing parent summary")

    slug = LESSON_SLUG
    status, lesson = request(
        "GET",
        f"/api/v1/lessons/{slug}?child_id={child_id}",
        token=token,
    )
    if status == 200 and isinstance(lesson, dict) and lesson.get("lesson_url"):
        fmt = lesson.get("lesson_format") or ("quest" if lesson.get("stations") else "tale")
        check.ok("GET /api/v1/lessons/{slug}", f"{lesson.get('title')} [{fmt}]")
        lesson_url = lesson["lesson_url"]
        try:
            req = urllib.request.Request(lesson_url, method="GET")
            with urllib.request.urlopen(req, timeout=30) as resp:
                check.ok("lesson_url reachable", f"HTTP {resp.status}")
        except urllib.error.HTTPError as exc:
            if exc.code in (200, 302):
                check.ok("lesson_url reachable", f"HTTP {exc.code}")
            else:
                check.fail("lesson_url reachable", f"HTTP {exc.code}")
    elif status == 403:
        check.ok("GET /api/v1/lessons/{slug}", f"403 (no access to {slug}) — skip")
    else:
        check.fail("GET /api/v1/lessons/{slug}", f"{status} {lesson}")

    tale_slug = (cabinet.get("chest") or {}).get("tale_slug") or ""
    if tale_slug:
        status, chest = request(
            "POST",
            "/api/v1/chest/claim",
            token=token,
            body={"child_id": child_id, "tale_slug": tale_slug},
        )
        if status in (200, 400) and isinstance(chest, dict):
            st = chest.get("status") or chest.get("detail") or status
            check.ok("POST /api/v1/chest/claim", str(st))
        else:
            check.fail("POST /api/v1/chest/claim", f"{status} {chest}")
    else:
        check.ok("POST /api/v1/chest/claim", "skipped (no chest tale_slug)")


def main() -> int:
    print(f"Mobile smoke against {BASE}")
    check = Check()
    smoke_public(check)

    if TOKEN and CHILD_ID:
        smoke_authenticated(check, TOKEN, CHILD_ID)
    elif TOKEN:
        status, me = request("GET", "/api/v1/auth/me", token=TOKEN)
        if status == 200 and isinstance(me, dict):
            children = me.get("children") or []
            if children:
                smoke_authenticated(check, TOKEN, str(children[0]["id"]))
            else:
                print("\n== Authenticated: skipped (no children in /me) ==")
        else:
            check.fail("AUTH_TEST_TOKEN", f"invalid token: {status}")
    else:
        print("\n== Authenticated: skipped ==")
        print("  Set AUTH_TEST_TOKEN (+ optional AUTH_TEST_CHILD_ID) for full cabinet/lesson smoke.")

    print(f"\nResult: {check.passed} passed, {check.failed} failed")
    return 1 if check.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
