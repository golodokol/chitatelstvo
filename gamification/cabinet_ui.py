"""Данные для игрового личного кабинета ученика (страница /progress)."""

from __future__ import annotations

from datetime import date
from typing import Any

from gamification.badge_assets import BADGE_ASSET_FILES, badge_image_filename
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
from lessons.access import EARLY_MODULE_START, early_lesson_opens_on
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

# Пробные early-уроки: короткий набор + закрытые тизеры полного модуля.
# Картинки для новых бейджей — docs/early-courses/12-trophy-badge-prompts.md
TRIAL_BADGE_CATALOG: list[dict[str, str]] = [
    {"name": "Первый шаг", "condition": "Первое задание в школе"},
    {"name": "Искатель искорок", "condition": "Собрал все искорки квеста"},
    {"name": "Хранитель сундука", "condition": "Открыл сундук урока"},
    {"name": "Слоговик", "condition": "Прочитал слог МА в квесте «Буквы»"},
    {"name": "Читатель", "condition": "Пройдена первая история"},
    {"name": "Знаю букву М", "condition": "Полный модуль «Буквы оживают»"},
    {"name": "Словарик", "condition": "Полный модуль «Первые истории»"},
    {"name": "Друг Словика", "condition": "Пройден весь модуль курса"},
]

BADGES_TOTAL = len(BADGE_CATALOG)

CHEST_STEPS = ("video_unlock", "comprehension", "meaning_analysis")
# Шаги после видео — если они уже в событиях, «просмотр» для сундука тоже засчитываем
# (тот же смысл, что child_has_video_unlock в lesson_player).
_POST_VIDEO_CHEST_STEPS = (
    "emotion_quiz",
    "reading_practice",
    "comprehension",
    "meaning_analysis",
    "retelling",
)

PAID_TARIFF_CODES = frozenset({"self_paced", "with_teacher", "single"})

EARLY_ASSETS_VERSION = "20260823c"

INTRO_TRIAL_COVERS: dict[str, str] = {
    "early-letters": "course-cover-letters-intro.jpg",
    "early-stories": "course-cover-stories-intro.jpg",
}

EARLY_COURSE_COVERS: dict[str, str] = {
    "early-letters": "course-cover-letters.jpg",
    "early-stories": "course-cover-stories.jpg",
    "wind": "course-cover-wind.jpg",
    "garden": "course-cover-garden.jpg",
    "rus-6-9": "course-cover-rus-6-9.jpg",
    "rus-10-12": "course-cover-rus-10-12.jpg",
}

# Вводный квест для early-трека, если в enrollment нет trial-урока (оплаченный / смешанный кабинет).
EARLY_INTRO_TRIALS: dict[str, dict[str, str]] = {
    "early-letters": {
        "slug": "early-letters-trial-lesson-01",
        "title": "Словик и пропавшие звуки",
        "tale_slug": "early-letters-stage1-tale-00",
    },
    "early-stories": {
        "slug": "early-stories-trial-lesson-01",
        "title": "Спаси первую историю",
        "tale_slug": "early-stories-stage1-tale-00",
    },
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
        "Мотор на поляне",
        "Поющая У",
        "Круглая О",
        "Змейка: с-с-с!",
        "Рычит буква Р",
        "Слоги дружат",
        "Первые слова",
        "Праздник у Словика",
    ],
    "early-stories": [
        "Кот и коробка",
        "Дождь за окном",
        "Где мяч?",
        "Словик проверяет память",
        "Мокрый кот",
        "Кот и плед",
        "Словик пришёл",
        "Словик дома",
    ],
}

# Полка книжек модуля 1 «Первые истории» (без оценок — только сбор).
# Урок 4 («Словик проверяет память») книжку на полку не даёт.
STORIES_SHELF_BOOKS: tuple[dict[str, Any], ...] = (
    {
        "slot": 1,
        "book_title": "Дома",
        "tale_slug": "early-stories-stage1-tale-00",
        "lesson_titles": ("Спаси первую историю", "Дома"),
        "cover_url": "/static/early/stories/book-cover-home.png",
        "tone": "amber",
    },
    {
        "slot": 2,
        "book_title": "Кот и коробка",
        "tale_slug": "early-stories-stage1-tale-01",
        "lesson_titles": ("Кот и коробка",),
        "cover_url": "/static/early/stories/scene-path.jpg",
        "tone": "coral",
    },
    {
        "slot": 3,
        "book_title": "Дождь за окном",
        "tale_slug": "early-stories-stage1-tale-02",
        "lesson_titles": ("Дождь за окном",),
        "cover_url": "/static/early/stories/scene-night.jpg",
        "tone": "blue",
    },
    {
        "slot": 4,
        "book_title": "Где мяч?",
        "tale_slug": "early-stories-stage1-tale-03",
        "lesson_titles": ("Где мяч?",),
        "cover_url": "/static/early/stories/scene-trail.jpg",
        "tone": "green",
    },
    {
        "slot": 5,
        "book_title": "Мокрый кот",
        "tale_slug": "early-stories-stage1-tale-05",
        "lesson_titles": ("Мокрый кот",),
        "cover_url": "/static/early/stories/scene-lesson.jpg",
        "tone": "teal",
    },
    {
        "slot": 6,
        "book_title": "Кот и плед",
        "tale_slug": "early-stories-stage1-tale-06",
        "lesson_titles": ("Кот и плед",),
        "cover_url": "/static/early/stories/scene-night-sleep.jpg",
        "tone": "violet",
    },
    {
        "slot": 7,
        "book_title": "Словик пришёл",
        "tale_slug": "early-stories-stage1-tale-07",
        "lesson_titles": ("Словик пришёл",),
        "cover_url": "/static/early/stories/scene-invite.jpg",
        "tone": "gold",
    },
    {
        "slot": 8,
        "book_title": "Словик дома",
        "tale_slug": "early-stories-stage1-tale-08",
        "lesson_titles": ("Словик дома",),
        "cover_url": "/static/early/stories/scene-book.jpg",
        "tone": "brown",
    },
)


def is_chest_step_done(step: str, done: set[str]) -> bool:
    """Шаг «видео»: 3 мин, досмотр или любой уже пройденный шаг после видео.

    Иначе сундук зависает: эмоциометр/квизы можно сдать без записи video_unlock,
    а кабинет продолжал ждать только video_unlock / lesson_complete.
    """
    if step == "video_unlock":
        if "video_unlock" in done or "lesson_complete" in done:
            return True
        return any(s in done for s in _POST_VIDEO_CHEST_STEPS)
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


def _badge_asset_url(base: str, filename: str | None) -> str | None:
    url = _asset_url(base, filename)
    if not url:
        return None
    return f"{url}?v={EARLY_ASSETS_VERSION}"


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
    if name == "Друг Словика":
        return ["Друг", "Словика"]
    if name.startswith("Знаю букву "):
        letter = name.replace("Знаю букву ", "").strip()
        return ["Знаю букву", letter]
    parts = name.split()
    if len(parts) <= 1:
        return [name]
    if len(parts) == 2:
        return parts
    return [parts[0], " ".join(parts[1:])]


COHORT_GROUPS = frozenset({"wind", "garden", "rus-6-9", "rus-10-12"})


def _is_trial_or_cohort_only_group(group: str) -> bool:
    return group.startswith("early-") or group in COHORT_GROUPS


def resolve_cabinet_mode(tracks: list[dict[str, Any]] | None) -> str:
    """
    Режим комнаты ребёнка:
    - trial_early — только пробные early-уроки
    - paid_early — куплен early/новинка или разовое (дневник сказок ещё скрыт)
    - full — есть сказочный/grade-модуль или смешанный доступ
    """
    rows = [t for t in (tracks or []) if t]
    if not rows:
        return "full"
    groups = [str(t.get("group_code") or "") for t in rows]
    tariffs = [str(t.get("tariff_code") or "") for t in rows]
    if not all(_is_trial_or_cohort_only_group(g) for g in groups):
        return "full"
    if any(t in PAID_TARIFF_CODES for t in tariffs):
        return "paid_early"
    return "trial_early"


def _course_cover_url(assets_base: str, group_code: str) -> str | None:
    filename = EARLY_COURSE_COVERS.get(group_code)
    if not filename:
        return None
    return f"{assets_base.rstrip('/')}/assets/{filename}?v={EARLY_ASSETS_VERSION}"


def _intro_trial_cover_url(assets_base: str, group_code: str) -> str | None:
    filename = INTRO_TRIAL_COVERS.get(group_code)
    if not filename:
        return _course_cover_url(assets_base, group_code)
    return f"{assets_base.rstrip('/')}/assets/{filename}?v={EARLY_ASSETS_VERSION}"


def _is_intro_trial_lesson(lesson: dict | None) -> bool:
    if not lesson:
        return False
    if str(lesson.get("tariff_code") or "") == "trial":
        return True
    slug = str(lesson.get("slug") or "")
    return "trial-lesson" in slug


def _completed_lesson_slugs(events: list[Any]) -> set[str]:
    done: set[str] = set()
    for event in events or []:
        if getattr(event, "event_type", "") != "lesson_complete":
            continue
        slug = canonical_tale_slug(getattr(event, "tale_slug", "") or "")
        if slug:
            done.add(slug)
    return done


def _lesson_is_completed(lesson: dict, completed_slugs: set[str]) -> bool:
    slug = canonical_tale_slug(lesson.get("tale_slug") or lesson.get("slug") or "")
    return bool(slug and slug in completed_slugs)


def _decorate_intro_trial_lesson(
    lesson: dict,
    *,
    assets_base: str,
    group_code: str,
) -> dict:
    row = dict(lesson)
    row["is_intro_trial"] = True
    # Общая обложка курса — как у остальных уроков трека.
    row["cover_url"] = (
        _course_cover_url(assets_base, group_code)
        or _intro_trial_cover_url(assets_base, group_code)
        or lesson.get("cover_url")
    )
    row["cover_state"] = "open" if lesson.get("url") else lesson.get("cover_state", "locked")
    return row


def _ensure_early_intro_trial(
    lesson_links: list[dict],
    *,
    group_code: str,
    child_id: str | None,
    assets_base: str,
) -> list[dict]:
    """Добавляет вводный trial в список уроков early-трека, если его ещё нет."""
    meta = EARLY_INTRO_TRIALS.get(group_code)
    if not meta or not child_id:
        return lesson_links
    if any(_is_intro_trial_lesson(les) for les in lesson_links):
        return lesson_links
    url = _trial_lesson_url(lesson_links, meta["slug"], child_id)
    if not url:
        return lesson_links
    intro = _decorate_intro_trial_lesson(
        {
            "slug": meta["slug"],
            "title": meta["title"],
            "tale_slug": meta["tale_slug"],
            "tariff_code": "trial",
            "group_code": group_code,
            "week_in_stage": 1,
            "module_week": 1,
            "url": url,
            "unlocked": True,
        },
        assets_base=assets_base,
        group_code=group_code,
    )
    return [intro, *lesson_links]


def _weekly_lessons_early(
    lesson_links: list[dict],
    *,
    events: list[Any],
    group_code: str,
    assets_base: str,
) -> tuple[list[dict], str]:
    """Пробный early: до 1 сентября — вводный; после — ближайший модульный урок."""
    label = "Урок этой недели"
    completed = _completed_lesson_slugs(events)
    intro = next((les for les in lesson_links if _is_intro_trial_lesson(les)), None)
    module_lessons = [
        les
        for les in lesson_links
        if _uses_lesson_labels(les) and not _is_intro_trial_lesson(les)
    ]
    module_lessons = sort_lessons_by_access(module_lessons)
    today = date.today()

    if today >= EARLY_MODULE_START and module_lessons:
        for les in module_lessons:
            if les.get("url") and not _lesson_is_completed(les, completed):
                return [les], label
        playable = [les for les in module_lessons if les.get("url")]
        if playable:
            return [sort_lessons_by_access(playable)[0]], label

    if intro and intro.get("url"):
        return [
            _decorate_intro_trial_lesson(
                intro,
                assets_base=assets_base,
                group_code=group_code,
            )
        ], label

    available = [les for les in lesson_links if les.get("url")]
    if available:
        return sort_lessons_by_access(available)[:1], label
    return sort_lessons_by_access(lesson_links)[:1], "Будет доступно позже"


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


def _early_quest_chest_ready_in_events(events: list[Any] | None) -> bool:
    """Есть lesson_complete early-квеста с готовым сундуком (без привязки к lesson_links)."""
    from gamification.rules import is_early_quest_title

    for event in events or []:
        if getattr(event, "event_type", "") != "lesson_complete":
            continue
        if not is_early_quest_title(getattr(event, "tale_title", None)):
            continue
        payload = getattr(event, "payload", None) or {}
        if payload.get("chest_ready") is True:
            return True
        try:
            sparks = int(payload.get("sparks") or 0)
        except (TypeError, ValueError):
            sparks = 0
        if sparks >= 3:
            return True
    return False


def _has_early_stories_complete(events: list[Any] | None) -> bool:
    from gamification.rules import is_early_stories_title

    for event in events or []:
        if getattr(event, "event_type", "") != "lesson_complete":
            continue
        if is_early_stories_title(getattr(event, "tale_title", None)):
            return True
    return False


def _trial_soft_earned_badges(
    events: list[Any],
    claims: list[Any],
    lesson_links: list[dict],
) -> set[str]:
    """Визуальные «получено» для пробных бейджей без отдельной записи в БД."""
    soft: set[str] = set()
    chest_ready = _early_quest_chest_ready_in_events(events)
    for les in lesson_links:
        if _is_early_lesson(les) and quest_chest_earned(events, les):
            chest_ready = True
            break
    if chest_ready:
        soft.add("Искатель искорок")
    letters_done = False
    for les in lesson_links:
        if str(les.get("group_code") or "") == "early-letters" and (
            quest_chest_earned(events, les) or chest_ready
        ):
            letters_done = True
            break
    if not letters_done:
        from gamification.rules import is_early_letters_title

        for event in events or []:
            if getattr(event, "event_type", "") != "lesson_complete":
                continue
            if is_early_letters_title(getattr(event, "tale_title", None)):
                letters_done = True
                break
    if letters_done and chest_ready:
        soft.add("Слоговик")
    if claims:
        soft.add("Хранитель сундука")
    # «Читатель» — только после первой истории, не после урока звуков/букв.
    if _has_early_stories_complete(events):
        soft.add("Читатель")
    return soft


def _filter_trial_earned_badges(
    earned: set[str],
    soft_earned: set[str],
    events: list[Any] | None = None,
) -> set[str]:
    """В пробном режиме «Читатель» не показываем, пока не пройдена история."""
    out = set(earned)
    if "Читатель" in out and (
        "Читатель" not in soft_earned or not _has_early_stories_complete(events)
    ):
        out.discard("Читатель")
    # «Непрерывная серия» убрали из пробного каталога — не тащим в UI.
    out.discard("Непрерывная серия")
    return out


def _tracks_have_early(tracks: list[dict[str, Any]] | None) -> bool:
    for track in tracks or []:
        group = str(track.get("group_code") or "")
        if group.startswith("early-") or group in COHORT_GROUPS:
            return True
    return False


def _merge_badge_catalogs(*catalogs: list[dict[str, str]]) -> list[dict[str, str]]:
    """Объединяет каталоги без дублей имён (порядок: early → сказки)."""
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for catalog in catalogs:
        for badge in catalog:
            name = badge["name"]
            if name in seen:
                continue
            seen.add(name)
            out.append(badge)
    return out


def _badge_catalog_for_mode(
    mode: str,
    tracks: list[dict[str, Any]] | None = None,
) -> list[dict[str, str]]:
    """Каталог трофеев: early / сказки / оба при смешанном кабинете."""
    if mode in ("trial_early", "paid_early"):
        return list(TRIAL_BADGE_CATALOG)
    if mode == "full" and _tracks_have_early(tracks):
        # Малыши + сказки в одном кабинете — показываем все бейджи.
        return _merge_badge_catalogs(TRIAL_BADGE_CATALOG, BADGE_CATALOG)
    return list(BADGE_CATALOG)


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
                "image": _badge_asset_url(assets_base, badge_image_filename(image_name)),
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
                "image": _badge_asset_url(assets_base, badge_image_filename(name)),
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


def _normalize_tale_title(title: str | None) -> str:
    raw = (title or "").strip().casefold().replace("ё", "е")
    raw = raw.replace("—", "-").replace("–", "-").replace("-", " ")
    return " ".join(raw.split())


def _events_for_tale(events: list[Any], tale_title: str) -> set[str]:
    title = _normalize_tale_title(tale_title)
    if not title:
        return set()
    out: set[str] = set()
    for e in events:
        ev_title = _normalize_tale_title(getattr(e, "tale_title", None))
        if ev_title == title:
            out.add(e.event_type)
            continue
        # Короткие совпадения / «Царевна-лягушка» vs «Царевна лягушка»
        if title and ev_title and (title in ev_title or ev_title in title):
            if abs(len(title) - len(ev_title)) <= 4:
                out.add(e.event_type)
    return out


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


def _weekly_is_open_intro(weekly: dict[str, Any] | None) -> bool:
    if not weekly or not weekly.get("url"):
        return False
    if weekly.get("chest_claimed") or weekly.get("cover_state") == "done":
        return False
    if weekly.get("is_intro_trial"):
        return True
    return str(weekly.get("headline") or "") == "Вводный урок"


def _track_has_open_intro(section: dict[str, Any]) -> bool:
    return any(_weekly_is_open_intro(w) for w in (section.get("weekly_lessons") or []))


def prioritize_open_early_intro_tracks(
    sections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """В смешанном кабинете: открытые вводные early — выше сказок."""
    if len(sections) < 2 or not any(_track_has_open_intro(s) for s in sections):
        return sections

    def sort_key(section: dict[str, Any]) -> tuple:
        group = str(section.get("group_code") or "")
        if _track_has_open_intro(section):
            early_rank = 0 if group.startswith("early-letters") else 1
            return (0, early_rank, group)
        if section.get("is_early"):
            return (1, 0, group)
        return (2, 0, str(section.get("group_label") or group))

    return sorted(sections, key=sort_key)


def _lesson_reward_slug(lesson: dict | None) -> str:
    if not lesson:
        return ""
    return canonical_tale_slug(lesson.get("tale_slug") or lesson.get("slug") or "")


def _claimed_slugs(claims: list[Any] | None) -> set[str]:
    out: set[str] = set()
    for claim in claims or []:
        slug = canonical_tale_slug(getattr(claim, "tale_slug", "") or "")
        if slug:
            out.add(slug)
    return out


def _claimed_slugs_for_links(claims: list[Any] | None, lesson_links: list[dict]) -> set[str]:
    """Slug'и забранных сундуков, в т.ч. если claim сохранён с другим slug, но тем же названием."""
    claimed = _claimed_slugs(claims)
    title_to_slug: dict[str, str] = {}
    for les in lesson_links or []:
        slug = _lesson_reward_slug(les)
        title = _normalize_tale_title(les.get("title") or les.get("tale_title"))
        if slug and title:
            title_to_slug[title] = slug
    for claim in claims or []:
        title = _normalize_tale_title(getattr(claim, "tale_title", None))
        if title and title in title_to_slug:
            claimed.add(title_to_slug[title])
    return claimed


def _claim_for_lesson(claims: list[Any] | None, lesson: dict | None) -> Any | None:
    if not lesson or not claims:
        return None
    slug = _lesson_reward_slug(lesson)
    if slug:
        for claim in claims:
            if canonical_tale_slug(getattr(claim, "tale_slug", "") or "") == slug:
                return claim
    title = _normalize_tale_title(lesson.get("title") or lesson.get("tale_title"))
    if not title:
        return None
    for claim in claims:
        if _normalize_tale_title(getattr(claim, "tale_title", None)) == title:
            return claim
    return None


def _lesson_chest_claimed(lesson: dict | None, claimed_slugs: set[str]) -> bool:
    slug = _lesson_reward_slug(lesson)
    return bool(slug and slug in claimed_slugs)


def _current_lesson(
    lesson_links: list[dict],
    *,
    claimed_slugs: set[str] | None = None,
) -> dict | None:
    """Текущий урок трека: первый доступный без забранного сундука."""
    claimed = claimed_slugs or set()
    ordered = sort_lessons_by_access(lesson_links)

    def _pick(prefer_unclaimed: bool) -> dict | None:
        for les in ordered:
            if not les.get("url"):
                continue
            if prefer_unclaimed and _lesson_chest_claimed(les, claimed):
                continue
            return les
        return None

    return _pick(True) or _pick(False) or (
        next((les for les in ordered if les.get("unlocked")), None)
        or (ordered[0] if ordered else None)
    )


def _is_early_lesson(lesson: dict | None) -> bool:
    if not lesson:
        return False
    group = str(lesson.get("group_code") or "")
    return group.startswith("early-") or str(lesson.get("lesson_format") or "") == "quest"


def _uses_lesson_labels(lesson: dict | None) -> bool:
    if not lesson:
        return False
    group = str(lesson.get("group_code") or "")
    return group.startswith("early-") or group in COHORT_GROUPS or _is_early_lesson(lesson)


def _is_early_links(lesson_links: list[dict]) -> bool:
    return any(_uses_lesson_labels(les) for les in lesson_links)


def _weekly_lessons(
    lesson_links: list[dict],
    *,
    early: bool | None = None,
    events: list[Any] | None = None,
    group_code: str = "",
    assets_base: str = "",
    claimed_slugs: set[str] | None = None,
) -> tuple[list[dict], str]:
    if not lesson_links:
        return [], "Будет доступно позже"
    if early is None:
        early = _is_early_links(lesson_links)
    if early and group_code.startswith("early-") and assets_base:
        return _weekly_lessons_early(
            lesson_links,
            events=events or [],
            group_code=group_code,
            assets_base=assets_base,
        )
    claimed = claimed_slugs or set()
    # Доступные уроки сверху; закрытые — ниже, по дате открытия.
    available = [les for les in lesson_links if les.get("url")]
    if available and claimed:
        unclaimed = [les for les in available if not _lesson_chest_claimed(les, claimed)]
        if unclaimed:
            available = unclaimed
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


def _weekly_lesson_cards(
    lessons: list[dict],
    *,
    claimed_slugs: set[str] | None = None,
) -> list[dict[str, Any]]:
    claimed = claimed_slugs or set()
    cards: list[dict[str, Any]] = []
    for lesson in sort_lessons_by_access(lessons):
        early = _uses_lesson_labels(lesson)
        num = lesson.get("week_in_stage") or lesson.get("module_week") or 1
        title = lesson.get("title", "Урок")
        group = str(lesson.get("group_code") or "")
        chest_claimed = _lesson_chest_claimed(lesson, claimed)
        cover_state = "done" if chest_claimed else lesson.get("cover_state", "locked")
        if lesson.get("is_intro_trial") or _is_intro_trial_lesson(lesson):
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
                    "headline": "Вводный урок",
                    "goal": goal,
                    "duration": "≈ 15–20 мин",
                    "reward_pts": 3,
                    "reward_label": "искорки",
                    "url": lesson.get("url"),
                    "unlocked": bool(lesson.get("url")),
                    "opens_on_label": lesson.get("opens_on_label"),
                    "cover_url": lesson.get("cover_url"),
                    "cover_state": cover_state,
                    "chest_claimed": chest_claimed,
                    "tale_slug": _lesson_reward_slug(lesson),
                    "week_in_stage": num,
                    "is_early": True,
                    "is_intro_trial": True,
                    "group_code": group,
                }
            )
            continue
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
                    "cover_state": cover_state,
                    "chest_claimed": chest_claimed,
                    "tale_slug": _lesson_reward_slug(lesson),
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
                    "cover_state": cover_state,
                    "chest_claimed": chest_claimed,
                    "tale_slug": _lesson_reward_slug(lesson),
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
    if claimed:
        steps_done = steps_total
        steps_remaining = 0
        pct = 100
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


def _story_stages(
    lesson_links: list[dict],
    *,
    claimed_slugs: set[str] | None = None,
) -> list[dict]:
    if not lesson_links:
        return []
    claimed = claimed_slugs or set()
    ordered = sort_lessons_by_access(lesson_links)
    by_stage: dict[str, list[dict]] = {}
    stage_order: list[str] = []
    for les in ordered:
        stage = les.get("stage") or "stage-1"
        if stage not in by_stage:
            stage_order.append(stage)
            by_stage[stage] = []
        row = dict(les)
        if _lesson_chest_claimed(les, claimed):
            row["cover_state"] = "done"
            row["chest_claimed"] = True
        by_stage[stage].append(row)
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


def _completed_story_keys(events: list[Any] | None) -> set[str]:
    """Ключи пройденных уроков историй: нормализованный title + tale_slug."""
    keys: set[str] = set()
    for event in events or []:
        if getattr(event, "event_type", "") != "lesson_complete":
            continue
        title = str(getattr(event, "tale_title", "") or "").strip().casefold()
        if title:
            keys.add(title)
        payload = getattr(event, "payload", None) or {}
        for raw in (
            payload.get("tale_slug"),
            payload.get("slug"),
            payload.get("lesson_slug"),
            getattr(event, "tale_slug", None),
        ):
            slug = canonical_tale_slug(str(raw or "").strip())
            if slug:
                keys.add(slug)
    return keys


def _stories_book_unlocked(book: dict[str, Any], completed: set[str]) -> bool:
    slug = canonical_tale_slug(str(book.get("tale_slug") or ""))
    if slug and slug in completed:
        return True
    for title in book.get("lesson_titles") or ():
        if str(title).strip().casefold() in completed:
            return True
    book_title = str(book.get("book_title") or "").strip().casefold()
    return bool(book_title and book_title in completed)


def _has_early_stories_track(tracks: list[dict[str, Any]] | None, lesson_links: list[dict]) -> bool:
    for track in tracks or []:
        group = str(track.get("group_code") or "")
        if group.startswith("early-stories") or "истори" in str(track.get("group_label") or "").lower():
            return True
        for les in track.get("lesson_links") or []:
            if str(les.get("group_code") or "").startswith("early-stories"):
                return True
    for les in lesson_links or []:
        if str(les.get("group_code") or "").startswith("early-stories"):
            return True
        slug = str(les.get("slug") or les.get("tale_slug") or "")
        if "early-stories" in slug:
            return True
    return False


def _stories_book_shelf(
    events: list[Any] | None,
    *,
    assets_base: str = "",
) -> dict[str, Any]:
    """Мини-полка: 8 мест модуля 1. Книжка появляется после прохождения урока."""
    completed = _completed_story_keys(events)
    slots: list[dict[str, Any]] = []
    unlocked_n = 0
    for book in STORIES_SHELF_BOOKS:
        unlocked = _stories_book_unlocked(book, completed)
        if unlocked:
            unlocked_n += 1
        cover = str(book.get("cover_url") or "")
        slots.append(
            {
                "slot": book["slot"],
                "book_title": book["book_title"],
                "tale_slug": book["tale_slug"],
                "unlocked": unlocked,
                "cover_url": cover if unlocked else "",
                "tone": book.get("tone") or "amber",
                "slot_label": f"место {book['slot']}",
            }
        )
    return {
        "title": "Полка книжек",
        "subtitle": "Прочитал урок — книжка встаёт на полку. Собери все 8 книжек модуля.",
        "slots": slots,
        "collected": unlocked_n,
        "total": len(STORIES_SHELF_BOOKS),
        "empty_hint": "Пройди вводный урок — первая книжка «Дома» займёт место 1.",
    }


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
    child_id: str | None = None,
) -> dict[str, Any]:
    group_code = str(track.get("group_code") or "")
    lesson_links = _ensure_early_intro_trial(
        list(track.get("lesson_links") or []),
        group_code=group_code,
        child_id=child_id,
        assets_base=assets_base,
    )
    claimed = _claimed_slugs_for_links(claims, lesson_links)
    weekly_source, weekly_label = _weekly_lessons(
        lesson_links,
        events=events,
        group_code=group_code,
        assets_base=assets_base,
        claimed_slugs=claimed,
    )
    early = _is_early_links(lesson_links) or group_code.startswith("early-") or group_code in COHORT_GROUPS

    def _chest_for_lesson(les: dict | None) -> dict[str, Any]:
        tale_slug = _lesson_reward_slug(les)
        current_claim = _claim_for_lesson(claims, les)
        reward_items = (
            rewards_for_tale(tale_slug, les.get("title", "")) if tale_slug and les else []
        )
        chest_state = _chest_state(events, les, claim=current_claim, reward_items=reward_items)
        chest_state["slovik_key"] = chest_slovik_key(chest_state)
        chest_state["slovik_url"] = slovik_url(chest_state["slovik_key"])
        return chest_state

    # Сундук на каждую открытую сказку трека (несколько разовых в одном блоке).
    chests = [_chest_for_lesson(les) for les in weekly_source]
    lesson = _current_lesson(lesson_links, claimed_slugs=claimed)
    if chests:
        ready = next((c for c in chests if c.get("ready") and not c.get("claimed")), None)
        chest = ready or next((c for c in chests if not c.get("claimed")), chests[0])
        # Текущий урок = сказка выбранного сундука.
        focus_slug = str(chest.get("tale_slug") or "")
        if focus_slug:
            for les in weekly_source:
                if _lesson_reward_slug(les) == focus_slug:
                    lesson = les
                    break
    else:
        chest = _chest_for_lesson(lesson)

    missions = _missions(events, lesson, points, chest)
    is_trial_track = cabinet_mode == "trial_early" or str(track.get("tariff_code") or "") == "trial"
    if is_trial_track and early:
        story_stages: list[dict] = []
        upcoming_lessons = _upcoming_module_lessons(group_code=group_code, assets_base=assets_base)
        stories_title = f"Дальше в программе · {track.get('group_label') or ''}".strip(" ·")
        stories_subtitle = "8 уроков модуля — по вторникам и четвергам с 1 сентября"
    else:
        story_stages = _story_stages(lesson_links, claimed_slugs=claimed)
        upcoming_lessons = []
        stories_title = (
            f"Мои уроки · {track.get('group_label') or ''}".strip(" ·")
            if early
            else f"Мои сказки · {track.get('group_label') or ''}".strip(" ·")
        )
        stories_subtitle = None
    treasury = _treasury_for_track(claims, lesson_links)
    weekly_cards = _weekly_lesson_cards(weekly_source, claimed_slugs=claimed)

    return {
        "group_code": group_code,
        "group_label": track.get("group_label", ""),
        "module_title": track.get("module_title", ""),
        "module_id": track.get("module_id"),
        "tariff_code": track.get("tariff_code") or "",
        "is_early": early,
        "is_trial": is_trial_track,
        "chest": chest,
        "chests": chests if chests else ([chest] if chest else []),
        "treasury": treasury,
        "weekly_lessons": weekly_cards,
        "weekly_lessons_label": weekly_label,
        "daily_lesson": weekly_cards[0] if weekly_cards else None,
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
        "continue_url": (
            None
            if lesson and _lesson_chest_claimed(lesson, claimed)
            else (lesson.get("url") if lesson and lesson.get("url") else None)
        ),
    }


def _lesson_url_by_slug(lesson_links: list[dict], slug: str) -> str:
    needle = str(slug or "").strip()
    if not needle:
        return ""
    for les in lesson_links or []:
        if str(les.get("slug") or "") == needle and les.get("url"):
            return str(les.get("url"))
    return f"/lesson/{needle}"


def _event_time(event: Any) -> float:
    for attr in ("created_at", "ts", "timestamp"):
        val = getattr(event, attr, None)
        if val is None:
            continue
        try:
            return float(val.timestamp())  # type: ignore[union-attr]
        except Exception:
            try:
                return float(val)
            except Exception:
                continue
    return 0.0


def _last_early_path_key(
    events: list[Any] | None,
    tracks: list[dict[str, Any]] | None,
    lesson_links: list[dict],
) -> str | None:
    """Какой early-курс привёл в сундук последним: early-letters | early-stories."""
    slug_to_key: dict[str, str] = {}
    title_to_key: dict[str, str] = {}
    for les in lesson_links or []:
        slug = str(les.get("slug") or "")
        group = str(les.get("group_code") or "")
        title = str(les.get("title") or "").strip().lower()
        key = None
        if "early-letters" in group or "early-letters" in slug or "букв" in title:
            key = "early-letters"
        elif "early-stories" in group or "early-stories" in slug or "истори" in title:
            key = "early-stories"
        if not key:
            continue
        if slug:
            slug_to_key[slug] = key
        if title:
            title_to_key[title] = key

    # Prefer a track whose chest is ready / just opened.
    for track in tracks or []:
        group = str(track.get("group_code") or track.get("code") or "")
        chest = track.get("chest") or {}
        if not (chest.get("ready") or chest.get("claimed")):
            continue
        if group.startswith("early-letters"):
            return "early-letters"
        if group.startswith("early-stories"):
            return "early-stories"

    ranked = sorted(events or [], key=_event_time, reverse=True)
    for event in ranked:
        if getattr(event, "event_type", "") != "lesson_complete":
            continue
        payload = getattr(event, "payload", None) or {}
        slug = str(payload.get("lesson_slug") or payload.get("slug") or "").strip()
        if slug in slug_to_key:
            return slug_to_key[slug]
        title = str(getattr(event, "tale_title", "") or "").strip().lower()
        if title in title_to_key:
            return title_to_key[title]
        if "букв" in title or "звук" in title:
            return "early-letters"
        if "истори" in title:
            return "early-stories"
    return None


def _trial_lesson_url(
    lesson_links: list[dict],
    slug: str,
    child_id: str | None,
) -> str | None:
    """Подписанная ссылка на пробный урок (в lesson_links его может не быть)."""
    needle = str(slug or "").strip()
    if not needle:
        return None
    for les in lesson_links or []:
        if str(les.get("slug") or "") != needle:
            continue
        url = str(les.get("url") or "").strip()
        # Нужна подписанная ссылка (?child=&exp=&sig=), не голый /lesson/slug.
        if url and "sig=" in url:
            return url
        break
    if not child_id:
        return None
    from api.lesson_signing import build_lesson_url

    return build_lesson_url(child_id, slug)


def _build_path_hint(
    *,
    events: list[Any] | None,
    tracks: list[dict[str, Any]] | None,
    lesson_links: list[dict],
    cabinet_mode: str,
    child_id: str | None = None,
) -> dict[str, Any] | None:
    # Блок «Куда дальше?» / отдельные кнопки пробных — скрыт:
    # вводные early-уроки показываются как обычные карточки урока в треке.
    return None


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
    child_id: str | None = None,
) -> dict[str, Any]:
    """Собирает контекст игрового кабинета для одного ребёнка."""
    earned_set = set(earned_badges)
    # Для toast — реальные бейджи из БД до trial-фильтра (иначе «Читатель»
    # каждый раз выглядит как новый и снова всплывает).
    toast_badge_names = list(earned_badges)
    display_level = level_from_points(points)
    lvl_idx = _level_index(display_level)
    progress = _level_progress(points, display_level)
    claims = chest_claims or []
    cabinet_mode = resolve_cabinet_mode(tracks)
    early_mode = cabinet_mode in ("trial_early", "paid_early")
    show_reading_diary = cabinet_mode == "full"
    show_book_shelf = early_mode and _has_early_stories_track(tracks, lesson_links)
    book_shelf = _stories_book_shelf(events, assets_base=assets_base) if show_book_shelf else None
    if not show_book_shelf and early_mode:
        # Урок историй пройден, даже если в tracks сейчас другой early-курс.
        completed = _completed_story_keys(events)
        if any(_stories_book_unlocked(book, completed) for book in STORIES_SHELF_BOOKS):
            show_book_shelf = True
            book_shelf = _stories_book_shelf(events, assets_base=assets_base)

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
                    child_id=child_id,
                )
            )
        if cabinet_mode == "full":
            track_sections = prioritize_open_early_intro_tracks(track_sections)
        for section in track_sections:
            section["pin_intro_top"] = _track_has_open_intro(section)

    if track_sections:
        primary = track_sections[0]
        lesson = _current_lesson(lesson_links, claimed_slugs=_claimed_slugs_for_links(claims, lesson_links))
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
            (
                t["continue_url"]
                for t in track_sections
                if t.get("continue_url") and _track_has_open_intro(t)
            ),
            None,
        )
        if not continue_url:
            continue_url = next(
                (t["continue_url"] for t in track_sections if t.get("continue_url")),
                None,
            )
    else:
        claimed = _claimed_slugs_for_links(claims, lesson_links)
        lesson = _current_lesson(lesson_links, claimed_slugs=claimed)
        tale_slug = _lesson_reward_slug(lesson)
        current_claim = _claim_for_lesson(claims, lesson)
        reward_items = (
            rewards_for_tale(tale_slug, lesson.get("title", "")) if tale_slug and lesson else []
        )
        chest = _chest_state(events, lesson, claim=current_claim, reward_items=reward_items)
        chest["slovik_key"] = chest_slovik_key(chest)
        chest["slovik_url"] = slovik_url(chest["slovik_key"])
        legacy_group = str((lesson_links[0] or {}).get("group_code") or "") if lesson_links else ""
        weekly_source, weekly_label = _weekly_lessons(
            lesson_links,
            events=events,
            group_code=legacy_group,
            assets_base=assets_base,
            claimed_slugs=claimed,
        )
        weekly_lessons = _weekly_lesson_cards(weekly_source, claimed_slugs=claimed)
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
        story_stages = _story_stages(lesson_links, claimed_slugs=claimed)
        continue_url = (
            None
            if lesson and _lesson_chest_claimed(lesson, claimed)
            else (lesson.get("url") if lesson and lesson.get("url") else None)
        )
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
        if cabinet_mode in ("trial_early", "paid_early")
        or (cabinet_mode == "full" and _tracks_have_early(tracks))
        else set()
    )
    if cabinet_mode == "trial_early" or (
        cabinet_mode == "full" and _tracks_have_early(tracks)
    ):
        earned_set = _filter_trial_earned_badges(earned_set, soft_earned, events)
    badge_catalog = _badge_catalog_for_mode(cabinet_mode, tracks)
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
    companion_hint = COMPANION_HINTS.get(companion_k, COMPANION_HINTS["main"])
    if any(_track_has_open_intro(t) for t in track_sections):
        companion_hint = "Вводный урок ждёт!"
    companion = {
        "key": companion_k,
        "url": slovik_url(companion_k),
        "hint": companion_hint,
        "lesson_url": continue_url,
    }
    recent_toast = recent_event_slovik(events, current_badges=toast_badge_names)
    path_hint = _build_path_hint(
        events=events,
        tracks=track_sections or tracks,
        lesson_links=lesson_links,
        cabinet_mode=cabinet_mode,
        child_id=child_id,
    )
    if path_hint and track_sections:
        src = str(path_hint.get("source") or "")
        track_sections.sort(
            key=lambda t: 0 if str(t.get("group_code") or "").startswith(src) else 1
        )
        primary = track_sections[0]
        chest = primary["chest"]
        primary_chest = chest
        ready_chest = next((t["chest"] for t in track_sections if t["chest"].get("ready")), None)
        if ready_chest:
            primary_chest = ready_chest
        daily = primary.get("daily_lesson")
        weekly_lessons = primary.get("weekly_lessons") or []
        weekly_label = primary.get("weekly_lessons_label") or weekly_label
        missions = primary["missions"]
        missions_title = primary["missions_title"]
        missions_subtitle = primary["missions_subtitle"]
        story_stages = primary["story_stages"]
        continue_url = next(
            (t["continue_url"] for t in track_sections if t.get("continue_url")),
            continue_url,
        )
        companion["lesson_url"] = continue_url

    return {
        "name": name,
        "cabinet_mode": cabinet_mode,
        "is_early": early_mode,
        "show_reading_diary": show_reading_diary,
        "show_book_shelf": show_book_shelf,
        "book_shelf": book_shelf,
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
        "collection": (
            {
                **_collection(events, earned_badges, points, early=early_mode),
                **(
                    {
                        "stories_count": book_shelf["collected"],
                        "stories_label": "книжек",
                    }
                    if show_book_shelf and book_shelf
                    else {}
                ),
            }
        ),
        "parent": parent,
        "companion": companion,
        "recent_toast": recent_toast,
        "continue_url": continue_url,
        "path_hint": path_hint,
        "slovik_main_url": slovik_url("main"),
        "slovik_preparing_url": slovik_url(POINTS_COUNTER_SLOVIK),
    }
