"""Награды сундука: slug урока → папка сказки."""

from __future__ import annotations

from gamification.chest_rewards import canonical_tale_slug, items_for_treasury, rewards_for_tale


def test_canonical_tale_slug_from_lesson_slug():
    assert (
        canonical_tale_slug("grade-1-self_paced-stage-1-lesson-01")
        == "grade-1-stage1-tale-01"
    )
    assert canonical_tale_slug("tsarevna-lyagushka") == "grade-1-stage1-tale-01"
    assert canonical_tale_slug("grade-1-stage1-tale-01") == "grade-1-stage1-tale-01"


def test_rewards_for_lesson_slug_use_creative_tasks():
    items = items_for_treasury(
        rewards_for_tale("grade-1-self_paced-stage-1-lesson-01", "Царевна лягушка")
    )
    labels = [item["label"] for item in items]
    assert labels == [
        "Нарисуй свою лягушку в болоте",
        "Раскрась лягушку",
        "Обведи стрелу",
    ]
    assert all(item.get("download_url") for item in items)


def test_opasnoe_leto_chest_rewards():
    items = items_for_treasury(
        rewards_for_tale("opasnoe-leto", "Опасное лето")
    )
    labels = [item["label"] for item in items]
    assert labels == [
        "Сделай комикс: потоп → театр → роль",
        "Нарисуй свой театр",
        "Напиши письмо герою",
    ]
    assert all(item.get("download_url", "").endswith(".pdf") for item in items)


def test_uralskie_skazy_chest_rewards():
    items = items_for_treasury(
        rewards_for_tale("uralskie-skazy", "Уральские сказы")
    )
    labels = [item["label"] for item in items]
    assert labels == [
        "Сделай комикс: чудо → испытание → цена выбора",
        "Нарисуй дух горы в двух обликах",
        "Напиши свой мини-сказ",
        "Нарисуй Хозяйку Медной горы",
    ]
    assert all(item.get("download_url", "").endswith(".pdf") for item in items)
