#!/usr/bin/env python3
"""Локальная проверка: разовое → модуль, один progress_token на email+имя."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from api.schemas import RegisterWebhook
from db import repository as repo
from db.models import Child, Enrollment
from db.session import SessionLocal
from services.enrollment import create_enrollment_from_registration


def _unique_email() -> str:
    return f"merge-test-{uuid.uuid4().hex[:12]}@example.com"


def _register_body(*, email: str, child_name: str, module_id: int, **extra):
    return RegisterWebhook.model_validate(
        {
            "parent_name": "Тест",
            "parent_email": email,
            "child_name": child_name,
            "notification_channel": "email",
            "module_id": module_id,
            **extra,
        }
    )


def main() -> int:
    db = SessionLocal()
    try:
        email = _unique_email()
        child_name = "Маша"

        family1, child1, returning1 = repo.resolve_or_create_family_child(
            db,
            parent_name="Анна",
            parent_email=email,
            parent_telegram=None,
            notification_channel="email",
            child_name=child_name,
            child_age=7,
        )
        assert not returning1, "first register should not be returning"

        body_single = _register_body(
            email=email,
            child_name=child_name,
            module_id=1,
            chosen_stage="1",
            chosen_tale_number=1,
        )
        create_enrollment_from_registration(db, child1, body_single)

        family2, child2, returning2 = repo.resolve_or_create_family_child(
            db,
            parent_name="Анна",
            parent_email=email,
            parent_telegram=None,
            notification_channel="email",
            child_name=child_name,
            child_age=8,
        )
        assert returning2, "second register same child should be returning"
        assert family2.progress_token == family1.progress_token
        assert child2.id == child1.id

        body_module = _register_body(
            email=email, child_name=child_name, module_id=2, chosen_stage="1"
        )
        create_enrollment_from_registration(db, child2, body_module)

        enrollments = list(
            db.scalars(
                select(Enrollment)
                .where(Enrollment.child_id == child2.id)
                .order_by(Enrollment.created_at.asc())
            ).all()
        )
        assert len(enrollments) == 2
        assert enrollments[0].status == "completed"
        assert enrollments[1].module_id == 2
        assert enrollments[1].status == "active"

        _, sibling, sibling_returning = repo.resolve_or_create_family_child(
            db,
            parent_name="Анна",
            parent_email=email,
            parent_telegram=None,
            notification_channel="email",
            child_name="Петя",
            child_age=9,
        )
        assert not sibling_returning
        assert sibling.id != child2.id

        children = list(
            db.scalars(select(Child).where(Child.family_id == family1.id)).all()
        )
        assert len(children) == 2

        print("OK: same email+name → same token; module supersedes single enrollment")
        print(f"  progress_token={family2.progress_token[:16]}…")
        return 0
    except Exception as exc:
        print("FAIL:", exc)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
