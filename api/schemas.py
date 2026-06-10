from __future__ import annotations

import uuid
from datetime import date
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

EventType = Literal[
    "first_task",
    "lesson_complete",
    "comprehension",
    "meaning_analysis",
    "creative_task",
    "retelling",
    "mini_check",
    "live_meeting",
    "initiative",
    "streak_3",
    "streak_5",
    "module_complete",
]

NotificationChannel = Literal["email", "telegram", "both", "web"]

_CHANNEL_ALIASES = {
    "email": "email",
    "telegram": "telegram",
    "telegram bot": "telegram",
    "both": "both",
    "web": "web",
    "max": "web",
}

_REGISTER_FIELDS = frozenset(
    {
        "parent_name",
        "parent_email",
        "parent_telegram",
        "telegram_chat_id",
        "notification_channel",
        "child_name",
        "child_age",
    }
)


class RegisterWebhook(BaseModel):
    parent_name: str = Field(min_length=1, max_length=200)
    parent_email: EmailStr
    parent_telegram: str | None = Field(default=None, max_length=100)
    telegram_chat_id: int | None = None
    notification_channel: NotificationChannel = "email"
    child_name: str = Field(min_length=1, max_length=100)
    child_age: int | None = Field(default=None, ge=5, le=14)

    @model_validator(mode="before")
    @classmethod
    def normalize_tilda_keys(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        tilda_aliases = {
            "name": "parent_name",
            "email": "parent_email",
            "phone": "parent_telegram",
            "selectbox": "notification_channel",
            "select": "notification_channel",
        }
        out: dict = {}
        for key, value in data.items():
            lk = str(key).lower()
            if lk in _REGISTER_FIELDS:
                out[lk] = value
            elif lk in tilda_aliases:
                out[tilda_aliases[lk]] = value
            else:
                out[key] = value
        return out

    @field_validator("notification_channel", mode="before")
    @classmethod
    def normalize_channel(cls, value: object) -> object:
        if value is None or value == "":
            return "email"
        key = str(value).strip().lower()
        return _CHANNEL_ALIASES.get(key, key)


class EventWebhook(BaseModel):
    event_type: EventType
    child_id: uuid.UUID | None = None
    child_name: str | None = Field(default=None, max_length=100)
    parent_email: EmailStr | None = None
    tale_title: str | None = Field(default=None, max_length=200)
    lesson_date: date | None = None
    module_week: int | None = Field(default=None, ge=1, le=12)
    notes: str | None = Field(default=None, max_length=2000)


class WebhookAccepted(BaseModel):
    status: Literal["accepted", "duplicate"] = "accepted"
    event_id: uuid.UUID | None = None
    job_id: str | None = None
    message: str = "Событие принято в обработку"


class RegisterResponse(BaseModel):
    family_id: uuid.UUID
    child_id: uuid.UUID
    progress_url: str
    link_telegram_page: str
    telegram_deep_link: str | None = None
    notification_channel: str
