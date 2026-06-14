#!/usr/bin/env bash
# HTTPS для api.chitatelstvo.ru (Let's Encrypt + nginx)
set -euo pipefail

DOMAIN="api.chitatelstvo.ru"
PROJECT_DIR="${PROJECT_DIR:-/root/chitatelstvo}"
EMAIL="${CERTBOT_EMAIL:-}"

if [[ -z "$EMAIL" ]]; then
  echo "ERROR: set CERTBOT_EMAIL (e.g. info@chitatelstvo.ru)"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq nginx certbot python3-certbot-nginx

if [[ -f "$PROJECT_DIR/deploy/nginx-chitatelstvo.conf" ]]; then
  cp "$PROJECT_DIR/deploy/nginx-chitatelstvo.conf" /etc/nginx/sites-available/chitatelstvo
  ln -sf /etc/nginx/sites-available/chitatelstvo /etc/nginx/sites-enabled/chitatelstvo
  rm -f /etc/nginx/sites-enabled/default
fi

nginx -t
systemctl enable nginx
systemctl reload nginx

if certbot certificates 2>/dev/null | grep -q "Certificate Name: $DOMAIN"; then
  certbot renew --dry-run
  echo "Certificate already exists for $DOMAIN"
else
  certbot --nginx -d "$DOMAIN" \
    --non-interactive --agree-tos -m "$EMAIL" \
    --redirect
fi

echo "--- checks ---"
curl -fsS "https://${DOMAIN}/health" | head -c 200
echo ""
curl -fsSI "https://${DOMAIN}/assets/logo-chitatelstvo.png" | head -n 3
echo "OK: HTTPS enabled for $DOMAIN"
