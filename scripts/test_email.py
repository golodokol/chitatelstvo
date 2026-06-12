"""Тест SMTP. На сервере: docker compose exec api python scripts/test_email.py"""

from notifications.email_channel import send_email
from notifications.email_templates import SUBJECT_WELCOME, build_welcome_message

send_email(
    "golod_ok@mail.ru",
    SUBJECT_WELCOME,
    build_welcome_message(
        parent_name="Тест",
        child_name="Колобок",
        progress_url="https://api.chitatelstvo.ru/progress/TEST",
    ),
)
print("OK")
