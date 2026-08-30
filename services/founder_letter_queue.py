"""Очередь отложенных писем основателя."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from config.settings import ROOT
from notifications.email_channel import send_email
from notifications.founder_letter import build_founder_letter
from notifications.send_window import is_founder_send_window, next_founder_send_time
from services.recommendation_rules import RecommendationRule, load_recommendation_rules

logger = logging.getLogger(__name__)

QUEUE_FILE = ROOT / "data" / "founder_letters_queue.jsonl"
FOUNDER_LETTER_DELAY = timedelta(hours=2)
DEDUP_DAYS = 7


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _load_rows() -> list[dict[str, Any]]:
    if not QUEUE_FILE.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in QUEUE_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            logger.warning("Skip bad founder queue line: %s", line[:80])
    return rows


def _save_rows(rows: list[dict[str, Any]]) -> None:
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with QUEUE_FILE.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _rule_by_id(rule_id: str) -> RecommendationRule | None:
    for rule in load_recommendation_rules():
        if rule.rule_id == rule_id:
            return rule
    return None


def _recently_scheduled(parent_email: str, rows: list[dict[str, Any]]) -> bool:
    email = parent_email.strip().lower()
    cutoff = _now_utc() - timedelta(days=DEDUP_DAYS)
    for row in rows:
        if (row.get("parent_email") or "").strip().lower() != email:
            continue
        created = row.get("created_at") or row.get("sent_at")
        if not created:
            continue
        try:
            if _parse_dt(created) >= cutoff:
                return True
        except ValueError:
            continue
    return False


def schedule_founder_letter(
    *,
    lead_id: str,
    parent_email: str,
    payload: dict[str, Any],
) -> str | None:
    """Планирует письмо. Возвращает id задачи или None при дедупе."""
    rows = _load_rows()
    if _recently_scheduled(parent_email, rows):
        logger.info("Founder letter skipped (dedup): %s", parent_email)
        return None

    now = _now_utc()
    send_after = max(now + FOUNDER_LETTER_DELAY, next_founder_send_time(now))
    job_id = str(uuid.uuid4())
    row = {
        "id": job_id,
        "lead_id": lead_id,
        "parent_email": parent_email.strip().lower(),
        "status": "pending",
        "created_at": now.isoformat(),
        "send_after": send_after.isoformat(),
        "payload": payload,
    }
    rows.append(row)
    _save_rows(rows)
    logger.info("Founder letter scheduled %s → %s at %s", job_id, parent_email, send_after.isoformat())
    return job_id


def process_due_founder_letters(*, force: bool = False) -> int:
    """Отправляет просроченные письма в рабочем окне. Возвращает число отправленных."""
    rows = _load_rows()
    if not rows:
        return 0

    now = _now_utc()
    in_window = is_founder_send_window()
    sent_count = 0
    changed = False

    for row in rows:
        if row.get("status") != "pending":
            continue
        try:
            send_after = _parse_dt(row["send_after"])
        except (KeyError, ValueError):
            continue

        if send_after > now and not force:
            continue

        if not in_window and not force:
            row["send_after"] = next_founder_send_time(now).isoformat()
            changed = True
            continue

        rule = _rule_by_id(str((row.get("payload") or {}).get("rule_id", "")))
        if not rule:
            row["status"] = "failed"
            row["error"] = "rule_not_found"
            changed = True
            continue

        payload = row.get("payload") or {}
        try:
            subject, plain, html_body = build_founder_letter(
                rule=rule,
                parent_name=str(payload.get("parent_name") or ""),
                child_name=str(payload.get("child_name") or ""),
                child_age=payload.get("child_age"),
                trial_lesson_url=payload.get("trial_lesson_url"),
                trial_progress_url=payload.get("trial_progress_url"),
                trial_title=payload.get("trial_title"),
            )
            send_email(
                row["parent_email"],
                subject,
                plain,
                html_body,
            )
            row["status"] = "sent"
            row["sent_at"] = now.isoformat()
            sent_count += 1
            changed = True
        except Exception:
            logger.exception("Founder letter send failed for %s", row.get("parent_email"))
            row["status"] = "failed"
            row["error"] = "send_error"
            changed = True

    if changed:
        _save_rows(rows)
    return sent_count
