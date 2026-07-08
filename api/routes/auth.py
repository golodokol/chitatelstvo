"""Вход по email + OTP → JWT + список детей."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from api.deps import get_current_family, rate_limit
from api.schemas import AuthChildSummary, AuthMeResponse, OtpRequestBody, OtpRequestResponse, OtpVerifyBody, OtpVerifyResponse
from config.settings import JWT_SECRET, PUBLIC_BASE_URL
from db import repository as repo
from db.child_age import child_age_years
from db.models import Child, Family
from db.session import get_db
from gamification.rules import level_from_points
from services.auth_jwt import create_access_token
from services.auth_otp import request_login_otp, verify_login_otp

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _child_summary(child: Child) -> AuthChildSummary:
    points = child.total_points or 0
    return AuthChildSummary(
        id=child.id,
        name=child.name,
        age=child_age_years(child),
        level=level_from_points(points),
        points=points,
        family_id=child.family_id,
    )


def _children_payload(children: list[Child]) -> list[AuthChildSummary]:
    return [_child_summary(child) for child in children]


def _progress_url(family: Family) -> str:
    return f"{PUBLIC_BASE_URL}/progress/{family.progress_token}"


@router.post("/otp/request", response_model=OtpRequestResponse)
def otp_request(
    body: OtpRequestBody,
    request: Request,
    db: Session = Depends(get_db),
) -> OtpRequestResponse:
    rate_limit(request)
    if not JWT_SECRET:
        raise HTTPException(503, "JWT_SECRET не настроен на сервере")

    try:
        request_login_otp(db, str(body.email))
    except ValueError as exc:
        if str(exc) == "rate_limit_send":
            raise HTTPException(429, "Слишком много запросов кода. Попробуйте позже.") from exc
        raise
    except RuntimeError as exc:
        if "SMTP" in str(exc):
            raise HTTPException(503, "Почта временно недоступна. Попробуйте позже.") from exc
        raise HTTPException(503, "Не удалось отправить код") from exc

    return OtpRequestResponse()


@router.post("/otp/verify", response_model=OtpVerifyResponse)
def otp_verify(
    body: OtpVerifyBody,
    request: Request,
    db: Session = Depends(get_db),
) -> OtpVerifyResponse:
    rate_limit(request)
    if not JWT_SECRET:
        raise HTTPException(503, "JWT_SECRET не настроен на сервере")

    try:
        family, children = verify_login_otp(db, str(body.email), body.code)
    except ValueError as exc:
        reason = str(exc)
        if reason == "rate_limit_verify":
            raise HTTPException(429, "Слишком много попыток. Запросите новый код.") from exc
        raise HTTPException(401, "Неверный код или код истёк") from exc

    if not children:
        raise HTTPException(404, "В семье пока нет детей")

    token, expires_in = create_access_token(family_id=family.id, email=family.parent_email)
    return OtpVerifyResponse(
        access_token=token,
        expires_in=expires_in,
        family_id=family.id,
        parent_name=family.parent_name,
        progress_url=_progress_url(family),
        children=_children_payload(children),
    )


@router.get("/me", response_model=AuthMeResponse)
def auth_me(
    family: Family = Depends(get_current_family),
    db: Session = Depends(get_db),
) -> AuthMeResponse:
    family = repo.get_family_by_id(db, family.id) or family
    children = repo.list_children_for_family(db, family.id)
    return AuthMeResponse(
        email=family.parent_email,
        family_id=family.id,
        parent_name=family.parent_name,
        progress_url=_progress_url(family),
        children=_children_payload(children),
    )
