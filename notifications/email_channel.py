from __future__ import annotations

import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from config.settings import (
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USER,
)

logger = logging.getLogger(__name__)


def send_email(
    to: str,
    subject: str,
    body: str,
    html_body: str | None = None,
    attachments: list[tuple[str, Path | bytes]] | None = None,
) -> None:
    if not SMTP_HOST:
        raise RuntimeError("SMTP_HOST не задан")

    msg = MIMEMultipart("mixed")
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(body, "plain", "utf-8"))
    if html_body:
        alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt)

    for filename, payload in attachments or []:
        if isinstance(payload, Path):
            data = payload.read_bytes()
        else:
            data = payload
        part = MIMEApplication(data, _subtype="pdf")
        part.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(part)

    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to

    # Mail.ru: 465 = SSL сразу, 587 = STARTTLS после подключения
    use_ssl = SMTP_PORT == 465
    smtp_cls = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP

    with smtp_cls(SMTP_HOST, SMTP_PORT, timeout=20) as server:
        if not use_ssl and SMTP_USE_TLS:
            server.starttls()
        if SMTP_USER and SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, [to], msg.as_string())

    logger.info("Email отправлен: %s", to)
