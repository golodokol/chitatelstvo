#!/usr/bin/env python3
"""Синхронизирует CHIT_SCHEDULE в Tilda JS с lessons/schedule.py."""

from __future__ import annotations

import re
from pathlib import Path

from lessons.schedule import (
    STAGE_1_LESSON_OPENS,
    STAGE_1_MEETINGS,
    STAGE_2_LESSON_OPENS,
    STAGE_2_MEETINGS,
    format_date_ru,
)


ROOT = Path(__file__).resolve().parent.parent
TILDA_DIR = ROOT / "docs" / "tilda-zero-main"

TALE_SCHEDULE_FN = """
var MEETING_ADDON_PRICE = 799;

function todayIsoLocal() {
  var d = new Date();
  return d.getFullYear() + '-' +
    String(d.getMonth() + 1).padStart(2, '0') + '-' +
    String(d.getDate()).padStart(2, '0');
}

function singleMeetingStatus(stage, taleNum) {
  var dates = CHIT_SINGLE_MEETINGS_ISO[String(stage)];
  if (!dates || !taleNum) return 'online_only';
  var meet = dates[Number(taleNum) - 1];
  return meet && meet > todayIsoLocal() ? 'with_meeting' : 'online_only';
}

function singleMeetingLine(stage, taleNum) {
  var s = CHIT_SCHEDULE[String(stage)];
  var idx = Number(taleNum) - 1;
  if (singleMeetingStatus(stage, taleNum) === 'with_meeting' && s && s.meetings[idx]) {
    return {
      available: true,
      date: 'четверг, ' + s.meetings[idx]
    };
  }
  return { available: false };
}

function taleScheduleHtml(stage, index, tariff) {
  var s = CHIT_SCHEDULE[stage];
  if (!s || index < 0 || index > 3) return '';
  var taleNum = index + 1;
  var html = '<div class="tale-schedule">';
  if (tariff === 'single') {
    html += '<span class="tale-schedule__line">Урок на платформе: <strong>понедельник, ' + s.lessons[index] + '</strong></span>';
    var meet = singleMeetingLine(stage, taleNum);
    if (meet.available) {
      html += '<span class="tale-schedule__meet tale-schedule__meet--optional">Присоединиться к занятиям с преподавателем в группе · <strong>' + meet.date + '</strong></span>';
    } else {
      html += '<span class="tale-schedule__meet tale-schedule__meet--online">Только онлайн · встреча по этой сказке недоступна</span>';
    }
  } else if (tariff === 'with_teacher') {
    html += '<span class="tale-schedule__meet">Встреча с преподавателем: <strong>четверг, ' + s.meetings[index] + '</strong></span>';
    html += '<span class="tale-schedule__line">Урок откроется: понедельник, ' + s.lessons[index] + '</span>';
  } else {
    html += '<span class="tale-schedule__line">Урок откроется: <strong>понедельник, ' + s.lessons[index] + '</strong></span>';
  }
  html += '</div>';
  return html;
}
""".strip()


def _labels(dates: tuple) -> list[str]:
    return [format_date_ru(d) for d in dates]


def chit_schedule_block() -> str:
    l1 = _labels(STAGE_1_LESSON_OPENS)
    m1 = _labels(STAGE_1_MEETINGS)
    l2 = _labels(STAGE_2_LESSON_OPENS)
    m2 = _labels(STAGE_2_MEETINGS)
    iso1 = [d.isoformat() for d in STAGE_1_MEETINGS]
    iso2 = [d.isoformat() for d in STAGE_2_MEETINGS]
    return f"""var CHIT_SCHEDULE = {{
  '1': {{
    lessons: {l1!r},
    meetings: {m1!r}
  }},
  '2': {{
    lessons: {l2!r},
    meetings: {m2!r}
  }}
}};

var CHIT_SINGLE_MEETINGS_ISO = {{
  '1': {iso1!r},
  '2': {iso2!r}
}};"""


def replace_schedule_block(text: str) -> str:
    block = chit_schedule_block()
    return re.sub(
        r"var CHIT_SCHEDULE = \{[\s\S]*?\n\};(?:\n\nvar CHIT_SINGLE_MEETINGS_ISO = \{[\s\S]*?\n\};)?",
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
