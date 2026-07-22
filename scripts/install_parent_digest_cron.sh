#!/usr/bin/env bash
# Cron: дневные сводки писем родителям (не чаще 1 раза в день).
# Запуск на сервере: bash scripts/install_parent_digest_cron.sh
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/chitatelstvo}"
LOG_DIR="/var/log/chitatelstvo"
CRON_TAG="chitatelstvo-parent-digest"

mkdir -p "$LOG_DIR"

DIGEST_CMD="cd ${PROJECT_DIR} && PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin /usr/bin/docker compose exec -T api python scripts/flush_parent_digests.py >> ${LOG_DIR}/parent-digest.log 2>&1"
# Каждые 30 минут — сводка уходит вечером или после паузы в занятиях
CRON_LINE="*/30 * * * * ${DIGEST_CMD} # ${CRON_TAG}"

TMP="$(mktemp)"
crontab -l 2>/dev/null | grep -v "${CRON_TAG}" > "$TMP" || true
echo "$CRON_LINE" >> "$TMP"
crontab "$TMP"
rm -f "$TMP"

echo "INSTALLED: parent digest cron every 30 minutes"
echo "LOG: ${LOG_DIR}/parent-digest.log"
cd "$PROJECT_DIR"
docker compose exec -T api python scripts/flush_parent_digests.py || true
