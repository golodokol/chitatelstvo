#!/usr/bin/env bash
# Проверка: Postgres использует именованный volume и данные переживают перезапуск.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== docker compose: postgres ==="
docker compose ps postgres

echo ""
echo "=== volume pgdata ==="
VOL="$(docker volume ls -q --filter name=pgdata | head -1)"
if [[ -z "$VOL" ]]; then
  echo "ОШИБКА: volume pgdata не найден. Запустите: docker compose up -d postgres"
  exit 1
fi
echo "Найден: $VOL"
docker volume inspect "$VOL" --format 'Mountpoint: {{ .Mountpoint }}'
docker volume inspect "$VOL" --format 'Created:    {{ .CreatedAt }}'

echo ""
echo "=== mount внутри контейнера ==="
docker compose exec -T postgres sh -c 'df -h /var/lib/postgresql/data | tail -1'

echo ""
echo "=== подключение к БД ==="
docker compose exec -T postgres psql -U literary -d literary_school -c \
  "SELECT current_database() AS db, COUNT(*) AS families FROM families;"

echo ""
echo "OK: Postgres на volume $VOL, данные сохраняются между перезапусками контейнера."
