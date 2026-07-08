# Пакет устойчивости Читательства

Минимальный набор, чтобы узнавать о сбоях по email (пока Telegram отключён).

## Что входит

| Компонент | Файл | Назначение |
|-----------|------|------------|
| Мониторинг | `scripts/monitor_health.py` | Проверки каждые 10 мин + письмо при сбое |
| Post-deploy | `scripts/post_deploy_check.py` | Smoke после деплоя |
| Установка cron | `scripts/resilience_install_monitor.sh` | Cron на сервере |
| Установка с ПК | `scripts/install_resilience.ps1` | Pull + cron + тест |

## Проверки

1. `GET /health` — API отвечает, `status: ok`
2. Статика: favicon, сундук, картинка урока
3. Docker: контейнеры `api`, `worker`, `postgres`, `redis` в Running

## Настройка (.env на сервере)

```env
PUBLIC_BASE_URL=https://api.chitatelstvo.ru

# SMTP (уже используется для писем родителям)
SMTP_HOST=smtp.mail.ru
SMTP_PORT=465
SMTP_USER=...
SMTP_PASSWORD=...
SMTP_FROM=info@chitatelstvo.ru
SMTP_USE_TLS=0

# Куда слать алерты (через запятую — несколько адресов)
MONITOR_ALERT_EMAIL=info@chitatelstvo.ru

# Не чаще одного письма о том же сбое (минуты)
MONITOR_COOLDOWN_MINUTES=30
```

## Установка на сервер

С Windows (после `git push`):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_resilience.ps1
```

Вручную на сервере:

```bash
cd /root/chitatelstvo
git pull origin main
bash scripts/resilience_install_monitor.sh
python3 scripts/post_deploy_check.py
```

## Логи и состояние

- Лог: `/var/log/chitatelstvo/monitor.log`
- Состояние (антиспам): `/var/lib/chitatelstvo-monitor/state.json`

Просмотр:

```bash
tail -f /var/log/chitatelstvo/monitor.log
crontab -l | grep chitatelstvo-monitor
```

Ручной прогон:

```bash
cd /root/chitatelstvo && python3 scripts/monitor_health.py
```

## Письма

- **Сбой** — при первой ошибке и далее раз в `MONITOR_COOLDOWN_MINUTES`, пока не починится
- **Восстановление** — одно письмо, когда все проверки снова зелёные

## Post-deploy

После каждого деплоя можно проверять:

```bash
python3 scripts/post_deploy_check.py
```

Код выхода `0` = `POST_DEPLOY_OK`, `1` = есть проблемы.

## Дальнейшие шаги (не в этом пакете)

- [ ] Nightly backup Postgres
- [ ] Telegram-алерты, когда заработает бот
- [ ] GitHub Action с внешним ping (если упал весь VPS)
