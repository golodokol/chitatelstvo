"""Подарок на день рождения: +1 неделя доступа к урокам (раз в год).

Вызывается при загрузке личного кабинета (/progress/{token}) — первый заход в день рождения.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from db.child_age import is_birthday_today
from db.models import Child


def maybe_grant_birthday_gift(db: Session, child: Child, *, on_date: date | None = None) -> bool:
    """Вернуть True, если подарок только что выдан."""
    if not child.birth_date:
        return False
    today = on_date or date.today()
    if not is_birthday_today(child.birth_date, on_date=today):
        return False
    if child.birthday_gift_year == today.year:
        return False

    child.bonus_unlock_weeks = (child.bonus_unlock_weeks or 0) + 1
    child.birthday_gift_year = today.year
    db.commit()
    db.refresh(child)
    return True
