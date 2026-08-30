#!/usr/bin/env bash
# Cron: письма основателя после квиза (09:00–18:00 МСК).
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/chitatelstvo}"
LOG_DIR="/var/log/chitatelstvo"
CRON_TAG="chitatelstvo-founder-letter"

mkdir -p "$LOG_DIR"

CMD="cd ${PROJECT_DIR} && PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin /usr/bin/docker compose exec -T api python scripts/send_due_founder_letters.py >> ${LOG_DIR}/founder-letter.log 2>&1"
CRON_LINE="*/15 * * * * ${CMD} # ${CRON_TAG}"

TMP="$(mktemp)"
crontab -l 2>/dev/null | grep -v "${CRON_TAG}" > "$TMP" || true
echo "$CRON_LINE" >> "$TMP"
crontab "$TMP"
rm -f "$TMP"

echo "INSTALLED: founder letter cron every 15 minutes"
echo "LOG: ${LOG_DIR}/founder-letter.log"
