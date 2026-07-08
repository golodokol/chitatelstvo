#!/usr/bin/env python3
"""Мониторинг Читательства: health, статика, Docker. Алерты на email.

Запуск на сервере (cron каждые 10 мин):
  cd /root/chitatelstvo && python3 scripts/monitor_health.py

Требует в .env:
  PUBLIC_BASE_URL, SMTP_*, MONITOR_ALERT_EMAIL
"""

from __future__ import annotations

import json
import os
import smtplib
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = Path(os.getenv("MONITOR_STATE_PATH", "/var/lib/chitatelstvo-monitor/state.json"))
DEFAULT_COOLDOWN_MIN = 30


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def base_url(cfg: dict[str, str]) -> str:
    return (env("PUBLIC_BASE_URL") or cfg.get("PUBLIC_BASE_URL") or "https://api.chitatelstvo.ru").rstrip("/")


def alert_emails(cfg: dict[str, str]) -> list[str]:
    raw = env("MONITOR_ALERT_EMAIL") or cfg.get("MONITOR_ALERT_EMAIL") or "info@chitatelstvo.ru"
    return [item.strip() for item in raw.split(",") if item.strip()]


def cooldown_minutes(cfg: dict[str, str]) -> int:
    raw = env("MONITOR_COOLDOWN_MINUTES") or cfg.get("MONITOR_COOLDOWN_MINUTES") or str(DEFAULT_COOLDOWN_MIN)
    try:
        return max(5, int(raw))
    except ValueError:
        return DEFAULT_COOLDOWN_MIN


def http_check(url: str, *, timeout: int = 15) -> tuple[bool, str]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "chitatelstvo-monitor/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            body = resp.read(4096)
            if code != 200:
                return False, f"HTTP {code}"
            return True, f"HTTP {code}, {len(body)} bytes"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def health_check(url: str) -> CheckResult:
    ok, detail = http_check(url)
    if not ok:
        return CheckResult("api_health", False, detail)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "chitatelstvo-monitor/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        if payload.get("status") != "ok":
            return CheckResult("api_health", False, f"status={payload.get('status')!r}")
        queue = payload.get("queue_length")
        return CheckResult("api_health", True, f"ok, queue={queue}")
    except Exception as exc:  # noqa: BLE001
        return CheckResult("api_health", False, str(exc))


def static_check(name: str, url: str) -> CheckResult:
    ok, detail = http_check(url)
    return CheckResult(name, ok, detail)


def docker_check(project_dir: Path) -> CheckResult:
    if env("MONITOR_DOCKER", "1") not in ("1", "true", "yes"):
        return CheckResult("docker", True, "skipped")
    compose_file = project_dir / "docker-compose.yml"
    if not compose_file.is_file():
        return CheckResult("docker", True, "no compose file")

    try:
        proc = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001
        return CheckResult("docker", False, str(exc))

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "docker compose failed").strip()
        return CheckResult("docker", False, err[:300])

    required = {"api", "worker", "postgres", "redis"}
    running: set[str] = set()
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        service = str(row.get("Service") or row.get("Name") or "").lower()
        state = str(row.get("State") or row.get("Status") or "").lower()
        if "running" in state:
            for key in required:
                if key in service:
                    running.add(key)

    missing = sorted(required - running)
    if missing:
        return CheckResult("docker", False, f"not running: {', '.join(missing)}")
    return CheckResult("docker", True, f"running: {', '.join(sorted(running))}")


def run_checks(cfg: dict[str, str]) -> list[CheckResult]:
    base = base_url(cfg)
    results = [
        health_check(f"{base}/health"),
        static_check("static_favicon", f"{base}/static/favicon.png"),
        static_check("static_chest", f"{base}/static/chest/chest-closed.png"),
        static_check(
            "lesson_reading_asset",
            f"{base}/static/lessons/tsarevna-lyagushka/reading/reading-01.png",
        ),
        docker_check(ROOT),
    ]
    return results


def load_state() -> dict:
    if not STATE_PATH.is_file():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def should_send_alert(state: dict, *, failed: bool, cooldown_min: int) -> bool:
    prev = state.get("last_status", "ok")
    if failed and prev != "fail":
        return True
    if not failed and prev == "fail":
        return True
    if failed:
        last_alert = parse_ts(state.get("last_alert_at"))
        if not last_alert:
            return True
        delta = datetime.now(timezone.utc) - last_alert.astimezone(timezone.utc)
        return delta.total_seconds() >= cooldown_min * 60
    return False


def send_email(cfg: dict[str, str], recipients: list[str], subject: str, body: str) -> None:
    host = env("SMTP_HOST") or cfg.get("SMTP_HOST", "")
    if not host:
        raise RuntimeError("SMTP_HOST не задан в .env")

    port = int(env("SMTP_PORT") or cfg.get("SMTP_PORT") or "587")
    user = env("SMTP_USER") or cfg.get("SMTP_USER", "")
    password = env("SMTP_PASSWORD") or cfg.get("SMTP_PASSWORD", "")
    from_addr = env("SMTP_FROM") or cfg.get("SMTP_FROM") or user or "monitor@chitatelstvo.ru"
    use_tls = (env("SMTP_USE_TLS") or cfg.get("SMTP_USE_TLS") or "1").lower() in ("1", "true", "yes")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(recipients)

    use_ssl = port == 465
    smtp_cls = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
    with smtp_cls(host, port, timeout=25) as server:
        if not use_ssl and use_tls:
            server.starttls(context=ssl.create_default_context())
        if user and password:
            server.login(user, password)
        server.sendmail(from_addr, recipients, msg.as_string())


def format_report(results: list[CheckResult], *, recovered: bool) -> str:
    lines = [
        "Читательство — мониторинг",
        f"Время (UTC): {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]
    if recovered:
        lines.append("Статус: восстановлено, все проверки прошли.")
    else:
        lines.append("Статус: проблема, требуется внимание.")
    lines.append("")
    for item in results:
        mark = "OK" if item.ok else "FAIL"
        lines.append(f"[{mark}] {item.name}: {item.detail}")
    lines.extend(
        [
            "",
            "Подсказки:",
            "  docker compose -f /root/chitatelstvo/docker-compose.yml ps",
            "  docker compose -f /root/chitatelstvo/docker-compose.yml logs --tail=80 api",
            "  curl -s https://api.chitatelstvo.ru/health",
            "",
            "Документация: docs/RESILIENCE.md",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    cfg = load_env_file(ROOT / ".env")
    results = run_checks(cfg)
    failed = [item for item in results if not item.ok]
    status = "fail" if failed else "ok"
    state = load_state()
    cooldown = cooldown_minutes(cfg)
    recipients = alert_emails(cfg)

    send = should_send_alert(state, failed=bool(failed), cooldown_min=cooldown)
    if send:
        recovered = status == "ok" and state.get("last_status") == "fail"
        subject = (
            "✅ Читательство: сервис восстановлен"
            if recovered
            else "🚨 Читательство: сбой мониторинга"
        )
        body = format_report(results, recovered=recovered)
        try:
            send_email(cfg, recipients, subject, body)
            print(f"ALERT_SENT to {', '.join(recipients)}")
        except Exception as exc:  # noqa: BLE001
            print(f"ALERT_FAILED: {exc}", file=sys.stderr)
            for item in results:
                mark = "OK" if item.ok else "FAIL"
                print(f"[{mark}] {item.name}: {item.detail}")
            return 2

    state["last_status"] = status
    if send:
        state["last_alert_at"] = datetime.now(timezone.utc).isoformat()
    state["last_check_at"] = datetime.now(timezone.utc).isoformat()
    state["last_failures"] = [item.name for item in failed]
    save_state(state)

    for item in results:
        mark = "OK" if item.ok else "FAIL"
        print(f"[{mark}] {item.name}: {item.detail}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
