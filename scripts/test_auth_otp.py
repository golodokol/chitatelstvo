#!/usr/bin/env python3
"""Smoke-тест OTP auth: request → verify (код вводится вручную из письма)."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.getenv("AUTH_TEST_BASE", "http://127.0.0.1:8000").rstrip("/")
EMAIL = os.getenv("AUTH_TEST_EMAIL", "").strip()


def post(path: str, payload: dict) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        raw = resp.read().decode()
        return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = raw
        return exc.code, body


def get(path: str, token: str) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        raw = resp.read().decode()
        return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = raw
        return exc.code, body


def main() -> int:
    if not EMAIL:
        print("Задайте AUTH_TEST_EMAIL=email@из.базы")
        return 1

    print("1) request OTP for", EMAIL)
    status, body = post("/api/v1/auth/otp/request", {"email": EMAIL})
    print("   status:", status, body)
    if status != 200:
        return 1

    code = input("2) Введите код из письма: ").strip()
    status, body = post("/api/v1/auth/otp/verify", {"email": EMAIL, "code": code})
    print("   status:", status)
    if status != 200 or not isinstance(body, dict):
        print(body)
        return 1

    token = body.get("access_token", "")
    children = body.get("children", [])
    print("   children:", [c.get("name") for c in children])

    status, me = get("/api/v1/auth/me", token)
    print("3) /me status:", status, "email:", me.get("email") if isinstance(me, dict) else me)
    return 0 if status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
