#!/usr/bin/env python3
"""Проверить, есть ли email в базе (для диагностики OTP)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from db import repository as repo
from db.session import SessionLocal


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_auth_email.py email@example.com")
        return 1

    email = sys.argv[1].strip().lower()
    db = SessionLocal()
    try:
        families = repo.list_families_by_email(db, email)
        if not families:
            print(f"NOT_FOUND: {email}")
            print("OTP не отправляется — семья с таким email не зарегистрирована.")
            print("Используйте тот же адрес, что в форме записи на chitatelstvo.ru,")
            print("или проверьте админку /admin.")
            return 2

        for family in families:
            children = repo.list_children_for_family(db, family.id)
            names = ", ".join(c.name for c in children) or "—"
            print(f"FOUND: {family.parent_email}")
            print(f"  parent: {family.parent_name}")
            print(f"  children: {names}")
            print(f"  progress: /progress/{family.progress_token}")
        print("OTP должен уходить на этот email (если SMTP настроен).")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
