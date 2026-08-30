"""Отправить HTML-превью приветственного письма родителям.

На сервере:
  docker compose exec -T api python scripts/send_welcome_html_preview.py
"""

from __future__ import annotations

from pathlib import Path

from notifications.email_channel import send_email
from notifications.email_templates import SUBJECT_WELCOME

TO = "info@chitatelstvo.ru"
ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "docs" / "email-templates" / "welcome-parent-example.html"

PLAIN = """Анна, здравствуйте!

Я Ольга Рощина, основатель Читательства.

Рада, что Маша теперь с нами. Для меня это всегда немного волнительный момент: в семью заходит новая привычка — читать не «потому что надо», а потому что интересно.

Я придумала школу, потому что вижу по своим детям: книга может конкурировать с гаджетами, если читать вместе по-человечески. Все занятия сначала проверяю дома.

Именно вам:
Спасибо, что написали про интерес Маши к сказкам. Давайте начнём с «Колобка». Если после первого урока захотите совет — просто ответьте на письмо.

Личная страница Маши:
https://api.chitatelstvo.ru/progress/EXAMPLE

Читайте в том темпе, который подходит вам. Лучше один живой урок в удовольствие, чем три на бегу.

С теплом,
Ольга
Читательство

Если что-то непонятно — ответьте на это письмо. Я читаю.
"""


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    send_email(
        TO,
        subject=f"{SUBJECT_WELCOME} — письмо от Ольги",
        body=PLAIN,
        html_body=html,
    )
    print(f"OK: sent to {TO}")


if __name__ == "__main__":
    main()
