from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from config.settings import ROOT

LEADS_FILE = ROOT / "data" / "quiz_leads.jsonl"


def _fmt_iso(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return iso[:16]


def _answers_text(answers: list) -> str:
    parts: list[str] = []
    for item in answers:
        if not isinstance(item, dict):
            continue
        question = (item.get("question") or "").strip()
        answer = (item.get("answer") or "").strip()
        if question and answer:
            parts.append(f"{question} → {answer}")
    return "\n".join(parts) if parts else "—"


def load_quiz_leads() -> list[dict]:
    if not LEADS_FILE.is_file():
        return []
    leads: list[dict] = []
    with LEADS_FILE.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                leads.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    leads.sort(key=lambda row: row.get("created_at") or "", reverse=True)
    return leads


def build_quiz_lead_rows(leads: list[dict] | None = None) -> list[dict]:
    rows: list[dict] = []
    for lead in leads if leads is not None else load_quiz_leads():
        answers = lead.get("answers") or []
        rows.append(
            {
                "created_at": _fmt_iso(lead.get("created_at")),
                "parent_name": lead.get("parent_name") or "—",
                "parent_email": lead.get("parent_email") or "—",
                "phone": lead.get("phone") or "—",
                "child_name": lead.get("child_name") or "—",
                "child_age": str(lead.get("child_age")) if lead.get("child_age") is not None else "—",
                "answers_text": _answers_text(answers),
            }
        )
    return rows
