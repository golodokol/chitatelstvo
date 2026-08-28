from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from config.settings import ROOT

LEADS_FILE = ROOT / "data" / "quiz_leads.jsonl"
STATUS_FILE = ROOT / "data" / "quiz_lead_status.json"


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


def quiz_lead_id(lead: dict) -> str:
    """Стабильный id заявки (новый id из записи или хеш от даты+email)."""
    existing = lead.get("id")
    if existing:
        return str(existing)
    raw = "|".join(
        [
            str(lead.get("created_at") or ""),
            str(lead.get("parent_email") or "").strip().lower(),
            str(lead.get("phone") or "").strip(),
            str(lead.get("child_name") or "").strip(),
        ]
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def load_quiz_lead_status() -> dict[str, dict]:
    if not STATUS_FILE.is_file():
        return {}
    try:
        data = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): v for k, v in data.items() if isinstance(v, dict)}


def set_quiz_lead_replied(lead_id: str, *, replied: bool) -> dict:
    status = load_quiz_lead_status()
    key = str(lead_id).strip()
    if not key:
        raise ValueError("empty lead_id")
    if replied:
        status[key] = {
            "replied": True,
            "replied_at": datetime.now(timezone.utc).isoformat(),
        }
    else:
        status.pop(key, None)
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(
        json.dumps(status, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return status.get(key) or {"replied": False, "replied_at": None}


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
    source = leads if leads is not None else load_quiz_leads()
    status = load_quiz_lead_status()
    rows: list[dict] = []
    for index, lead in enumerate(source):
        answers = lead.get("answers") or []
        lid = quiz_lead_id(lead)
        st = status.get(lid) or {}
        replied = bool(st.get("replied"))
        rows.append(
            {
                "id": lid,
                "created_at": _fmt_iso(lead.get("created_at")),
                "parent_name": lead.get("parent_name") or "—",
                "parent_email": lead.get("parent_email") or "—",
                "phone": lead.get("phone") or "—",
                "child_name": lead.get("child_name") or "—",
                "child_age": str(lead.get("child_age")) if lead.get("child_age") is not None else "—",
                "answers_text": _answers_text(answers),
                "replied": replied,
                "replied_at": _fmt_iso(st.get("replied_at")) if replied and st.get("replied_at") else "",
                "_order": index,
            }
        )
    # Сначала без ответа (свежие сверху), потом отвеченные.
    rows.sort(key=lambda row: (1 if row["replied"] else 0, row["_order"]))
    for row in rows:
        row.pop("_order", None)
    return rows
