#!/usr/bin/env bash
# Установка cron-мониторинга на сервере. Запуск: bash scripts/resilience_install_monitor.sh
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/chitatelstvo}"
LOG_DIR="/var/log/chitatelstvo"
STATE_DIR="/var/lib/chitatelstvo-monitor"
CRON_TAG="chitatelstvo-monitor"

mkdir -p "$LOG_DIR" "$STATE_DIR"
chmod 755 "$LOG_DIR" "$STATE_DIR"

MONITOR_CMD="cd ${PROJECT_DIR} && /usr/bin/python3 scripts/monitor_health.py >> ${LOG_DIR}/monitor.log 2>&1"
CRON_LINE="*/10 * * * * ${MONITOR_CMD} # ${CRON_TAG}"

TMP="$(mktemp)"
crontab -l 2>/dev/null | grep -v "${CRON_TAG}" > "$TMP" || true
echo "$CRON_LINE" >> "$TMP"
crontab "$TMP"
rm -f "$TMP"

echo "INSTALLED: cron every 10 minutes"
echo "LOG: ${LOG_DIR}/monitor.log"
echo "STATE: ${STATE_DIR}/state.json"
echo "Test run:"
cd "$PROJECT_DIR"
/usr/bin/python3 scripts/monitor_health.py || true
