"""Public smoke checks for mobile API (prod-safe, no credentials)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

BASE = os.getenv("MOBILE_SMOKE_BASE", "https://api.chitatelstvo.ru").rstrip("/")


def _request(method: str, path: str, body: dict | None = None, token: str | None = None) -> tuple[int, dict | str]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw
        return exc.code, parsed


def test_health_ok():
    status, body = _request("GET", "/health")
    assert status == 200
    assert isinstance(body, dict)
    assert body.get("status") == "ok"


def test_otp_request_neutral():
    status, body = _request(
        "POST",
        "/api/v1/auth/otp/request",
        {"email": "pytest-smoke-not-registered@example.com"},
    )
    assert status == 200
    assert body.get("status") == "sent"


def test_cabinet_requires_auth():
    status, _ = _request("GET", "/api/v1/cabinet")
    assert status == 401


def test_auth_me_requires_auth():
    status, _ = _request("GET", "/api/v1/auth/me")
    assert status == 401


def test_invalid_jwt_rejected():
    status, _ = _request("GET", "/api/v1/cabinet", token="not.a.jwt")
    assert status == 401
