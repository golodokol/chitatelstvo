#!/usr/bin/env bash
# Ежедневный дамп PostgreSQL (запуск вручную или из cron).
set -euo pipefail

cd "$(dirname "$0")/.."

BACKUP_DIR="${BACKUP_DIR:-/root/chitatelstvo/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
PGUSER="${POSTGRES_USER:-literary}"
PGDB="${POSTGRES_DB:-literary_school}"

mkdir -p "$BACKUP_DIR"

STAMP="$(date +%Y%m%d_%H%M%S)"
FILE="$BACKUP_DIR/${PGDB}_${STAMP}.sql.gz"

if ! docker compose ps --status running postgres | grep -q postgres; then
  echo "ОШИБКА: контейнер postgres не запущен"
  exit 1
fi

docker compose exec -T postgres pg_dump -U "$PGUSER" -d "$PGDB" \
  --no-owner --no-acl --clean --if-exists | gzip > "$FILE"

find "$BACKUP_DIR" -name "${PGDB}_*.sql.gz" -type f -mtime +"$RETENTION_DAYS" -delete

SIZE="$(du -h "$FILE" | cut -f1)"
echo "OK: $FILE ($SIZE), храним последние $RETENTION_DAYS дн."
