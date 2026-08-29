# Админ-уведомления об оплате: Telegram + MAX

После успешной регистрации через `POST /webhook/register` (оплата на Тильде → webhook)
сервер шлёт короткое сообщение админу в **Telegram** и/или **MAX**.

Повторный webhook (duplicate) **не** шлёт повторный алерт.

Код: `notifications/admin_alerts.py`, вызов из `services/registration.py`.

---

## 1. Telegram-бот

1. В Telegram (с VPN, если нужно): [@BotFather](https://t.me/BotFather) → `/newbot` → имя и username.
2. Скопируйте токен в `.env` на сервере:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC...
   TELEGRAM_BOT_USERNAME=YourSchoolBot
   ```
3. Напишите боту `/start` с аккаунта, куда нужны уведомления.
4. Узнайте свой `chat_id` (любой способ):
   - откройте `https://api.telegram.org/bot<TOKEN>/getUpdates` после `/start`, поле `message.chat.id`;
   - или бот вроде `@userinfobot`.
5. В `.env`:
   ```
   ADMIN_TELEGRAM_CHAT_ID=123456789
   ```
6. Перезапустите API.

Админ-алерты идут с `force=True` — **не зависят** от `TELEGRAM_ENABLED=0` (родительский канал можно оставить выключенным).

Если с VPS нет доступа к `api.telegram.org`, Telegram-алерты не дойдут — смотрите логи (`Admin Telegram alert failed`). Тогда опирайтесь на MAX и/или email-мониторинг.

Webhook родителя (`/telegram/webhook`) по-прежнему включается только при `TELEGRAM_ENABLED=1`.

---

## 2. MAX-бот

Официально: [MAX для разработчиков](https://dev.max.ru/docs-api), API-хост `platform-api2.max.ru`, токен в заголовке `Authorization`.

1. Создайте организацию / чат-бота в [MAX для бизнеса](https://business.max.ru/) или через платформу разработчика (нужна верификация юрлица/ИП по правилам MAX — уточните в их кабинете).
2. Скопируйте токен бота:
   ```
   MAX_BOT_TOKEN=...
   MAX_ENABLED=1
   MAX_WEBHOOK_SECRET=случайная-строка-A-Za-z0-9-
   ```
3. Подпишите webhook (один раз с машины с доступом в интернет):
   ```bash
   curl -X POST "https://platform-api2.max.ru/subscriptions" \
     -H "Authorization: $MAX_BOT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://api.chitatelstvo.ru/max/webhook",
       "update_types": ["message_created", "bot_started"],
       "secret": "ТОТ_ЖЕ_ЧТО_MAX_WEBHOOK_SECRET"
     }'
   ```
4. Откройте бота в MAX и нажмите «Начать» / напишите `/start`.
5. Бот ответит вашим `user_id`. Пропишите:
   ```
   ADMIN_MAX_USER_ID=...
   ```
   (альтернатива — `ADMIN_MAX_CHAT_ID` для канала/группы, если так настроите).
6. Перезапустите API.

На сервере endpoint: `POST /max/webhook` (`api/routes/max_bot.py`).

Если TLS к `platform-api2.max.ru` ругается на сертификат Минцифры — добавьте Russian Trusted Root CA в системное хранилище доверенных (см. документацию MAX).

---

## 3. Проверка

На сервере (из каталога проекта, с загруженным `.env`):

```bash
python scripts/test_admin_alerts.py
```

Или тестовая регистрация через админку / webhook с `WEBHOOK_SECRET` — после успешного enrollment должно прийти сообщение в оба канала (если оба настроены).

---

## Переменные `.env` (кратко)

| Переменная | Назначение |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Токен TG-бота |
| `ADMIN_TELEGRAM_CHAT_ID` | Куда слать оплату в TG |
| `MAX_ENABLED` | `1` включить MAX |
| `MAX_BOT_TOKEN` | Токен MAX-бота |
| `MAX_WEBHOOK_SECRET` | Секрет подписки webhook |
| `ADMIN_MAX_USER_ID` | Личный id в MAX |
| `ADMIN_MAX_CHAT_ID` | Опционально chat/канал |
