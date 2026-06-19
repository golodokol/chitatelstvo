"""Проверка сценария «разовое → модуль»: один token, прогресс на child_id."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select

from db import repository as repo
from db.models import Child, Enrollment
from db.session import SessionLocal
from services.enrollment import create_enrollment_from_registration

pytestmark = pytest.mark.integration


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _unique_email() -> str:
    return f"merge-test-{uuid.uuid4().hex[:12]}@example.com"


def _register_body(*, email: str, child_name: str, module_id: int, **extra):
    from api.schemas import RegisterWebhook

    data = {
        "parent_name": "Тест",
        "parent_email": email,
        "child_name": child_name,
        "notification_channel": "email",
        "module_id": module_id,
        **extra,
    }
    return RegisterWebhook.model_validate(data)


def test_same_email_and_child_reuses_token_and_child(db):
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
    assert returning1 is False

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
    assert returning2 is True
    assert family2.progress_token == family1.progress_token
    assert child2.id == child1.id
    assert child2.age == 8

    body_module = _register_body(email=email, child_name=child_name, module_id=2, chosen_stage="1")
    create_enrollment_from_registration(db, child2, body_module)

    enrollments = list(
        db.scalars(
            select(Enrollment)
            .where(Enrollment.child_id == child2.id)
            .order_by(Enrollment.created_at.asc())
        ).all()
    )
    assert len(enrollments) == 2
    assert enrollments[0].module_id == 1
    assert enrollments[0].status == "completed"
    assert enrollments[1].module_id == 2
    assert enrollments[1].status == "active"


def test_same_email_different_children_share_family_token(db):
    email = _unique_email()

    family1, child1, _ = repo.resolve_or_create_family_child(
        db,
        parent_name="Анна",
        parent_email=email,
        parent_telegram=None,
        notification_channel="email",
        child_name="Маша",
        child_age=7,
    )
    family2, child2, returning = repo.resolve_or_create_family_child(
        db,
        parent_name="Анна",
        parent_email=email,
        parent_telegram=None,
        notification_channel="email",
        child_name="Петя",
        child_age=9,
    )

    assert returning is False
    assert child2.id != child1.id
    assert family2.progress_token == family1.progress_token

    children = list(
        db.scalars(select(Child).where(Child.family_id == family1.id)).all()
    )
    assert len(children) == 2


def test_parallel_enrollments_different_groups(db):
    email = _unique_email()
    child_name = "Маша"

    family, child, _ = repo.resolve_or_create_family_child(
        db,
        parent_name="Анна",
        parent_email=email,
        parent_telegram=None,
        notification_channel="email",
        child_name=child_name,
        child_age=7,
    )

    create_enrollment_from_registration(
        db,
        child,
        _register_body(email=email, child_name=child_name, module_id=2, chosen_stage="1"),
    )
    create_enrollment_from_registration(
        db,
        child,
        _register_body(email=email, child_name=child_name, module_id=17, chosen_stage="1"),
    )

    enrollments = list(
        db.scalars(
            select(Enrollment)
            .where(Enrollment.child_id == child.id, Enrollment.status == "active")
            .order_by(Enrollment.module_id.asc())
        ).all()
    )
    assert len(enrollments) == 2
    assert {e.module_id for e in enrollments} == {2, 17}


def test_delete_family_removes_child_and_enrollments(db):
    email = _unique_email()
    child_name = "Маша"

    family, child, _ = repo.resolve_or_create_family_child(
        db,
        parent_name="Анна",
        parent_email=email,
        parent_telegram=None,
        notification_channel="email",
        child_name=child_name,
        child_age=7,
    )
    create_enrollment_from_registration(
        db,
        child,
        _register_body(email=email, child_name=child_name, module_id=1, chosen_stage="1", chosen_tale_number=1),
    )

    assert repo.delete_family(db, family.id) is True
    assert repo.get_family_by_id(db, family.id) is None
    assert db.get(Child, child.id) is None
    remaining = db.scalars(select(Enrollment).where(Enrollment.child_id == child.id)).all()
    assert remaining == []


def test_different_email_creates_new_family(db):
    email1 = _unique_email()
    email2 = _unique_email()

    family1, _, _ = repo.resolve_or_create_family_child(
        db,
        parent_name="Анна",
        parent_email=email1,
        parent_telegram=None,
        notification_channel="email",
        child_name="Маша",
        child_age=7,
    )
    family2, _, _ = repo.resolve_or_create_family_child(
        db,
        parent_name="Борис",
        parent_email=email2,
        parent_telegram=None,
        notification_channel="email",
        child_name="Маша",
        child_age=7,
    )

    assert family1.id != family2.id
    assert family1.progress_token != family2.progress_token
