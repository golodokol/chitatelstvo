"""Общая логика плеера урока — HTML и JSON API."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any, Literal

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from api.event_types import MANUAL_MARK_ONLY
from api.lesson_signing import build_lesson_url, sign_quest_next_paths
from api.test_lesson_auth import verify_test_lesson_key
from catalog.loader import get_module
from config.settings import (
    LESSON_WEEK_DAYS,
    MEETING_ADDON_MODULE_ID,
    MEETING_ADDON_PRICE_RUB,
    PUBLIC_BASE_URL,
    VIDEO_BADGE_THRESHOLD,
    VIDEO_UNLOCK_SECONDS,
)
from db import repository as repo
from db.models import Child, Enrollment, Event
from gamification.cabinet_ui import quest_goal_count, quest_spark_station_ids
from gamification.chest_rewards import canonical_tale_slug
from gamification.chest_rewards import canonical_tale_slug
from gamification.sloviki import LESSON_STEP_SLOVIK, lesson_step_key, slovik_url, slovik_urls
from lessons.access import is_lesson_unlocked
from lessons.enrollment_access import child_can_access_lesson, find_enrollment_for_lesson, normalize_stage
from lessons.loader import (
    emotion_quiz_for_client,
    get_lesson,
    quiz_answer_results,
    quiz_for_client,
    reading_practice_for_client,
    retelling_quiz_for_client,
    score_emotion_quiz,
    score_quiz,
)
from lessons.step_labels import lesson_step_labels_payload
from lessons.schedule import effective_module_week, meeting_date_label, meeting_still_bookable
from lessons.single_content import merge_single_lesson_content
from services.cabinet import build_child_payload
from services.early_trial import ensure_sibling_early_trial
from services.events import submit_learning_event
from storage.yandex import resolve_video_src


def get_child_or_404(db: Session, child_id: uuid.UUID) -> Child:
    child = repo.get_child_with_family(db, child_id)
    if not child:
        raise HTTPException(404, "Ребёнок не найден")
    return child


def require_lesson_unlocked(
    db: Session,
    child_id: uuid.UUID,
    lesson: dict[str, Any],
    *,
    bypass: bool = False,
) -> Child:
    if bypass:
        return get_child_or_404(db, child_id)

    child = get_child_or_404(db, child_id)
    ensure_sibling_early_trial(db, child=child, lesson_slug=str(lesson.get("slug") or ""))
    child = get_child_or_404(db, child_id)
    enrollment = find_enrollment_for_lesson(child, lesson)
    if not child_can_access_lesson(child, lesson, enrollment):
        raise HTTPException(403, "Этот урок недоступен для вашего модуля.")
    module = get_module(enrollment.module_id) if enrollment else None
    if not is_lesson_unlocked(
        child,
        lesson,
        week_days=LESSON_WEEK_DAYS,
        enrollment=enrollment,
        module=module,
    ):
        week = effective_module_week(lesson, enrollment, module)
        raise HTTPException(
            403,
            f"Урок недели {week} ещё закрыт. Новая сказка откроется по расписанию модуля.",
        )
    playable = merge_single_lesson_content(lesson, enrollment)
    if playable.get("module_id") is not None and not playable.get("active", True):
        raise HTTPException(403, "Урок ещё готовится — скоро появится на странице прогресса.")
    return child


def load_lesson(db: Session, slug: str, *, child: Child | None = None) -> dict[str, Any]:
    lesson = get_lesson(slug)
    if not lesson:
        raise HTTPException(404, "Урок не найден")
    if child is None:
        return lesson
    enrollment = find_enrollment_for_lesson(child, lesson)
    return merge_single_lesson_content(lesson, enrollment)


def _chest_track_index(child_payload: dict[str, Any], lesson: dict[str, Any]) -> int | None:
    tale_slug = (lesson.get("tale_slug") or lesson.get("slug") or "").strip()
    slug = (lesson.get("slug") or "").strip()
    tracks = (child_payload.get("cabinet") or {}).get("tracks") or []
    for idx, track in enumerate(tracks, start=1):
        chest = track.get("chest") or {}
        if tale_slug and chest.get("tale_slug") == tale_slug:
            return idx
        for les in track.get("lesson_links") or []:
            if slug and les.get("slug") == slug:
                return idx
            if tale_slug and les.get("tale_slug") == tale_slug:
                return idx
    return 1 if tracks else None


def build_lesson_nav_urls(db: Session, child: Child, lesson: dict[str, Any]) -> dict[str, str]:
    """Ссылки на комнату приключений и сундук текущей сказки."""
    child = repo.get_child_with_family(db, child.id) or child
    family = child.family
    if not family:
        raise HTTPException(404, "Семья не найдена")

    progress_url = f"{PUBLIC_BASE_URL.rstrip('/')}/progress/{family.progress_token}"
    child_payload = build_child_payload(db, child)
    chest_idx = _chest_track_index(child_payload, lesson)
    tale_slug = canonical_tale_slug((lesson.get("tale_slug") or lesson.get("slug") or "").strip())

    chest_url = progress_url
    if tale_slug:
        chest_url += f"?chest={tale_slug}&open_chest=1"
    if chest_idx:
        chest_url += f"#chest-{chest_idx}"

    return {
        "progress_url": progress_url,
        "chest_url": chest_url,
    }


def build_slovik_payload(lesson: dict[str, Any]) -> dict[str, Any]:
    emotion = lesson.get("emotion_quiz")
    reading = lesson.get("reading_practice")
    comprehension = lesson.get("comprehension_quiz")
    meaning = lesson.get("meaning_quiz")
    retelling = lesson.get("retelling_quiz")
    initial_step = lesson_step_key(
        has_emotion=bool(emotion),
        has_reading=bool(reading),
        has_comprehension=bool(comprehension),
        has_meaning=bool(meaning),
        has_retelling=bool(retelling),
    )
    return {
        "urls": slovik_urls(),
        "initial_step": initial_step,
        "initial_url": slovik_url(initial_step),
        "step_keys": LESSON_STEP_SLOVIK,
    }


def build_video_payload(lesson: dict[str, Any]) -> dict[str, Any]:
    video = dict(lesson.get("video") or {})
    payload: dict[str, Any] = {
        "type": video.get("type"),
        "id": video.get("id"),
        "title": video.get("title"),
        "url": video.get("url"),
        "src": None,
    }
    if video.get("type") in ("yandex", "html5"):
        payload["src"] = resolve_video_src(video)
    if video.get("type") == "kinescope" and video.get("id") and not video.get("url"):
        payload["url"] = f"https://kinescope.io/{video['id']}"
    return payload


def _child_has_meeting_addon(child: Child, lesson: dict[str, Any]) -> bool:
    """Докупленная встреча с преподавателем (module_id=19) для этой сказки."""
    lesson_slug = (lesson.get("slug") or "").strip()
    tale_slug = (lesson.get("tale_slug") or lesson_slug).strip()
    tale_number = lesson.get("tale_number")
    stage = lesson.get("stage")
    for enrollment in child.enrollments:
        if enrollment.status != "active" or enrollment.module_id != MEETING_ADDON_MODULE_ID:
            continue
        if lesson_slug and enrollment.chosen_tale_slug == lesson_slug:
            return True
        if tale_slug and enrollment.chosen_tale_slug == tale_slug:
            return True
        if (
            tale_number
            and stage
            and enrollment.chosen_tale_number == tale_number
            and normalize_stage(enrollment.chosen_stage) == normalize_stage(stage)
        ):
            return True
    return False


def build_live_lesson_block(
    lesson: dict[str, Any],
    enrollment: Enrollment | None,
    *,
    child: Child | None = None,
) -> dict[str, Any] | None:
    """Блок живой встречи: ссылка при тарифе с преподавателем, иначе — запись на разовый урок."""
    live = lesson.get("live_lesson")
    if live is False:
        return None

    config = live if isinstance(live, dict) else {}
    has_live_access = False
    if child and _child_has_meeting_addon(child, lesson):
        has_live_access = True
    if enrollment and enrollment.status == "active":
        module = get_module(enrollment.module_id)
        # Только тариф с преподавателем даёт встречи «в комплекте».
        # Разовое — онлайн; встречу можно докупить отдельно, пока дата не прошла.
        if module and module.get("tariff_code") == "with_teacher":
            has_live_access = True

    if has_live_access:
        return {
            "mode": "link",
            "url": config.get("meeting_url"),
        }

    group_code = lesson.get("group_code") or "grade-1"
    stage = lesson.get("stage") or "stage-1"
    tale_number = int(lesson.get("tale_number") or 1)
    week = int(lesson.get("module_week") or 0) or None
    if not meeting_still_bookable(
        stage=stage,
        tale_number=tale_number,
        module_week=week,
        group_code=group_code,
    ):
        return None

    slug = lesson.get("slug", "")
    purchase_url = (
        f"/order/meeting?group={group_code}&stage={stage}&tale={tale_number}&slug={slug}"
    )
    default_price = int(config.get("price_rub", MEETING_ADDON_PRICE_RUB))
    # Явный null в JSON даёт None — .get(key, default) тогда не срабатывает.
    label = config.get("next_meeting_label")
    if not label:
        if week:
            label = meeting_date_label(
                week,
                weekday="четверг",
                group_code=group_code if group_code in ("early-letters", "early-stories") else None,
            )
        else:
            label = meeting_date_label(
                stage=stage,
                tale_number=tale_number,
                weekday="четверг",
                group_code=group_code if group_code in ("early-letters", "early-stories") else None,
            )
    return {
        "mode": "upsell",
        "date": label,
        "purchase_url": purchase_url,
        "price": default_price,
    }


def prepare_lesson_for_child(
    db: Session,
    child_id: uuid.UUID,
    slug: str,
    *,
    bypass: bool = False,
) -> tuple[Child, dict[str, Any]]:
    lesson = get_lesson(slug)
    if not lesson:
        raise HTTPException(404, "Урок не найден")
    child = require_lesson_unlocked(db, child_id, lesson, bypass=bypass)
    enrollment = find_enrollment_for_lesson(child, lesson)
    return child, merge_single_lesson_content(lesson, enrollment)


def lesson_has_playable_video(lesson: dict[str, Any]) -> bool:
    """Есть ли реальное видео (не заглушка «ещё не добавлено»)."""
    video = lesson.get("video") or {}
    video_id = str(video.get("id") or "").strip()
    placeholders = {"", "KINESCOPE_VIDEO_ID", "YOUTUBE_VIDEO_ID"}
    if video_id and video_id not in placeholders:
        return True
    if video.get("src"):
        return True
    # URL без id у kinescope — всё ещё заглушка; для yandex/html5 src важнее.
    if video.get("type") in ("yandex", "html5") and video.get("url"):
        return True
    return False


def lesson_tale_titles(lesson: dict[str, Any]) -> list[str]:
    """Возможные названия сказки в событиях (title мог меняться при правках)."""
    titles: list[str] = []
    for key in ("title", "tale_title"):
        value = (lesson.get(key) or "").strip()
        if value and value not in titles:
            titles.append(value)
    return titles


def _child_has_event_any_title(
    db: Session,
    child_id: uuid.UUID,
    *,
    titles: list[str],
    event_type: str,
) -> bool:
    for title in titles:
        if repo.child_has_learning_event(db, child_id, tale_title=title, event_type=event_type):
            return True
    return False


def _child_has_lesson_complete_any_title(
    db: Session,
    child_id: uuid.UUID,
    *,
    titles: list[str],
) -> bool:
    for title in titles:
        if repo.child_has_lesson_complete(db, child_id, tale_title=title):
            return True
    return False


def child_has_video_unlock(
    db: Session,
    child_id: uuid.UUID,
    *,
    tale_title: str,
    lesson: dict[str, Any] | None = None,
) -> bool:
    """Достаточно просмотра для шагов после видео (3 мин или любой следующий шаг)."""
    if lesson is not None and not lesson_has_playable_video(lesson):
        return True
    titles = lesson_tale_titles(lesson) if lesson else []
    if tale_title.strip() and tale_title.strip() not in titles:
        titles = [tale_title.strip(), *titles]
    if not titles:
        return False
    if _child_has_lesson_complete_any_title(db, child_id, titles=titles):
        return True
    if _child_has_event_any_title(db, child_id, titles=titles, event_type="video_unlock"):
        return True
    for event_type in ("emotion_quiz", "reading_practice", "comprehension", "meaning_analysis", "retelling"):
        if _child_has_event_any_title(db, child_id, titles=titles, event_type=event_type):
            return True
    return False


def _resolve_tale_rating(db: Session, child_id: uuid.UUID, tale_slug: str):
    canonical = canonical_tale_slug(tale_slug)
    row = repo.get_tale_rating(db, child_id, canonical)
    if row:
        return row
    if canonical != tale_slug:
        return repo.get_tale_rating(db, child_id, tale_slug)
    return None


def child_can_rate_tale(
    db: Session,
    child_id: uuid.UUID,
    *,
    lesson: dict[str, Any],
    tale_title: str,
) -> bool:
    """Оценка сказки — после просмотра видео или финального блока заданий."""
    titles = lesson_tale_titles(lesson)
    if tale_title.strip() and tale_title.strip() not in titles:
        titles = [tale_title.strip(), *titles]
    if not titles:
        return False
    if _child_has_lesson_complete_any_title(db, child_id, titles=titles):
        return True
    if lesson.get("retelling_quiz"):
        return _child_has_event_any_title(
            db, child_id, titles=titles, event_type="retelling"
        )
    if lesson.get("meaning_quiz"):
        return _child_has_event_any_title(
            db, child_id, titles=titles, event_type="meaning_analysis"
        )
    if lesson.get("comprehension_quiz"):
        return _child_has_event_any_title(
            db, child_id, titles=titles, event_type="comprehension"
        )
    return False


def build_lesson_json(
    db: Session,
    *,
    child: Child,
    slug: str,
    test_bypass: bool = False,
) -> dict[str, Any]:
    _, lesson = prepare_lesson_for_child(db, child.id, slug, bypass=test_bypass)
    sign_quest_next_paths(lesson, child.id)
    raw = get_lesson(slug)
    enrollment = find_enrollment_for_lesson(child, raw) if raw else None

    emotion = lesson.get("emotion_quiz")
    reading = lesson.get("reading_practice")
    comprehension = lesson.get("comprehension_quiz")
    meaning = lesson.get("meaning_quiz")
    retelling = lesson.get("retelling_quiz")
    group_code = lesson.get("group_code")
    tale_slug = canonical_tale_slug(lesson.get("tale_slug") or slug)
    tale_title = lesson["title"]
    event_titles = lesson_tale_titles(lesson)
    existing_rating = _resolve_tale_rating(db, child.id, tale_slug)
    can_rate = child_can_rate_tale(
        db, child.id, lesson=lesson, tale_title=lesson["title"]
    )
    video_unlocked = child_has_video_unlock(
        db, child.id, tale_title=tale_title, lesson=lesson
    )
    progress = {
        "video_unlocked": video_unlocked,
        "video_done": can_rate,
        "emotion_done": (
            _child_has_event_any_title(
                db, child.id, titles=event_titles, event_type="emotion_quiz"
            )
            if emotion
            else False
        ),
        "reading_done": (
            _child_has_event_any_title(
                db, child.id, titles=event_titles, event_type="reading_practice"
            )
            if reading
            else False
        ),
        "comprehension_done": (
            _child_has_event_any_title(
                db, child.id, titles=event_titles, event_type="comprehension"
            )
            if comprehension
            else False
        ),
        "meaning_done": (
            _child_has_event_any_title(
                db, child.id, titles=event_titles, event_type="meaning_analysis"
            )
            if meaning
            else False
        ),
        "retelling_done": (
            _child_has_event_any_title(
                db, child.id, titles=event_titles, event_type="retelling"
            )
            if retelling
            else False
        ),
        "creative_done": _child_has_event_any_title(
            db, child.id, titles=event_titles, event_type="creative_task"
        ),
    }

    nav_urls = build_lesson_nav_urls(db, child, lesson)

    return {
        "slug": slug,
        "title": lesson["title"],
        "lesson": lesson,
        "child_id": str(child.id),
        "child_name": child.name,
        "progress_url": nav_urls["progress_url"],
        "chest_url": nav_urls["chest_url"],
        "module_week": lesson.get("module_week"),
        "active": lesson.get("active", True),
        "video_unlock_seconds": VIDEO_UNLOCK_SECONDS,
        "video_badge_threshold": VIDEO_BADGE_THRESHOLD,
        "video_threshold": VIDEO_BADGE_THRESHOLD,
        "video": build_video_payload(lesson),
        "emotion_quiz": emotion_quiz_for_client(emotion) if emotion else None,
        "reading_practice": reading_practice_for_client(reading) if reading else None,
        "comprehension_quiz": quiz_for_client(comprehension, block_key="comprehension_quiz") if comprehension else None,
        "meaning_quiz": quiz_for_client(meaning, block_key="meaning_quiz") if meaning else None,
        "retelling_quiz": retelling_quiz_for_client(retelling, group_code=group_code) if retelling else None,
        "creative_tasks": lesson.get("creative_tasks"),
        "live_lesson": build_live_lesson_block(lesson, enrollment, child=child),
        "stations": lesson.get("stations") or [],
        "quest": lesson.get("quest") or {},
        "lesson_format": lesson.get("lesson_format") or ("quest" if lesson.get("stations") else "tale"),
        "slovik": build_slovik_payload(lesson),
        "existing_rating": existing_rating.rating if existing_rating else None,
        "can_rate": can_rate,
        "progress": progress,
        "lesson_url": build_lesson_url(child.id, slug),
        "manual_mark_types": list(MANUAL_MARK_ONLY),
        "assets_base": PUBLIC_BASE_URL,
        "step_labels": lesson_step_labels_payload(),
    }


def _required_video_unlock_seconds(duration_seconds: float | None) -> float:
    if duration_seconds and duration_seconds > 0 and duration_seconds < VIDEO_UNLOCK_SECONDS:
        return float(duration_seconds)
    return float(VIDEO_UNLOCK_SECONDS)


def handle_video_unlock(
    db: Session,
    *,
    child_id: uuid.UUID,
    slug: str,
    watched_seconds: float,
    duration_seconds: float | None = None,
    test_key: str | None = None,
) -> dict[str, Any]:
    _, lesson = prepare_lesson_for_child(
        db,
        child_id,
        slug,
        bypass=verify_test_lesson_key(test_key),
    )
    tale_title = lesson["title"]
    if child_has_video_unlock(db, child_id, tale_title=tale_title, lesson=lesson):
        return {
            "status": "duplicate",
            "message": "Можно переходить к заданиям ниже.",
        }

    # Нет ролика — засчитываем «просмотр», чтобы открылись шаги и оценка книги.
    if not lesson_has_playable_video(lesson) or verify_test_lesson_key(test_key):
        pass
    else:
        required = _required_video_unlock_seconds(duration_seconds)
        if watched_seconds < required:
            minutes = max(1, int(round(required / 60)))
            raise HTTPException(400, f"Нужно посмотреть первые {minutes} мин видео-урока.")

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type="video_unlock",
        tale_title=tale_title,
        lesson_date=date.today(),
        notes=f"auto: video {int(watched_seconds)}s",
        payload={"source": "lesson_player", "watched_seconds": watched_seconds},
    )
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "message": (
            "Первые 3 минуты засчитаны — можно переходить к заданиям."
            if status == "accepted"
            else "Можно переходить к заданиям ниже."
        ),
    }


def handle_video_complete(
    db: Session,
    *,
    child_id: uuid.UUID,
    slug: str,
    percent: float,
    test_key: str | None = None,
) -> dict[str, Any]:
    _, lesson = prepare_lesson_for_child(
        db,
        child_id,
        slug,
        bypass=verify_test_lesson_key(test_key),
    )
    if (
        not verify_test_lesson_key(test_key)
        and lesson_has_playable_video(lesson)
        and percent < VIDEO_BADGE_THRESHOLD
    ):
        raise HTTPException(
            400,
            f"Для бейджа «Читатель» нужно досмотреть минимум {int(VIDEO_BADGE_THRESHOLD * 100)}% видео.",
        )

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type="lesson_complete",
        tale_title=lesson["title"],
        lesson_date=date.today(),
        notes=f"auto: video {int(percent * 100)}%",
        payload={"source": "lesson_player", "percent": percent},
    )
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "message": (
            "Бейдж «Читатель» получен! +2 Словика."
            if status == "accepted"
            else "Бейдж за видео уже был получен ранее"
        ),
    }


def handle_emotion_quiz_submit(
    db: Session,
    *,
    child_id: uuid.UUID,
    slug: str,
    answers: dict[str, list[str]],
    test_key: str | None = None,
) -> dict[str, Any]:
    _, lesson = prepare_lesson_for_child(
        db,
        child_id,
        slug,
        bypass=verify_test_lesson_key(test_key),
    )

    quiz = lesson.get("emotion_quiz")
    if not quiz:
        raise HTTPException(404, "Эмоциометр для этого урока ещё не настроен")

    passed = score_emotion_quiz(quiz, answers)
    if not passed:
        q = quiz.get("question") or {}
        return {
            "status": "failed",
            "message": quiz.get(
                "feedback_retry",
                "Попробуй ещё раз — подумай, что чувствовал герой в этот момент.",
            ),
            "correct": list(q.get("correct") or []),
        }

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type="emotion_quiz",
        tale_title=lesson["title"],
        lesson_date=date.today(),
        notes="auto: emotion wheel",
        payload={"source": "lesson_player", "answers": answers},
    )
    q = quiz.get("question") or {}
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "correct": list(q.get("correct") or []),
        "message": quiz.get(
            "feedback_ok",
            "Верно! Задание засчитано!" if status == "accepted" else "Уже было засчитано ранее",
        ),
    }


def handle_quiz_submit(
    db: Session,
    *,
    child_id: uuid.UUID,
    slug: str,
    quiz_type: Literal["comprehension", "meaning_analysis"],
    answers: dict[str, Any],
    test_key: str | None = None,
) -> dict[str, Any]:
    _, lesson = prepare_lesson_for_child(
        db,
        child_id,
        slug,
        bypass=verify_test_lesson_key(test_key),
    )

    quiz_key = "comprehension_quiz" if quiz_type == "comprehension" else "meaning_quiz"
    quiz = lesson.get(quiz_key)
    if not quiz:
        raise HTTPException(404, "Квиз для этого урока ещё не настроен")

    tale_title = lesson["title"]
    titles = lesson_tale_titles(lesson)
    if quiz_type == "comprehension" and lesson.get("reading_practice"):
        if not _child_has_event_any_title(
            db, child_id, titles=titles, event_type="reading_practice"
        ):
            raise HTTPException(400, "Сначала прочитайте сказку по предложениям выше.")

    correct, total = score_quiz(quiz, answers)
    pass_score = int(quiz.get("pass_score", total))
    results = quiz_answer_results(quiz, answers)
    passed = correct >= pass_score

    if not passed:
        return {
            "status": "failed",
            "score": correct,
            "total": total,
            "pass_score": pass_score,
            "results": results,
            "message": "Попробуйте ещё раз — перечитайте вопросы вместе с ребёнком.",
        }

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type=quiz_type,
        tale_title=lesson["title"],
        lesson_date=date.today(),
        notes=f"auto: quiz {correct}/{total}",
        payload={"source": "lesson_player", "score": correct, "total": total},
    )
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "score": correct,
        "total": total,
        "pass_score": pass_score,
        "results": results,
        "message": "Задание засчитано!" if status == "accepted" else "Уже было засчитано ранее",
    }


def handle_retelling_submit(
    db: Session,
    *,
    child_id: uuid.UUID,
    slug: str,
    answers: dict[str, Any],
    test_key: str | None = None,
) -> dict[str, Any]:
    _, lesson = prepare_lesson_for_child(
        db,
        child_id,
        slug,
        bypass=verify_test_lesson_key(test_key),
    )

    quiz = lesson.get("retelling_quiz")
    if not quiz:
        raise HTTPException(404, "Задание на пересказ для этого урока ещё не настроено")

    tale_title = lesson["title"]
    titles = lesson_tale_titles(lesson)
    if lesson.get("meaning_quiz") and not _child_has_event_any_title(
        db, child_id, titles=titles, event_type="meaning_analysis"
    ):
        raise HTTPException(400, "Сначала выполните задания по сказке выше.")

    correct, total = score_quiz(quiz, answers)
    pass_score = int(quiz.get("pass_score", total))
    results = quiz_answer_results(quiz, answers)
    passed = correct >= pass_score

    if not passed:
        return {
            "status": "failed",
            "score": correct,
            "total": total,
            "pass_score": pass_score,
            "results": results,
            "message": "Попробуйте ещё раз — расставьте события по порядку сказки.",
        }

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type="retelling",
        tale_title=tale_title,
        lesson_date=date.today(),
        notes=f"auto: retelling {correct}/{total}",
        payload={"source": "lesson_player", "score": correct, "total": total},
    )
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "score": correct,
        "total": total,
        "pass_score": pass_score,
        "results": results,
        "message": "Задание засчитано!" if status == "accepted" else "Уже было засчитано ранее",
    }


def handle_reading_practice_submit(
    db: Session,
    *,
    child_id: uuid.UUID,
    slug: str,
    cards_read: list[str],
    test_key: str | None = None,
) -> dict[str, Any]:
    _, lesson = prepare_lesson_for_child(
        db,
        child_id,
        slug,
        bypass=verify_test_lesson_key(test_key),
    )

    block = lesson.get("reading_practice")
    if not block:
        raise HTTPException(404, "Практика чтения для этого урока ещё не настроена")

    tale_title = lesson["title"]
    if (
        not child_has_video_unlock(db, child_id, tale_title=tale_title, lesson=lesson)
        and not verify_test_lesson_key(test_key)
    ):
        raise HTTPException(400, "Сначала посмотрите начало видео-урока.")

    expected_ids = {str(card.get("id")) for card in (block.get("cards") or []) if card.get("id")}
    read_ids = {str(cid) for cid in cards_read if cid}
    if not expected_ids or read_ids != expected_ids:
        missing = expected_ids - read_ids
        return {
            "status": "failed",
            "message": "Отметь «Я прочитал!» у каждого предложения, прежде чем отправить.",
            "missing": sorted(missing),
        }

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type="reading_practice",
        tale_title=tale_title,
        lesson_date=date.today(),
        notes=f"auto: reading_practice {len(read_ids)}/{len(expected_ids)}",
        payload={"source": "lesson_player", "cards_read": sorted(read_ids)},
    )
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "message": "Задание засчитано!" if status == "accepted" else "Уже было засчитано ранее",
    }


def handle_manual_mark(
    db: Session,
    *,
    child_id: uuid.UUID,
    slug: str,
    event_type: Literal["creative_task", "live_meeting"],
    notes: str | None,
    test_key: str | None = None,
) -> dict[str, Any]:
    _, lesson = prepare_lesson_for_child(
        db,
        child_id,
        slug,
        bypass=verify_test_lesson_key(test_key),
    )
    if event_type not in MANUAL_MARK_ONLY:
        raise HTTPException(400, "Этот тип события только для ручной отметки")

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type=event_type,
        tale_title=lesson["title"],
        lesson_date=date.today(),
        notes=notes or "manual: parent mark",
        payload={"source": "lesson_player_manual", "event_type": event_type},
    )
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "message": "Отметка сохранена" if status == "accepted" else "Уже отмечено ранее",
    }


def handle_tale_rating(
    db: Session,
    *,
    child_id: uuid.UUID,
    slug: str,
    rating: int,
    test_key: str | None = None,
) -> dict[str, Any]:
    _, lesson = prepare_lesson_for_child(
        db,
        child_id,
        slug,
        bypass=verify_test_lesson_key(test_key),
    )
    if not child_can_rate_tale(
        db, child_id, lesson=lesson, tale_title=lesson["title"]
    ):
        raise HTTPException(400, "Сначала пройди задания по сказке — затем можно поставить оценку.")

    tale_slug = canonical_tale_slug(lesson.get("tale_slug") or slug)
    row = repo.save_tale_rating(
        db,
        child_id=child_id,
        tale_slug=tale_slug,
        tale_title=lesson["title"],
        rating=rating,
    )
    return {
        "status": "saved",
        "rating": row.rating,
        "message": "Спасибо! Оценка попала в читательский дневник.",
    }


def handle_quest_complete(
    db: Session,
    *,
    child_id: uuid.UUID,
    slug: str,
    sparks: int = 0,
    passed_stations: list[str] | None = None,
    test_key: str | None = None,
) -> dict[str, Any]:
    _, lesson = prepare_lesson_for_child(
        db,
        child_id,
        slug,
        bypass=verify_test_lesson_key(test_key),
    )
    if lesson.get("lesson_format") != "quest" and not lesson.get("stations"):
        raise HTTPException(400, "Этот урок не является квестом со станциями.")

    spark_ids = quest_spark_station_ids(lesson)
    valid_ids = {
        str(station.get("id") or "").strip()
        for station in (lesson.get("stations") or [])
        if station.get("id")
    }
    passed = [
        str(sid).strip()
        for sid in (passed_stations or [])
        if str(sid).strip() in valid_ids
    ]
    sparks_earned = sum(1 for sid in spark_ids if sid in passed)
    goal = quest_goal_count(lesson)
    chest_ok = (
        (bool(spark_ids) and set(spark_ids) <= set(passed))
        or sparks_earned >= goal
        or int(sparks or 0) >= goal
    )
    payload = {
        "sparks": sparks_earned,
        "format": "quest",
        "passed_stations": passed,
        "chest_ready": chest_ok,
        "client_sparks": int(sparks or 0),
    }
    notes = f"quest complete sparks={sparks_earned} chest={int(chest_ok)}"

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type="lesson_complete",
        tale_title=lesson["title"],
        notes=notes,
        payload=payload,
    )
    if status == "duplicate" and event_id:
        event = db.get(Event, event_id)
        old = (event.payload if event else None) or {}
        if event is not None and chest_ok and not old.get("chest_ready"):
            event.payload = payload
            flag_modified(event, "payload")
            event.notes = notes
            db.commit()
        elif old.get("chest_ready"):
            chest_ok = True
            try:
                sparks_earned = max(sparks_earned, int(old.get("sparks") or 0))
            except (TypeError, ValueError):
                pass

    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "sparks": sparks_earned,
        "chest_ready": chest_ok,
        "message": (
            "Урок пройден!"
            if chest_ok
            else "Маршрут пройден. Сундук откроется, когда вернутся все искорки."
        ),
    }
