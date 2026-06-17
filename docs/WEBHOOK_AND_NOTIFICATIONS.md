# Webhook, масштабирование и связь с родителями

Архитектура рассчитана на **1000+ семей**. Tilda → API → очередь → worker → БД + уведомления.

---

## Схема

```
Tilda (форма)
    │ POST + X-Webhook-Secret
    ▼
FastAPI (api/)          ← ответ 202 за < 300 мс
    │
    ▼
Redis (очередь)         ← можно запустить 2–4 worker
    │
    ▼
Worker (worker/)        ← gamification + Postgres + уведомления
    ├── PostgreSQL
    ├── LLM + RAG
    └── Родителям: web / email / telegram
```

---

## Каналы связи с родителями

| Канал | Код | Когда использовать |
|-------|-----|-------------------|
| **Личная страница** | `web` | Всегда включена. Ссылка в закладках — без Telegram и без почты |
| **Email** | `email` | Универсальная альтернатива Telegram |
| **Telegram** | `telegram` | Нужен `telegram_chat_id` (родитель написал боту /start) |
| **Оба** | `both` | Email + Telegram |

При регистрации поле `notification_channel` в форме Tilda.

**Важно:** даже при `web` все сообщения сохраняются на странице `/progress/{token}`. Email и Telegram — дополнительный push.

---

## Быстрый старт (локально)

### 1. Окружение

```powershell
cd "c:\Users\Оля\Documents\ЧИТАТЕЛЬСТВО"
copy .env.example .env
# Заполните WEBHOOK_SECRET и при необходимости OPENAI_API_KEY
```

### 2. Postgres + Redis

```powershell
docker compose up -d postgres redis
python scripts/init_db.py
```

### 3. API и worker (два терминала)

```powershell
# Терминал 1
uvicorn api.main:app --reload --port 8000

# Терминал 2
python worker/run_worker.py
```

### 4. Проверка

```powershell
curl http://localhost:8000/health
```

---

## Endpoints

### `POST /webhook/register`

Регистрация семьи. Заголовок: `X-Webhook-Secret: ваш_секрет`.

```json
{
  "parent_name": "Анна",
  "parent_email": "anna@example.com",
  "parent_telegram": "@anna",
  "telegram_chat_id": null,
  "notification_channel": "email",
  "child_name": "Маша",
  "child_age": 8
}
```

Ответ:

```json
{
  "family_id": "uuid",
  "child_id": "uuid",
  "progress_url": "https://school.example.com/progress/TOKEN",
  "notification_channel": "email"
}
```

Сохраните `child_id` и `progress_url` — они нужны для форм уроков и письма родителю.

### Повторная покупка (разовое → модуль)

Регистрация идентифицирует семью по **`parent_email` + `child_name`** (имя без учёта регистра).

| Ситуация | Поведение |
|----------|-----------|
| Тот же email и то же имя ребёнка | Тот же `progress_url`, тот же `child_id`, баллы и бейджи сохраняются |
| Тот же email, другое имя | Новый ребёнок в той же семье — **одна** ссылка `/progress/{token}` на всех детей |
| Новый email | Новая семья и новая ссылка |

При новой покупке модуля предыдущая активная запись (`enrollment`) закрывается (`completed`), создаётся новая — на странице прогресса отображаются уроки нового тарифа.

В ответе webhook поле `is_returning: true` — ребёнок уже был в системе (удобно для отладки и писем).

```json
{
  "family_id": "uuid",
  "child_id": "uuid",
  "progress_url": "https://school.example.com/progress/TOKEN",
  "notification_channel": "email",
  "module_id": 2,
  "module_title": "1 класс — модуль",
  "is_returning": true
}
```

### `POST /webhook/event`

Событие обучения. Ответ **202 Accepted** — обработка в фоне.

```json
{
  "event_type": "comprehension",
  "child_id": "uuid-ребёнка",
  "tale_title": "Колобок",
  "lesson_date": "2026-06-09",
  "notes": "Ответила на все вопросы"
}
```

Если `child_id` нет в форме — передайте `child_name` + `parent_email`.

### `GET /progress/{token}`

Личная страница прогресса для родителей (альтернатива мессенджерам).

---

## Настройка Tilda

### Форма регистрации

1. Поля с именами как в API (`parent_name`, `parent_email`, `child_name`, …).
2. Выпадающий список `notification_channel`: email / telegram / both / web.
3. Webhook URL: `https://ВАШ_ДОМЕН/webhook/register`
4. Заголовок: `X-Webhook-Secret` = значение из `.env`.

### Форма задания (на странице урока)

Ссылка на урок с ID ребёнка:

```
https://school.tilda.ws/lesson-kolobok?child=UUID
```

Скрытое поле формы `child_id` = параметр из URL.

Webhook URL: `https://ВАШ_ДОМЕН/webhook/event`

---

## Масштабирование до 1000

| Компонент | Старт | 1000 семей |
|-----------|-------|------------|
| API | 1 инстанс | 2 за балансировщиком |
| Worker | 1 процесс | `docker compose up --scale worker=4` |
| Postgres | 1 контейнер | Managed Postgres (Supabase, RDS) |
| Redis | 1 контейнер | Managed Redis |

Оценка нагрузки: ~20 000 событий за модуль, пики ~200–400 webhook/час.

---

## Привязка Telegram (автоматически)

1. Создайте бота через @BotFather → `TELEGRAM_BOT_TOKEN` и `TELEGRAM_BOT_USERNAME` в `.env`.
2. Установите webhook бота на API:
   ```powershell
   python scripts/set_telegram_webhook.py
   ```
3. Родитель после регистрации открывает **личную страницу** → **«Привязать Telegram»**.
4. Переходит в бота → **Start** → `chat_id` сохраняется в БД.

**Endpoints:**

| URL | Назначение |
|-----|------------|
| `POST /telegram/webhook` | Принимает сообщения от Telegram |
| `GET /link-telegram/{token}/page` | Страница с кнопкой привязки |
| `GET /link-telegram/{token}` | Редирект в `t.me/bot?start=link_...` |

Подробные поля форм Tilda: **`docs/TILDA_FORMS.md`**

---

## Email (SMTP)

Примеры провайдеров: Yandex 360, Mailgun, SendGrid, корпоративная почта.

```env
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=587
SMTP_USER=school@yandex.ru
SMTP_PASSWORD=пароль_приложения
SMTP_FROM=Литературная школа <school@yandex.ru>
```

Если SMTP не настроен — web-страница всё равно работает.

---

## Вход по email + OTP (приложение)

Для мобильного приложения и альтернативного входа без ссылки из письма.

| Метод | URL | Назначение |
|-------|-----|------------|
| POST | `/api/v1/auth/otp/request` | `{ "email": "anna@example.com" }` → код на почту |
| POST | `/api/v1/auth/otp/verify` | `{ "email": "...", "code": "482913" }` → JWT + список детей |
| GET | `/api/v1/auth/me` | `Authorization: Bearer …` → семья и дети |

**Выбор ребёнка:** клиент сохраняет `child_id` из списка `children` локально (в JWT не зашит).

**Env:** `JWT_SECRET` (или fallback на `WEBHOOK_SECRET`), `OTP_TTL_SECONDS=600`, SMTP обязателен для отправки кода.

```powershell
curl -X POST https://api.chitatelstvo.ru/api/v1/auth/otp/request -H "Content-Type: application/json" -d "{\"email\":\"anna@example.com\"}"
curl -X POST https://api.chitatelstvo.ru/api/v1/auth/otp/verify -H "Content-Type: application/json" -d "{\"email\":\"anna@example.com\",\"code\":\"123456\"}"
curl https://api.chitatelstvo.ru/api/v1/auth/me -H "Authorization: Bearer TOKEN"
```

Старая ссылка `/progress/{token}` продолжает работать параллельно.

---

## Деплой в прод

```powershell
docker compose up -d --build
docker compose exec api python scripts/init_db.py
```

Публичный URL через Railway / Render / VPS + nginx.  
`PUBLIC_BASE_URL` — ваш реальный домен (для ссылок в письмах и на странице прогресса).

---

## Безопасность

- `WEBHOOK_SECRET` в заголовке, не в URL
- Rate limit: 120 req/min на IP (настраивается)
- Идемпотентность: повторная отправка формы не дублирует баллы
- `progress_token` — 32 байта, угадать нельзя

---

## Структура файлов

```
ЧИТАТЕЛЬСТВО/
├── api/                 # FastAPI webhook + страница прогресса
├── worker/              # обработчик очереди
├── db/                  # Postgres schema + repository
├── job_queue/           # Redis
├── notifications/       # email, telegram, dispatcher
├── gamification/        # LLM + RAG (уже было)
├── templates/progress.html
├── templates/link_telegram.html
├── scripts/set_telegram_webhook.py
├── docker-compose.yml
├── docs/WEBHOOK_AND_NOTIFICATIONS.md
└── docs/TILDA_FORMS.md
```
