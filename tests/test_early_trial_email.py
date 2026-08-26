from notifications.email_templates import (
    build_early_trial_email,
    build_early_trial_email_html,
)


def test_early_trial_email_templates_build():
    lesson = "https://api.chitatelstvo.ru/lesson/early-letters-trial-lesson-01?child=x"
    progress = "https://api.chitatelstvo.ru/progress/x"
    plain = build_early_trial_email(
        parent_name="Светлана",
        child_name="Лука",
        child_age=6,
        trial_title="Словик и пропавшие звуки",
        trial_lesson_url=lesson,
        trial_progress_url=progress,
        trial_slug="early-letters-trial-lesson-01",
        course_group="early-letters",
    )
    html = build_early_trial_email_html(
        parent_name="Светлана",
        child_name="Лука",
        child_age=6,
        trial_title="Словик и пропавшие звуки",
        trial_lesson_url=lesson,
        trial_progress_url=progress,
        trial_slug="early-letters-trial-lesson-01",
        course_group="early-letters",
        assets_url="https://api.chitatelstvo.ru",
    )
    assert lesson in plain
    assert lesson in html
    assert "Открыть пробный урок" in html
