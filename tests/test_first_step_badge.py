from gamification.bonus_badges import FIRST_STEP_BADGE, check_first_step_badge


def test_first_step_granted_on_learning_event():
    grant = check_first_step_badge(
        child_name="Даниил",
        current_badges=["Читатель"],
        event_type="lesson_complete",
    )
    assert grant is not None
    assert grant.badge_name == FIRST_STEP_BADGE


def test_first_step_skipped_if_already_owned():
    grant = check_first_step_badge(
        child_name="Даниил",
        current_badges=[FIRST_STEP_BADGE, "Читатель"],
        event_type="comprehension",
    )
    assert grant is None


def test_first_step_skipped_for_streak_meta():
    grant = check_first_step_badge(
        child_name="Даниил",
        current_badges=[],
        event_type="streak_3",
    )
    assert grant is None
