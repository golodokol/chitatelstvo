from __future__ import annotations

from notifications.founder_letter import build_founder_letter
from services.recommendation_rules import load_recommendation_rules, match_recommendation_rule


def setup_function() -> None:
    load_recommendation_rules.cache_clear()


def test_teacher_letter_starts_with_trial_not_teacher_course() -> None:
    rule = match_recommendation_rule(
        quiz_variant="reading",
        child_age=11,
        answers_by_id={"format": "С живым преподавателем в группе"},
    )
    assert rule is not None
    subject, plain, html = build_founder_letter(
        rule=rule,
        parent_name="Анна",
        child_name="Глеб",
        child_age=11,
        trial_lesson_url="https://example.com/lesson",
        trial_progress_url="https://example.com/progress",
        trial_title="Опасное лето",
    )
    assert "Глеб — формат с преподавателем" in subject
    assert "Рекомендую начать с: пробного урока «Опасное лето»" in plain
    assert "Рекомендую начать с: Таинственный сад" not in plain
    assert "лист ожидания" not in plain.lower()
    assert "жду с преподавателем" not in plain.lower()
    assert "Таинственный сад" in plain
    assert "пробного урока «Опасное лето»" in html
