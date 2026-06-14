from __future__ import annotations

import secrets
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from db.models import Child, ChildBadge, Enrollment, Event, Family, ParentNotification, Reward
from gamification.engine import GamificationResponse


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def make_progress_token() -> str:
    return secrets.token_urlsafe(32)


def make_idempotency_key(
    child_id: uuid.UUID,
    event_type: str,
    tale_title: str | None,
    lesson_date: date | None,
) -> str:
    tale = (tale_title or "").strip().lower()
    day = lesson_date.isoformat() if lesson_date else "none"
    return f"{child_id}:{event_type}:{tale}:{day}"


def register_family(
    db: Session,
    *,
    parent_name: str,
    parent_email: str,
    parent_telegram: str | None,
    notification_channel: str,
    child_name: str,
    child_age: int | None,
    telegram_chat_id: int | None = None,
) -> tuple[Family, Child]:
    family = Family(
        parent_name=parent_name.strip(),
        parent_email=parent_email.strip().lower(),
        parent_telegram=(parent_telegram or "").strip() or None,
        telegram_chat_id=telegram_chat_id,
        notification_channel=notification_channel,
        progress_token=make_progress_token(),
    )
    db.add(family)
    db.flush()

    child = Child(
        family_id=family.id,
        name=child_name.strip(),
        age=child_age,
    )
    db.add(child)
    db.commit()
    db.refresh(family)
    db.refresh(child)
    return family, child


def create_enrollment(
    db: Session,
    *,
    child_id: uuid.UUID,
    module_id: int,
    chosen_stage: str | None = None,
    chosen_tale_number: int | None = None,
    chosen_tale_slug: str | None = None,
    chosen_tale_title: str | None = None,
    start_date: date | None = None,
) -> Enrollment:
    enrollment = Enrollment(
        child_id=child_id,
        module_id=module_id,
        status="active",
        start_date=start_date,
        chosen_stage=chosen_stage,
        chosen_tale_number=chosen_tale_number,
        chosen_tale_slug=chosen_tale_slug,
        chosen_tale_title=chosen_tale_title,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def get_active_enrollment(db: Session, child_id: uuid.UUID) -> Enrollment | None:
    stmt = (
        select(Enrollment)
        .where(Enrollment.child_id == child_id, Enrollment.status == "active")
        .order_by(Enrollment.created_at.desc())
    )
    return db.scalars(stmt).first()


def find_child(
    db: Session,
    *,
    child_id: uuid.UUID | None = None,
    child_name: str | None = None,
    parent_email: str | None = None,
) -> Child | None:
    if child_id:
        return get_child_with_family(db, child_id)

    if child_name and parent_email:
        stmt = (
            select(Child)
            .join(Family)
            .where(
                Child.name.ilike(child_name.strip()),
                Family.parent_email == parent_email.strip().lower(),
            )
            .options(
                joinedload(Child.family),
                joinedload(Child.badges),
                joinedload(Child.enrollments),
            )
        )
        return db.scalars(stmt).first()

    if child_name:
        stmt = (
            select(Child)
            .where(Child.name.ilike(child_name.strip()))
            .options(
                joinedload(Child.family),
                joinedload(Child.badges),
                joinedload(Child.enrollments),
            )
        )
        return db.scalars(stmt).first()

    return None


def get_child_with_family(db: Session, child_id: uuid.UUID) -> Child | None:
    stmt = (
        select(Child)
        .where(Child.id == child_id)
        .options(
            joinedload(Child.family),
            joinedload(Child.badges),
            joinedload(Child.enrollments),
        )
    )
    return db.scalars(stmt).first()


def get_event_by_idempotency(db: Session, key: str) -> Event | None:
    return db.scalars(select(Event).where(Event.idempotency_key == key)).first()


def create_event(
    db: Session,
    *,
    child_id: uuid.UUID,
    event_type: str,
    tale_title: str | None,
    lesson_date: date | None,
    notes: str | None,
    payload: dict,
) -> Event:
    key = make_idempotency_key(child_id, event_type, tale_title, lesson_date)
    existing = get_event_by_idempotency(db, key)
    if existing:
        return existing

    event = Event(
        idempotency_key=key,
        child_id=child_id,
        event_type=event_type,
        tale_title=tale_title,
        lesson_date=lesson_date,
        notes=notes,
        payload=payload,
        status="pending",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def mark_event_processing(db: Session, event_id: uuid.UUID) -> Event | None:
    event = db.get(Event, event_id)
    if not event:
        return None
    if event.status in ("done", "processing"):
        return None
    event.status = "processing"
    db.commit()
    db.refresh(event)
    return event


def save_reward_and_update_child(
    db: Session,
    event: Event,
    child: Child,
    reward: GamificationResponse,
) -> Reward:
    db.add(
        Reward(
            event_id=event.id,
            reward_type=reward.reward_type,
            points=reward.points,
            badge_name=reward.badge_name,
            level_change=reward.level_change,
            child_message=reward.child_message,
            parent_message=reward.parent_message,
            next_action=reward.next_action,
            source=reward.source,
        )
    )

    if reward.points:
        child.total_points += reward.points
        child.streak_count += 1

    if reward.level_change:
        child.current_level = reward.level_change

    if reward.badge_name:
        exists = db.get(ChildBadge, {"child_id": child.id, "badge_name": reward.badge_name})
        if not exists:
            db.add(ChildBadge(child_id=child.id, badge_name=reward.badge_name))

    event.status = "done"
    event.processed_at = _utcnow()
    db.commit()
    db.refresh(event)
    return db.get(Reward, event.id)  # type: ignore[return-value]


def mark_event_failed(db: Session, event_id: uuid.UUID, error: str) -> None:
    event = db.get(Event, event_id)
    if event:
        event.status = "failed"
        event.error_message = error[:2000]
        event.processed_at = _utcnow()
        db.commit()


def store_notification(
    db: Session,
    *,
    family_id: uuid.UUID,
    child_id: uuid.UUID,
    event_id: uuid.UUID | None,
    channel: str,
    message: str,
    status: str = "pending",
) -> ParentNotification:
    note = ParentNotification(
        family_id=family_id,
        child_id=child_id,
        event_id=event_id,
        channel=channel,
        message=message,
        status=status,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def mark_notification_sent(db: Session, note_id: uuid.UUID) -> None:
    note = db.get(ParentNotification, note_id)
    if note:
        note.status = "sent"
        note.sent_at = _utcnow()
        db.commit()


def mark_notification_failed(db: Session, note_id: uuid.UUID, error: str) -> None:
    note = db.get(ParentNotification, note_id)
    if note:
        note.status = "failed"
        note.error_message = error[:1000]
        db.commit()


def link_telegram_chat(
    db: Session,
    *,
    progress_token: str,
    chat_id: int,
    username: str | None = None,
) -> Family | None:
    family = db.scalars(select(Family).where(Family.progress_token == progress_token)).first()
    if not family:
        return None

    family.telegram_chat_id = chat_id
    if username:
        handle = username if username.startswith("@") else f"@{username}"
        family.parent_telegram = handle

    if family.notification_channel == "email":
        family.notification_channel = "both"
    elif family.notification_channel == "web":
        family.notification_channel = "telegram"

    db.commit()
    db.refresh(family)
    return family


def get_family_by_token(db: Session, token: str) -> Family | None:
    stmt = (
        select(Family)
        .where(Family.progress_token == token)
        .options(
            joinedload(Family.children).joinedload(Child.badges),
            joinedload(Family.children).joinedload(Child.enrollments),
        )
    )
    return db.scalars(stmt).first()


def get_family_notifications(db: Session, family_id: uuid.UUID, limit: int = 50) -> list[ParentNotification]:
    stmt = (
        select(ParentNotification)
        .where(ParentNotification.family_id == family_id)
        .order_by(ParentNotification.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def get_child_events(db: Session, child_id: uuid.UUID, limit: int = 30) -> list[Event]:
    stmt = (
        select(Event)
        .where(Event.child_id == child_id, Event.status == "done")
        .order_by(Event.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())
