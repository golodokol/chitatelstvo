from __future__ import annotations

import csv
import hmac
import io
import uuid
from datetime import datetime
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from api.admin_auth import (
    admin_enabled,
    clear_admin_cookie,
    is_admin,
    require_admin,
    set_admin_cookie,
)
from api.schemas import RegisterWebhook
from catalog.loader import get_module, load_modules
from config.settings import ADMIN_PASSWORD, PUBLIC_BASE_URL, ROOT
from db import repository as repo
from db.session import get_db
from lessons.enrollment_access import get_active_enrollment
from services.quiz_leads import build_quiz_lead_rows, load_quiz_leads
from services.registration import grant_enrollment_to_child, process_registration

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def _fmt_dt(value: datetime | None) -> str:
    if not value:
        return "—"
    return value.strftime("%d.%m.%Y %H:%M")


def _build_rows(families) -> list[dict]:
    rows: list[dict] = []
    for family in families:
        progress_url = f"{PUBLIC_BASE_URL}/progress/{family.progress_token}"
        if not family.children:
            rows.append(
                {
                    "registered_at": _fmt_dt(family.created_at),
                    "parent_name": family.parent_name,
                    "parent_email": family.parent_email,
                    "parent_telegram": family.parent_telegram or "—",
                    "channel": family.notification_channel,
                    "telegram_linked": "да" if family.telegram_chat_id else "нет",
                    "child_name": "—",
                    "child_age": "—",
                    "child_id": None,
                    "module": "—",
                    "stage": "—",
                    "tale": "—",
                    "level": "—",
                    "points": "—",
                    "progress_url": progress_url,
                }
            )
            continue

        for child in family.children:
            enrollment = get_active_enrollment(child)
            module_title = "—"
            stage = "—"
            tale = "—"
            if enrollment:
                module = get_module(enrollment.module_id)
                module_title = module["title"] if module else f"Модуль {enrollment.module_id}"
                stage = enrollment.chosen_stage or "—"
                if enrollment.chosen_tale_title:
                    tale = enrollment.chosen_tale_title
                elif enrollment.chosen_tale_number:
                    tale = f"№{enrollment.chosen_tale_number}"

            rows.append(
                {
                    "registered_at": _fmt_dt(family.created_at),
                    "parent_name": family.parent_name,
                    "parent_email": family.parent_email,
                    "parent_telegram": family.parent_telegram or "—",
                    "channel": family.notification_channel,
                    "telegram_linked": "да" if family.telegram_chat_id else "нет",
                    "child_name": child.name,
                    "child_age": str(child.age) if child.age is not None else "—",
                    "child_id": str(child.id),
                    "module": module_title,
                    "stage": stage,
                    "tale": tale,
                    "level": child.current_level,
                    "points": str(child.total_points),
                    "progress_url": progress_url,
                }
            )
    return rows


def _admin_modules() -> list[dict]:
    return sorted(load_modules(), key=lambda m: m["id"])


def _flash_from_query(request: Request) -> dict | None:
    params = request.query_params
    if params.get("enrolled") == "1":
        return {
            "type": "ok",
            "message": params.get("msg") or "Доступ выдан.",
            "progress_url": params.get("progress_url") or "",
        }
    if params.get("error"):
        return {
            "type": "error",
            "message": params.get("error"),
            "progress_url": "",
        }
    return None


def _redirect_admin_ok(progress_url: str, module_title: str | None) -> RedirectResponse:
    msg = f"Доступ выдан: {module_title or 'модуль'}."
    url = (
        "/admin?enrolled=1"
        f"&msg={quote(msg)}"
        f"&progress_url={quote(progress_url)}"
        "#enroll"
    )
    return RedirectResponse(url, status_code=303)


def _redirect_admin_error(message: str) -> RedirectResponse:
    return RedirectResponse(f"/admin?error={quote(message)}#enroll", status_code=303)


def _parse_child_age(raw: str | None) -> int | None:
    if raw is None or str(raw).strip() == "":
        return None
    return int(raw)


def _parse_tale_number(raw: str | None) -> int | None:
    if raw is None or str(raw).strip() == "":
        return None
    return int(raw)


@router.get("", response_class=HTMLResponse)
def admin_page(
    request: Request,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    if not admin_enabled():
        raise HTTPException(503, "Админ-панель не настроена: задайте ADMIN_PASSWORD в .env")

    if not is_admin(request):
        return templates.TemplateResponse(
            request,
            "admin_login.html",
            {"error": None},
        )

    families = repo.list_all_families(db)
    rows = _build_rows(families)
    quiz_leads = load_quiz_leads()
    quiz_rows = build_quiz_lead_rows(quiz_leads)
    return templates.TemplateResponse(
        request,
        "admin.html",
        {
            "rows": rows,
            "family_count": len(families),
            "child_count": sum(len(f.children) for f in families),
            "quiz_rows": quiz_rows,
            "quiz_count": len(quiz_rows),
            "modules": _admin_modules(),
            "flash": _flash_from_query(request),
        },
    )


@router.get("/login")
def admin_login_page() -> RedirectResponse:
    return RedirectResponse("/admin", status_code=302)


@router.post("/login")
def admin_login(
    request: Request,
    password: str = Form(...),
) -> RedirectResponse:
    if not admin_enabled():
        raise HTTPException(503, "Админ-панель не настроена")

    if not hmac.compare_digest(password, ADMIN_PASSWORD):
        return templates.TemplateResponse(
            request,
            "admin_login.html",
            {"error": "Неверный пароль"},
            status_code=401,
        )

    response = RedirectResponse("/admin", status_code=303)
    set_admin_cookie(response, request)
    return response


@router.post("/logout")
def admin_logout() -> RedirectResponse:
    response = RedirectResponse("/admin", status_code=303)
    clear_admin_cookie(response)
    return response


@router.post("/enroll")
def admin_enroll_new(
    request: Request,
    db: Session = Depends(get_db),
    parent_name: str = Form(...),
    parent_email: str = Form(...),
    parent_telegram: str = Form(default=""),
    child_name: str = Form(...),
    child_age: str = Form(default=""),
    notification_channel: str = Form(default="email"),
    module_id: int = Form(...),
    chosen_stage: str = Form(...),
    chosen_tale_number: str = Form(default=""),
    send_email: str | None = Form(default=None),
):
    require_admin(request)
    try:
        body = RegisterWebhook(
            parent_name=parent_name.strip(),
            parent_email=parent_email.strip(),
            parent_telegram=parent_telegram.strip() or None,
            child_name=child_name.strip(),
            child_age=_parse_child_age(child_age),
            notification_channel=notification_channel.strip() or "email",
            module_id=module_id,
            chosen_stage=chosen_stage.strip(),
            chosen_tale_number=_parse_tale_number(chosen_tale_number),
        )
        result = process_registration(
            db,
            body,
            send_email=send_email == "on",
            log_source="admin",
        )
    except (ValidationError, ValueError) as exc:
        return _redirect_admin_error(str(exc))
    except HTTPException as exc:
        return _redirect_admin_error(str(exc.detail))

    return _redirect_admin_ok(result.progress_url, result.module_title)


@router.post("/enroll/{child_id}")
def admin_enroll_grant(
    request: Request,
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    module_id: int = Form(...),
    chosen_stage: str = Form(...),
    chosen_tale_number: str = Form(default=""),
    send_email: str | None = Form(default=None),
):
    require_admin(request)
    try:
        result = grant_enrollment_to_child(
            db,
            child_id,
            module_id=module_id,
            chosen_stage=chosen_stage.strip(),
            chosen_tale_number=_parse_tale_number(chosen_tale_number),
            send_email=send_email == "on",
        )
    except (ValidationError, ValueError) as exc:
        return _redirect_admin_error(str(exc))
    except HTTPException as exc:
        return _redirect_admin_error(str(exc.detail))

    return _redirect_admin_ok(result.progress_url, result.module_title)


@router.get("/export.csv")
def admin_export_csv(
    request: Request,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    require_admin(request)

    families = repo.list_all_families(db)
    rows = _build_rows(families)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Дата регистрации",
            "Родитель",
            "Email",
            "Telegram",
            "Канал",
            "TG привязан",
            "Ребёнок",
            "Возраст",
            "Модуль",
            "Этап",
            "Сказка",
            "Уровень",
            "Баллы",
            "Ссылка прогресса",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row["registered_at"],
                row["parent_name"],
                row["parent_email"],
                row["parent_telegram"],
                row["channel"],
                row["telegram_linked"],
                row["child_name"],
                row["child_age"],
                row["module"],
                row["stage"],
                row["tale"],
                row["level"],
                row["points"],
                row["progress_url"],
            ]
        )

    buffer.seek(0)
    filename = f"registrations_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/quiz-export.csv")
def admin_quiz_export_csv(request: Request) -> StreamingResponse:
    require_admin(request)

    quiz_rows = build_quiz_lead_rows()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "Дата",
            "Родитель",
            "Email",
            "Телефон",
            "Ребёнок",
            "Возраст",
            "Ответы квиза",
        ]
    )
    for row in quiz_rows:
        writer.writerow(
            [
                row["created_at"],
                row["parent_name"],
                row["parent_email"],
                row["phone"],
                row["child_name"],
                row["child_age"],
                row["answers_text"].replace("\n", " | "),
            ]
        )

    buffer.seek(0)
    filename = f"quiz_leads_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
