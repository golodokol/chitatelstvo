from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from config.settings import PUBLIC_BASE_URL, ROOT
from services import expedition_cabinet as cabinet

router = APIRouter(tags=["expedition"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))

SITE = "https://chitatelstvo.ru"
ASSET = "/static/expedition/"
DATA_PATH = ROOT / "static" / "expedition" / "data.json"
STORE = ROOT / "data" / "expedition"
OG = f"{PUBLIC_BASE_URL}/static/expedition/images/hero-map.png"

_SLUG = re.compile(r"^[a-z0-9-]{1,80}$")

PAGE_META = {
    "/": (
        "Читательская экспедиция — литературная школа «Читательство»",
        "Интерактивное путешествие по сказкам, героям и легендам народов России от литературной школы «Читательство».",
    ),
    "/map": (
        "Карта Читательской экспедиции — Читательство",
        "Интерактивная карта сказок и маршрутов народов России. Выберите регион, историю и задание.",
    ),
    "/routes": (
        "Маршруты Читательской экспедиции — Читательство",
        "Готовые литературные маршруты для детей 6–8, 9–11 лет и семейного чтения.",
    ),
    "/passport": (
        "Паспорт экспедитора — Читательство",
        "Цифровой паспорт Читательской экспедиции: штампы регионов, бейджи и открытия.",
    ),
    "/cabinet": (
        "Моя экспедиция — Читательство",
        "Текущая история, прогресс и следующая остановка Читательской экспедиции.",
    ),
    "/collection": (
        "Коллекция историй — Читательская экспедиция",
        "Завершённые и доступные истории Читательской экспедиции.",
    ),
    "/parents": (
        "Родителям — Читательская экспедиция",
        "Прогресс ребёнка, рекомендации и тарифы Читательской экспедиции.",
    ),
    "/libraries": (
        "Библиотекам — Читательская экспедиция «Читательства»",
        "Станьте точкой Читательской экспедиции: готовый сценарий, материалы и карта читающих регионов.",
    ),
    "/add-legend": (
        "Помогите нанести историю на карту — Читательство",
        "Предложите сказку, предание или легенду своего края. После проверки редакции она может войти в экспедицию.",
    ),
    "/about": (
        "О проекте «Читательская экспедиция» — Читательство",
        "Интерактивный литературный маршрут от школы «Читательство» для детей 6–11 лет, семей и библиотек.",
    ),
}


def _load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def _meta_for(path: str) -> tuple[str, str]:
    data = _load_data()
    if path in PAGE_META:
        return PAGE_META[path]
    parts = path.strip("/").split("/")
    if len(parts) == 2 and _SLUG.match(parts[1]):
        slug = parts[1]
        if parts[0] == "regions":
            item = next((r for r in data["regions"] if r["slug"] == slug), None)
            if item:
                return (
                    f"{item['name']} — Читательская экспедиция",
                    item.get("short") or PAGE_META["/"][1],
                )
        if parts[0] == "stories":
            item = next((s for s in data["stories"] if s["slug"] == slug), None)
            if item:
                return (
                    f"{item['title']} — Читательская экспедиция",
                    item.get("who") or PAGE_META["/"][1],
                )
        if parts[0] == "heroes":
            item = next((h for h in data["heroes"] if h["slug"] == slug), None)
            if item:
                return (
                    f"{item['name']} — Читательская экспедиция",
                    item.get("blurb") or PAGE_META["/"][1],
                )
        if parts[0] == "routes":
            item = next((r for r in data["routes"] if r["slug"] == slug), None)
            if item:
                return (
                    f"{item['title']} — Читательская экспедиция",
                    item.get("blurb") or PAGE_META["/"][1],
                )
    return PAGE_META["/"]


def _page(request: Request, path: str) -> HTMLResponse:
    title, description = _meta_for(path)
    canonical = f"{SITE}/expedition" + ("" if path in ("", "/") else path)
    return templates.TemplateResponse(
        request,
        "expedition/app.html",
        {
            "title": title,
            "description": description,
            "canonical": canonical,
            "og_image": OG,
            "asset": ASSET,
        },
    )


@router.get("/expedition", response_class=HTMLResponse)
@router.get("/expedition/", response_class=HTMLResponse)
def expedition_home(request: Request) -> HTMLResponse:
    return _page(request, "/")


@router.get("/expedition/kit.html", response_class=HTMLResponse)
def expedition_kit() -> FileResponse:
    return FileResponse(
        ROOT / "templates" / "expedition" / "kit.html",
        media_type="text/html; charset=utf-8",
    )


@router.get("/expedition/api/data.json")
def expedition_data() -> FileResponse:
    return FileResponse(DATA_PATH, media_type="application/json")


@router.get("/expedition/api/tariffs")
def expedition_tariffs() -> JSONResponse:
    return JSONResponse({"ok": True, "items": cabinet.public_tariffs()})


@router.get("/expedition/api/cabinet")
def expedition_cabinet_state(request: Request) -> JSONResponse:
    token = _bearer(request)
    return JSONResponse(cabinet.session_state(token))


@router.post("/expedition/api/cabinet/register")
async def expedition_cabinet_register(request: Request) -> JSONResponse:
    payload = await _json_body(request)
    guest = payload.get("progress") if isinstance(payload.get("progress"), dict) else None
    try:
        age = payload.get("child_age")
        age_int = int(age) if age not in (None, "") else None
        result = cabinet.register_expedition(
            child_name=str(payload.get("child_name") or ""),
            parent_name=str(payload.get("parent_name") or ""),
            email=str(payload.get("email") or ""),
            child_age=age_int,
            password=str(payload.get("password") or "") or None,
            avatar=str(payload.get("avatar") or "compass"),
            consent=bool(payload.get("consent") or payload.get("pd")),
            guest_progress=guest,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return JSONResponse({"ok": True, **result})


@router.post("/expedition/api/cabinet/login")
async def expedition_cabinet_login(request: Request) -> JSONResponse:
    payload = await _json_body(request)
    try:
        result = cabinet.login_expedition(
            email=str(payload.get("email") or ""),
            password=str(payload.get("password") or "") or None,
            token=_bearer(request) or str(payload.get("token") or "") or None,
        )
    except ValueError as exc:
        code = str(exc)
        status = 401 if code in {"password", "session"} else 404 if code == "not_found" else 400
        raise HTTPException(status_code=status, detail=code) from exc
    return JSONResponse({"ok": True, **result})


@router.post("/expedition/api/cabinet/progress")
async def expedition_cabinet_progress(request: Request) -> JSONResponse:
    token = _bearer(request)
    if not token:
        raise HTTPException(status_code=401, detail="session")
    payload = await _json_body(request)
    try:
        profile = cabinet.save_progress(token, payload)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return JSONResponse({"ok": True, "profile": profile})


def _bearer(request: Request) -> str | None:
    header = request.headers.get("authorization") or ""
    if header.lower().startswith("bearer "):
        return header[7:].strip() or None
    return request.headers.get("x-expedition-token")


async def _json_body(request: Request) -> dict:
    try:
        payload = await request.json()
        if not isinstance(payload, dict):
            raise ValueError("json")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=400, detail="invalid json") from exc


@router.post("/expedition/api/{kind}")
async def expedition_submit(kind: str, request: Request) -> JSONResponse:
    if kind not in {"library", "legend", "error"}:
        raise HTTPException(status_code=404, detail="unknown form")
    try:
        payload = await request.json()
        if not isinstance(payload, dict):
            raise ValueError("json")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="invalid json") from exc
    rec_id = str(uuid.uuid4())
    payload = {
        **payload,
        "id": rec_id,
        "kind": kind,
        "status": "submitted",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    folder = STORE / kind
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{rec_id}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return JSONResponse({"ok": True, "id": rec_id, "status": "submitted"})


@router.get("/expedition/{full_path:path}", response_class=HTMLResponse)
def expedition_page(request: Request, full_path: str) -> HTMLResponse:
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="not found")
    path = "/" + full_path.strip("/")
    return _page(request, path)
