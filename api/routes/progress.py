from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from config.settings import PUBLIC_BASE_URL, ROOT
from db import repository as repo
from db.session import get_db
from services.cabinet import build_family_cabinet

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

    payload = build_family_cabinet(db, family)
    return templates.TemplateResponse(
        request,
        "progress.html",
        {
            "progress_token": token,
            "open_chest": request.query_params.get("open_chest") == "1",
            "chest_tale": (request.query_params.get("chest") or "").strip(),
            "parent_name": payload["parent_name"],
            "assets_url": PUBLIC_BASE_URL,
            "logo_url": f"{PUBLIC_BASE_URL}/assets/logo-chitatelstvo.png",
            "channel": payload["notification_channel"],
            "telegram_linked": payload["telegram"]["linked"],
            "telegram_enabled": payload["telegram"]["enabled"],
            "telegram_link": payload["telegram"]["deep_link"],
            "link_page": f"/link-telegram/{token}/page",
            "children": payload["children"],
            "module_start_date": payload["module_start_date"],
            "notifications": payload["notifications"],
            "parent_guide": payload["parent_guide"],
        },
    )
