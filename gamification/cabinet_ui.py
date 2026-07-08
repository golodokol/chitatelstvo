"""Данные для игрового личного кабинета ученика (страница /progress)."""

from __future__ import annotations

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

BADGES_TOTAL = len(BADGE_CATALOG)

CHEST_STEPS = ("video_unlock", "comprehension", "meaning_analysis")


def is_chest_step_done(step: str, done: set[str]) -> bool:
    """Шаг «видео»: засчитывается и 3 мин (video_unlock), и досмотр (lesson_complete)."""
    if step == "video_unlock":
        return "video_unlock" in done or "lesson_complete" in done
    return step in done


def chest_ready_from_done(done: set[str]) -> bool:
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


def _current_lesson(lesson_links: list[dict]) -> dict | None:
    for les in lesson_links:
        if les.get("url"):
            return les
    for les in lesson_links:
        if les.get("unlocked"):
            return les
    return lesson_links[0] if lesson_links else None


def _weekly_lessons(lesson_links: list[dict]) -> tuple[list[dict], str]:
    if not lesson_links:
        return [], "Урок этой недели"
    unlocked = [les for les in lesson_links if les.get("unlocked")]
    if unlocked:
        current_week = max(int(les.get("module_week") or 1) for les in unlocked)
    else:
        current_week = int(lesson_links[0].get("module_week") or 1)
    week_lessons = [
        les for les in lesson_links if int(les.get("module_week") or 1) == current_week
    ]
    if not week_lessons:
        week_lessons = [_current_lesson(lesson_links) or lesson_links[0]]
    label = "Уроки этой недели" if len(week_lessons) > 1 else "Урок этой недели"
    return week_lessons, label


def _weekly_lesson_cards(lessons: list[dict]) -> list[dict[str, Any]]:
    reward_pts = 15
    cards: list[dict[str, Any]] = []
    for lesson in lessons:
        cards.append(
            {
                "title": lesson.get("title", "Урок"),
                "goal": (
                    "За 30 минут пройдёшь видео-сказку, практику чтения, "
                    "тесты, пересказ и задания из волшебного сундука."
                ),
                "duration": "≈ 30 мин",
                "reward_pts": reward_pts,
                "url": lesson.get("url"),
                "unlocked": bool(lesson.get("url")),
                "opens_on_label": lesson.get("opens_on_label"),
                "cover_url": lesson.get("cover_url"),
                "cover_state": lesson.get("cover_state", "locked"),
                "week_in_stage": lesson.get("week_in_stage"),
            }
        )
    return cards


def _chest_title(tale_title: str) -> str:
    tale = (tale_title or "").strip()
    if tale:
        return f"Сундук к сказке «{tale}»"
    return "Сундук Сказки"


def _chest_subtitle(tale_title: str) -> str:
    tale = (tale_title or "").strip()
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

    if not lesson:
        return {
            "title": "Сундук Сказки",
            "subtitle": "Когда откроется первая сказка — здесь появится награда.",
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
    elif steps_remaining == 1:
        hint = "До открытия осталось 1 задание"
    else:
        hint = f"До открытия осталось {steps_remaining} задания"

    return {
        "title": _chest_title(tale_title),
        "subtitle": _chest_subtitle(tale_title),
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

    def status(key: str) -> str:
        if key in done:
            return "done"
        if lesson and lesson.get("url"):
            return "active"
        return "locked"

    chest_ready = bool(chest.get("ready"))
    chest_claimed = bool(chest.get("claimed"))
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
            "status": "done" if chest_claimed else ("active" if chest_ready else ("active" if lesson and lesson.get("url") else "locked")),
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


def _collection(events: list[Any], earned_badges: list[str], points: int) -> dict[str, Any]:
    tales = {
        (e.tale_title or "").strip()
        for e in events
        if e.event_type == "lesson_complete" and (e.tale_title or "").strip()
    }
    secrets = sum(1 for e in events if e.event_type == "meaning_analysis")
    return {
        "stories_count": len(tales),
        "stories_preview": sorted(tales)[:4],
        "badges_count": len(earned_badges),
        "points": points,
        "secrets_count": secrets,
        "cards_count": len(earned_badges) + len(tales),
    }


def _parent_summary(
    child_name: str,
    level: str,
    points: int,
    badges_count: int,
    chest: dict,
    lesson: dict | None,
    events: list[Any],
) -> dict[str, str]:
    skill = "понимание текста и поиск смысла в сказке"
    if level in ("Мастер слова", "Литературный детектив"):
        skill = "пересказ, творчество и глубокое чтение"
    elif level == "Исследователь":
        skill = "внимательное чтение и анализ смысла"

    completed = sum(1 for e in events if e.event_type == "lesson_complete")
    lesson_line = lesson["title"] if lesson else "скоро откроется первая сказка"

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
    by_stage: dict[str, list[dict]] = {}
    for les in lesson_links:
        stage = les.get("stage") or "stage-1"
        by_stage.setdefault(stage, []).append(les)
    stages: list[dict] = []
    for stage_key in ("stage-1", "stage-2"):
        items = by_stage.get(stage_key)
        if not items:
            continue
        stages.append(
            {
                "key": stage_key,
                "label": STAGE_LABELS.get(stage_key, stage_key),
                "lessons": items,
            }
        )
    return stages


def _reading_diary(ratings: list[Any], lesson_links: list[dict]) -> list[dict[str, Any]]:
    """Записи дневника: оценённые сказки, от высшей оценки к низшей."""
    by_slug = {les.get("slug"): les for les in lesson_links if les.get("slug")}
    entries: list[dict[str, Any]] = []
    for row in ratings:
        lesson = by_slug.get(row.tale_slug)
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
        "downloadable": bool(item.get("downloadable")),
    }


def _treasury_items_for_claim(claim: Any) -> list[dict[str, Any]]:
    """Актуальные награды сказки — из текущего конфига сундука, не из устаревшего JSON в БД."""
    title = (claim.tale_title or "").strip() or "Сказка"
    current = items_for_treasury(rewards_for_tale(claim.tale_slug, title))
    if current:
        source_items = current
    else:
        source_items = [
            item for item in (claim.items or []) if item.get("kind") != LETTER_KIND
        ]
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
) -> dict[str, Any]:
    lesson_links = track.get("lesson_links") or []
    lesson = _current_lesson(lesson_links)
    weekly_source, weekly_label = _weekly_lessons(lesson_links)
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
    story_stages = track.get("lesson_stages") or _story_stages(lesson_links)
    treasury = _treasury_for_track(claims, lesson_links)

    return {
        "group_code": track.get("group_code", ""),
        "group_label": track.get("group_label", ""),
        "module_title": track.get("module_title", ""),
        "module_id": track.get("module_id"),
        "chest": chest,
        "treasury": treasury,
        "weekly_lessons": _weekly_lesson_cards(weekly_source),
        "weekly_lessons_label": weekly_label,
        "daily_lesson": _weekly_lesson_cards(weekly_source)[0] if weekly_source else None,
        "story_stages": story_stages,
        "missions": missions,
        "missions_title": "Миссии на эту неделю",
        "missions_subtitle": (
            f"Сказка {lesson.get('week_in_stage')}: {lesson.get('title')}"
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

    track_sections: list[dict[str, Any]] = []
    if tracks:
        for track in tracks:
            track_sections.append(
                _build_track_section(
                    track=track,
                    events=events,
                    claims=claims,
                    points=points,
                    assets_base=assets_base,
                )
            )

    if track_sections:
        primary = track_sections[0]
        lesson = _current_lesson(lesson_links)
        chest = primary["chest"]
        daily = primary.get("daily_lesson")
        weekly_lessons = primary.get("weekly_lessons") or []
        weekly_label = primary.get("weekly_lessons_label") or "Урок этой недели"
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
            f"Сказка {lesson.get('week_in_stage')}: {lesson.get('title')}"
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

    badges_ui = []
    next_badge = None
    for badge in BADGE_CATALOG:
        earned = badge["name"] in earned_set
        if not earned and next_badge is None:
            next_badge = badge["name"]
        badges_ui.append(
            {
                "name": badge["name"],
                "condition": badge["condition"],
                "earned": earned,
                "image": _asset_url(assets_base, BADGE_IMAGES.get(badge["name"])),
                "status": "earned" if earned else ("next" if badge["name"] == next_badge else "locked"),
            }
        )

    primary_chest = chest
    if track_sections:
        ready_chest = next((t["chest"] for t in track_sections if t["chest"].get("ready")), None)
        if ready_chest:
            primary_chest = ready_chest
    parent = _parent_summary(name, display_level, points, len(earned_badges), primary_chest, lesson, events)
    companion_k = companion_key(events, lesson, primary_chest)
    companion = {
        "key": companion_k,
        "url": slovik_url(companion_k),
        "hint": COMPANION_HINTS.get(companion_k, COMPANION_HINTS["main"]),
    }
    recent_toast = recent_event_slovik(events)

    return {
        "name": name,
        "level": display_level,
        "level_image": _asset_url(assets_base, LEVEL_IMAGES.get(display_level)),
        "points": points,
        "points_label": "Словиков",
        "progress_pct": progress["pct"],
        "points_to_next": progress["remaining"],
        "next_level_name": progress["next_level_name"],
        "levels": levels_ui,
        "badges": badges_ui,
        "badges_earned_count": len(earned_badges),
        "badges_total": BADGES_TOTAL,
        "tracks": track_sections,
        "chest": chest,
        "weekly_lessons": weekly_lessons,
        "weekly_lessons_label": weekly_label,
        "daily_lesson": daily,
        "story_stages": story_stages,
        "missions": missions,
        "missions_title": missions_title,
        "missions_subtitle": missions_subtitle,
        "reading_diary": _reading_diary(tale_ratings or [], lesson_links),
        "treasury": _treasury(claims),
        "collection": _collection(events, earned_badges, points),
        "parent": parent,
        "companion": companion,
        "recent_toast": recent_toast,
        "continue_url": continue_url,
        "slovik_main_url": slovik_url("main"),
        "slovik_preparing_url": slovik_url(POINTS_COUNTER_SLOVIK),
    }
