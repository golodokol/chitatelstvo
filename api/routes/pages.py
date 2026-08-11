from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from config.settings import MEETING_ADDON_MODULE_ID, MEETING_ADDON_PRICE_RUB, PUBLIC_BASE_URL, ROOT
from lessons.schedule import (
    meeting_addon_closed_message,
    meeting_date_label,
    meeting_still_bookable,
    module_week_for_tale,
)
from lessons.single_content import content_slug_for_single
from gamification.sloviki import slovik_url
from gamification.sloviki import slovik_url
from services.checkout_urls import build_meeting_addon_pay_url

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))

SITE_URL = "https://chitatelstvo.ru"

PAGE_CONTEXT = {
    "site_url": SITE_URL,
    "api_url": PUBLIC_BASE_URL,
    "legal_politika": f"{PUBLIC_BASE_URL}/legal/politika",
    "legal_oferta": f"{PUBLIC_BASE_URL}/legal/oferta",
    "legal_rekvizity": f"{PUBLIC_BASE_URL}/legal/rekvizity",
    "contact_email": "info@chitatelstvo.ru",
    "contact_phone": "+7 (958) 500-08-50",
    "contact_phone_tel": "+79585000850",
    "ip_name": "ИП Рощина Ольга Владимировна",
}


@router.get("/spasibo", response_class=HTMLResponse)
def page_spasibo(request: Request) -> HTMLResponse:
    """Страница после успешной оплаты (Success URL для ST100)."""
    return templates.TemplateResponse(
        request,
        "pages/spasibo.html",
        {
            **PAGE_CONTEXT,
            "slovik_victory_url": slovik_url("victory"),
        },
    )


@router.get("/zapis", include_in_schema=False)
def page_zapis_redirect() -> RedirectResponse:
    """Запись на главной — редирект на блок «Выберите свой путь»."""
    return RedirectResponse(url=f"{SITE_URL}/#program", status_code=302)


@router.get("/order/meeting", response_class=HTMLResponse)
def page_order_meeting(
    request: Request,
    group: str = "grade-1",
    stage: str = "stage-1",
    tale: int = 1,
    slug: str = "",
) -> HTMLResponse:
    """Страница докупки встречи с преподавателем для выбранной сказки."""
    from catalog.loader import get_tale

    tale_info = get_tale(group, stage, tale) or {}
    tale_title = tale_info.get("tale_title") or tale_info.get("title") or "Царевна лягушка"
    stage_num = "1" if stage in ("stage-1", "1") else "2" if stage in ("stage-2", "2") else "1"
    module_week = module_week_for_tale(stage, tale)
    if not meeting_still_bookable(stage=stage, tale_number=tale, module_week=module_week):
        raise HTTPException(
            status_code=410,
            detail=meeting_addon_closed_message(
                stage=stage, tale_number=tale, module_week=module_week
            ),
        )
    lesson_slug = slug or content_slug_for_single(
        group_code=group,
        stage=stage,
        tale_number=tale,
    )
    pay_url = build_meeting_addon_pay_url(
        module_id=MEETING_ADDON_MODULE_ID,
        chosen_stage=stage_num,
        chosen_tale_number=tale,
        lesson_slug=lesson_slug,
        group_code=group,
    )
    return templates.TemplateResponse(
        request,
        "order_meeting.html",
        {
            **PAGE_CONTEXT,
            "tale_title": tale_title,
            "price": MEETING_ADDON_PRICE_RUB,
            "meeting_date": meeting_date_label(module_week),
            "pay_url": pay_url,
            "module_id": MEETING_ADDON_MODULE_ID,
            "group_code": group,
            "stage": stage,
            "stage_num": stage_num,
            "tale_number": tale,
            "lesson_slug": lesson_slug,
        },
    )
