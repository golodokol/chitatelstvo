"""Заявки на пробный early-урок (с согласиями)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from config.settings import ROOT

LEADS_FILE = ROOT / "data" / "early_trial_leads.jsonl"


def append_early_trial_lead(row: dict) -> None:
    LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(row)
    payload.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    with LEADS_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def load_early_trial_leads() -> list[dict]:
    if not LEADS_FILE.exists():
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


def build_early_trial_lead_rows(leads: list[dict] | None = None) -> list[dict]:
    rows: list[dict] = []
    for lead in leads if leads is not None else load_early_trial_leads():
        created = lead.get("created_at") or ""
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            created_fmt = dt.strftime("%d.%m.%Y %H:%M")
        except ValueError:
            created_fmt = created[:16] or "—"
        rows.append(
            {
                "created_at": created_fmt,
                "parent_name": lead.get("parent_name") or "—",
                "parent_email": lead.get("parent_email") or "—",
                "child_name": lead.get("child_name") or "—",
                "child_age": lead.get("child_age") if lead.get("child_age") is not None else "—",
                "course": lead.get("course_label") or lead.get("trial_slug") or "—",
                "trial_title": lead.get("trial_title") or "—",
                "consent_privacy": "да" if lead.get("consent_privacy") else "нет",
                "consent_offer": "да" if lead.get("consent_offer") else "нет",
                "consent_marketing": "да" if lead.get("consent_marketing") else "нет",
            }
        )
    return rows
