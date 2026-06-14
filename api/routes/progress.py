from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from config.settings import LESSON_WEEK_DAYS, MODULE_START_DATE, ROOT, TELEGRAM_ENABLED
from db import repository as repo
from db.session import get_db
from api.lesson_signing import build_lesson_url
from catalog.loader import get_module
from lessons.access import lesson_access_info
from lessons.enrollment_access import get_active_enrollment, list_lessons_for_child
from notifications.telegram_bot import build_link_url

router = APIRouter(tags=["progress"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))


@router.get("/progress/{token}", response_class=HTMLResponse)
def family_progress(
    token: str,
    request: Request,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    family = repo.get_family_by_token(db, token)
    if not family:
        raise HTTPException(404, "Страница не найдена")

    children_data = []
    for child in family.children:
        events = repo.get_child_events(db, child.id, limit=20)
        badges = [b.badge_name for b in child.badges]
        enrollment = get_active_enrollment(child)
        module_title = None
        if enrollment:
            module = get_module(enrollment.module_id)
            module_title = module["title"] if module else None

        lesson_links = []
        for les in list_lessons_for_child(child):
            access = lesson_access_info(child, les, week_days=LESSON_WEEK_DAYS)
            link = {
                "title": les["title"],
                "module_week": access["module_week"],
                "unlocked": access["unlocked"],
                "opens_on": access["opens_on"],
                "stage_label": les.get("stage_label"),
                "ready": les.get("active", True),
            }
            if access["unlocked"] and les.get("active", True):
                link["url"] = build_lesson_url(child.id, les["slug"])
            lesson_links.append(link)
        children_data.append(
            {
                "name": child.name,
                "level": child.current_level,
                "points": child.total_points,
                "badges": badges,
                "lessons": lesson_links,
                "module_title": module_title,
                "events": [
                    {
                        "type": e.event_type,
                        "tale": e.tale_title or "—",
                        "date": e.created_at.strftime("%d.%m.%Y %H:%M") if e.created_at else "",
                    }
                    for e in events
                ],
            }
        )

    notifications = repo.get_family_notifications(db, family.id, limit=30)

    telegram_link = build_link_url(token)
    link_page = f"/link-telegram/{token}/page"

    return templates.TemplateResponse(
        request,
        "progress.html",
        {
            "parent_name": family.parent_name,
            "channel": family.notification_channel,
            "telegram_linked": family.telegram_chat_id is not None,
            "telegram_enabled": TELEGRAM_ENABLED,
            "telegram_link": telegram_link,
            "link_page": link_page,
            "children": children_data,
            "module_start_date": (
                MODULE_START_DATE.strftime("%d.%m.%Y") if MODULE_START_DATE else None
            ),
            "notifications": [
                {
                    "message": n.message,
                    "channel": n.channel,
                    "date": n.created_at.strftime("%d.%m.%Y %H:%M") if n.created_at else "",
                }
                for n in notifications
            ],
        },
    )
