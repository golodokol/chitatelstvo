#!/usr/bin/env bash
# Восстановление БД из .sql или .sql.gz (осторожно: перезаписывает текущие данные).
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Использование: $0 путь/к/дампу.sql.gz"
  exit 1
fi

DUMP="$1"
cd "$(dirname "$0")/.."

PGUSER="${POSTGRES_USER:-literary}"
PGDB="${POSTGRES_DB:-literary_school}"

if [[ ! -f "$DUMP" ]]; then
  echo "Файл не найден: $DUMP"
  exit 1
fi

echo "Восстановление $PGDB из $DUMP"
read -r -p "Продолжить? [y/N] " ans
[[ "$ans" == "y" || "$ans" == "Y" ]] || exit 0

if [[ "$DUMP" == *.gz ]]; then
  gunzip -c "$DUMP" | docker compose exec -T postgres psql -U "$PGUSER" -d "$PGDB"
else
  docker compose exec -T postgres psql -U "$PGUSER" -d "$PGDB" < "$DUMP"
fi

echo "OK: восстановление завершено"
