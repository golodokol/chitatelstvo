"""Прототип Читательской экспедиции."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_expedition_home_ok():
    res = client.get("/expedition")
    assert res.status_code == 200
    assert "Читательская экспедиция" in res.text
    assert "chit-exp-root" in res.text


def test_expedition_story_seo_title():
    res = client.get("/expedition/stories/tsarevna-lyagushka")
    assert res.status_code == 200
    assert "Царевна-лягушка" in res.text


def test_expedition_data_json():
    res = client.get("/static/expedition/data.json")
    assert res.status_code == 200
    data = res.json()
    assert len(data["regions"]) >= 10
    assert len(data["stories"]) >= 10
    assert len(data["routes"]) == 3


def test_expedition_library_form():
    res = client.post(
        "/expedition/api/library",
        json={"org": "Детская библиотека", "city": "Ярославль", "email": "lib@example.com"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["status"] == "submitted"


def test_expedition_tariffs_json():
    res = client.get("/expedition/api/tariffs")
    assert res.status_code == 200
    items = res.json()["items"]
    codes = {item["code"] for item in items}
    assert "route_purchase" in codes
    assert "expedition_subscription" in codes
    assert all("price_rub" in item for item in items)


def test_expedition_cabinet_guest_state():
    res = client.get("/expedition/api/cabinet")
    assert res.status_code == 200
    body = res.json()
    assert body["signed_in"] is False
    assert body["access"]["tsarevna-lyagushka"] == "demo"
    assert body["access"]["morozko"] == "locked"


def test_expedition_register_and_progress(tmp_path, monkeypatch):
    from services import expedition_cabinet as cabinet

    monkeypatch.setattr(cabinet, "STORE", tmp_path)
    monkeypatch.setattr(cabinet, "SESSIONS", tmp_path / "sessions")
    monkeypatch.setattr(cabinet, "PROFILES", tmp_path / "profiles")

    res = client.post(
        "/expedition/api/cabinet/register",
        json={
            "child_name": "Мира",
            "child_age": 8,
            "parent_name": "Анна",
            "email": "anna-exp@example.com",
            "consent": True,
            "progress": {"stories": {"tsarevna-lyagushka": {"done": True}}},
        },
    )
    assert res.status_code == 200
    token = res.json()["token"]
    profile = res.json()["profile"]
    assert profile["child_name"] == "Мира"
    assert profile["progress"]["stamps"]["yaroslavskaya-oblast"]["level"] == "basic"

    saved = client.post(
        "/expedition/api/cabinet/progress",
        headers={"Authorization": f"Bearer {token}"},
        json={"stories": {"alenushka": {"done": True}}, "badges": ["reader"]},
    )
    assert saved.status_code == 200
    stamps = saved.json()["profile"]["progress"]["stamps"]
    assert stamps["yaroslavskaya-oblast"]["poetic_title"]


def test_expedition_register_requires_consent():
    res = client.post(
        "/expedition/api/cabinet/register",
        json={"child_name": "Мира", "parent_name": "Анна", "email": "x@example.com"},
    )
    assert res.status_code == 400


def test_expedition_kit():
    res = client.get("/expedition/kit.html")
    assert res.status_code == 200
    assert "Литературные детективы" in res.text


def test_expedition_badges_in_school_rules():
    from gamification.rules import EVENT_RULES

    assert EVENT_RULES["expedition_story"]["badge"] == "Искатель сказок"
    assert EVENT_RULES["expedition_detail"]["badge"] == "Сыщик деталей"
