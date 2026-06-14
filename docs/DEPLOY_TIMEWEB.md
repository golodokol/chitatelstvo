# Деплой Читательство на Timeweb

**Сервер:** `194.87.201.99`  
**Домен:** `chitatelstvo.ru`  
**API:** `https://api.chitatelstvo.ru`  
**Сайт Tilda:** `https://chitatelstvo.ru`

---

## Подробно: что делать после A-записи

A-запись вы уже сделали — это «указатель»: когда кто-то открывает `api.chitatelstvo.ru`, интернет направляет запрос на ваш сервер `194.87.201.99`.  
**Сам сервер пока пустой.** Дальше нужно зайти на него, загрузить код проекта и запустить.

### Общая схема

```
Вы (компьютер)  →  SSH / WinSCP  →  Сервер Timeweb
                                         ↓
                              Docker: API + база + worker
                                         ↓
                              nginx + HTTPS (api.chitatelstvo.ru)
                                         ↓
                              Tilda шлёт регистрации на API
```

### Шаг 0. Подождать и проверить DNS (15–60 мин)

На **вашем** компьютере откройте PowerShell и выполните:

```powershell
nslookup api.chitatelstvo.ru
```

В ответе должно быть `Address: 194.87.201.99`.  
Если ещё другой IP — подождите и повторите позже. Без этого HTTPS не выдадут.

---

### Шаг 1. Найти пароль от сервера

1. Зайдите в [timeweb.cloud](https://timeweb.cloud)
2. Откройте ваш сервер (VPS)
3. Найдите **пароль root** (в письме на почту или в карточке сервера → «Доступ» / «Пароль»)

Запишите: логин `root`, IP `194.87.201.99`, пароль.

---

### Шаг 2. Зайти на сервер (два способа)

**Способ А — терминал в Timeweb (проще, если SSH не получается):**

1. В панели Timeweb → ваш сервер → **Консоль** / **VNC** / **Терминал в браузере**
2. Откроется чёрное окно — вы уже на сервере, вводите команды там

**Способ Б — SSH с Windows:**

1. Откройте PowerShell (Win+X → «Терминал»)
2. Введите:

```powershell
ssh root@194.87.201.99
```

3. На вопрос `Are you sure...` напишите `yes` и Enter
4. Введите пароль root (символы **не видны** — это нормально) и Enter
5. Увидите что-то вроде `root@имя-сервера:~#` — вы на сервере

---

### Шаг 3. Установить программы на сервере

В терминале сервера (после входа) **скопируйте и вставьте** по одной строке или целиком:

```bash
apt update
apt install -y docker.io docker-compose-v2 git nginx certbot python3-certbot-nginx
systemctl enable docker nginx --now
```

Подождите 2–5 минут. Ошибок быть не должно.

---

### Шаг 4. Загрузить проект на сервер

**Через WinSCP (рекомендуется на Windows):**

1. Скачайте [WinSCP](https://winscp.net/eng/download.php) и установите
2. Новое подключение:
   - Протокол: **SFTP**
   - Хост: `194.87.201.99`
   - Пользователь: `root`
   - Пароль: ваш пароль root
3. Слева — ваш компьютер, справа — сервер
4. На сервере создайте папку `/root/chitatelstvo` (правый клик → Create directory)
5. Слева откройте `C:\Users\Оля\Documents\ЧИТАТЕЛЬСТВО`
6. Выделите **всё содержимое** папки (api, worker, docker-compose.yml, deploy, lessons и т.д.)
7. Перетащите на сервер в `/root/chitatelstvo`

Должно получиться: `/root/chitatelstvo/docker-compose.yml`, `/root/chitatelstvo/api/`, и т.д.

---

### Шаг 5. Настроить `.env` (пароли и секреты)

Снова в **терминале сервера**:

```bash
cd /root/chitatelstvo
cp deploy/env.production.example .env
nano .env
```

В `nano` замените строки (пример — придумайте свой пароль БД или используйте свой):

```env
WEBHOOK_SECRET=kiaxd8uU3nbdDHaxJaDtDDMG7BM4zohIAw2JTNaDRlgx
LESSON_SIGNING_SECRET=BxRsRQtBxNdrx83BOHDkcaJSF7FQPySj9x6FKsVOe4gx
TELEGRAM_WEBHOOK_SECRET=IvenFSvK7fyQiZIT2jOLc2vxXfPAx6GU5Q4pMUxsdxgx
DATABASE_URL=postgresql+psycopg://literary:МойСекретныйПароль123@postgres:5432/literary_school
```

`PUBLIC_BASE_URL` уже должен быть `https://api.chitatelstvo.ru` — не меняйте.

Сохранить в nano: **Ctrl+O**, Enter, выйти: **Ctrl+X**.

Тот же пароль `МойСекретныйПароль123` пропишите в docker-compose:

```bash
nano docker-compose.yml
```

Найдите строку `POSTGRES_PASSWORD: literary` и замените на **тот же** пароль, что в `DATABASE_URL`.

Сохранить: Ctrl+O, Enter, Ctrl+X.

---

### Шаг 6. Запустить проект

```bash
cd /root/chitatelstvo
docker compose up -d --build
```

Первый раз — 5–15 минут (скачиваются образы). Потом:

```bash
docker compose exec api python scripts/init_db.py
docker compose ps
curl http://127.0.0.1:8000/health
```

Ожидаемый ответ последней команды: `{"status":"ok"}` или похожий JSON.  
Если `docker compose ps` показывает api, worker, postgres, redis — всё **Up** — хорошо.

---

### Шаг 7. Включить HTTPS (чтобы Tilda могла слать данные)

```bash
cp /root/chitatelstvo/deploy/nginx-chitatelstvo.conf /etc/nginx/sites-available/chitatelstvo
ln -sf /etc/nginx/sites-available/chitatelstvo /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
certbot --nginx -d api.chitatelstvo.ru --agree-tos -m ваш@email.ru
```

На вопросы certbot — соглашайтесь (Enter).  
Проверка в браузере на **вашем** компьютере: откройте

`https://api.chitatelstvo.ru/health`

Должна открыться страница с `ok` / JSON. **Это главный признак, что деплой удался.**

**Админ-панель** (список регистраций): `https://api.chitatelstvo.ru/admin`  
В `.env` на сервере задайте `ADMIN_PASSWORD=ваш_пароль`, затем перезапустите API:

```bash
docker compose up -d --force-recreate api
```

После входа доступны таблица семей и экспорт CSV.

---

### Шаг 8. Подключить Tilda

В настройках формы регистрации на Tilda:

| Что | Значение |
|-----|----------|
| URL webhook | `https://api.chitatelstvo.ru/webhook/register` |
| Метод | POST |
| Заголовок | Имя: `X-Webhook-Secret`, значение: ваш `WEBHOOK_SECRET` из `.env` |

Поля формы — в `docs/TILDA_FORMS.md`.

Тест: отправьте форму с тестовыми данными → в ответе API должна быть ссылка на страницу прогресса.

---

### Шаг 9. Видео (когда будет готово)

В файле `lessons/kolobok.json` на сервере (через WinSCP) замените `KINESCOPE_VIDEO_ID` на ID ролика с Kinescope, затем в терминале:

```bash
cd /root/chitatelstvo
docker compose restart api worker
```

---

### Если что-то пошло не так

| Проблема | Что проверить |
|----------|----------------|
| `ssh` не подключается | Пароль, IP, или используйте консоль в панели Timeweb |
| `nslookup` не показывает ваш IP | Подождать DNS, проверить A-запись `api` |
| certbot ошибка | DNS ещё не обновился — подождать час |
| `curl /health` не работает | `docker compose logs api` — пришлите текст ошибки |
| Tilda не шлёт webhook | URL с `https://`, заголовок `X-Webhook-Secret` |

---

## Шаг 1. DNS (сделайте первым)

В панели, где управляете доменом `chitatelstvo.ru`, добавьте запись:

| Тип | Имя | Значение | TTL |
|-----|-----|----------|-----|
| **A** | `api` | `194.87.201.99` | 300–3600 |

Проверка (через 15–60 мин):

```powershell
nslookup api.chitatelstvo.ru
```

Должен показать `194.87.201.99`.

> Основной домен `chitatelstvo.ru` **не трогайте** — он остаётся на Tilda.

---

## Шаг 2. Подключение к серверу

Пароль root — из письма / панели Timeweb.

**Windows PowerShell:**

```powershell
ssh root@194.87.201.99
```

---

## Шаг 3. Установка Docker на сервере

```bash
apt update && apt install -y docker.io docker-compose-v2 git nginx certbot python3-certbot-nginx
systemctl enable docker nginx --now
```

---

## Шаг 4. Загрузка проекта

**Вариант А — с вашего компьютера (WinSCP / FileZilla):**

Скопируйте папку `ЧИТАТЕЛЬСТВО` в `/root/chitatelstvo` на сервере.

**Вариант Б — git (если есть репозиторий):**

```bash
mkdir -p /root/chitatelstvo
cd /root/chitatelstvo
git clone ВАШ_REPO .
```

---

## Шаг 5. Файл `.env` на сервере

```bash
cd /root/chitatelstvo
cp deploy/env.production.example .env
nano .env
```

Обязательно замените:
- `POSTGRES_PASSWORD` — свой длинный пароль
- `WEBHOOK_SECRET` — случайная строка 32+ символов
- `TELEGRAM_WEBHOOK_SECRET` — ещё одна случайная строка

Тот же `WEBHOOK_SECRET` потом укажете в Tilda.

---

## Шаг 6. Пароль Postgres в docker-compose

```bash
nano docker-compose.yml
```

Замените `POSTGRES_PASSWORD: literary` на **тот же пароль**, что в `.env`.

---

## Шаг 7. Запуск

```bash
cd /root/chitatelstvo
docker compose up -d --build
docker compose exec api python scripts/init_db.py
docker compose ps
curl http://127.0.0.1:8000/health
```

---

## Шаг 8. Nginx + HTTPS

```bash
cp /root/chitatelstvo/deploy/nginx-chitatelstvo.conf /etc/nginx/sites-available/chitatelstvo
ln -sf /etc/nginx/sites-available/chitatelstvo /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
certbot --nginx -d api.chitatelstvo.ru --non-interactive --agree-tos -m ВАШ_EMAIL
```

Проверка:

```bash
curl https://api.chitatelstvo.ru/health
```

---

## Шаг 9. Kinescope

В `lessons/kolobok.json` замените `KINESCOPE_VIDEO_ID` на ID ролика, затем:

```bash
docker compose restart api worker
```

---

## Шаг 10. Tilda — webhook регистрации

**URL:** `https://api.chitatelstvo.ru/webhook/register`  
**Метод:** POST  
**Заголовок:** `X-Webhook-Secret: значение из .env`

Поля формы — см. `docs/TILDA_FORMS.md`.

---

## Шаг 11. Telegram (когда будет VPN и бот)

Пока с VPS нет доступа к `api.telegram.org`, держите в `.env`:

```env
TELEGRAM_ENABLED=0
```

Уведомления о курсе идут на **личную страницу прогресса** и email. Каналы «Telegram» / «Email и Telegram» в форме автоматически переключаются на web/email.

Когда настроите VPN:

```env
TELEGRAM_ENABLED=1
TELEGRAM_BOT_TOKEN=...
TELEGRAM_BOT_USERNAME=ваш_бот
PUBLIC_BASE_URL=https://api.chitatelstvo.ru
```

```bash
docker compose up -d --force-recreate api worker
docker compose exec api python scripts/set_telegram_webhook.py
```

---

## Шаг 12. Volume Postgres и бэкапы

### Проверка volume

В `docker-compose.yml` данные Postgres лежат в именованном volume `pgdata` → `/var/lib/postgresql/data`.  
При `docker compose restart postgres` или `docker compose up -d` данные **не пропадают**.

На сервере после `git pull`:

```bash
cd /root/chitatelstvo
chmod +x scripts/*.sh
bash scripts/verify_postgres_volume.sh
```

Должно быть: volume найден, `families` отвечает, в конце `OK`.

Жёсткая проверка (по желанию): запомните число семей, затем `docker compose restart postgres` и снова `verify_postgres_volume.sh` — число не изменится.

### Ежедневный бэкап

```bash
cd /root/chitatelstvo
bash scripts/backup_postgres.sh
ls -lh backups/postgres/
```

Автоматически каждый день в 03:00:

```bash
bash scripts/install_backup_cron.sh
```

Дампы: `backups/postgres/literary_school_ГГГГММДД_ЧЧММСС.sql.gz`, хранятся **14 дней**.

Лог cron: `/var/log/chitatelstvo-backup.log`

Восстановление (если понадобится):

```bash
bash scripts/restore_postgres.sh backups/postgres/literary_school_20260609_030001.sql.gz
```

Рекомендуется раз в неделю скачивать последний `.sql.gz` на свой компьютер (WinSCP) или включить снимки диска в панели Timeweb.

---

## Полезные команды

```bash
cd /root/chitatelstvo
docker compose logs -f api      # логи API
docker compose logs -f worker # логи worker
docker compose restart api worker
bash scripts/backup_postgres.sh
```

---

## Чеклист

- [ ] DNS: `api.chitatelstvo.ru` → `194.87.201.99`
- [ ] `https://api.chitatelstvo.ru/health` отвечает
- [ ] `.env` с паролями и секретами
- [ ] `init_db.py` выполнен
- [ ] `verify_postgres_volume.sh` — OK
- [ ] `install_backup_cron.sh` — бэкап по расписанию
- [ ] Kinescope ID в `kolobok.json`
- [ ] Tilda webhook настроен
- [ ] Тест регистрации → страница прогресса → урок «Колобок»
