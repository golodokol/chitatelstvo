"""Единая точка создания событий обучения."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.orm import Session

from db import repository as repo
from job_queue.redis_queue import enqueue


def submit_learning_event(
    db: Session,
    *,
    child_id: uuid.UUID,
    event_type: str,
    tale_title: str,
    lesson_date: date | None = None,
    notes: str | None = None,
    payload: dict | None = None,
) -> tuple[str, uuid.UUID | None]:
    """
    Создаёт событие и ставит в очередь.
    Возвращает (status, event_id): accepted | duplicate.
    """
    event, created = repo.create_event(
        db,
        child_id=child_id,
        event_type=event_type,
        tale_title=tale_title,
        lesson_date=lesson_date,
        notes=notes,
        payload=payload or {},
    )
    if not created:
        return "duplicate", event.id

    enqueue("process_event", {"event_id": str(event.id)})
    return "accepted", event.id
