"""SMTP diagnostics — no secrets printed."""
from __future__ import annotations

import smtplib
import ssl

from config.settings import SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USE_TLS, SMTP_USER


def main() -> None:
    print("host", SMTP_HOST or "(empty)")
    print("port", SMTP_PORT)
    print("user", SMTP_USER or "(empty)")
    print("from", SMTP_FROM or "(empty)")
    print("use_tls", SMTP_USE_TLS)
    print("password_set", bool(SMTP_PASSWORD))
    if not SMTP_HOST:
        print("ERROR: SMTP_HOST empty")
        return
    for port, use_ssl in ((465, True), (587, False)):
        label = f"port_{port}"
        try:
            cls = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
            with cls(SMTP_HOST, port, timeout=20) as server:
                if not use_ssl:
                    server.starttls(context=ssl.create_default_context())
                if SMTP_USER and SMTP_PASSWORD:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                print(label, "login_ok")
        except Exception as exc:  # noqa: BLE001
            print(label, "fail", type(exc).__name__, str(exc)[:120])


if __name__ == "__main__":
    main()
