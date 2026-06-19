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
        "module_id",
        "chosen_stage",
        "chosen_tale_number",
        "promo_code",
    }
)


class RegisterWebhook(BaseModel):
    parent_name: str = Field(min_length=1, max_length=200)
    parent_email: EmailStr
    parent_telegram: str | None = Field(default=None, max_length=100)
    telegram_chat_id: int | None = None
    notification_channel: NotificationChannel = "email"
    child_name: str = Field(min_length=1, max_length=100)
    child_age: int | None = Field(default=None)
    module_id: int | None = Field(default=None, ge=1, le=18)
    chosen_stage: str | None = Field(default=None, max_length=50)
    chosen_tale_number: int | None = Field(default=None, ge=1, le=4)
    promo_code: str | None = Field(default=None, max_length=50)

    @model_validator(mode="before")
    @classmethod
    def normalize_tilda_keys(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        tilda_aliases = {
            "name": "parent_name",
            "email": "parent_email",
            "phone": "parent_telegram",
            "telegram": "parent_telegram",
            "selectbox": "notification_channel",
            "select": "notification_channel",
            "module": "module_id",
            "module_id": "module_id",
            "tariff": "module_id",
            "stage": "chosen_stage",
            "chosen_stage": "chosen_stage",
            "tale_number": "chosen_tale_number",
            "chosen_tale_number": "chosen_tale_number",
            "tale": "chosen_tale_number",
            "child": "child_name",
            "age": "child_age",
            "promocode": "promo_code",
            "promo": "promo_code",
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

    @field_validator("module_id", "chosen_tale_number", "child_age", mode="before")
    @classmethod
    def coerce_optional_int(cls, value: object) -> object:
        if value is None or value == "":
            return None
        return int(value)

    @field_validator("chosen_stage", mode="before")
    @classmethod
    def normalize_stage(cls, value: object) -> object:
        if value is None or value == "":
            return None
        raw = str(value).strip().lower()
        if raw in ("1", "stage-1", "stage_1", "june", "22", "22.06", "22 июня"):
            return "1"
        if raw in ("2", "stage-2", "stage_2", "july", "20", "20.07", "20 июля"):
            return "2"
        if "22" in raw and "июн" in raw:
            return "1"
        if "20" in raw and "июл" in raw:
            return "2"
        return str(value).strip()

    @field_validator("promo_code", mode="before")
    @classmethod
    def normalize_promo_code(cls, value: object) -> object:
        if value is None or value == "":
            return None
        code = str(value).strip()
        return code or None


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
    module_id: int | None = None
    module_title: str | None = None
    is_returning: bool = False


class OtpRequestBody(BaseModel):
    email: EmailStr


class OtpRequestResponse(BaseModel):
    status: Literal["sent"] = "sent"
    message: str = "Если этот email зарегистрирован, код отправлен на почту."


class AuthChildSummary(BaseModel):
    id: uuid.UUID
    name: str
    age: int | None = None
    level: str
    points: int
    family_id: uuid.UUID


class OtpVerifyBody(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=8)


class OtpVerifyResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    family_id: uuid.UUID
    parent_name: str
    progress_url: str
    children: list[AuthChildSummary]


class AuthMeResponse(BaseModel):
    email: str
    family_id: uuid.UUID
    parent_name: str
    progress_url: str
    children: list[AuthChildSummary]
