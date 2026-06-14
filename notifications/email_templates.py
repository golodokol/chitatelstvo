"""Тексты писем родителям — согласованы с docs/TILDA_TEXTS.md §4 и §10."""

from __future__ import annotations

SUBJECT_WELCOME = "Добро пожаловать в Читательство"
SUBJECT_PROGRESS = "Читательство — прогресс ребёнка"


def build_welcome_message(
    *,
    parent_name: str,
    child_name: str,
    progress_url: str,
    link_telegram_page: str | None = None,
    include_telegram: bool = False,
    module_title: str | None = None,
) -> str:
    parent = parent_name.strip() or "родитель"
    child = child_name.strip() or "ребёнок"

    lines = [
        f"Здравствуйте, {parent}!",
        "",
        f"Ребёнок {child} записан в литературную школу Читательство.",
    ]

    if module_title:
        lines.extend(["", f"Модуль: {module_title}."])

    lines.extend(
        [
            "",
            "Личная страница прогресса:",
            progress_url,
            "",
            "Здесь — баллы, бейджи, кнопки уроков и справка: как устроены занятия и за что начисляются баллы. Сохраните ссылку в закладки.",
            "",
            "Как начать:",
            "Откройте сказку на странице прогресса. Ребёнок смотрит видео (досмотрел — уже +2 балла)",
            "и отвечает на вопросы в том же окне — баллы приходят сами, без форм для родителя.",
        ]
    )

    if include_telegram and link_telegram_page:
        lines.extend(
            [
                "",
                "Telegram (если выбрали):",
                link_telegram_page,
            ]
        )

    lines.extend(
        [
            "",
            "Читайте в удобное время, без спешки.",
            "",
            "С теплом,",
            "Команда Читательства",
            "",
            "—",
            "Письма с уроками: lessons@chitatelstvo.ru",
            "По общим вопросам: info@chitatelstvo.ru",
        ]
    )

    return "\n".join(lines)


def build_progress_message(
    *,
    parent_name: str,
    child_name: str,
    parent_message: str,
    next_action: str,
    progress_url: str,
) -> str:
    parent = parent_name.strip() or "родитель"
    child = child_name.strip() or "ребёнок"

    return (
        f"Здравствуйте, {parent}!\n\n"
        f"Ребёнок: {child}\n"
        f"{parent_message}\n\n"
        f"Следующий шаг: {next_action}\n\n"
        f"Все обновления также на личной странице:\n{progress_url}\n\n"
        f"—\n"
        f"Читательство · lessons@chitatelstvo.ru"
    )
