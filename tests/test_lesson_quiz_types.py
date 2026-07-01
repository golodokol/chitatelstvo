"""Тесты расширенных типов вопросов в квизах урока."""

from lessons.loader import score_question, score_quiz


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


def test_score_ordering_question():
    q = {"id": "m4", "type": "ordering", "correct": ["e1", "e2", "e3"]}
    assert score_question(q, ["e1", "e2", "e3"]) is True
    assert score_question(q, ["e2", "e1", "e3"]) is False


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
