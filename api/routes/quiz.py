from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from api.deps import rate_limit
from config.settings import PUBLIC_BASE_URL, ROOT

router = APIRouter(tags=["quiz"])
templates = Jinja2Templates(directory=str(ROOT / "templates"))

SITE_URL = "https://chitatelstvo.ru"
LEADS_FILE = ROOT / "data" / "quiz_leads.jsonl"

PAGE_CONTEXT = {
    "site_url": SITE_URL,
    "api_url": PUBLIC_BASE_URL,
    "legal_politika": f"{PUBLIC_BASE_URL}/legal/politika",
}


class QuizAnswer(BaseModel):
    question: str = Field(min_length=1, max_length=300)
    answer: str = Field(min_length=1, max_length=300)


class QuizLeadRequest(BaseModel):
    parent_name: str = Field(min_length=1, max_length=200)
    phone: str = Field(min_length=7, max_length=40)
    child_name: str = Field(min_length=1, max_length=100)
    child_age: int = Field(ge=4, le=18)
    answers: list[QuizAnswer] = Field(min_length=1, max_length=10)


@router.get("/quiz", response_class=HTMLResponse)
def quiz_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "quiz/page.html", PAGE_CONTEXT)


@router.get("/quiz/checklist", response_class=HTMLResponse)
def quiz_checklist(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "quiz/checklist.html", PAGE_CONTEXT)


@router.post("/api/quiz/lead")
def quiz_lead(body: QuizLeadRequest, request: Request, _: None = Depends(rate_limit)) -> dict:
    LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ip": request.client.host if request.client else None,
        "parent_name": body.parent_name,
        "phone": body.phone,
        "child_name": body.child_name,
        "child_age": body.child_age,
        "answers": [a.model_dump() for a in body.answers],
    }
    with LEADS_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {
        "ok": True,
        "checklist_url": f"{PUBLIC_BASE_URL}/quiz/checklist",
        "message": "Спасибо! Скоро вы получите персональную сказку и PDF-чек-лист.",
    }
