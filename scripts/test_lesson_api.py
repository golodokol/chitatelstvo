#!/usr/bin/env python3
"""Smoke-тест GET /api/v1/lessons/{slug} после OTP."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

BASE = os.getenv("AUTH_TEST_BASE", "https://api.chitatelstvo.ru").rstrip("/")
EMAIL = os.getenv("AUTH_TEST_EMAIL", "").strip()
TOKEN = os.getenv("AUTH_TEST_TOKEN", "").strip()
CHILD_ID = os.getenv("AUTH_TEST_CHILD_ID", "").strip()
SLUG = os.getenv("AUTH_TEST_LESSON_SLUG", "tsarevna-lyagushka")
TEST_KEY = os.getenv("TEST_LESSON_SECRET", "").strip()


def post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def get_lesson(token: str, child_id: str, slug: str) -> tuple[int, dict | str]:
    url = f"{BASE}/api/v1/lessons/{slug}?child_id={child_id}"
    if TEST_KEY:
        url += f"&test_key={TEST_KEY}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = raw
        return exc.code, body


def main() -> int:
    token = TOKEN
    child_id = CHILD_ID

    if not token:
        if not EMAIL:
            print("Задайте AUTH_TEST_TOKEN или AUTH_TEST_EMAIL")
            return 1
        post("/api/v1/auth/otp/request", {"email": EMAIL})
        code = input("Код из письма: ").strip()
        verify = post("/api/v1/auth/otp/verify", {"email": EMAIL, "code": code})
        token = verify["access_token"]
        children = verify.get("children") or []
        if children:
            child_id = str(children[0]["id"])

    if not child_id:
        print("Нет child_id")
        return 1

    status, body = get_lesson(token, child_id, SLUG)
    print("lesson GET:", status)
    if status != 200 or not isinstance(body, dict):
        print(body)
        return 1

    print("  title:", body.get("title"))
    print("  video.type:", (body.get("video") or {}).get("type"))
    print("  comprehension:", "yes" if body.get("comprehension_quiz") else "no")
    print("  lesson_url:", (body.get("lesson_url") or "")[:80], "...")
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
