from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from api.lesson_signing import build_lesson_url
from catalog.loader import get_module
from config.settings import LESSON_WEEK_DAYS, MODULE_START_DATE, PUBLIC_BASE_URL, ROOT, TELEGRAM_ENABLED
from db import repository as repo
from db.session import get_db
from gamification.cabinet_ui import build_child_cabinet
from lessons.access import lesson_access_info
from lessons.enrollment_access import get_active_enrollment, list_lessons_for_child
from lessons.covers import enrich_lesson_link
from lessons.schedule import STAGE_LABELS, tariff_has_meetings
from notifications.telegram_bot import build_link_url

router = APIRouter(tags=["progress"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def _group_lessons(lesson_links: list[dict]) -> list[dict]:
    if not lesson_links:
        return []
    stages: list[dict] = []
    by_stage: dict[str, list[dict]] = {}
    for les in lesson_links:
        stage = les.get("stage") or "stage-1"
        by_stage.setdefault(stage, []).append(les)
    for stage_key in ("stage-1", "stage-2"):
        items = by_stage.get(stage_key)
        if not items:
            continue
        stages.append(
            {
                "key": stage_key,
                "label": STAGE_LABELS.get(stage_key, stage_key),
                "lessons": items,
            }
        )
    return stages


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
        tale_ratings = repo.get_child_tale_ratings(db, child.id)
        badges = [b.badge_name for b in child.badges]
        enrollment = get_active_enrollment(child)
        module = get_module(enrollment.module_id) if enrollment else None
        module_title = module["title"] if module else None
        has_meetings = tariff_has_meetings(module)

        lesson_links = []
        for les in list_lessons_for_child(child):
            access = lesson_access_info(
                child,
                les,
                week_days=LESSON_WEEK_DAYS,
                enrollment=enrollment,
                module=module,
            )
            link = {
                "slug": les["slug"],
                "title": les["title"],
                "module_week": access["module_week"],
                "week_in_stage": access["week_in_stage"],
                "stage": access["stage"],
                "unlocked": access["unlocked"],
                "opens_on": access["opens_on"],
                "opens_on_label": access["opens_on_label"],
                "stage_label": les.get("stage_label"),
                "ready": les.get("active", True),
            }
            if access.get("meeting_on_label"):
                link["meeting_on"] = access["meeting_on"]
                link["meeting_on_label"] = access["meeting_on_label"]
            if access["unlocked"] and les.get("active", True):
                link["url"] = build_lesson_url(child.id, les["slug"])
            enrich_lesson_link(link)
            lesson_links.append(link)

        children_data.append(
            {
                "name": child.name,
                "level": child.current_level,
                "points": child.total_points,
                "badges": badges,
                "lessons": lesson_links,
                "lesson_stages": _group_lessons(lesson_links),
                "module_title": module_title,
                "has_meetings": has_meetings,
                "cabinet": build_child_cabinet(
                    name=child.name,
                    level=child.current_level or "Старт",
                    points=child.total_points or 0,
                    earned_badges=badges,
                    events=events,
                    lesson_links=lesson_links,
                    tale_ratings=tale_ratings,
                    assets_base=PUBLIC_BASE_URL,
                ),
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
            "assets_url": PUBLIC_BASE_URL,
            "logo_url": f"{PUBLIC_BASE_URL}/assets/logo-chitatelstvo.png",
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
