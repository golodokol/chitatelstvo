"""Тесты расширенных типов вопросов в квизах урока."""

from lessons.loader import (
    get_lesson,
    quiz_for_client,
    retelling_quiz_for_client,
    retelling_uses_images,
    score_question,
    score_quiz,
)


def test_score_single_question():
    q = {"id": "q1", "type": "single", "correct": "a"}
    assert score_question(q, "a") is True
    assert score_question(q, "b") is False


def test_score_multi_question():
    q = {"id": "m1", "type": "multi", "correct": ["a", "c"]}
    assert score_question(q, ["c", "a"]) is True
    assert score_question(q, ["a"]) is False


def test_score_matching_question():
    q = {
        "id": "m2",
        "type": "matching",
        "correct": {"ivan": "yard", "frog": "swamp"},
    }
    assert score_question(q, {"frog": "swamp", "ivan": "yard"}) is True
    assert score_question(q, {"ivan": "swamp", "frog": "yard"}) is False


def test_quiz_for_client_keeps_picture_match_images():
    quiz = get_lesson("tsarevna-lyagushka")["meaning_quiz"]
    client = quiz_for_client(quiz, shuffle_options=False)
    q5 = next(q for q in client["questions"] if q["id"] == "m5")
    assert q5["type"] == "picture_match"
    assert [pic["image"] for pic in q5["pictures"]] == [
        "/static/lessons/tsarevna/ivan.png",
        "/static/lessons/tsarevna/lyagushka.png",
        "/static/lessons/tsarevna/koschei.png",
        "/static/lessons/tsarevna/vasilisa.png",
    ]
    assert {label["text"] for label in q5["labels"]} == {
        "Царевна Лягушка",
        "Иван-царевич",
        "Кощей бессмертный",
        "Василиса Премудрая",
    }


def test_retelling_uses_images_by_group():
    assert retelling_uses_images("grade-1") is True
    assert retelling_uses_images("grade-2") is True
    assert retelling_uses_images("extra-6-8") is True
    assert retelling_uses_images("grade-3") is False
    assert retelling_uses_images("grade-4") is False
    assert retelling_uses_images("extra-9-11") is False


def test_retelling_quiz_for_client_ordering_images():
    quiz = get_lesson("tsarevna-lyagushka")["retelling_quiz"]
    client = retelling_quiz_for_client(quiz, group_code="grade-1", shuffle_options=False)
    q1 = client["questions"][0]
    assert q1["type"] == "ordering"
    assert q1["id"] == "r1"
    assert [item["id"] for item in q1["items"]] == ["e1", "e2", "e3", "e4", "e5"]
    assert all(item.get("image") for item in q1["items"])


def test_retelling_quiz_for_client_strips_images_for_older():
    quiz = get_lesson("tsarevna-lyagushka")["retelling_quiz"]
    client = retelling_quiz_for_client(quiz, group_code="grade-3", shuffle_options=False)
    q1 = client["questions"][0]
    assert q1["type"] == "ordering"
    assert all("image" not in item for item in q1["items"])
    assert q1["items"][0]["text"] == "Царь собрал трёх сыновей у замка"


def test_retelling_quiz_for_client_shuffles_ordering_items():
    quiz = get_lesson("tsarevna-lyagushka")["retelling_quiz"]
    orders = {
        tuple(item["id"] for item in retelling_quiz_for_client(quiz, shuffle_options=True)["questions"][0]["items"])
        for _ in range(30)
    }
    assert len(orders) > 1


def test_score_picture_match_question():
    q = {
        "id": "m5",
        "type": "picture_match",
        "correct": {"p1": "l2", "p2": "l1", "p3": "l3", "p4": "l4"},
    }
    assert score_question(q, {"p1": "l2", "p2": "l1", "p3": "l3", "p4": "l4"}) is True
    assert score_question(q, {"p1": "l1", "p2": "l2", "p3": "l3", "p4": "l4"}) is False


def test_score_ordering_question():
    q = {"id": "r1", "type": "ordering", "correct": ["e1", "e2", "e3", "e4", "e5"]}
    assert score_question(q, ["e1", "e2", "e3", "e4", "e5"]) is True
    assert score_question(q, ["e2", "e1", "e3", "e4", "e5"]) is False


def test_score_quiz_mixed():
    quiz = {
        "questions": [
            {"id": "q1", "type": "single", "correct": "a"},
            {"id": "m1", "type": "multi", "correct": ["x", "y"]},
        ]
    }
    correct, total = score_quiz(quiz, {"q1": "a", "m1": ["y", "x"]})
    assert correct == 2
    assert total == 2
