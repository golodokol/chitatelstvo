from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, ForeignKey, Integer, SmallInteger, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Family(Base):
    __tablename__ = "families"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_name: Mapped[str] = mapped_column(Text, nullable=False)
    parent_email: Mapped[str] = mapped_column(Text, nullable=False)
    parent_telegram: Mapped[str | None] = mapped_column(Text)
    telegram_chat_id: Mapped[int | None] = mapped_column(BigInteger)
    notification_channel: Mapped[str] = mapped_column(Text, nullable=False, default="email")
    progress_token: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    children: Mapped[list[Child]] = relationship(
        back_populates="family",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Child(Base):
    __tablename__ = "children"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("families.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    age: Mapped[int | None] = mapped_column(SmallInteger)
    birth_date: Mapped[date | None] = mapped_column(Date)
    birthday_gift_year: Mapped[int | None] = mapped_column(SmallInteger)
    bonus_unlock_weeks: Mapped[int] = mapped_column(SmallInteger, default=0)
    current_level: Mapped[str] = mapped_column(Text, default="Старт")
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    module_week: Mapped[int] = mapped_column(SmallInteger, default=1)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    family: Mapped[Family] = relationship(back_populates="children")
    badges: Mapped[list[ChildBadge]] = relationship(back_populates="child")
    enrollments: Mapped[list[Enrollment]] = relationship(back_populates="child")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"))
    module_id: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    start_date: Mapped[date | None] = mapped_column(Date)
    chosen_stage: Mapped[str | None] = mapped_column(Text)
    chosen_tale_number: Mapped[int | None] = mapped_column(SmallInteger)
    chosen_tale_slug: Mapped[str | None] = mapped_column(Text)
    chosen_tale_title: Mapped[str | None] = mapped_column(Text)
    promo_code: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    child: Mapped[Child] = relationship(back_populates="enrollments")


class ChildBadge(Base):
    __tablename__ = "child_badges"

    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), primary_key=True)
    badge_name: Mapped[str] = mapped_column(Text, primary_key=True)
    earned_at: Mapped[datetime] = mapped_column(server_default=func.now())

    child: Mapped[Child] = relationship(back_populates="badges")


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idempotency_key: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    tale_title: Mapped[str | None] = mapped_column(Text)
    lesson_date: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(Text, default="pending")
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column()

    reward: Mapped[Reward | None] = relationship(back_populates="event")


class Reward(Base):
    __tablename__ = "rewards"

    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    reward_type: Mapped[str | None] = mapped_column(Text)
    points: Mapped[int] = mapped_column(Integer, default=0)
    badge_name: Mapped[str | None] = mapped_column(Text)
    level_change: Mapped[str | None] = mapped_column(Text)
    child_message: Mapped[str] = mapped_column(Text)
    parent_message: Mapped[str] = mapped_column(Text)
    next_action: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(Text, default="rules")

    event: Mapped[Event] = relationship(back_populates="reward")


class ParentNotification(Base):
    __tablename__ = "parent_notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("families.id", ondelete="CASCADE"))
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"))
    event_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"))
    channel: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="pending")
    message: Mapped[str] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    sent_at: Mapped[datetime | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ChestClaim(Base):
    __tablename__ = "chest_claims"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"))
    tale_slug: Mapped[str] = mapped_column(Text, nullable=False)
    tale_title: Mapped[str | None] = mapped_column(Text)
    module_week: Mapped[int | None] = mapped_column(SmallInteger)
    items: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    claimed_at: Mapped[datetime] = mapped_column(server_default=func.now())


class TaleRating(Base):
    __tablename__ = "tale_ratings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"))
    tale_slug: Mapped[str] = mapped_column(Text, nullable=False)
    tale_title: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class ExpeditionProfile(Base):
    """Профиль ребёнка внутри Читательской экспедиции (не LMS-кабинет)."""

    __tablename__ = "expedition_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), unique=True)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("families.id", ondelete="CASCADE"))
    nickname: Mapped[str | None] = mapped_column(Text)
    avatar: Mapped[str] = mapped_column(Text, default="compass")
    started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    level: Mapped[str] = mapped_column(Text, default="Старт")
    payload: Mapped[dict | None] = mapped_column(JSONB)


class ExpeditionPassport(Base):
    __tablename__ = "expedition_passports"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("expedition_profiles.id", ondelete="CASCADE"), primary_key=True
    )
    favorite_story: Mapped[str | None] = mapped_column(Text)
    favorite_hero: Mapped[str | None] = mapped_column(Text)
    last_work: Mapped[str | None] = mapped_column(Text)
    next_stop: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class UserStoryProgress(Base):
    __tablename__ = "expedition_story_progress"

    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), primary_key=True)
    story_slug: Mapped[str] = mapped_column(Text, primary_key=True)
    status: Mapped[str] = mapped_column(Text, default="open")
    creative: Mapped[str | None] = mapped_column(Text)
    completed_at: Mapped[datetime | None] = mapped_column()
    payload: Mapped[dict | None] = mapped_column(JSONB)


class UserRegionStamp(Base):
    __tablename__ = "expedition_region_stamps"

    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), primary_key=True)
    region_slug: Mapped[str] = mapped_column(Text, primary_key=True)
    stamp_level: Mapped[str] = mapped_column(Text, default="marker")
    poetic_title: Mapped[str | None] = mapped_column(Text)
    earned_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ExpeditionTariff(Base):
    __tablename__ = "expedition_tariffs"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    blurb: Mapped[str | None] = mapped_column(Text)
    price_rub: Mapped[int | None] = mapped_column(Integer)
    period_days: Mapped[int | None] = mapped_column(Integer)
    child_profiles: Mapped[int] = mapped_column(SmallInteger, default=1)
    features: Mapped[dict | None] = mapped_column(JSONB)
    audience: Mapped[str] = mapped_column(Text, default="parent")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class ExpeditionPurchase(Base):
    __tablename__ = "expedition_purchases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("families.id", ondelete="CASCADE"))
    tariff_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, default="pending")
    payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ExpeditionUserBadge(Base):
    __tablename__ = "expedition_user_badges"

    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), primary_key=True)
    badge_id: Mapped[str] = mapped_column(Text, primary_key=True)
    earned_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ExpeditionRouteProgress(Base):
    __tablename__ = "expedition_route_progress"

    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), primary_key=True)
    route_slug: Mapped[str] = mapped_column(Text, primary_key=True)
    step_index: Mapped[int] = mapped_column(SmallInteger, default=0)
    status: Mapped[str] = mapped_column(Text, default="open")
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class ExpeditionTaskAttempt(Base):
    __tablename__ = "expedition_task_attempts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    child_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"))
    story_slug: Mapped[str] = mapped_column(Text, nullable=False)
    option_id: Mapped[str | None] = mapped_column(Text)
    ok: Mapped[bool | None] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class ExpeditionSubscription(Base):
    __tablename__ = "expedition_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("families.id", ondelete="CASCADE"))
    tariff_id: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, default="active")
    starts_at: Mapped[datetime] = mapped_column(server_default=func.now())
    ends_at: Mapped[datetime | None] = mapped_column()
    payload: Mapped[dict | None] = mapped_column(JSONB)


class LibraryPartner(Base):
    __tablename__ = "expedition_library_partners"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str | None] = mapped_column(Text)
    region: Mapped[str | None] = mapped_column(Text)
    contact: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="new")
    payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class LibraryEvent(Base):
    __tablename__ = "expedition_library_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("expedition_library_partners.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    event_date: Mapped[date | None] = mapped_column(Date)
    payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class LibraryQRCode(Base):
    __tablename__ = "expedition_library_qr"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("expedition_library_partners.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    target_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
