#!/usr/bin/env bash
# Одноразовая настройка: привязка WinSCP-папки к GitHub + бэкапы Postgres.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/chitatelstvo}"
REPO_URL="${REPO_URL:-https://github.com/golodokol/chitatelstvo.git}"
BRANCH="${BRANCH:-main}"

cd "$PROJECT_DIR"

echo "=== резервная копия .env ==="
if [[ -f .env ]]; then
  cp .env "/root/.env.chitatelstvo.bak.$(date +%Y%m%d_%H%M%S)"
  cp .env /root/.env.chitatelstvo.bak
  echo "OK: .env сохранён в /root/.env.chitatelstvo.bak"
else
  echo "ВНИМАНИЕ: .env не найден"
fi

echo ""
echo "=== git ==="
if [[ ! -d .git ]]; then
  git init
  git remote add origin "$REPO_URL" 2>/dev/null || git remote set-url origin "$REPO_URL"
else
  git remote set-url origin "$REPO_URL" 2>/dev/null || git remote add origin "$REPO_URL"
fi

git fetch origin "$BRANCH"
git checkout -B "$BRANCH"
git reset --hard "origin/$BRANCH"

echo ""
echo "=== восстановление .env ==="
if [[ -f /root/.env.chitatelstvo.bak ]]; then
  cp /root/.env.chitatelstvo.bak .env
  echo "OK: .env восстановлен"
fi

chmod +x scripts/*.sh

echo ""
echo "=== проверка postgres volume ==="
bash scripts/verify_postgres_volume.sh

echo ""
echo "=== тестовый бэкап ==="
bash scripts/backup_postgres.sh

echo ""
echo "=== cron (03:00 ежедневно) ==="
bash scripts/install_backup_cron.sh

echo ""
echo "ГОТОВО: git привязан, бэкапы настроены."
echo "Дальше обновления: cd $PROJECT_DIR && git pull"
