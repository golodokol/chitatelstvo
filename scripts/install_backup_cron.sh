#!/usr/bin/env bash
# Установить cron: бэкап Postgres каждый день в 03:00 (МСК — время сервера).
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_SCRIPT="$PROJECT_DIR/scripts/backup_postgres.sh"
LOG_FILE="/var/log/chitatelstvo-backup.log"
CRON_LINE="0 3 * * * $BACKUP_SCRIPT >> $LOG_FILE 2>&1"

chmod +x "$BACKUP_SCRIPT"
mkdir -p "$PROJECT_DIR/backups/postgres"

if crontab -l 2>/dev/null | grep -Fq "$BACKUP_SCRIPT"; then
  echo "Cron уже настроен:"
  crontab -l | grep "$BACKUP_SCRIPT"
  exit 0
fi

(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -

echo "Добавлено в crontab:"
echo "  $CRON_LINE"
echo ""
echo "Проверка вручную:"
echo "  $BACKUP_SCRIPT"
echo "  ls -lh $PROJECT_DIR/backups/postgres/"
