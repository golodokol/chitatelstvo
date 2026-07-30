from notifications.email_templates import (
    build_progress_digest_item,
    build_progress_digest_message,
    normalize_progress_digest_line,
)


def test_digest_item_omits_next_step_and_name():
    item = build_progress_digest_item(
        child_name="Артем",
        parent_message="Артем завершил(а) шаг «Смотрим видео-урок» «Сказка о рыбаке и рыбке». +2 балла.",
        next_action="Перейти к шагу «Изучаем эмоциональный интеллект».",
    )
    assert item == "Завершил(а) шаг «Смотрим видео-урок» «Сказка о рыбаке и рыбке». +2 балла."
    assert "Следующий шаг" not in item
    assert "Ребёнок:" not in item
    assert not item.startswith("Артем")


def test_digest_message_groups_by_child_once():
    body = build_progress_digest_message(
        parent_name="Оля",
        progress_url="https://example.test/progress/x",
        children_updates=[
            (
                "Артем",
                [
                    "Артем завершил(а) шаг «Смотрим видео-урок» «Сказка о рыбаке и рыбке». +2 балла.",
                    "Ребёнок: Артем\nАртем прошёл(а) шаг «Мини-тест по сказке» «Сказка о царе Салтане». +2 балла.\nСледующий шаг: Перейти к шагу «Выполняем задания».",
                ],
            )
        ],
    )
    assert body.count("Артем:") == 1
    assert "Ребёнок: Артем" not in body
    assert "Следующий шаг" not in body
    assert "• Завершил(а) шаг «Смотрим видео-урок»" in body
    assert "• Прошёл(а) шаг «Мини-тест по сказке»" in body


def test_normalize_strips_legacy_next_step():
    line = normalize_progress_digest_line(
        "Ребёнок: Артем\nАртем завершил(а) шаг «Смотрим видео-урок» «Сказка о царе Салтане». +2 балла.\nСледующий шаг: Перейти к шагу «Изучаем эмоциональный интеллект».",
        "Артем",
    )
    assert line == "Завершил(а) шаг «Смотрим видео-урок» «Сказка о царе Салтане». +2 балла."
