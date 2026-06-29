"""Приватная тестовая страница урока — только по секретному ключу в URL."""

from __future__ import annotations

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from api.test_lesson_auth import test_lesson_enabled, verify_test_lesson_key
from config.settings import ROOT
from db import repository as repo
from db.session import get_db
from lessons.loader import get_lesson
from sqlalchemy.orm import Session

router = APIRouter(tags=["test-lesson"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))

TEST_LESSON_SLUG = "tsarevna-lyagushka"
TEST_LESSON_SLUG_CATALOG = "grade-1-self_paced-stage-1-lesson-01"


def _request_origin(request: Request) -> str:
    """Базовый URL API с учётом nginx (https)."""
    scheme = request.headers.get("x-forwarded-proto") or request.url.scheme
    host = request.headers.get("host") or request.url.netloc
    return f"{scheme}://{host}"


def _lesson_url_with_test_key(
    request: Request,
    child_id,
    slug: str,
    test_key: str,
) -> str | None:
    """Ссылка на урок: test_key снимает проверку подписи, домен — текущий хост."""
    if not get_lesson(slug):
        return None
    origin = _request_origin(request)
    qs = urlencode(
        {
            "child": str(child_id),
            "exp": "0",
            "sig": "0",
            "test_key": test_key,
        }
    )
    return f"{origin}/lesson/{slug}?{qs}"


@router.get("/test/urok/{secret}", response_class=HTMLResponse)
def test_lesson_hub(
    secret: str,
    request: Request,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    if not test_lesson_enabled() or not verify_test_lesson_key(secret):
        raise HTTPException(404, "Страница не найдена")

    origin = _request_origin(request)
    token = (request.query_params.get("token") or "").strip()
    error = None
    children: list[dict] = []

    if token:
        family = repo.get_family_by_token(db, token)
        if not family:
            error = (
                "Токен не найден. Откройте страницу прогресса в браузере — "
                "если она открывается, скопируйте токен из адреса после /progress/ "
                "(без пробелов в начале и в конце)."
            )
        elif not family.children:
            error = "У этой семьи пока нет детей в базе."
        else:
            progress_url = f"{origin}/progress/{token}"
            for child in family.children:
                lesson_url = _lesson_url_with_test_key(
                    request, child.id, TEST_LESSON_SLUG, secret
                )
                catalog_url = _lesson_url_with_test_key(
                    request, child.id, TEST_LESSON_SLUG_CATALOG, secret
                )
                children.append(
                    {
                        "id": str(child.id),
                        "name": child.name,
                        "level": child.current_level,
                        "points": child.total_points or 0,
                        "lesson_url": lesson_url,
                        "catalog_url": catalog_url,
                        "progress_url": progress_url,
                    }
                )

    lesson = get_lesson(TEST_LESSON_SLUG)
    response = templates.TemplateResponse(
        request,
        "test_lesson_hub.html",
        {
            "secret": secret,
            "token": token,
            "error": error,
            "children": children,
            "lesson_title": lesson["title"] if lesson else TEST_LESSON_SLUG,
            "hub_url": f"{origin}/test/urok/{secret}",
        },
    )
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    response.headers["Cache-Control"] = "no-store"
    return response
