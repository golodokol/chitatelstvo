#!/usr/bin/env python3
"""Синхронизирует CHIT_SCHEDULE в Tilda JS с lessons/schedule.py."""

from __future__ import annotations

import re
from pathlib import Path

from lessons.schedule import (
    EARLY_MEETINGS,
    STAGE_1_LESSON_OPENS,
    STAGE_1_MEETINGS,
    STAGE_2_LESSON_OPENS,
    STAGE_2_MEETINGS,
    format_date_ru,
    weekday_ru,
)


ROOT = Path(__file__).resolve().parent.parent
TILDA_DIR = ROOT / "docs" / "tilda-zero-main"

TALE_SCHEDULE_FN = """
var MEETING_ADDON_PRICE = 799;
var WITH_TEACHER_STAGE1_CLOSED = true;

function todayIsoLocal() {
  var d = new Date();
  return d.getFullYear() + '-' +
    String(d.getMonth() + 1).padStart(2, '0') + '-' +
    String(d.getDate()).padStart(2, '0');
}

function lessonIsOpen(stage, taleNum) {
  var dates = CHIT_LESSON_OPENS_ISO[String(stage)];
  if (!dates || !taleNum) return false;
  var open = dates[Number(taleNum) - 1];
  return !!(open && open <= todayIsoLocal());
}

function lessonOpenLabel(stage, index) {
  var s = CHIT_SCHEDULE[String(stage)];
  if (!s || index < 0) return '';
  if (lessonIsOpen(stage, index + 1)) {
    return 'Уже доступен для прохождения';
  }
  var lessonDay = lessonWeekday(stage, index);
  var lessonPrefix = lessonDay ? lessonDay + ', ' : '';
  return 'Урок откроется: ' + lessonPrefix + s.lessons[index];
}

/** Можно ли ещё докупить встречу. Блок 1 с преподавателем закрыт; блок 2 — если дата в будущем. */
function singleMeetingAddonAvailable(stage, taleNum) {
  if (String(stage) === '1') return false;
  var dates = CHIT_SINGLE_MEETINGS_ISO[String(stage)];
  if (!dates || !taleNum) return false;
  var meet = dates[Number(taleNum) - 1];
  return !!(meet && meet > todayIsoLocal());
}

function singleMeetingUnavailableLabel(stage) {
  if (String(stage) === '1') {
    return 'Только онлайн. Живые занятия по сказкам блока 1 сейчас не проводятся — выберите блок 2';
  }
  return 'Только онлайн. Занятие-квест по этой сказке уже нельзя докупить';
}

function singleMeetingAddonLine(stage, taleNum) {
  var s = CHIT_SCHEDULE[String(stage)];
  var idx = Number(taleNum) - 1;
  if (singleMeetingAddonAvailable(stage, taleNum) && s && s.meetings[idx]) {
    return {
      available: true,
      date: 'четверг, ' + s.meetings[idx]
    };
  }
  return { available: false };
}

function lessonWeekday(stage, index) {
  var s = CHIT_SCHEDULE[stage];
  return s && s.weekdays && s.weekdays[index] ? s.weekdays[index] : '';
}

function meetingWeekday(stage, index) {
  var s = CHIT_SCHEDULE[stage];
  return s && s.meetingWeekdays && s.meetingWeekdays[index] ? s.meetingWeekdays[index] : 'четверг';
}

function taleScheduleHtml(stage, index, tariff) {
  var s = CHIT_SCHEDULE[stage];
  if (!s || index < 0 || index > 3) return '';
  var taleNum = index + 1;
  var html = '<div class="tale-schedule">';
  if (tariff === 'single') {
    html += '<span class="tale-schedule__line"><strong>' + lessonOpenLabel(stage, index) + '</strong></span>';
  } else if (tariff === 'with_teacher') {
    html += '<span class="tale-schedule__meet">Встреча с преподавателем: <strong>' + meetingWeekday(stage, index) + ', ' + s.meetings[index] + '</strong></span>';
    html += '<span class="tale-schedule__line">' + lessonOpenLabel(stage, index) + '</span>';
  } else {
    html += '<span class="tale-schedule__line"><strong>' + lessonOpenLabel(stage, index) + '</strong></span>';
  }
  html += '</div>';
  return html;
}
""".strip()


def _labels(dates: tuple) -> list[str]:
    return [format_date_ru(d) for d in dates]


def _weekdays(dates: tuple) -> list[str]:
    return [weekday_ru(d) for d in dates]


def chit_schedule_block() -> str:
    l1 = _labels(STAGE_1_LESSON_OPENS)
    w1 = _weekdays(STAGE_1_LESSON_OPENS)
    m1 = _labels(STAGE_1_MEETINGS)
    mw1 = _weekdays(STAGE_1_MEETINGS)
    l2 = _labels(STAGE_2_LESSON_OPENS)
    w2 = _weekdays(STAGE_2_LESSON_OPENS)
    m2 = _labels(STAGE_2_MEETINGS)
    mw2 = _weekdays(STAGE_2_MEETINGS)
    iso1 = [d.isoformat() for d in STAGE_1_MEETINGS]
    iso2 = [d.isoformat() for d in STAGE_2_MEETINGS]
    open1 = [d.isoformat() for d in STAGE_1_LESSON_OPENS]
    open2 = [d.isoformat() for d in STAGE_2_LESSON_OPENS]
    em = _labels(EARLY_MEETINGS)
    emw = _weekdays(EARLY_MEETINGS)
    em_iso = [d.isoformat() for d in EARLY_MEETINGS]
    return f"""var CHIT_SCHEDULE = {{
  '1': {{
    lessons: {l1!r},
    weekdays: {w1!r},
    meetings: {m1!r},
    meetingWeekdays: {mw1!r}
  }},
  '2': {{
    lessons: {l2!r},
    weekdays: {w2!r},
    meetings: {m2!r},
    meetingWeekdays: {mw2!r}
  }}
}};

var CHIT_SINGLE_MEETINGS_ISO = {{
  '1': {iso1!r},
  '2': {iso2!r}
}};

var CHIT_LESSON_OPENS_ISO = {{
  '1': {open1!r},
  '2': {open2!r}
}};

/** Early-курсы (Буквы / Истории), модуль 1: 4 встречи по четвергам */
var CHIT_EARLY_SCHEDULE = {{
  meetings: {em!r},
  meetingWeekdays: {emw!r},
  meetingsIso: {em_iso!r}
}};"""


def replace_schedule_block(text: str) -> str:
    block = chit_schedule_block()
    return re.sub(
        r"var CHIT_SCHEDULE = \{[\s\S]*?\n\};(?:\n\nvar CHIT_SINGLE_MEETINGS_ISO = \{[\s\S]*?\n\};)?(?:\n\nvar CHIT_LESSON_OPENS_ISO = \{[\s\S]*?\n\};)?(?:\n\n/\*\* Early-курсы[\s\S]*?\n\};)?",
        block,
        text,
        count=1,
    )


def ensure_tale_schedule_fn(text: str) -> str:
    if "function taleScheduleHtml" in text:
        return text
    return text.replace(
        "function getTaleInfo(title) {",
        "function getTaleInfo(title) {",
        1,
    ).replace(
        "  return { desc: 'Уточните название сказки — напишите команде Читательства.', quote: null };\n}",
        "  return { desc: 'Уточните название сказки — напишите команде Читательства.', quote: null };\n}\n\n"
        + chit_schedule_block()
        + "\n\n"
        + TALE_SCHEDULE_FN,
        1,
    )


def patch_render_tales_lite(text: str) -> str:
    old = (
        "        btn.innerHTML = '<span class=\"tale-num\">' + (i + 1) + '</span>' + title;"
    )
    new = (
        "        btn.innerHTML =\n"
        "          '<span class=\"tale-num\">' + (i + 1) + '</span>' +\n"
        "          '<span class=\"tale-btn__body\">' +\n"
        "            '<span class=\"tale-btn__title\">' + title + '</span>' +\n"
        "            taleScheduleHtml(state.stage, i, state.tariff) +\n"
        "          '</span>';"
    )
    if old in text:
        text = text.replace(old, new, 1)
    old_preview = (
        "      elPreview.innerHTML = '<strong style=\"color:var(--blue)\">4 сказки в этом блоке:</strong><br>' +\n"
        "        list.map(function(t, i) { return (i + 1) + '. ' + t; }).join('<br>');"
    )
    new_preview = (
        "      elPreview.innerHTML =\n"
        "        '<div class=\"block-preview__title\"><strong>4 сказки в этом блоке</strong>' +\n"
        "        (state.tariff === 'with_teacher' ? ' · встречи по четвергам' : '') +\n"
        "        '</div>' +\n"
        "        '<div class=\"block-preview__cards\">' +\n"
        "        list.map(function(t, i) {\n"
        "          return '<div class=\"block-preview__card\">' +\n"
        "            '<div class=\"block-preview__num\">Сказка ' + (i + 1) + '</div>' +\n"
        "            '<div class=\"block-preview__name\">' + t + '</div>' +\n"
        "            taleScheduleHtml(state.stage, i, state.tariff) +\n"
        "          '</div>';\n"
        "        }).join('') +\n"
        "        '</div>';"
    )
    if old_preview in text:
        text = text.replace(old_preview, new_preview, 1)
    return text


def main() -> None:
    schedule = chit_schedule_block()
    print(schedule)

    src = TILDA_DIR / "chit-zero.src.js"
    src_text = replace_schedule_block(src.read_text(encoding="utf-8"))
    src.write_text(src_text, encoding="utf-8")
    print("updated", src.relative_to(ROOT))

    lite = TILDA_DIR / "03-js.txt"
    lite_text = lite.read_text(encoding="utf-8")
    if "var CHIT_SCHEDULE" not in lite_text:
        lite_text = ensure_tale_schedule_fn(lite_text)
    else:
        lite_text = replace_schedule_block(lite_text)
    lite_text = patch_render_tales_lite(lite_text)
    lite.write_text(lite_text, encoding="utf-8")
    print("updated", lite.relative_to(ROOT))


if __name__ == "__main__":
    main()
