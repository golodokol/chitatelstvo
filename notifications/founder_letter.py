"""Сборка письма основателя после квиза."""

from __future__ import annotations

import re
from pathlib import Path

from config.settings import ROOT
from services.recommendation_rules import RecommendationRule

TEMPLATE_HTML = ROOT / "docs" / "email-templates" / "founder-trial-letter.html"
TEMPLATE_TXT = ROOT / "docs" / "email-templates" / "founder-trial-letter.txt"

MEETING_PREFIX = "Рекомендую посмотреть курс"

DEFAULT_STEPS = (
    "Откройте сказку на странице прогресса — кнопка «Начать урок» ведёт в интерактивный плеер.",
    "Ребёнок смотрит видео и отвечает на вопросы в том же окне — баллы приходят сами.",
    "Загляните в «Словики» и трофеи — там видно, что уже получилось.",
)

DEFAULT_ALTERNATIVE = (
    "Если захотите другую программу — на сайте есть курсы по классам и внеклассное чтение. "
    "Можно начать с одной сказки, без обязательств на весь модуль."
)


def split_founder_note(text: str) -> tuple[str, str]:
    idx = text.find(MEETING_PREFIX)
    if idx >= 0:
        return text[:idx].strip(), text[idx:].strip()
    return text.strip(), ""


def build_intro_paragraph(*, child_name: str) -> str:
    return (
        f"Рада, что {child_name} теперь с нами в Читательстве. "
        "Спасибо, что прошли короткий опрос — по вашим ответам я подобрала рекомендации ниже."
    )


def _replace(template: str, mapping: dict[str, str]) -> str:
    out = template
    for key, value in mapping.items():
        out = out.replace(f"{{{{{key}}}}}", value)
    return out


def _strip_trial_blocks(html_body: str) -> str:
    html_body = re.sub(
        r'<p style="margin:0 0 16px[^"]*">\s*Пробный урок «[^»]*» уже открыт[^<]*</p>\s*',
        "",
        html_body,
        count=1,
    )
    html_body = re.sub(
        r'<div style="margin:0 0 20px;padding:16px 18px;background:#fff;border:1px solid #E4E0EC[^"]*">'
        r"\s*<p style=\"margin:0 0 10px[^\"]*\">Пробный урок</p>.*?</div>\s*",
        "",
        html_body,
        count=1,
        flags=re.DOTALL,
    )
    return html_body


def build_founder_letter(
    *,
    rule: RecommendationRule,
    parent_name: str,
    child_name: str,
    child_age: int | None,
    trial_lesson_url: str | None,
    trial_progress_url: str | None,
    trial_title: str | None,
) -> tuple[str, str, str]:
    """Возвращает (subject, plain, html)."""
    note_raw = rule.founder_note_template.replace("{{CHILD_NAME}}", child_name)
    founder_note, meeting = split_founder_note(note_raw)
    subject = rule.subject_line.replace("{{CHILD_NAME}}", child_name)

    lesson_url = (trial_lesson_url or "").strip()
    progress_url = (trial_progress_url or "").strip()
    title = (trial_title or rule.trial_lesson_title or "").strip()
    has_trial = bool(lesson_url and title)

    if not progress_url and lesson_url:
        progress_url = lesson_url

    if has_trial:
        start_with = f"пробного урока «{title}»"
    else:
        start_with = rule.recommended_course_title or "программы на сайте"

    mapping = {
        "SUBJECT": subject,
        "PARENT_NAME": parent_name,
        "CHILD_NAME": child_name,
        "INTRO_PARAGRAPH": build_intro_paragraph(child_name=child_name),
        "FOUNDER_NOTE": founder_note,
        "START_WITH": start_with,
        "RECOMMENDED_COURSE": rule.recommended_course_title,
        "TRIAL_TITLE": title or "пробный урок",
        "TRIAL_LESSON_URL": lesson_url or rule.program_url,
        "PROGRESS_URL": progress_url or rule.program_url,
        "PROGRAM_URL": rule.program_url,
        "STEP_1": DEFAULT_STEPS[0].replace("сказку", f"сказку «{title}»") if title else DEFAULT_STEPS[0],
        "STEP_2": DEFAULT_STEPS[1],
        "STEP_3": DEFAULT_STEPS[2],
        "ALTERNATIVE_PARAGRAPH": DEFAULT_ALTERNATIVE,
        "NEXT_OFFER_1": "Форматы и запись — на странице программы.",
        "MEETING_ANNOUNCE": meeting or (
            "Рекомендую посмотреть курсы с преподавателем в группе — расписание на сайте."
        ),
    }

    plain = _replace(TEMPLATE_TXT.read_text(encoding="utf-8"), mapping)
    html_body = _replace(TEMPLATE_HTML.read_text(encoding="utf-8"), mapping)
    if not has_trial:
        html_body = _strip_trial_blocks(html_body)
        plain = plain.replace(f'Пробный урок «{mapping["TRIAL_TITLE"]}» уже открыт.\n\n', "")
        plain = plain.replace(f"Открыть урок: {mapping['TRIAL_LESSON_URL']}\n", "")

    return subject, plain, html_body
