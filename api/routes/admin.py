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
from db.child_age import child_age_years
from db import repository as repo
from db.session import get_db
from lessons.enrollment_access import get_active_enrollments, normalize_stage
from services.quiz_leads import build_quiz_lead_rows, load_quiz_leads
from services.meeting_attendance import mark_meeting_attendance, meeting_tale_options
from services.registration import grant_enrollment_to_child, process_registration

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))

_TARIFF_LABELS = {
    "single": "Разовое",
    "self_paced": "Индивидуальное",
    "with_teacher": "С преподавателем",
}

_GRADE_SHORT = {
    "1 класс": "1",
    "2 класс": "2",
    "3 класс": "3",
    "4 класс": "4",
    "Внеклассное чтение 6–8 лет": "6–8",
    "Внеклассное чтение 9–11 лет": "9–11",
}


def _short_grade_label(label: str | None) -> str:
    if not label or label == "—":
        return "—"
    return _GRADE_SHORT.get(label, label[:6])


def _format_stage_label(chosen_stage: str | None) -> str:
    stage = normalize_stage(chosen_stage)
    if stage == "stage-1":
        return "6 июля"
    if stage == "stage-2":
        return "27 июля"
    if not chosen_stage:
        return "—"
    return str(chosen_stage)


def _format_lesson_label(enrollment, module: dict | None) -> str:
    if not enrollment or not module:
        return "—"
    if module.get("tariff_code") == "single":
        if enrollment.chosen_tale_title:
            return enrollment.chosen_tale_title
        if enrollment.chosen_tale_number:
            return f"Сказка №{enrollment.chosen_tale_number}"
        return "—"
    count = module.get("tales_count") or 4
    return f"Блок · {count} сказки"


def _enrollment_columns(enrollment, module: dict | None) -> dict[str, str]:
    if not enrollment:
        return {
            "grade": "—",
            "grade_short": "—",
            "tariff": "—",
            "tariff_code": "",
            "stage": "—",
            "lesson": "—",
        }
    mod = module or get_module(enrollment.module_id)
    tariff_code = mod["tariff_code"] if mod else ""
    grade = mod["group_label"] if mod else "—"
    return {
        "grade": grade,
        "grade_short": _short_grade_label(grade),
        "tariff": _TARIFF_LABELS.get(tariff_code, mod["tariff_label"] if mod else "—"),
        "tariff_code": tariff_code,
        "stage": _format_stage_label(enrollment.chosen_stage),
        "lesson": _format_lesson_label(enrollment, mod),
    }


def _fmt_dt(value: datetime | None) -> str:
    if not value:
        return "—"
    return value.strftime("%d.%m.%Y %H:%M")


def _build_rows(families, db: Session) -> list[dict]:
    rows: list[dict] = []
    seen_families: set[str] = set()
    for family in families:
        progress_url = f"{PUBLIC_BASE_URL}/progress/{family.progress_token}"
        family_id = str(family.id)
        show_delete = family_id not in seen_families
        seen_families.add(family_id)
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
                    "family_id": family_id,
                    "show_delete": show_delete,
                    "grade": "—",
                    "grade_short": "—",
                    "tariff": "—",
                    "tariff_code": "",
                    "stage": "—",
                    "lesson": "—",
                    "promo_code": "—",
                    "level": "—",
                    "points": "—",
                    "progress_url": progress_url,
                    "meeting_tales": [],
                }
            )
            continue

        for child in family.children:
            enrollments = get_active_enrollments(child)
            if not enrollments:
                rows.append(
                    {
                        "registered_at": _fmt_dt(family.created_at),
                        "parent_name": family.parent_name,
                        "parent_email": family.parent_email,
                        "parent_telegram": family.parent_telegram or "—",
                        "channel": family.notification_channel,
                        "telegram_linked": "да" if family.telegram_chat_id else "нет",
                        "child_name": child.name,
                        "child_age": str(child_age_years(child)) if child_age_years(child) is not None else "—",
                        "child_id": str(child.id),
                        "family_id": family_id,
                        "show_delete": show_delete,
                        "grade": "—",
                        "grade_short": "—",
                        "tariff": "—",
                        "tariff_code": "",
                        "stage": "—",
                        "lesson": "—",
                        "promo_code": "—",
                        "level": child.current_level,
                        "points": str(child.total_points),
                        "progress_url": progress_url,
                        "meeting_tales": [],
                    }
                )
                show_delete = False
                continue

            for idx, enrollment in enumerate(enrollments):
                module = get_module(enrollment.module_id)
                cols = _enrollment_columns(enrollment, module)
                rows.append(
                    {
                        "registered_at": _fmt_dt(family.created_at),
                        "parent_name": family.parent_name,
                        "parent_email": family.parent_email,
                        "parent_telegram": family.parent_telegram or "—",
                        "channel": family.notification_channel,
                        "telegram_linked": "да" if family.telegram_chat_id else "нет",
                        "child_name": child.name,
                        "child_age": str(child_age_years(child)) if child_age_years(child) is not None else "—",
                        "child_id": str(child.id),
                        "family_id": family_id,
                        "show_delete": show_delete and idx == 0,
                        "grade": cols["grade"],
                        "grade_short": cols["grade_short"],
                        "tariff": cols["tariff"],
                        "tariff_code": cols["tariff_code"],
                        "stage": cols["stage"],
                        "lesson": cols["lesson"],
                        "promo_code": enrollment.promo_code or "—",
                        "level": child.current_level,
                        "points": str(child.total_points),
                        "progress_url": progress_url,
                        "meeting_tales": meeting_tale_options(
                            db,
                            child.id,
                            module=module,
                            enrollment=enrollment,
                        ),
                    }
                )
                if idx == 0:
                    show_delete = False
    return rows


def _admin_modules() -> list[dict]:
    return sorted(load_modules(), key=lambda m: m["id"])


def _admin_module_groups() -> list[dict]:
    by_group: dict[str, list[dict]] = {}
    for mod in _admin_modules():
        by_group.setdefault(mod["group_label"], []).append(mod)
    ordered: list[dict] = []
    for label in sorted(by_group, key=lambda name: by_group[name][0]["id"]):
        ordered.append({"label": label, "modules": by_group[label]})
    return ordered


def _flash_from_query(request: Request) -> dict | None:
    params = request.query_params
    if params.get("enrolled") == "1":
        return {
            "type": "ok",
            "message": params.get("msg") or "Доступ выдан.",
            "progress_url": params.get("progress_url") or "",
        }
    if params.get("deleted") == "1":
        return {
            "type": "ok",
            "message": params.get("msg") or "Запись удалена.",
            "progress_url": "",
        }
    if params.get("meeting") == "1":
        return {
            "type": "ok",
            "message": params.get("msg") or "Присутствие отмечено.",
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


def _redirect_admin_error(message: str, *, anchor: str = "enroll") -> RedirectResponse:
    return RedirectResponse(f"/admin?error={quote(message)}#{anchor}", status_code=303)


def _redirect_admin_deleted(parent_name: str) -> RedirectResponse:
    msg = f"Удалена семья: {parent_name}."
    return RedirectResponse(
        f"/admin?deleted=1&msg={quote(msg)}#registrations",
        status_code=303,
    )


def _redirect_admin_meeting(
    *,
    child_name: str,
    tale_title: str,
    status: str,
    progress_url: str,
) -> RedirectResponse:
    if status == "duplicate":
        msg = (
            f"Присутствие уже отмечено сегодня: {child_name} — «{tale_title}»."
        )
    else:
        msg = (
            f"Отмечено присутствие на встрече: {child_name} — «{tale_title}». "
            "Бейдж «Слушатель» начисляется при первой встрече."
        )
    url = (
        "/admin?meeting=1"
        f"&msg={quote(msg)}"
        f"&progress_url={quote(progress_url)}"
        "#meetings"
    )
    return RedirectResponse(url, status_code=303)


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
    rows = _build_rows(families, db)
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
            "module_groups": _admin_module_groups(),
            "tariff_labels": _TARIFF_LABELS,
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


@router.post("/children/{child_id}/meeting-attendance")
def admin_mark_meeting_attendance(
    request: Request,
    child_id: uuid.UUID,
    db: Session = Depends(get_db),
    tale_title: str = Form(...),
):
    require_admin(request)
    try:
        result = mark_meeting_attendance(
            db,
            child_id=child_id,
            tale_title=tale_title.strip(),
        )
    except HTTPException as exc:
        return _redirect_admin_error(str(exc.detail), anchor="meetings")

    child = repo.get_child_with_family(db, child_id)
    progress_url = ""
    if child and child.family:
        progress_url = f"{PUBLIC_BASE_URL}/progress/{child.family.progress_token}"

    return _redirect_admin_meeting(
        child_name=result["child_name"],
        tale_title=result["tale_title"],
        status=result["status"],
        progress_url=progress_url,
    )


@router.post("/families/{family_id}/delete")
def admin_delete_family(
    request: Request,
    family_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    require_admin(request)
    family = repo.get_family_by_id(db, family_id)
    if not family:
        return _redirect_admin_error("Семья не найдена.", anchor="registrations")
    parent_name = family.parent_name
    try:
        deleted = repo.delete_family(db, family_id)
    except Exception as exc:
        db.rollback()
        return _redirect_admin_error(f"Не удалось удалить запись: {exc}", anchor="registrations")
    if not deleted:
        return _redirect_admin_error("Не удалось удалить запись.", anchor="registrations")
    return _redirect_admin_deleted(parent_name)


@router.get("/export.csv")
def admin_export_csv(
    request: Request,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    require_admin(request)

    families = repo.list_all_families(db)
    rows = _build_rows(families, db)

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
            "Класс",
            "Формат",
            "Этап",
            "Сказка / блок",
            "Промокод",
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
                row["grade"],
                row["tariff"],
                row["stage"],
                row["lesson"],
                row["promo_code"],
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
