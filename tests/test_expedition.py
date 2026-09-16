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


def test_expedition_unknown_form_404():
    res = client.post("/expedition/api/unknown", json={})
    assert res.status_code == 404


def test_expedition_kit():
    res = client.get("/expedition/kit.html")
    assert res.status_code == 200
    assert "Литературные детективы" in res.text


def test_expedition_badges_in_school_rules():
    from gamification.rules import EVENT_RULES

    assert EVENT_RULES["expedition_story"]["badge"] == "Искатель сказок"
    assert EVENT_RULES["expedition_detail"]["badge"] == "Сыщик деталей"
