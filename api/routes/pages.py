from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from config.settings import PUBLIC_BASE_URL, ROOT

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
        PAGE_CONTEXT,
    )


@router.get("/zapis", include_in_schema=False)
def page_zapis_redirect() -> RedirectResponse:
    """Запись на главной — редирект на блок «Выберите свой путь»."""
    return RedirectResponse(url=f"{SITE_URL}/#program", status_code=302)
