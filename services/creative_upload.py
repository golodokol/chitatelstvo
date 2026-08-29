"""Загрузка выполненных творческих заданий и начисление бейджа «Сказочник»."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile

from config.settings import ROOT
from db import repository as repo
from services.events import submit_learning_event
from services.lesson_player import prepare_lesson_for_child

CREATIVE_UPLOAD_ROOT = ROOT / "data" / "creative_uploads"
MAX_FILES = 5
MAX_FILE_BYTES = 12 * 1024 * 1024
ALLOWED_SUFFIXES = frozenset({".pdf", ".jpg", ".jpeg", ".png", ".webp"})
_SAFE_NAME = re.compile(r"[^a-zA-Z0-9._-]+")


def _safe_filename(name: str) -> str:
    base = Path(name or "file").name
    stem = Path(base).stem[:80] or "file"
    suffix = Path(base).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        suffix = ""
    cleaned = _SAFE_NAME.sub("_", stem).strip("._") or "file"
    return f"{cleaned}{suffix}"


def _lesson_prerequisite_met(db, child_id: uuid.UUID, tale_title: str, lesson: dict) -> bool:
    if lesson.get("meaning_quiz"):
        return repo.child_has_learning_event(
            db, child_id, tale_title=tale_title, event_type="meaning_analysis"
        )
    if lesson.get("comprehension_quiz"):
        return repo.child_has_learning_event(
            db, child_id, tale_title=tale_title, event_type="comprehension"
        )
    return repo.child_has_lesson_complete(db, child_id, tale_title=tale_title)


async def handle_creative_upload(
    db,
    *,
    child_id: uuid.UUID,
    slug: str,
    files: list[UploadFile],
    test_key: str | None = None,
    enrollment_id: uuid.UUID | str | None = None,
) -> dict[str, Any]:
    from api.test_lesson_auth import verify_test_lesson_key

    if not files:
        raise HTTPException(400, "Выберите хотя бы один файл (фото или PDF).")

    if len(files) > MAX_FILES:
        raise HTTPException(400, f"Можно загрузить не больше {MAX_FILES} файлов за раз.")

    _, lesson = prepare_lesson_for_child(
        db,
        child_id,
        slug,
        bypass=verify_test_lesson_key(test_key),
        enrollment_id=enrollment_id,
    )
    tale_title = lesson["title"]
    tale_slug = lesson.get("tale_slug") or slug

    if not lesson.get("creative_tasks"):
        raise HTTPException(404, "Творческие задания для этого урока не настроены.")

    already_done = repo.child_has_learning_event(
        db, child_id, tale_title=tale_title, event_type="creative_task"
    )

    if not already_done and not _lesson_prerequisite_met(db, child_id, tale_title, lesson):
        raise HTTPException(
            400,
            "Сначала завершите задания урока выше, затем загрузите выполненные творческие работы.",
        )

    dest_dir = CREATIVE_UPLOAD_ROOT / str(child_id) / tale_slug
    dest_dir.mkdir(parents=True, exist_ok=True)

    saved: list[dict[str, Any]] = []
    for upload in files:
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise HTTPException(
                400,
                "Поддерживаются только фото (JPG, PNG, WEBP) и PDF.",
            )
        data = await upload.read()
        if not data:
            raise HTTPException(400, "Один из файлов пустой.")
        if len(data) > MAX_FILE_BYTES:
            raise HTTPException(400, "Каждый файл — не больше 12 МБ.")

        safe = _safe_filename(upload.filename or "file")
        unique = f"{uuid.uuid4().hex[:10]}_{safe}"
        path = dest_dir / unique
        path.write_bytes(data)
        saved.append(
            {
                "original_name": upload.filename or safe,
                "stored_name": unique,
                "relative_path": f"{child_id}/{tale_slug}/{unique}",
                "size": len(data),
                "content_type": upload.content_type or "",
            }
        )

    if already_done:
        return {
            "status": "duplicate",
            "files_saved": len(saved),
            "message": (
                f"Файлы сохранены ({len(saved)}). "
                "Творческие задания уже были отправлены ранее — бейдж «Сказочник» получен."
            ),
        }

    status, event_id = submit_learning_event(
        db,
        child_id=child_id,
        event_type="creative_task",
        tale_title=tale_title,
        lesson_date=None,
        notes="auto: creative upload",
        payload={
            "source": "lesson_creative_upload",
            "tale_slug": tale_slug,
            "files": saved,
        },
    )
    return {
        "status": status,
        "event_id": str(event_id) if event_id else None,
        "files_saved": len(saved),
        "message": (
            "Загружено! Бейдж «Сказочник» и +3 Словика начисляются."
            if status == "accepted"
            else (
                f"Файлы сохранены ({len(saved)}). "
                "Творческие задания уже были отправлены ранее — бейдж «Сказочник» получен."
            )
        ),
    }
