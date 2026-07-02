"""Общая логика плеера урока — HTML и JSON API."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any, Literal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.event_types import MANUAL_MARK_ONLY
from api.lesson_signing import build_lesson_url
from api.test_lesson_auth import verify_test_lesson_key
from catalog.loader import get_module
from config.settings import (
    LESSON_WEEK_DAYS,
    MEETING_ADDON_MODULE_ID,
    MEETING_ADDON_PRICE_RUB,
    PUBLIC_BASE_URL,
    VIDEO_WATCH_THRESHOLD,
)
from db import repository as repo
from db.models import Child, Enrollment
from gamification.sloviki import LESSON_STEP_SLOVIK, lesson_step_key, slovik_url, slovik_urls
from lessons.access import is_lesson_unlocked
from lessons.enrollment_access import child_can_access_lesson, find_enrollment_for_lesson, normalize_stage
from lessons.loader import (
    emotion_quiz_for_client,
    get_lesson,
    quiz_answer_results,
    quiz_for_client,
    score_emotion_quiz,
    score_quiz,
)
from lessons.step_labels import lesson_step_labels_payload
from lessons.schedule import effective_module_week
from lessons.single_content import merge_single_lesson_content
from services.cabinet import build_child_payload
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
    tale_slug = (lesson.get("tale_slug") or lesson.get("slug") or "").strip()

    chest_url = progress_url
    if tale_slug:
        chest_url += f"?chest={tale_slug}"
    if chest_idx:
        chest_url += f"#chest-{chest_idx}"

    return {
        "progress_url": progress_url,
        "chest_url": chest_url,
    }


def build_slovik_payload(lesson: dict[str, Any]) -> dict[str, Any]:
    emotion = lesson.get("emotion_quiz")
    comprehension = lesson.get("comprehension_quiz")
    meaning = lesson.get("meaning_quiz")
    initial_step = lesson_step_key(
        has_emotion=bool(emotion),
        has_comprehension=bool(comprehension),
        has_meaning=bool(meaning),
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
        if module and module.get("tariff_code") in ("with_teacher", "single"):
            has_live_access = True

    if has_live_access:
        return {
            "mode": "link",
            "url": config.get("meeting_url"),
        }

    group_code = lesson.get("group_code") or "grade-1"
    stage = lesson.get("stage") or "stage-1"
    tale_number = lesson.get("tale_number") or lesson.get("lesson_number") or 1
    slug = lesson.get("slug", "")
    purchase_url = (
        f"/order/meeting?group={group_code}&stage={stage}&tale={tale_number}&slug={slug}"
    )
    default_price = int(config.get("price_rub", MEETING_ADDON_PRICE_RUB))
    return {
        "mode": "upsell",
        "date": config.get("next_meeting_label", "20 июля 2026"),
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


def build_lesson_json(
    db: Session,
    *,
    child: Child,
    slug: str,
    test_bypass: bool = False,
) -> dict[str, Any]:
    _, lesson = prepare_lesson_for_child(db, child.id, slug, bypass=test_bypass)
    raw = get_lesson(slug)
    enrollment = find_enrollment_for_lesson(child, raw) if raw else None

    emotion = lesson.get("emotion_quiz")
    comprehension = lesson.get("comprehension_quiz")
    meaning = lesson.get("meaning_quiz")
    tale_slug = lesson.get("tale_slug") or slug
    existing_rating = repo.get_tale_rating(db, child.id, tale_slug)
    can_rate = repo.child_has_lesson_complete(db, child.id, tale_title=lesson["title"])
    tale_title = lesson["title"]
    progress = {
        "video_done": can_rate,
        "emotion_done": (
            repo.child_has_learning_event(db, child.id, tale_title=tale_title, event_type="emotion_quiz")
            if emotion
            else False
        ),
        "comprehension_done": (
            repo.child_has_learning_event(db, child.id, tale_title=tale_title, event_type="comprehension")
            if comprehension
            else False
        ),
        "meaning_done": (
            repo.child_has_learning_event(db, child.id, tale_title=tale_title, event_type="meaning_analysis")
            if meaning
            else False
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
        "video_threshold": VIDEO_WATCH_THRESHOLD,
        "video": build_video_payload(lesson),
        "emotion_quiz": emotion_quiz_for_client(emotion) if emotion else None,
        "comprehension_quiz": quiz_for_client(comprehension, block_key="comprehension_quiz") if comprehension else None,
        "meaning_quiz": quiz_for_client(meaning, block_key="meaning_quiz") if meaning else None,
        "creative_tasks": lesson.get("creative_tasks"),
        "live_lesson": build_live_lesson_block(lesson, enrollment, child=child),
        "slovik": build_slovik_payload(lesson),
        "existing_rating": existing_rating.rating if existing_rating else None,
        "can_rate": can_rate,
        "progress": progress,
        "lesson_url": build_lesson_url(child.id, slug),
        "manual_mark_types": list(MANUAL_MARK_ONLY),
        "assets_base": PUBLIC_BASE_URL,
        "step_labels": lesson_step_labels_payload(),
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
    if not verify_test_lesson_key(test_key) and percent < VIDEO_WATCH_THRESHOLD:
        raise HTTPException(400, f"Нужно досмотреть минимум {int(VIDEO_WATCH_THRESHOLD * 100)}%")

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
        "message": "Урок засчитан" if status == "accepted" else "Уже было засчитано ранее",
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
    if not repo.child_has_lesson_complete(db, child_id, tale_title=lesson["title"]):
        raise HTTPException(400, "Сначала нужно досмотреть видео-урок по сказке.")

    tale_slug = lesson.get("tale_slug") or slug
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
