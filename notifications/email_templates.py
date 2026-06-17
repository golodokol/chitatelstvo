"""Тексты писем родителям — согласованы с docs/TILDA_TEXTS.md §4 и §10."""

from __future__ import annotations

import html

from notifications.russian_morph import (
    age_band_intro,
    age_years_phrase,
    name_dative,
    name_genitive,
    name_prepositional,
    reflexive_sam,
)

SUBJECT_WELCOME = "Добро пожаловать в Читательство"
SUBJECT_PROGRESS = "Читательство — прогресс ребёнка"
SUBJECT_QUIZ_AUTO = "PDF-чек-лист от Читательства"
SUBJECT_OTP = "Код для входа в Читательство"

QUIZ_AGE_MIN = 6
QUIZ_AGE_MAX = 11
QUIZ_LOGO_ASSET = "/assets/logo-chitatelstvo-quiz.png?v=20260616c"


def quiz_logo_url(api_base: str = "https://api.chitatelstvo.ru") -> str:
    return f"{api_base.rstrip('/')}{QUIZ_LOGO_ASSET}"


def build_otp_message(*, code: str, ttl_minutes: int = 10) -> str:
    return "\n".join(
        [
            "Здравствуйте!",
            "",
            f"Код для входа в Читательство: {code}",
            "",
            f"Код действует {ttl_minutes} мин. Никому его не сообщайте.",
            "",
            "Если вы не запрашивали вход — просто проигнорируйте это письмо.",
            "",
            "С теплом,",
            "Команда Читательства",
        ]
    )


def build_welcome_message(
    *,
    parent_name: str,
    child_name: str,
    progress_url: str,
    link_telegram_page: str | None = None,
    include_telegram: bool = False,
    module_title: str | None = None,
    is_returning: bool = False,
) -> str:
    parent = parent_name.strip() or "родитель"
    child = child_name.strip() or "ребёнок"

    lines = [
        f"Здравствуйте, {parent}!",
        "",
    ]

    if is_returning:
        lines.append(f"{child} продолжает занятия в литературной школе Читательство — прогресс сохранён.")
    else:
        lines.append(f"Ребёнок {child} записан в литературную школу Читательство.")

    if module_title:
        lines.extend(["", f"Модуль: {module_title}."])

    progress_hint = (
        "Личная страница прогресса (та же ссылка, что и раньше):"
        if is_returning
        else "Личная страница прогресса:"
    )
    lines.extend(
        [
            "",
            progress_hint,
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


def _age_in_quiz_range(age: int | None) -> bool:
    return age is not None and QUIZ_AGE_MIN <= age <= QUIZ_AGE_MAX


def _quiz_age_intro(child_age: int | None) -> str:
    if _age_in_quiz_range(child_age):
        return age_band_intro(child_age)  # type: ignore[arg-type]
    return (
        "Наши материалы помогают проверить, насколько ребёнок понимает прочитанное, "
        "и мягко поддержать интерес к книге — без упрёков и спешки."
    )


def _quiz_problem_paragraph(child_name: str, answers_by_id: dict[str, str]) -> str:
    child_nom = child_name.strip() or "ребёнок"
    child_gen = name_genitive(child_nom)
    child_dat = name_dative(child_nom)
    child_prep = name_prepositional(child_nom)
    sam = reflexive_sam(child_nom)
    parts: list[str] = []

    hard = answers_by_id.get("hard", "")
    if hard == "Понять, о чём текст":
        parts.append(
            f"Вы отметили, что {child_dat} трудно понять, о чём текст. "
            "Это частая история — с ней можно работать спокойно и без давления."
        )
    elif hard == "Дочитать до конца":
        parts.append(
            f"Понимаем: {child_dat} сложно дочитать до конца. "
            "Короткие сказки и понятный ритм часто помогают вернуть интерес."
        )
    elif hard == "Пересказать своими словами":
        parts.append(
            "Пересказ — не любимое занятие у многих детей. "
            f"Для {child_gen} мы подберём формат, где смысл текста раскрывается через вопросы и игру."
        )
    elif hard == "Начать читать без напоминаний":
        parts.append(
            f"Вы написали, что {child_nom} редко берёт книгу {sam}. "
            "Хорошая новость: привычку можно вырастить — главное, без упрёков и спешки."
        )

    blocker = answers_by_id.get("blocker", "")
    if blocker == "Гаджеты и экраны":
        parts.append(
            "Экраны отвлекают почти всех — мы учитываем это и предлагаем короткие занятия, "
            "которые легче встроить в день."
        )
    elif blocker == "«Скучно» или неинтересно":
        parts.append(
            "Когда «скучно», обычно не хватает живой истории и маленьких побед. "
            "Именно так устроены наши уроки."
        )
    elif blocker == "Сложные слова и длинные тексты":
        parts.append(
            "Длинные тексты пугают — поэтому мы идём от короткой сказки, "
            "где каждое слово можно обсудить."
        )
    elif blocker == "Нет привычки читать дома":
        parts.append(
            "Если привычки пока нет — это нормально. Начать можно с пяти минут в день, "
            "без обязаловки."
        )

    frequency = answers_by_id.get("frequency", "")
    if frequency == "Почти не читает сам" and not parts:
        parts.append(
            f"Мы видим, что {child_nom} пока почти не читает {sam} — "
            "и это как раз тот случай, когда внешняя поддержка особенно помогает."
        )

    priority = answers_by_id.get("priority", "")
    if priority == "Чтобы ребёнок полюбил чтение":
        parts.append("Ваш главный запрос — полюбить чтение. Мы с этим полностью согласны.")
    elif priority == "Чтобы понимал прочитанное":
        parts.append("Понимание прочитанного — сердце нашей программы.")
    elif priority == "Чтобы был план и структура":
        parts.append("План и понятный ритм — как раз то, что даёт школа: сказка за сказкой, без хаоса.")
    elif priority == "Попробовать без давления":
        parts.append("Без давления — наш принцип. Ребёнок идёт в своём темпе, а вы видите прогресс.")

    if not parts:
        parts.append(
            f"Мы учли ваши ответы о {child_prep} и подготовили материалы, "
            "которые могут быть полезны уже сейчас."
        )

    return " ".join(parts[:2])


def _quiz_email_parts(
    *,
    parent_name: str,
    child_name: str,
    child_age: int | None,
    answers_by_id: dict[str, str],
    checklist_url: str,
    site_url: str,
) -> dict[str, str]:
    parent = parent_name.strip() or "родитель"
    child_gen = name_genitive(child_name)
    problem = _quiz_problem_paragraph(child_name, answers_by_id)
    age_intro = _quiz_age_intro(child_age)

    if _age_in_quiz_range(child_age):
        thanks = (
            f"Спасибо, что прошли короткий опрос для {child_gen} "
            f"({age_years_phrase(child_age)})."  # type: ignore[arg-type]
        )
    else:
        thanks = f"Спасибо, что прошли короткий опрос для {child_gen}."

    return {
        "parent": parent,
        "thanks": thanks,
        "age_intro": age_intro,
        "problem": problem,
        "checklist_url": checklist_url,
        "program_url": f"{site_url}/#program",
    }


def build_quiz_auto_email(
    *,
    parent_name: str,
    child_name: str,
    child_age: int | None,
    answers_by_id: dict[str, str],
    checklist_url: str,
    site_url: str = "https://chitatelstvo.ru",
) -> str:
    """Автоматическое письмо после квиза: только PDF-чек-лист, без персональной сказки."""
    parts = _quiz_email_parts(
        parent_name=parent_name,
        child_name=child_name,
        child_age=child_age,
        answers_by_id=answers_by_id,
        checklist_url=checklist_url,
        site_url=site_url,
    )

    lines = [
        f"Здравствуйте, {parts['parent']}!",
        "",
        parts["thanks"],
        parts["age_intro"],
        "",
        parts["problem"],
        "",
        "Ваш PDF-чек-лист «10 признаков, что ребёнок не понимает прочитанное» прикреплён к письму.",
        f"Если вложение не открылось — скачайте по ссылке: {parts['checklist_url']}",
        "",
        "Отметьте пункты вместе с ребёнком — так проще увидеть, где нужна поддержка.",
        "",
        "Личное письмо от основателя школы с персональной сказкой и рекомендациями "
        "придёт чуть позже — отдельно, чтобы мы успели учесть ваши ответы.",
        "",
        "с теплом, команда Читательства",
        "",
        "—",
        "info@chitatelstvo.ru",
    ]
    return "\n".join(line for line in lines if line is not None)


def build_quiz_auto_email_html(
    *,
    parent_name: str,
    child_name: str,
    child_age: int | None,
    answers_by_id: dict[str, str],
    checklist_url: str,
    site_url: str = "https://chitatelstvo.ru",
    assets_url: str = "https://api.chitatelstvo.ru",
) -> str:
    parts = _quiz_email_parts(
        parent_name=parent_name,
        child_name=child_name,
        child_age=child_age,
        answers_by_id=answers_by_id,
        checklist_url=checklist_url,
        site_url=site_url,
    )
    logo_url = quiz_logo_url(assets_url)
    home_url = html.escape(site_url, quote=True)
    age_block = f'<p style="margin:0 0 16px;line-height:1.6;">{html.escape(parts["age_intro"])}</p>'

    return f"""<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:24px 16px;background:#F6F4F9;font-family:Nunito,Arial,sans-serif;color:#3D5266;">
  <div style="max-width:560px;margin:0 auto;background:#fff;border:1px solid #E4E0EC;border-radius:16px;padding:28px 24px 32px;">
    <p style="margin:0 0 24px;text-align:center;">
      <a href="{home_url}" style="text-decoration:none;display:inline-block;background:#ffffff;padding:12px 16px;border-radius:14px;border:1px solid #E4E0EC;">
        <img src="{html.escape(logo_url, quote=True)}" alt="Читательство" width="180" style="max-width:180px;height:auto;display:block;background:#ffffff;border:0;">
      </a>
    </p>
    <p style="margin:0 0 16px;font-size:16px;line-height:1.6;">Здравствуйте, {html.escape(parts["parent"])}!</p>
    <p style="margin:0 0 16px;line-height:1.6;">{html.escape(parts["thanks"])}</p>
    {age_block}
    <p style="margin:0 0 16px;line-height:1.6;">{html.escape(parts["problem"])}</p>
    <p style="margin:0 0 8px;line-height:1.6;">Ваш PDF-чек-лист «10 признаков, что ребёнок не понимает прочитанное» <strong>прикреплён к письму</strong>.</p>
    <p style="margin:0 0 16px;line-height:1.6;">Если вложение не открылось — <a href="{html.escape(parts["checklist_url"], quote=True)}" style="color:#5B7FA6;">скачайте PDF по ссылке</a>.</p>
    <p style="margin:0 0 16px;line-height:1.6;">Отметьте пункты вместе с ребёнком — так проще увидеть, где нужна поддержка.</p>
    <p style="margin:0 0 16px;line-height:1.6;">Личное письмо от основателя школы с персональной сказкой и рекомендациями придёт чуть позже — отдельно, чтобы мы успели учесть ваши ответы.</p>
    <p style="margin:0;line-height:1.6;">с теплом, команда Читательства</p>
    <p style="margin:24px 0 0;font-size:13px;color:#7A8FA3;line-height:1.5;"><a href="mailto:info@chitatelstvo.ru" style="color:#7A8FA3;">info@chitatelstvo.ru</a></p>
  </div>
</body>
</html>"""
