"""Данные для игрового личного кабинета ученика (страница /progress)."""

from __future__ import annotations

from datetime import date
from typing import Any

from gamification.badge_assets import BADGE_ASSET_FILES
from gamification.chest_rewards import (
    CHEST_IMAGES,
    CHEST_REWARD_SUMMARY,
    LETTER_KIND,
    canonical_tale_slug,
    chest_image_for_state,
    chest_visual_state,
    items_for_treasury,
    reward_summary_text,
    rewards_for_tale,
)
from gamification.rules import EVENT_RULES, LEVELS, LEVEL_SLOVIK_THRESHOLDS, level_from_points
from lessons.step_labels import LESSON_STEP_LABELS, event_type_label
from gamification.sloviki import (
    COMPANION_HINTS,
    POINTS_COUNTER_SLOVIK,
    chest_slovik_key,
    companion_key,
    mission_slovik_key,
    recent_event_slovik,
    slovik_url,
)
from lessons.diary_covers import diary_cover_url_for_tale
from lessons.schedule import STAGE_LABELS
from notifications.russian_morph import name_genitive


def _guide_reward_note(event_type: str) -> str:
    rule = EVENT_RULES.get(event_type, {})
    pts = int(rule.get("points") or 0)
    badge = rule.get("badge")
    parts: list[str] = []
    if pts:
        parts.append(f"+{pts} {_sloviki_word(pts)}")
    if badge:
        parts.append(f"бейдж «{badge}»")
    return ", ".join(parts)


def parent_lesson_guide_steps() -> list[dict[str, str]]:
    """Шаги урока для блока «Как проходит урок» на вкладке родителя."""
    meaning = _guide_reward_note("meaning_analysis")
    creative = _guide_reward_note("creative_task")
    return [
        {
            "label": LESSON_STEP_LABELS["video"],
            "note": _guide_reward_note("lesson_complete") + ".",
        },
        {
            "label": LESSON_STEP_LABELS["emotion_quiz"],
            "note": _guide_reward_note("emotion_quiz") + ".",
        },
        {
            "label": LESSON_STEP_LABELS["comprehension_quiz"],
            "note": _guide_reward_note("comprehension") + ".",
        },
        {
            "label": LESSON_STEP_LABELS["tasks"],
            "note": (
                f"проверяются автоматически ({meaning}); "
                f"творческие выполняются дома — по желанию отметьте кнопкой в уроке ({creative})."
            ),
        },
        {
            "label": "Пересказ или встреча",
            "note": "по желанию и тарифу.",
        },
    ]


def parent_points_rows() -> list[dict[str, str]]:
    """Таблица «За что начисляются Словики» на вкладке родителя."""
    rows: list[tuple[str, str]] = [
        ("lesson_complete", LESSON_STEP_LABELS["video"]),
        ("emotion_quiz", LESSON_STEP_LABELS["emotion_quiz"]),
        ("comprehension", LESSON_STEP_LABELS["comprehension_quiz"]),
        ("meaning_analysis", LESSON_STEP_LABELS["tasks"]),
        ("creative_task", "Творческое задание"),
        ("retelling", "Пересказ сказки"),
        ("live_meeting", "Живая встреча"),
        ("streak_3", "3 дня подряд"),
    ]
    result: list[dict[str, str]] = []
    for event_type, label in rows:
        rule = EVENT_RULES.get(event_type, {})
        pts = int(rule.get("points") or 0)
        if event_type == "streak_3":
            value = "+3 и бейдж"
        else:
            value = f"+{pts}"
        result.append({"label": label, "value": value})
    return result


LEVEL_IMAGES: dict[str, str] = {
    "Старт": "gamify-level-start.png",
    "Юный читатель": "gamify-level-young-reader.png",
    "Исследователь": "gamify-level-explorer.png",
    "Мастер слова": "gamify-level-word-master.png",
    "Литературный детектив": "gamify-level-detective.png",
}

BADGE_IMAGES: dict[str, str] = BADGE_ASSET_FILES

BADGE_CATALOG: list[dict[str, str]] = [
    {"name": "Первый шаг", "condition": "Первое задание в школе"},
    {"name": "Читатель", "condition": "Первая сказка пройдена"},
    {"name": "Слушатель", "condition": "Первая живая встреча"},
    {"name": "Следопыт", "condition": "Точные ответы на вопросы"},
    {"name": "Ловец смысла", "condition": "Понимание смысла сказки"},
    {"name": "Мастер пересказа", "condition": "Хороший пересказ"},
    {"name": "Сказочник", "condition": "Своё творческое задание"},
    {"name": "Исследователь сказки", "condition": "Весь модуль пройден"},
    {"name": "Непрерывная серия", "condition": "3 дня подряд"},
    {"name": "Путешественник по сказке", "condition": "Все 4 сказки модуля пройдены"},
]

# Пробные early-уроки: короткий набор. «Читатель» — только после первой истории.
# image_key — откуда взять картинку, если у бейджа ещё нет своего файла.
TRIAL_BADGE_CATALOG: list[dict[str, str]] = [
    {"name": "Первый шаг", "condition": "Первое задание в школе"},
    {
        "name": "Искатель искорок",
        "condition": "Собрал все искорки квеста",
        "image_key": "Следопыт",
    },
    {
        "name": "Хранитель сундука",
        "condition": "Открыл сундук урока",
        "image_key": "Исследователь сказки",
    },
    {
        "name": "Читатель",
        "condition": "Пройдена первая история",
        "image_key": "Читатель",
    },
]

BADGES_TOTAL = len(BADGE_CATALOG)

CHEST_STEPS = ("video_unlock", "comprehension", "meaning_analysis")

PAID_TARIFF_CODES = frozenset({"self_paced", "with_teacher", "single"})

EARLY_ASSETS_VERSION = "20260822n"

EARLY_COURSE_COVERS: dict[str, str] = {
    "early-letters": "course-cover-letters.jpg",
    "early-stories": "course-cover-stories.jpg",
}

EARLY_BUY_URLS: dict[str, str] = {
    "early-letters": "https://chitatelstvo.ru/#programs",
    "early-stories": "https://chitatelstvo.ru/#programs",
}

# Даты открытия 8 уроков модуля (сентября) — вместо «после покупки» / «Скоро».
EARLY_MODULE_OPEN_LABELS: list[str] = [
    "1 сентября",
    "3 сентября",
    "8 сентября",
    "10 сентября",
    "15 сентября",
    "17 сентября",
    "22 сентября",
    "24 сентября",
]

# Названия 8 уроков модуля — для сетки «Скоро» у пробных (пока уроки в кабинете ещё не открыты).
EARLY_MODULE_LESSON_TITLES: dict[str, list[str]] = {
    "early-letters": [
        "Мир звуков",
        "Первый звук слова",
        "Буква А — голос открывается",
        "Буква М — звук мотора",
        "Буква С — звук змейки",
        "Буквы дружат",
        "Буквы в моём мире",
        "Буквенный праздник",
    ],
    "early-stories": [
        "Как буквы становятся слогом",
        "Читаем слог без остановки",
        "Из слогов — слова",
        "Слово находит картинку",
        "Слова строят фразу",
        "Что случилось сначала?",
        "Герой, место, действие",
        "Моя первая история",
    ],
}


def is_chest_step_done(step: str, done: set[str]) -> bool:
    """Шаг «видео»: засчитывается и 3 мин (video_unlock), и досмотр (lesson_complete)."""
    if step == "video_unlock":
        return "video_unlock" in done or "lesson_complete" in done
    return step in done


def quest_spark_station_ids(lesson: dict | None) -> list[str]:
    ids: list[str] = []
    for station in (lesson or {}).get("stations") or []:
        if not (station.get("spark") or station.get("spark_kind")):
            continue
        sid = str(station.get("id") or "").strip()
        if sid:
            ids.append(sid)
    return ids


def quest_goal_count(lesson: dict | None) -> int:
    quest = (lesson or {}).get("quest") or {}
    raw = quest.get("goal_count")
    if raw not in (None, ""):
        try:
            return max(1, int(raw))
        except (TypeError, ValueError):
            pass
    return len(quest_spark_station_ids(lesson)) or 3


def quest_chest_earned(events: list[Any] | None, lesson: dict | None) -> bool:
    """Сундук early-квеста открывается только если собраны все искорки за верные ответы."""
    title = str((lesson or {}).get("title") or "").strip()
    spark_ids = quest_spark_station_ids(lesson)
    goal = quest_goal_count(lesson)
    for event in events or []:
        if getattr(event, "event_type", "") != "lesson_complete":
            continue
        if str(getattr(event, "tale_title", "") or "").strip() != title:
            continue
        payload = getattr(event, "payload", None) or {}
        if payload.get("chest_ready") is True:
            return True
        passed = {str(sid) for sid in (payload.get("passed_stations") or []) if sid}
        if spark_ids and set(spark_ids) <= passed:
            return True
        if spark_ids:
            continue
        try:
            sparks = int(payload.get("sparks") or 0)
        except (TypeError, ValueError):
            sparks = 0
        if sparks >= goal:
            return True
    return False


def chest_ready_from_done(
    done: set[str],
    lesson: dict | None = None,
    events: list[Any] | None = None,
) -> bool:
    if lesson and _is_early_lesson(lesson):
        if "lesson_complete" not in done:
            return False
        return quest_chest_earned(events, lesson)
    return all(is_chest_step_done(step, done) for step in CHEST_STEPS)


def _level_index(level_name: str) -> int:
    try:
        return LEVELS.index(level_name)
    except ValueError:
        return 0


def _asset_url(base: str, filename: str | None) -> str | None:
    if not filename:
        return None
    return f"{base.rstrip('/')}/assets/{filename}"


def _sloviki_word(n: int) -> str:
    n = abs(int(n))
    if n % 10 == 1 and n % 100 != 11:
        return "Словик"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return "Словика"
    return "Словиков"


def _sloviki_label(n: int) -> str:
    return f"{n} {_sloviki_word(n)}"


def _badge_name_lines(name: str) -> list[str]:
    """Строки подписи бейджа для ровного центрирования в узкой ячейке."""
    if name == "Путешественник по сказке":
        return ["Путешественник", "по сказке"]
    if name == "Искатель искорок":
        return ["Искатель", "искорок"]
    if name == "Хранитель сундука":
        return ["Хранитель", "сундука"]
    parts = name.split()
    if len(parts) <= 1:
        return [name]
    if len(parts) == 2:
        return parts
    return [parts[0], " ".join(parts[1:])]


def resolve_cabinet_mode(tracks: list[dict[str, Any]] | None) -> str:
    """
    Режим комнаты ребёнка:
    - trial_early — только пробные early-уроки
    - paid_early — куплен early-модуль/разовое (дневник сказок ещё скрыт)
    - full — есть сказочный/grade-модуль или смешанный доступ
    """
    rows = [t for t in (tracks or []) if t]
    if not rows:
        return "full"
    groups = [str(t.get("group_code") or "") for t in rows]
    tariffs = [str(t.get("tariff_code") or "") for t in rows]
    all_early = all(g.startswith("early-") for g in groups)
    if not all_early:
        return "full"
    if any(t in PAID_TARIFF_CODES for t in tariffs):
        return "paid_early"
    return "trial_early"


def _course_cover_url(assets_base: str, group_code: str) -> str | None:
    filename = EARLY_COURSE_COVERS.get(group_code)
    if not filename:
        return None
    return f"{assets_base.rstrip('/')}/assets/{filename}?v={EARLY_ASSETS_VERSION}"


def _buy_url_for_group(group_code: str) -> str:
    return EARLY_BUY_URLS.get(group_code) or "https://chitatelstvo.ru/#programs"


def _upcoming_module_lessons(
    *,
    group_code: str,
    assets_base: str,
) -> list[dict[str, Any]]:
    """Плейсхолдеры уроков 1–8 модуля для пробного кабинета (даты сентября + покупка)."""
    titles = EARLY_MODULE_LESSON_TITLES.get(group_code) or [f"Урок {i}" for i in range(1, 9)]
    cover = _course_cover_url(assets_base, group_code)
    buy_url = _buy_url_for_group(group_code)
    rows: list[dict[str, Any]] = []
    for idx, title in enumerate(titles, start=1):
        date_label = (
            EARLY_MODULE_OPEN_LABELS[idx - 1]
            if idx <= len(EARLY_MODULE_OPEN_LABELS)
            else "после покупки"
        )
        rows.append(
            {
                "week_in_stage": idx,
                "title": title,
                "cover_url": cover,
                "cover_state": "soon",
                "opens_on_label": date_label,
                "buy_url": buy_url,
                "group_code": group_code,
                "url": None,
                "unlocked": False,
            }
        )
    return rows


def _trial_soft_earned_badges(
    events: list[Any],
    claims: list[Any],
    lesson_links: list[dict],
) -> set[str]:
    """Визуальные «получено» для пробных бейджей без отдельной записи в БД."""
    from gamification.rules import is_early_stories_title

    soft: set[str] = set()
    for les in lesson_links:
        if _is_early_lesson(les) and quest_chest_earned(events, les):
            soft.add("Искатель искорок")
            break
    if claims:
        soft.add("Хранитель сундука")
    # «Читатель» в пробном кабинете — только если пройдена история (не буквы).
    for event in events or []:
        if getattr(event, "event_type", "") != "lesson_complete":
            continue
        if is_early_stories_title(getattr(event, "tale_title", None)):
            soft.add("Читатель")
            break
    return soft


def _filter_trial_earned_badges(earned: set[str], soft_earned: set[str]) -> set[str]:
    """В пробном режиме «Читатель» не показываем, пока не пройдена история."""
    out = set(earned)
    if "Читатель" in out and "Читатель" not in soft_earned:
        out.discard("Читатель")
    # «Непрерывная серия» убрали из пробного каталога — не тащим в UI.
    out.discard("Непрерывная серия")
    return out


def _badge_catalog_for_mode(mode: str) -> list[dict[str, str]]:
    if mode == "trial_early":
        return TRIAL_BADGE_CATALOG
    return BADGE_CATALOG


def _build_badges_ui(
    *,
    earned_set: set[str],
    soft_earned: set[str],
    catalog: list[dict[str, str]],
    assets_base: str,
) -> tuple[list[dict[str, Any]], int]:
    badges_ui: list[dict[str, Any]] = []
    next_badge = None
    earned_count = 0
    for badge in catalog:
        name = badge["name"]
        earned = name in earned_set or name in soft_earned
        if earned:
            earned_count += 1
        if not earned and next_badge is None:
            next_badge = name
        image_name = badge.get("image_key") or name
        badges_ui.append(
            {
                "name": name,
                "name_lines": _badge_name_lines(name),
                "condition": badge["condition"],
                "earned": earned,
                "image": _asset_url(assets_base, BADGE_IMAGES.get(image_name)),
                "status": "earned" if earned else ("next" if name == next_badge else "locked"),
            }
        )
    # Уже полученные «сказочные» бейджи — в конец, чтобы прогресс не пропал при смене режима.
    catalog_names = {b["name"] for b in catalog}
    for name in sorted(earned_set - catalog_names):
        earned_count += 1
        badges_ui.append(
            {
                "name": name,
                "name_lines": _badge_name_lines(name),
                "condition": "Уже получен",
                "earned": True,
                "image": _asset_url(assets_base, BADGE_IMAGES.get(name)),
                "status": "earned",
            }
        )
    return badges_ui, earned_count


def _level_progress(points: int, level_name: str) -> dict[str, Any]:
    idx = _level_index(level_name)
    if idx >= len(LEVELS) - 1:
        return {
            "pct": 100,
            "remaining": 0,
            "next_level": None,
            "next_level_name": None,
        }
    cur_thr = LEVEL_SLOVIK_THRESHOLDS[idx]
    next_thr = LEVEL_SLOVIK_THRESHOLDS[idx + 1]
    span = max(next_thr - cur_thr, 1)
    in_level = max(0, points - cur_thr)
    pct = min(100, int(in_level / span * 100))
    remaining = max(0, next_thr - points)
    return {
        "pct": pct,
        "remaining": remaining,
        "next_level": idx + 1,
        "next_level_name": LEVELS[idx + 1],
    }


def _events_for_tale(events: list[Any], tale_title: str) -> set[str]:
    title = (tale_title or "").strip()
    if not title:
        return set()
    return {
        e.event_type
        for e in events
        if (e.tale_title or "").strip() == title
    }


def _opens_on_sort_value(lesson: dict) -> date:
    value = lesson.get("opens_on")
    if isinstance(value, date):
        return value
    iso = lesson.get("opens_on_iso")
    if iso:
        try:
            return date.fromisoformat(str(iso)[:10])
        except ValueError:
            pass
    return date.max


def _lesson_access_sort_key(lesson: dict) -> tuple:
    """Сначала доступные (есть ссылка), затем по дате открытия."""
    available = 0 if lesson.get("url") else 1
    week = int(lesson.get("module_week") or 999)
    title = str(lesson.get("title") or "")
    return (available, _opens_on_sort_value(lesson), week, title)


def sort_lessons_by_access(lesson_links: list[dict]) -> list[dict]:
    return sorted(lesson_links, key=_lesson_access_sort_key)


def _track_access_sort_key(track: dict) -> tuple:
    links = track.get("lesson_links") or []
    if not links:
        return (1, date.max, "")
    has_url = any(les.get("url") for les in links)
    soonest = min((_opens_on_sort_value(les) for les in links), default=date.max)
    label = str(track.get("module_title") or track.get("group_label") or "")
    return (0 if has_url else 1, soonest, label)


def sort_tracks_by_access(tracks: list[dict]) -> list[dict]:
    return sorted(tracks, key=_track_access_sort_key)


def _current_lesson(lesson_links: list[dict]) -> dict | None:
    ordered = sort_lessons_by_access(lesson_links)
    for les in ordered:
        if les.get("url"):
            return les
    for les in ordered:
        if les.get("unlocked"):
            return les
    return ordered[0] if ordered else None


def _is_early_lesson(lesson: dict | None) -> bool:
    if not lesson:
        return False
    group = str(lesson.get("group_code") or "")
    return group.startswith("early-") or str(lesson.get("lesson_format") or "") == "quest"


def _is_early_links(lesson_links: list[dict]) -> bool:
    return any(_is_early_lesson(les) for les in lesson_links)


def _weekly_lessons(
    lesson_links: list[dict],
    *,
    early: bool | None = None,
) -> tuple[list[dict], str]:
    if not lesson_links:
        return [], "Будет доступно позже"
    if early is None:
        early = _is_early_links(lesson_links)
    # Доступные уроки сверху; закрытые — ниже, по дате открытия.
    available = [les for les in lesson_links if les.get("url")]
    if available:
        week_lessons = sort_lessons_by_access(available)
        if early:
            label = "Уроки этой недели" if len(week_lessons) > 1 else "Урок этой недели"
        else:
            label = "Сказки этой недели" if len(week_lessons) > 1 else "Сказка этой недели"
    else:
        week_lessons = sort_lessons_by_access(lesson_links)[:1]
        label = "Будет доступно позже"
    return week_lessons, label


def _weekly_lesson_cards(lessons: list[dict]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for lesson in sort_lessons_by_access(lessons):
        early = _is_early_lesson(lesson)
        num = lesson.get("week_in_stage") or lesson.get("module_week") or 1
        title = lesson.get("title", "Урок")
        group = str(lesson.get("group_code") or "")
        if early:
            if group == "early-stories" or "истори" in title.lower():
                goal = (
                    "Короткий квест со Словиком: слово, фраза и смысл. "
                    "Собери искорки и спаси первую историю."
                )
            else:
                goal = (
                    "Короткий квест со Словиком: станции со звуками, буквами и слогами. "
                    "Собери искорки и помоги вернуть звуки."
                )
            cards.append(
                {
                    "title": title,
                    "headline": f"Урок {num}: {title}",
                    "goal": goal,
                    "duration": "≈ 15–20 мин",
                    "reward_pts": 3,
                    "reward_label": "искорки",
                    "url": lesson.get("url"),
                    "unlocked": bool(lesson.get("url")),
                    "opens_on_label": lesson.get("opens_on_label"),
                    "cover_url": lesson.get("cover_url"),
                    "cover_state": lesson.get("cover_state", "locked"),
                    "week_in_stage": num,
                    "is_early": True,
                    "group_code": group,
                }
            )
        else:
            cards.append(
                {
                    "title": title,
                    "headline": f"Сказка {num}: {title}",
                    "goal": (
                        "За 30 минут пройдёшь видео-сказку, практику чтения, "
                        "тесты, пересказ и задания из волшебного сундука."
                    ),
                    "duration": "≈ 30 мин",
                    "reward_pts": 15,
                    "reward_label": "Словиков и шаг к сундуку",
                    "url": lesson.get("url"),
                    "unlocked": bool(lesson.get("url")),
                    "opens_on_label": lesson.get("opens_on_label"),
                    "cover_url": lesson.get("cover_url"),
                    "cover_state": lesson.get("cover_state", "locked"),
                    "week_in_stage": num,
                    "is_early": False,
                    "group_code": group,
                }
            )
    return cards


def _chest_title(tale_title: str, *, early: bool = False) -> str:
    tale = (tale_title or "").strip()
    if early:
        if tale:
            return f"Сундук к уроку «{tale}»"
        return "Сундук урока"
    if tale:
        return f"Сундук к сказке «{tale}»"
    return "Сундук Сказки"


def _chest_subtitle(tale_title: str, *, early: bool = False) -> str:
    tale = (tale_title or "").strip()
    if early:
        if tale:
            return (
                f"Откроется, когда пройдёшь квест и соберёшь все искорки "
                f"в уроке «{tale}»."
            )
        return "Когда откроется первый урок — здесь появится награда."
    if tale:
        return (
            f"Откроется после начала видео (3 мин), "
            f"«{LESSON_STEP_LABELS['comprehension_quiz']}» и "
            f"«{LESSON_STEP_LABELS['tasks']}» по сказке «{tale}»."
        )
    return "Когда откроется первая сказка — здесь появится награда."


def _chest_state(
    events: list[Any],
    lesson: dict | None,
    *,
    claim: Any | None = None,
    reward_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    reward_items = reward_items or []
    reward_text = reward_summary_text(reward_items) if reward_items else CHEST_REWARD_SUMMARY
    tale_slug = canonical_tale_slug((lesson or {}).get("tale_slug") or (lesson or {}).get("slug") or "")
    early = _is_early_lesson(lesson)

    if not lesson:
        return {
            "title": "Сундук урока" if early else "Сундук Сказки",
            "subtitle": (
                "Когда откроется первый урок — здесь появится награда."
                if early
                else "Когда откроется первая сказка — здесь появится награда."
            ),
            "reward": reward_text,
            "tale_title": "",
            "tale_slug": "",
            "steps_total": 3,
            "steps_done": 0,
            "steps_remaining": 3,
            "pct": 0,
            "ready": False,
            "claimed": False,
            "visual": "closed",
            "image_url": CHEST_IMAGES["closed"],
            "image_closed": CHEST_IMAGES["closed"],
            "image_opening": CHEST_IMAGES["opening"],
            "image_open": CHEST_IMAGES["open"],
            "hint": "До открытия 3 шага",
            "items": [],
        }

    tale = lesson.get("title", "")
    tale_title = tale.strip()
    done = _events_for_tale(events, tale)
    if early:
        steps_total = 1
        earned = quest_chest_earned(events, lesson)
        steps_done = 1 if earned else 0
        steps_remaining = 0 if earned else 1
        pct = 100 if earned else 0
    else:
        steps_done = sum(1 for s in CHEST_STEPS if is_chest_step_done(s, done))
        steps_total = len(CHEST_STEPS)
        steps_remaining = max(0, steps_total - steps_done)
        pct = int(steps_done / steps_total * 100) if steps_total else 0
    ready = steps_remaining == 0 and not claim
    claimed = claim is not None
    visual = chest_visual_state(
        steps_done=steps_done,
        steps_total=steps_total,
        ready=ready or claimed,
        claimed=claimed,
    )

    if claimed:
        hint = "Награда уже в сокровищнице"
    elif ready:
        hint = "Сундук готов — можно открывать!"
    elif early and "lesson_complete" in done:
        hint = "Сундук откроется, когда вернутся все искорки — за правильные ответы."
    elif steps_remaining == 1:
        hint = "До открытия осталось 1 задание"
    else:
        hint = f"До открытия осталось {steps_remaining} задания"

    return {
        "title": _chest_title(tale_title, early=early),
        "subtitle": _chest_subtitle(tale_title, early=early),
        "reward": reward_text,
        "tale_title": tale_title,
        "tale_slug": tale_slug,
        "steps_total": steps_total,
        "steps_done": steps_done,
        "steps_remaining": steps_remaining,
        "pct": pct,
        "ready": ready,
        "claimed": claimed,
        "visual": visual,
        "image_url": chest_image_for_state(visual if not ready else "closed"),
        "image_closed": CHEST_IMAGES["closed"],
        "image_opening": CHEST_IMAGES["opening"],
        "image_open": CHEST_IMAGES["open"],
        "hint": hint,
        "items": reward_items,
        "claimed_at_label": (
            claim.claimed_at.strftime("%d.%m.%Y") if claim and getattr(claim, "claimed_at", None) else ""
        ),
    }


def _missions(events: list[Any], lesson: dict | None, points: int, chest: dict) -> list[dict]:
    tale = (lesson or {}).get("title", "")
    done = _events_for_tale(events, tale)
    early = _is_early_lesson(lesson)

    def status(key: str) -> str:
        if key in done:
            return "done"
        if lesson and lesson.get("url"):
            return "active"
        return "locked"

    chest_ready = bool(chest.get("ready"))
    chest_claimed = bool(chest.get("claimed"))

    if early:
        spark_done = quest_chest_earned(events, lesson) or "lesson_complete" in done
        items = [
            {
                "id": "read",
                "text": "Пройти квест урока",
                "status": status("lesson_complete"),
            },
            {
                "id": "quiz",
                "text": "Собрать все искорки",
                "status": (
                    "done"
                    if quest_chest_earned(events, lesson)
                    else ("active" if spark_done or (lesson and lesson.get("url")) else "locked")
                ),
            },
            {
                "id": "points",
                "text": "Собрать 5 Словиков",
                "status": "done" if points >= 5 else ("active" if lesson and lesson.get("url") else "locked"),
            },
            {
                "id": "chest",
                "text": "Открыть сундук урока",
                "status": (
                    "done"
                    if chest_claimed
                    else ("active" if chest_ready or (lesson and lesson.get("url")) else "locked")
                ),
            },
        ]
    else:
        items = [
            {
                "id": "read",
                "text": LESSON_STEP_LABELS["video"],
                "status": status("lesson_complete"),
            },
            {
                "id": "quiz",
                "text": LESSON_STEP_LABELS["comprehension_quiz"],
                "status": status("comprehension"),
            },
            {
                "id": "points",
                "text": "Собрать 10 Словиков за неделю",
                "status": "done" if points >= 10 else ("active" if lesson and lesson.get("url") else "locked"),
            },
            {
                "id": "chest",
                "text": "Открыть сундук сказки",
                "status": (
                    "done"
                    if chest_claimed
                    else ("active" if chest_ready or (lesson and lesson.get("url")) else "locked")
                ),
            },
            {
                "id": "secret",
                "text": LESSON_STEP_LABELS["tasks"],
                "status": status("meaning_analysis"),
            },
        ]
    for item in items:
        key = mission_slovik_key(
            item["id"],
            chest_ready=chest_ready and item["id"] == "chest",
        )
        item["slovik_key"] = key
        item["slovik_url"] = slovik_url(key)
    return items


def _collection(
    events: list[Any],
    earned_badges: list[str],
    points: int,
    *,
    early: bool = False,
) -> dict[str, Any]:
    tales = {
        (e.tale_title or "").strip()
        for e in events
        if e.event_type == "lesson_complete" and (e.tale_title or "").strip()
    }
    secrets = sum(1 for e in events if e.event_type == "meaning_analysis")
    return {
        "stories_count": len(tales),
        "stories_preview": sorted(tales)[:4],
        "stories_label": "уроков" if early else "сказок",
        "badges_count": len(earned_badges),
        "points": points,
        "secrets_count": secrets,
        "cards_count": len(earned_badges) + len(tales),
        "show_secrets": not early,
    }


def _parent_summary(
    child_name: str,
    level: str,
    points: int,
    badges_count: int,
    chest: dict,
    lesson: dict | None,
    events: list[Any],
    *,
    early: bool = False,
) -> dict[str, str]:
    if early:
        skill = "звуки, буквы и первые шаги чтения"
    elif level in ("Мастер слова", "Литературный детектив"):
        skill = "пересказ, творчество и глубокое чтение"
    elif level == "Исследователь":
        skill = "внимательное чтение и анализ смысла"
    else:
        skill = "понимание текста и поиск смысла в сказке"

    completed = sum(1 for e in events if e.event_type == "lesson_complete")
    if lesson:
        lesson_line = lesson["title"]
    else:
        lesson_line = "скоро откроется первый урок" if early else "скоро откроется первая сказка"

    return {
        "completed_lessons": str(completed),
        "skill": skill,
        "points": str(points),
        "chest_hint": chest.get("hint", ""),
        "chest_ready": "да, можно открыть" if chest.get("ready") else chest.get("hint", ""),
        "support_tip": (
            f"Сегодня у {name_genitive(child_name)} урок «{lesson_line}». "
            "Можно пройти частями — главное, без спешки и с интересом."
        ),
        "badges_count": str(badges_count),
        "current_lesson": lesson_line,
        "level": level,
    }


def _story_stages(lesson_links: list[dict]) -> list[dict]:
    if not lesson_links:
        return []
    ordered = sort_lessons_by_access(lesson_links)
    by_stage: dict[str, list[dict]] = {}
    stage_order: list[str] = []
    for les in ordered:
        stage = les.get("stage") or "stage-1"
        if stage not in by_stage:
            stage_order.append(stage)
            by_stage[stage] = []
        by_stage[stage].append(les)
    # Этапы тоже: сначала где есть доступные уроки, иначе stage-1 → stage-2.
    def stage_key(stage: str) -> tuple:
        items = by_stage[stage]
        has_url = any(les.get("url") for les in items)
        preferred = {"stage-1": 0, "stage-2": 1}.get(stage, 9)
        return (0 if has_url else 1, preferred, stage)

    stages: list[dict] = []
    for stage_key_name in sorted(stage_order, key=stage_key):
        stages.append(
            {
                "key": stage_key_name,
                "label": STAGE_LABELS.get(stage_key_name, stage_key_name),
                "lessons": by_stage[stage_key_name],
            }
        )
    return stages


def _reading_diary(ratings: list[Any], lesson_links: list[dict]) -> list[dict[str, Any]]:
    """Записи дневника: оценённые сказки, от высшей оценки к низшей."""
    entries: list[dict[str, Any]] = []
    for row in ratings:
        lesson = None
        row_slug = canonical_tale_slug(row.tale_slug)
        for les in lesson_links:
            les_slug = canonical_tale_slug(les.get("tale_slug") or les.get("slug") or "")
            if les_slug and les_slug == row_slug:
                lesson = les
                break
        title = (row.tale_title or "").strip() or (lesson or {}).get("title") or "Сказка"
        rated_at = getattr(row, "updated_at", None) or getattr(row, "created_at", None)
        entries.append(
            {
                "title": title,
                "slug": row.tale_slug,
                "rating": row.rating,
                "rated_at_label": rated_at.strftime("%d.%m.%Y") if rated_at else "",
                "diary_image_url": diary_cover_url_for_tale(
                    row.tale_slug,
                    title,
                    module_week=(lesson or {}).get("module_week"),
                ),
                "week_in_stage": (lesson or {}).get("week_in_stage"),
            }
        )
    return entries


def _treasury_row(
    *,
    tale_title: str,
    tale_slug: str,
    item: dict[str, Any],
) -> dict[str, Any]:
    title = (tale_title or "").strip() or "Сказка"
    return {
        "tale_title": title,
        "tale_slug": tale_slug,
        "lesson_caption": f"Урок «{title}»",
        "kind": item.get("kind", ""),
        "label": item.get("label", ""),
        "description": item.get("description", ""),
        "image_url": item.get("image_url"),
        "download_url": item.get("download_url"),
        "download_name": item.get("download_name") or "",
        "downloadable": bool(item.get("downloadable")),
    }


def _treasury_items_for_claim(claim: Any) -> list[dict[str, Any]]:
    """Актуальные награды сказки — только из текущего конфига (не из устаревшего JSON в БД)."""
    title = (claim.tale_title or "").strip() or "Сказка"
    source_items = items_for_treasury(rewards_for_tale(claim.tale_slug, title))
    return [
        _treasury_row(
            tale_title=title,
            tale_slug=claim.tale_slug,
            item=item,
        )
        for item in source_items
    ]


def _treasury_for_tale(chest_claims: list[Any], tale_slug: str) -> list[dict[str, Any]]:
    if not tale_slug:
        return []
    needle = canonical_tale_slug(tale_slug)
    claim = next(
        (c for c in chest_claims if canonical_tale_slug(c.tale_slug) == needle),
        None,
    )
    if not claim:
        return []
    return _treasury_items_for_claim(claim)


def _track_tale_slugs(lesson_links: list[dict]) -> set[str]:
    slugs: set[str] = set()
    for les in lesson_links or []:
        for raw in (les.get("tale_slug"), les.get("slug")):
            slug = (raw or "").strip()
            if slug:
                slugs.add(canonical_tale_slug(slug))
    return slugs


def _treasury_for_track(chest_claims: list[Any], lesson_links: list[dict]) -> list[dict[str, Any]]:
    """Все награды сокровищницы по сказкам этого модуля (не только текущей недели)."""
    tale_slugs = _track_tale_slugs(lesson_links)
    if not tale_slugs:
        return []
    rows: list[dict[str, Any]] = []
    for claim in chest_claims:
        if canonical_tale_slug(claim.tale_slug) not in tale_slugs:
            continue
        rows.extend(_treasury_items_for_claim(claim))
    return rows


def _treasury(chest_claims: list[Any]) -> list[dict[str, Any]]:
    """Сокровищница: все награды из открытых сундуков."""
    rows: list[dict[str, Any]] = []
    for claim in chest_claims:
        rows.extend(_treasury_items_for_claim(claim))
    return rows


def _build_track_section(
    *,
    track: dict[str, Any],
    events: list[Any],
    claims: list[Any],
    points: int,
    assets_base: str,
    cabinet_mode: str,
) -> dict[str, Any]:
    lesson_links = track.get("lesson_links") or []
    lesson = _current_lesson(lesson_links)
    weekly_source, weekly_label = _weekly_lessons(lesson_links)
    early = _is_early_links(lesson_links) or str(track.get("group_code") or "").startswith("early-")
    tale_slug = canonical_tale_slug((lesson or {}).get("tale_slug") or (lesson or {}).get("slug") or "")
    current_claim = (
        next(
            (c for c in claims if canonical_tale_slug(c.tale_slug) == tale_slug),
            None,
        )
        if tale_slug
        else None
    )
    reward_items = (
        rewards_for_tale(tale_slug, lesson.get("title", "")) if tale_slug and lesson else []
    )
    chest = _chest_state(events, lesson, claim=current_claim, reward_items=reward_items)
    chest["slovik_key"] = chest_slovik_key(chest)
    chest["slovik_url"] = slovik_url(chest["slovik_key"])

    missions = _missions(events, lesson, points, chest)
    group_code = str(track.get("group_code") or "")
    is_trial_track = cabinet_mode == "trial_early" or str(track.get("tariff_code") or "") == "trial"
    if is_trial_track and early:
        story_stages: list[dict] = []
        upcoming_lessons = _upcoming_module_lessons(group_code=group_code, assets_base=assets_base)
        stories_title = f"Дальше в программе · {track.get('group_label') or ''}".strip(" ·")
        stories_subtitle = "8 уроков модуля — по вторникам и четвергам с 1 сентября"
    else:
        story_stages = _story_stages(lesson_links)
        upcoming_lessons = []
        stories_title = (
            f"Мои уроки · {track.get('group_label') or ''}".strip(" ·")
            if early
            else f"Мои сказки · {track.get('group_label') or ''}".strip(" ·")
        )
        stories_subtitle = None
    treasury = _treasury_for_track(claims, lesson_links)

    return {
        "group_code": group_code,
        "group_label": track.get("group_label", ""),
        "module_title": track.get("module_title", ""),
        "module_id": track.get("module_id"),
        "tariff_code": track.get("tariff_code") or "",
        "is_early": early,
        "is_trial": is_trial_track,
        "chest": chest,
        "treasury": treasury,
        "weekly_lessons": _weekly_lesson_cards(weekly_source),
        "weekly_lessons_label": weekly_label,
        "daily_lesson": _weekly_lesson_cards(weekly_source)[0] if weekly_source else None,
        "story_stages": story_stages,
        "upcoming_lessons": upcoming_lessons,
        "stories_title": stories_title,
        "stories_subtitle": stories_subtitle,
        "buy_url": _buy_url_for_group(group_code) if early else None,
        "missions": missions,
        "missions_title": "Миссии на эту неделю",
        "missions_subtitle": (
            (
                f"Урок {lesson.get('week_in_stage')}: {lesson.get('title')}"
                if early
                else f"Сказка {lesson.get('week_in_stage')}: {lesson.get('title')}"
            )
            if lesson and lesson.get("title")
            else None
        ),
        "continue_url": lesson.get("url") if lesson and lesson.get("url") else None,
    }


def build_child_cabinet(
    *,
    name: str,
    level: str,
    points: int,
    earned_badges: list[str],
    events: list[Any],
    lesson_links: list[dict],
    tracks: list[dict[str, Any]] | None = None,
    tale_ratings: list[Any] | None = None,
    chest_claims: list[Any] | None = None,
    assets_base: str,
) -> dict[str, Any]:
    """Собирает контекст игрового кабинета для одного ребёнка."""
    earned_set = set(earned_badges)
    display_level = level_from_points(points)
    lvl_idx = _level_index(display_level)
    progress = _level_progress(points, display_level)
    claims = chest_claims or []
    cabinet_mode = resolve_cabinet_mode(tracks)
    early_mode = cabinet_mode in ("trial_early", "paid_early")
    show_reading_diary = cabinet_mode == "full"

    track_sections: list[dict[str, Any]] = []
    if tracks:
        for track in sort_tracks_by_access(tracks):
            track_sections.append(
                _build_track_section(
                    track=track,
                    events=events,
                    claims=claims,
                    points=points,
                    assets_base=assets_base,
                    cabinet_mode=cabinet_mode,
                )
            )

    if track_sections:
        primary = track_sections[0]
        lesson = _current_lesson(lesson_links)
        chest = primary["chest"]
        daily = primary.get("daily_lesson")
        weekly_lessons = primary.get("weekly_lessons") or []
        weekly_label = primary.get("weekly_lessons_label") or (
            "Урок этой недели" if early_mode else "Сказка этой недели"
        )
        missions = primary["missions"]
        missions_title = primary["missions_title"]
        missions_subtitle = primary["missions_subtitle"]
        story_stages = primary["story_stages"]
        continue_url = next(
            (t["continue_url"] for t in track_sections if t.get("continue_url")),
            None,
        )
    else:
        lesson = _current_lesson(lesson_links)
        tale_slug = canonical_tale_slug((lesson or {}).get("tale_slug") or (lesson or {}).get("slug") or "")
        current_claim = (
            next(
                (c for c in claims if canonical_tale_slug(c.tale_slug) == tale_slug),
                None,
            )
            if tale_slug
            else None
        )
        reward_items = (
            rewards_for_tale(tale_slug, lesson.get("title", "")) if tale_slug and lesson else []
        )
        chest = _chest_state(events, lesson, claim=current_claim, reward_items=reward_items)
        chest["slovik_key"] = chest_slovik_key(chest)
        chest["slovik_url"] = slovik_url(chest["slovik_key"])
        weekly_source, weekly_label = _weekly_lessons(lesson_links)
        weekly_lessons = _weekly_lesson_cards(weekly_source)
        daily = weekly_lessons[0] if weekly_lessons else None
        missions = _missions(events, lesson, points, chest)
        missions_title = "Миссии на эту неделю"
        missions_subtitle = (
            (
                f"Урок {lesson.get('week_in_stage')}: {lesson.get('title')}"
                if _is_early_lesson(lesson)
                else f"Сказка {lesson.get('week_in_stage')}: {lesson.get('title')}"
            )
            if lesson and lesson.get("title")
            else None
        )
        story_stages = _story_stages(lesson_links)
        continue_url = lesson.get("url") if lesson and lesson.get("url") else None
        track_sections = []

    levels_ui = []
    for i, lvl_name in enumerate(LEVELS):
        if i < lvl_idx:
            st = "done"
        elif i == lvl_idx:
            st = "current"
        elif i == lvl_idx + 1:
            st = "next"
        else:
            st = "locked"
        thr = LEVEL_SLOVIK_THRESHOLDS[i] if i < len(LEVEL_SLOVIK_THRESHOLDS) else 0
        levels_ui.append(
            {
                "name": lvl_name,
                "status": st,
                "image": _asset_url(assets_base, LEVEL_IMAGES.get(lvl_name)),
                "threshold": thr,
                "sloviki_label": _sloviki_label(thr),
                "points_to_unlock": max(0, thr - points) if st == "next" else 0,
            }
        )

    soft_earned = (
        _trial_soft_earned_badges(events, claims, lesson_links)
        if cabinet_mode == "trial_early"
        else set()
    )
    if cabinet_mode == "trial_early":
        earned_set = _filter_trial_earned_badges(earned_set, soft_earned)
    badge_catalog = _badge_catalog_for_mode(cabinet_mode)
    badges_ui, badges_earned_count = _build_badges_ui(
        earned_set=earned_set,
        soft_earned=soft_earned,
        catalog=badge_catalog,
        assets_base=assets_base,
    )

    primary_chest = chest
    if track_sections:
        ready_chest = next((t["chest"] for t in track_sections if t["chest"].get("ready")), None)
        if ready_chest:
            primary_chest = ready_chest
    parent = _parent_summary(
        name,
        display_level,
        points,
        badges_earned_count,
        primary_chest,
        lesson,
        events,
        early=early_mode,
    )
    companion_k = companion_key(events, lesson, primary_chest)
    companion = {
        "key": companion_k,
        "url": slovik_url(companion_k),
        "hint": COMPANION_HINTS.get(companion_k, COMPANION_HINTS["main"]),
        "lesson_url": continue_url,
    }
    recent_toast = recent_event_slovik(events)

    return {
        "name": name,
        "cabinet_mode": cabinet_mode,
        "is_early": early_mode,
        "show_reading_diary": show_reading_diary,
        "level": display_level,
        "level_image": _asset_url(assets_base, LEVEL_IMAGES.get(display_level)),
        "points": points,
        "points_label": "Словиков",
        "progress_pct": progress["pct"],
        "points_to_next": progress["remaining"],
        "next_level_name": progress["next_level_name"],
        "levels": levels_ui,
        "badges": badges_ui,
        "badges_earned_count": badges_earned_count,
        "badges_total": len(badge_catalog),
        "tracks": track_sections,
        "chest": chest,
        "weekly_lessons": weekly_lessons,
        "weekly_lessons_label": weekly_label,
        "daily_lesson": daily,
        "story_stages": story_stages,
        "missions": missions,
        "missions_title": missions_title,
        "missions_subtitle": missions_subtitle,
        "reading_diary": (
            _reading_diary(tale_ratings or [], lesson_links) if show_reading_diary else []
        ),
        "treasury": _treasury(claims),
        "collection": _collection(events, earned_badges, points, early=early_mode),
        "parent": parent,
        "companion": companion,
        "recent_toast": recent_toast,
        "continue_url": continue_url,
        "slovik_main_url": slovik_url("main"),
        "slovik_preparing_url": slovik_url(POINTS_COUNTER_SLOVIK),
    }
