from __future__ import annotations

import secrets
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import delete as sa_delete, select
from sqlalchemy.orm import Session, joinedload

from db.models import ChestClaim, Child, ChildBadge, Enrollment, Event, Family, ParentNotification, Reward, TaleRating
from gamification.engine import GamificationResponse
from gamification.rules import level_from_points


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


def find_family_by_email(db: Session, email: str) -> Family | None:
    stmt = (
        select(Family)
        .where(Family.parent_email == email.strip().lower())
        .options(
            joinedload(Family.children).joinedload(Child.badges),
            joinedload(Family.children).joinedload(Child.enrollments),
        )
    )
    return db.scalars(stmt).first()


def list_families_by_email(db: Session, email: str) -> list[Family]:
    stmt = (
        select(Family)
        .where(Family.parent_email == email.strip().lower())
        .options(
            joinedload(Family.children).joinedload(Child.badges),
            joinedload(Family.children).joinedload(Child.enrollments),
        )
        .order_by(Family.created_at.desc())
    )
    return list(db.scalars(stmt).unique().all())


def get_primary_family_for_email(db: Session, email: str) -> Family | None:
    families = list_families_by_email(db, email)
    return families[0] if families else None


def get_family_by_id(db: Session, family_id: uuid.UUID) -> Family | None:
    stmt = (
        select(Family)
        .where(Family.id == family_id)
        .options(
            joinedload(Family.children).joinedload(Child.badges),
            joinedload(Family.children).joinedload(Child.enrollments),
        )
    )
    return db.scalars(stmt).unique().first()


def list_children_by_parent_email(db: Session, email: str) -> list[Child]:
    stmt = (
        select(Child)
        .join(Family)
        .where(Family.parent_email == email.strip().lower())
        .options(joinedload(Child.family))
        .order_by(Child.name.asc())
    )
    return list(db.scalars(stmt).unique().all())


def list_children_for_family(db: Session, family_id: uuid.UUID) -> list[Child]:
    stmt = (
        select(Child)
        .where(Child.family_id == family_id)
        .order_by(Child.name.asc(), Child.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def _update_family_on_reregister(
    family: Family,
    *,
    parent_name: str,
    parent_telegram: str | None,
    notification_channel: str,
    telegram_chat_id: int | None,
) -> None:
    family.parent_name = parent_name.strip()
    family.notification_channel = notification_channel
    if parent_telegram is not None:
        tg = parent_telegram.strip()
        family.parent_telegram = tg or None
    if telegram_chat_id is not None:
        family.telegram_chat_id = telegram_chat_id


def resolve_or_create_family_child(
    db: Session,
    *,
    parent_name: str,
    parent_email: str,
    parent_telegram: str | None,
    notification_channel: str,
    child_name: str,
    child_age: int | None,
    telegram_chat_id: int | None = None,
) -> tuple[Family, Child, bool]:
    """Найти или создать семью и ребёнка по parent_email + child_name.

    Возвращает (family, child, is_returning).
    is_returning=True — тот же ребёнок уже был в системе (ссылка и прогресс сохраняются).
    """
    email = parent_email.strip().lower()
    name = child_name.strip()

    existing_child = find_child(db, child_name=name, parent_email=email)
    if existing_child:
        family = existing_child.family
        _update_family_on_reregister(
            family,
            parent_name=parent_name,
            parent_telegram=parent_telegram,
            notification_channel=notification_channel,
            telegram_chat_id=telegram_chat_id,
        )
        if child_age is not None:
            existing_child.age = child_age
        db.commit()
        db.refresh(family)
        db.refresh(existing_child)
        return family, existing_child, True

    family = find_family_by_email(db, email)
    if family:
        _update_family_on_reregister(
            family,
            parent_name=parent_name,
            parent_telegram=parent_telegram,
            notification_channel=notification_channel,
            telegram_chat_id=telegram_chat_id,
        )
        child = Child(
            family_id=family.id,
            name=name,
            age=child_age,
        )
        db.add(child)
        db.commit()
        db.refresh(family)
        db.refresh(child)
        return family, child, False

    family, child = register_family(
        db,
        parent_name=parent_name,
        parent_email=email,
        parent_telegram=parent_telegram,
        notification_channel=notification_channel,
        child_name=name,
        child_age=child_age,
        telegram_chat_id=telegram_chat_id,
    )
    return family, child, False


def complete_active_enrollments(
    db: Session,
    child_id: uuid.UUID,
    *,
    group_code: str | None = None,
) -> int:
    """Закрыть активные записи перед новой покупкой в том же направлении (group_code)."""
    from catalog.loader import get_module

    stmt = select(Enrollment).where(
        Enrollment.child_id == child_id,
        Enrollment.status == "active",
    )
    enrollments = list(db.scalars(stmt).all())
    closed = 0
    for enrollment in enrollments:
        if group_code is not None:
            mod = get_module(enrollment.module_id)
            if not mod or mod["group_code"] != group_code:
                continue
        enrollment.status = "completed"
        closed += 1
    if closed:
        db.commit()
    return closed


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

    child.current_level = level_from_points(child.total_points)

    if reward.badge_name:
        exists = db.get(ChildBadge, {"child_id": child.id, "badge_name": reward.badge_name})
        if not exists:
            db.add(ChildBadge(child_id=child.id, badge_name=reward.badge_name))

    event.status = "done"
    event.processed_at = _utcnow()
    db.commit()
    db.refresh(event)
    return db.get(Reward, event.id)  # type: ignore[return-value]


def count_distinct_completed_tales(
    db: Session,
    child_id: uuid.UUID,
    *,
    extra_tale: str | None = None,
) -> int:
    """Сколько разных сказок ребёнок уже прошёл (lesson_complete)."""
    stmt = select(Event.tale_title).where(
        Event.child_id == child_id,
        Event.event_type == "lesson_complete",
        Event.status == "done",
    )
    tales = {(title or "").strip() for title in db.scalars(stmt).all() if (title or "").strip()}
    if extra_tale:
        extra = extra_tale.strip()
        if extra:
            tales.add(extra)
    return len(tales)


def grant_bonus_badge(
    db: Session,
    child: Child,
    *,
    badge_name: str,
    level_change: str | None = None,
) -> bool:
    """Выдаёт бонусный бейдж, если его ещё нет. Возвращает True, если добавлен."""
    exists = db.get(ChildBadge, {"child_id": child.id, "badge_name": badge_name})
    if exists:
        return False
    db.add(ChildBadge(child_id=child.id, badge_name=badge_name))
    child.current_level = level_from_points(child.total_points)
    db.commit()
    db.refresh(child)
    return True


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


def list_all_families(db: Session) -> list[Family]:
    stmt = (
        select(Family)
        .options(
            joinedload(Family.children).joinedload(Child.enrollments),
        )
        .order_by(Family.created_at.desc())
    )
    return list(db.scalars(stmt).unique().all())


def delete_family(db: Session, family_id: uuid.UUID) -> bool:
    """Удалить семью и все связанные записи (каскад в PostgreSQL)."""
    result = db.execute(sa_delete(Family).where(Family.id == family_id))
    if result.rowcount == 0:
        return False
    db.commit()
    return True


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


def child_has_lesson_complete(
    db: Session,
    child_id: uuid.UUID,
    *,
    tale_title: str,
) -> bool:
    title = tale_title.strip()
    if not title:
        return False
    stmt = (
        select(Event.id)
        .where(
            Event.child_id == child_id,
            Event.event_type == "lesson_complete",
            Event.tale_title == title,
            Event.status.in_(("done", "pending", "processing")),
        )
        .limit(1)
    )
    return db.scalar(stmt) is not None


def get_tale_rating(db: Session, child_id: uuid.UUID, tale_slug: str) -> TaleRating | None:
    stmt = select(TaleRating).where(
        TaleRating.child_id == child_id,
        TaleRating.tale_slug == tale_slug,
    )
    return db.scalars(stmt).first()


def get_child_tale_ratings(db: Session, child_id: uuid.UUID) -> list[TaleRating]:
    stmt = (
        select(TaleRating)
        .where(TaleRating.child_id == child_id)
        .order_by(TaleRating.rating.desc(), TaleRating.updated_at.desc())
    )
    return list(db.scalars(stmt).all())


def save_tale_rating(
    db: Session,
    *,
    child_id: uuid.UUID,
    tale_slug: str,
    tale_title: str,
    rating: int,
) -> TaleRating:
    row = get_tale_rating(db, child_id, tale_slug)
    now = _utcnow()
    if row:
        row.rating = rating
        row.tale_title = tale_title.strip() or row.tale_title
        row.updated_at = now
    else:
        row = TaleRating(
            child_id=child_id,
            tale_slug=tale_slug,
            tale_title=tale_title.strip() or None,
            rating=rating,
            updated_at=now,
        )
        db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_chest_claim(db: Session, child_id: uuid.UUID, tale_slug: str) -> ChestClaim | None:
    stmt = select(ChestClaim).where(
        ChestClaim.child_id == child_id,
        ChestClaim.tale_slug == tale_slug,
    )
    return db.scalars(stmt).first()


def get_child_chest_claims(db: Session, child_id: uuid.UUID) -> list[ChestClaim]:
    stmt = (
        select(ChestClaim)
        .where(ChestClaim.child_id == child_id)
        .order_by(ChestClaim.claimed_at.desc())
    )
    return list(db.scalars(stmt).all())


def save_chest_claim(
    db: Session,
    *,
    child_id: uuid.UUID,
    tale_slug: str,
    tale_title: str,
    module_week: int | None,
    items: list,
) -> ChestClaim:
    row = get_chest_claim(db, child_id, tale_slug)
    if row:
        return row
    row = ChestClaim(
        child_id=child_id,
        tale_slug=tale_slug,
        tale_title=tale_title.strip() or None,
        module_week=module_week,
        items=items,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
