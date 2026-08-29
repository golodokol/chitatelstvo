# Аудит → фикс → деплой (сервер + Tilda)

Версия ассетов: **`?v=20260828a`**

## На сервере (делает агент / DevOps)

1. **nginx** — применить `deploy/nginx-cors-snippet.conf` в `location /assets/` (HTTP и HTTPS), затем:
   ```bash
   nginx -t && systemctl reload nginx
   ```
2. **Ассеты** — скопировать на `api.chitatelstvo.ru/assets/` (`/var/www/chitatelstvo-assets/`):
   - `chit-zero.js`, `chit-zero.css`
   - `chit-quiz.js`, `chit-quiz.css`
   - `chit-pay-page.js`
   - `order-config.json`
   - при необходимости `course-pages/*`

   Источник в репо: `docs/tilda-zero-main/` (+ `docs/course-pages/`).

## В Tilda (вручную)

1. **Главная** — обновить Zero Block + HEAD (`?v=20260828a`), опубликовать.
2. **/oplata** — HEAD из `seo-ai/15-oplata-HEAD.html` (если есть) или скрипт `chit-pay-page.js?v=20260828a`; подпись поля «Дата рождения ребёнка»; галочка согласия **не** отмечена по умолчанию.
3. **Метрика** — убрать дубль `tag.js`; маскирование PII в Вебвизоре; цель JS-событие **`order_config_error`**.

## Проверка после деплоя

- [ ] Консоль главной: нет CORS на `order-config.json`
- [ ] Запись → `/oplata` без `parent_name` / `child_birth_date` в URL
- [ ] Поля на оплате заполняются из `sessionStorage`
- [ ] Мобильный ≤820px — бургер-меню
- [ ] Квиз — прогресс до 100%
