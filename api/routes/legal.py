from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from config.settings import PUBLIC_BASE_URL, ROOT

router = APIRouter(tags=["legal"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))

SITE_URL = "https://chitatelstvo.ru"
ROBOTS_NOINDEX = "noindex, nofollow, noarchive, nosnippet"

LEGAL_CONTEXT = {
    "ip_name": "ИП Рощина Ольга Владимировна",
    "inn": "231150315327",
    "ogrnip": "323774600435824",
    "legal_address": "115522, г. Москва, ул. Москворечье, 4к5, кв. 200",
    "actual_address": "123022, г. Москва, Столярный пер., 3, к. 13",
    "contact_email": "info@chitatelstvo.ru",
    "contact_phone": "+7 (958) 500-08-50",
    "contact_phone_tel": "+79585000850",
    "bank_account": "40802810738000326225",
    "bank_name": "ПАО Сбербанк",
    "bank_bik": "044525225",
    "bank_ks": "30101810400000000225",
    "site_url": SITE_URL,
    "api_url": PUBLIC_BASE_URL,
    "legal_politika": f"{PUBLIC_BASE_URL}/legal/politika",
    "legal_oferta": f"{PUBLIC_BASE_URL}/legal/oferta",
    "legal_rekvizity": f"{PUBLIC_BASE_URL}/legal/rekvizity",
}


def _render(request: Request, template: str, *, noindex: bool = False) -> HTMLResponse:
    context = dict(LEGAL_CONTEXT)
    if noindex:
        context["noindex"] = True
    response = templates.TemplateResponse(
        request,
        template,
        context,
    )
    if noindex:
        response.headers["X-Robots-Tag"] = ROBOTS_NOINDEX
    return response


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt() -> PlainTextResponse:
    body = "\n".join(
        [
            "User-agent: *",
            "Disallow: /legal/rekvizity",
            "",
        ]
    )
    return PlainTextResponse(body, media_type="text/plain")


@router.get("/legal/politika", response_class=HTMLResponse)
def legal_politika(request: Request) -> HTMLResponse:
    return _render(request, "legal/politika.html")


@router.get("/legal/oferta", response_class=HTMLResponse)
def legal_oferta(request: Request) -> HTMLResponse:
    return _render(request, "legal/oferta.html")


@router.get("/legal/rekvizity", response_class=HTMLResponse)
def legal_rekvizity(request: Request) -> HTMLResponse:
    return _render(request, "legal/rekvizity.html", noindex=True)
