#!/usr/bin/env python3
"""Smoke-тест GET /api/v1/cabinet после OTP-входа."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.getenv("AUTH_TEST_BASE", "https://api.chitatelstvo.ru").rstrip("/")
EMAIL = os.getenv("AUTH_TEST_EMAIL", "").strip()
TOKEN = os.getenv("AUTH_TEST_TOKEN", "").strip()
CHILD_ID = os.getenv("AUTH_TEST_CHILD_ID", "").strip()


def post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def get(path: str, token: str, child_id: str | None = None) -> tuple[int, dict | str]:
    headers = {"Authorization": f"Bearer {token}"}
    if child_id:
        headers["X-Child-Id"] = child_id
    url = f"{BASE}{path}"
    if child_id and "?" not in path:
        url = f"{url}?child_id={child_id}"
    req = urllib.request.Request(url, headers=headers, method="GET")
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
            print("Задайте AUTH_TEST_TOKEN или AUTH_TEST_EMAIL для OTP")
            return 1
        print("OTP request for", EMAIL)
        post("/api/v1/auth/otp/request", {"email": EMAIL})
        code = input("Код из письма: ").strip()
        verify = post("/api/v1/auth/otp/verify", {"email": EMAIL, "code": code})
        token = verify["access_token"]
        children = verify.get("children") or []
        print("children:", [c.get("name") for c in children])

    status, body = get("/api/v1/cabinet", token)
    print("cabinet (all):", status)
    if status != 200 or not isinstance(body, dict):
        print(body)
        return 1
    print("  children:", [c.get("name") for c in body.get("children", [])])

    cab_children = body.get("children") or []
    if cab_children:
        child_id = str(cab_children[0]["id"])

    if child_id:
        status, one = get("/api/v1/cabinet", token, child_id)
        print("cabinet (one):", status)
        if status != 200:
            print(one)
            return 1
        cab = (one.get("children") or [{}])[0].get("cabinet") or {}
        print("  level:", cab.get("level"), "points:", cab.get("points"))
        print("  continue_url:", cab.get("continue_url"))

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
