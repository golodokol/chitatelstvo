#!/usr/bin/env bash
# Автозапуск docker compose после перезагрузки VPS.
# Запуск на сервере: bash scripts/install_compose_autostart.sh
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/root/chitatelstvo}"
SERVICE_NAME="chitatelstvo-compose.service"
SERVICE_SRC="${PROJECT_DIR}/deploy/chitatelstvo-compose.service"
SERVICE_DST="/etc/systemd/system/${SERVICE_NAME}"

if [[ ! -f "$SERVICE_SRC" ]]; then
  echo "Missing ${SERVICE_SRC}" >&2
  exit 1
fi

systemctl enable docker
systemctl start docker

install -m 644 "$SERVICE_SRC" "$SERVICE_DST"
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

cd "$PROJECT_DIR"
docker compose up -d --remove-orphans
docker compose ps

echo "OK: ${SERVICE_NAME} enabled"
echo "Check: systemctl status ${SERVICE_NAME}"
echo "Health: curl -sS http://127.0.0.1:8000/health"
