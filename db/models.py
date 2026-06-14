from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, SmallInteger, Text, func
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

    children: Mapped[list[Child]] = relationship(back_populates="family")


class Child(Base):
    __tablename__ = "children"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("families.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    age: Mapped[int | None] = mapped_column(SmallInteger)
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
