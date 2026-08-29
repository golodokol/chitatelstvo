"""Разовая проверка админ-алертов Telegram + MAX (без реальной оплаты)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from notifications.admin_alerts import notify_admin_payment  # noqa: E402


def main() -> None:
    notify_admin_payment(
        parent_name="Тест Родитель",
        parent_email="test@example.com",
        parent_phone="+79001234567",
        child_name="Тест Ребёнок",
        child_age=8,
        module_id=1,
        module_title="Тестовая программа",
        chosen_stage=None,
        chosen_tale_number=None,
        promo_code=None,
        source="test_script",
        is_returning=False,
    )
    print("Готово. Проверьте Telegram и MAX; ошибки — в логах выше.")


if __name__ == "__main__":
    main()
