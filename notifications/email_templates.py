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
SUBJECT_PROGRESS_DIGEST = "Читательство — итоги дня"
SUBJECT_QUIZ_AUTO = "PDF-чек-лист от Читательства"
SUBJECT_OTP = "Код для входа в Читательство"

QUIZ_AGE_MIN = 6
QUIZ_AGE_MAX = 11
QUIZ_EARLY_AGE_MIN = 4
QUIZ_EARLY_AGE_MAX = 7
QUIZ_LOGO_ASSET = "/assets/logo-chitatelstvo-quiz.png?v=20260616c"
SUBJECT_QUIZ_EARLY = "Пробный урок от Читательства"


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


def strip_child_name_prefix(text: str, child_name: str) -> str:
    """Убирает имя ребёнка в начале строки, чтобы не дублировать его в сводке."""
    raw = (text or "").strip()
    name = (child_name or "").strip()
    if not raw or not name:
        return raw
    for prefix in (f"{name} ", f"{name}\u00a0"):
        if raw.startswith(prefix):
            rest = raw[len(prefix) :]
            if not rest:
                return raw
            return rest[:1].upper() + rest[1:]
    return raw


def normalize_progress_digest_line(message: str, child_name: str) -> str:
    """Достаёт строку прогресса из новой или старой записи pending-письма."""
    child = (child_name or "").strip() or "ребёнок"
    for raw in (message or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("• ") or line.startswith("- "):
            line = line[2:].strip()
        if line.startswith("Ребёнок:"):
            continue
        if line.startswith("Следующий шаг:"):
            continue
        return strip_child_name_prefix(line, child)
    return strip_child_name_prefix((message or "").strip(), child)


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


def build_progress_digest_item(*, child_name: str, parent_message: str, next_action: str = "") -> str:
    """Короткая запись для дневной сводки (хранится в pending email).

    next_action намеренно не включаем — в письме родителям только факт прохождения.
    """
    child = child_name.strip() or "ребёнок"
    return strip_child_name_prefix((parent_message or "").strip(), child)


def build_progress_digest_message(
    *,
    parent_name: str,
    progress_url: str,
    children_updates: list[tuple[str, list[str]]] | None = None,
    items: list[str] | None = None,
) -> str:
    """Одно письмо за день: имя ребёнка один раз, ниже список пройденного."""
    parent = parent_name.strip() or "родитель"
    sections = children_updates
    if sections is None and items is not None:
        # Старый вызов: плоский список строк
        sections = [("", list(items))]
    sections = sections or []

    blocks: list[str] = []
    for child_name, lines in sections:
        child = (child_name or "").strip()
        clean_lines: list[str] = []
        for raw in lines:
            line = normalize_progress_digest_line(raw, child)
            if line:
                clean_lines.append(line)
        if not clean_lines:
            continue
        block_lines: list[str] = []
        if child:
            block_lines.append(f"{child}:")
        for line in clean_lines:
            block_lines.append(f"• {line}")
        blocks.append("\n".join(block_lines))

    body_items = "\n\n".join(blocks) if blocks else "• Сегодня были обновления на личной странице."

    return (
        f"Здравствуйте, {parent}!\n\n"
        f"Краткая сводка за день — что прошёл ребёнок:\n\n"
        f"{body_items}\n\n"
        f"Подробности на личной странице:\n{progress_url}\n\n"
        f"—\n"
        f"Читательство · lessons@chitatelstvo.ru"
    )


def _age_in_quiz_range(age: int | None) -> bool:
    return age is not None and QUIZ_AGE_MIN <= age <= QUIZ_AGE_MAX


def _age_in_early_range(age: int | None) -> bool:
    return age is not None and QUIZ_EARLY_AGE_MIN <= age <= QUIZ_EARLY_AGE_MAX


def _quiz_age_intro(child_age: int | None, *, quiz_variant: str | None = None) -> str:
    if quiz_variant == "early" or _age_in_early_range(child_age):
        return (
            "Мы помогаем детям, которые ещё только знакомятся с буквами и первыми историями: "
            "через короткие квесты со Словиком — без спешки и без «надо читать»."
        )
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

    # --- Early (ещё не читает) ---
    readiness = answers_by_id.get("readiness", "")
    if readiness == "Ещё почти не знает буквы":
        parts.append(
            f"Вы отметили, что {child_nom} ещё почти не знает буквы. "
            "Это отличный момент для мягкого старта через звуки и игру — без спешки."
        )
    elif readiness == "Знает некоторые буквы":
        parts.append(
            f"У {child_gen} уже есть знакомые буквы — сейчас важно связать их со звуком "
            "и первыми слогами в коротких квестах."
        )
    elif readiness == "Складывает слоги или короткие слова":
        parts.append(
            f"{child_nom} уже складывает слоги — хороший мост к первым историям "
            "и уверенному чтению коротких фраз."
        )
    elif readiness == "Уже читает простые тексты":
        parts.append(
            f"Раз {child_nom} уже читает простые тексты, можно смотреть "
            "и литературные сказки рядом с early-курсами — подскажем в письме."
        )

    sounds = answers_by_id.get("sounds", "")
    if sounds == "Слушать и повторять звуки":
        parts.append("Сильная сторона — слух и повтор. Начнём с звуковых станций.")
    elif sounds == "Узнавать буквы на картинках":
        parts.append("Буквы на картинках — отличная опора. Добавим к ним звук и игру.")
    elif sounds == "Складывать слоги в слова":
        parts.append("Слоги уже получаются — поддержим ритмом коротких слов и историй.")
    elif sounds == "Пока всё в новинку":
        parts.append("Всё в новинку — нормально. Пробный квест как раз для мягкого знакомства.")

    interest = answers_by_id.get("interest", "")
    if interest == "Игры со звуками и буквами":
        parts.append("Интерес к играм со звуками — путь курса «Буквы оживают».")
    elif interest == "Короткие истории и картинки":
        parts.append("Короткие истории — ближе к курсу «Первые истории».")
    elif interest == "Сказки вслух вместе со взрослым":
        parts.append("Совместное чтение вслух — прекрасная база; квест дополнит её игрой.")

    goal_early = answers_by_id.get("goal_early", "")
    if goal_early == "Мягко подготовить к школе":
        parts.append("Мягкая подготовка к школе — наш принцип: короткие шаги и успех без давления.")
    elif goal_early == "Чтобы полюбил буквы и истории":
        parts.append("Чтобы полюбить буквы и истории — через игру и Словика, а не через «надо».")
    elif goal_early == "Уверенность в первых словах":
        parts.append("Уверенность в первых словах растёт от маленьких побед на каждой станции.")
    elif goal_early == "Попробовать без давления":
        parts.append("Без давления — наш принцип. Ребёнок идёт в своём темпе.")

    if parts:
        return " ".join(parts[:2])

    # --- Reading (уже читает) ---
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
    trial_title: str | None = None,
    trial_lesson_url: str | None = None,
    trial_progress_url: str | None = None,
    quiz_variant: str | None = None,
) -> dict[str, str]:
    parent = parent_name.strip() or "родитель"
    child_gen = name_genitive(child_name)
    problem = _quiz_problem_paragraph(child_name, answers_by_id)
    age_intro = _quiz_age_intro(child_age, quiz_variant=quiz_variant)
    trial = (trial_title or "").strip()
    lesson_url = (trial_lesson_url or "").strip()
    progress_url = (trial_progress_url or "").strip()
    is_early = (quiz_variant or "") == "early" or bool(
        answers_by_id.get("readiness") or answers_by_id.get("goal_early")
    )

    if _age_in_quiz_range(child_age) or _age_in_early_range(child_age):
        thanks = (
            f"Спасибо, что прошли короткий опрос для {child_gen} "
            f"({age_years_phrase(child_age)})."  # type: ignore[arg-type]
        )
    else:
        thanks = f"Спасибо, что прошли короткий опрос для {child_gen}."

    if trial and lesson_url:
        gift_line = (
            f"Ваш бесплатный урок «{trial}» уже открыт.\n"
            f"Открыть урок: {lesson_url}\n"
            f"Личная страница: {progress_url or lesson_url}"
        )
    elif trial:
        gift_line = (
            f"Вы выбрали бесплатный урок «{trial}». "
            "Мы откроем доступ к платформе — ссылка придёт отдельно, если не пришла в этом письме."
        )
    else:
        gift_line = (
            "Личное письмо от основателя школы с персональной сказкой и рекомендациями "
            "придёт чуть позже — отдельно, чтобы мы успели учесть ваши ответы."
        )

    return {
        "parent": parent,
        "thanks": thanks,
        "age_intro": age_intro,
        "problem": problem,
        "checklist_url": checklist_url,
        "program_url": f"{site_url}/#program",
        "gift_line": gift_line,
        "trial_lesson_url": lesson_url,
        "trial_progress_url": progress_url,
        "is_early": "1" if is_early else "",
    }


def build_quiz_auto_email(
    *,
    parent_name: str,
    child_name: str,
    child_age: int | None,
    answers_by_id: dict[str, str],
    checklist_url: str,
    site_url: str = "https://chitatelstvo.ru",
    trial_title: str | None = None,
    trial_lesson_url: str | None = None,
    trial_progress_url: str | None = None,
    quiz_variant: str | None = None,
) -> str:
    """Автоматическое письмо после квиза: PDF-чек-лист и/или ссылка на пробный урок."""
    parts = _quiz_email_parts(
        parent_name=parent_name,
        child_name=child_name,
        child_age=child_age,
        answers_by_id=answers_by_id,
        checklist_url=checklist_url,
        site_url=site_url,
        trial_title=trial_title,
        trial_lesson_url=trial_lesson_url,
        trial_progress_url=trial_progress_url,
        quiz_variant=quiz_variant,
    )

    lines = [
        f"Здравствуйте, {parts['parent']}!",
        "",
        parts["thanks"],
        parts["age_intro"],
        "",
        parts["problem"],
        "",
    ]
    if parts["is_early"]:
        lines.extend(
            [
                parts["gift_line"],
                "",
                "Откройте урок вместе с ребёнком — это короткий квест со Словиком.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "Ваш PDF-чек-лист «10 признаков, что ребёнок не понимает прочитанное» прикреплён к письму.",
                f"Если вложение не открылось — скачайте по ссылке: {parts['checklist_url']}",
                "",
                "Отметьте пункты вместе с ребёнком — так проще увидеть, где нужна поддержка.",
                "",
                parts["gift_line"],
                "",
            ]
        )
    lines.extend(
        [
            "с теплом, команда Читательства",
            "",
            "—",
            "info@chitatelstvo.ru",
        ]
    )
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
    trial_title: str | None = None,
    trial_lesson_url: str | None = None,
    trial_progress_url: str | None = None,
    quiz_variant: str | None = None,
) -> str:
    parts = _quiz_email_parts(
        parent_name=parent_name,
        child_name=child_name,
        child_age=child_age,
        answers_by_id=answers_by_id,
        checklist_url=checklist_url,
        site_url=site_url,
        trial_title=trial_title,
        trial_lesson_url=trial_lesson_url,
        trial_progress_url=trial_progress_url,
        quiz_variant=quiz_variant,
    )
    logo_url = quiz_logo_url(assets_url)
    home_url = html.escape(site_url, quote=True)
    age_block = f'<p style="margin:0 0 16px;line-height:1.6;">{html.escape(parts["age_intro"])}</p>'
    gift_html = html.escape(parts["gift_line"]).replace("\n", "<br>")
    trial_btn = ""
    if parts.get("trial_lesson_url"):
        trial_btn = (
            f'<p style="margin:0 0 16px;text-align:center;">'
            f'<a href="{html.escape(parts["trial_lesson_url"], quote=True)}" '
            f'style="display:inline-block;background:#5B7FA6;color:#fff;text-decoration:none;'
            f'padding:12px 22px;border-radius:12px;font-weight:700;">Открыть пробный урок</a></p>'
        )
        if parts.get("trial_progress_url"):
            trial_btn += (
                f'<p style="margin:0 0 16px;text-align:center;font-size:14px;">'
                f'<a href="{html.escape(parts["trial_progress_url"], quote=True)}" '
                f'style="color:#5B7FA6;">Личная страница ребёнка</a></p>'
            )

    if parts["is_early"]:
        mid = (
            f"{trial_btn}"
            f'<p style="margin:0 0 16px;line-height:1.6;">{gift_html}</p>'
            f'<p style="margin:0 0 16px;line-height:1.6;">Откройте урок вместе с ребёнком — это короткий квест со Словиком.</p>'
        )
    else:
        mid = (
            f'<p style="margin:0 0 8px;line-height:1.6;">Ваш PDF-чек-лист «10 признаков, что ребёнок не понимает прочитанное» '
            f'<strong>прикреплён к письму</strong>.</p>'
            f'<p style="margin:0 0 16px;line-height:1.6;">Если вложение не открылось — '
            f'<a href="{html.escape(parts["checklist_url"], quote=True)}" style="color:#5B7FA6;">скачайте PDF по ссылке</a>.</p>'
            f'<p style="margin:0 0 16px;line-height:1.6;">Отметьте пункты вместе с ребёнком — так проще увидеть, где нужна поддержка.</p>'
            f"{trial_btn}"
            f'<p style="margin:0 0 16px;line-height:1.6;">{gift_html}</p>'
        )

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
    {mid}
    <p style="margin:0;line-height:1.6;">с теплом, команда Читательства</p>
    <p style="margin:24px 0 0;font-size:13px;color:#7A8FA3;line-height:1.5;"><a href="mailto:info@chitatelstvo.ru" style="color:#7A8FA3;">info@chitatelstvo.ru</a></p>
  </div>
</body>
</html>"""
