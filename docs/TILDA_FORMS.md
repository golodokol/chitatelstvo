# Шаблоны форм Tilda — Читательство

Готовые поля и настройки webhook для литературной школы **Читательство**.

**Базовый URL API:** `https://ВАШ_ДОМЕН`  
**Заголовок для всех webhook:** `X-Webhook-Secret: значение из .env`

---

## 1. Форма регистрации (набор в школу)

### Поля формы

Имена полей (**Variable name** в Tilda) должны совпадать точно:

| Поле в Tilda | Variable name | Тип | Обязательное |
|--------------|---------------|-----|--------------|
| Имя родителя | `parent_name` | text | да |
| Email | `parent_email` | email | да |
| Telegram (ник, опционально) | `parent_telegram` | text | нет |
| Имя ребёнка | `child_name` | text | да |
| Возраст ребёнка | `child_age` | number | нет |
| Как присылать новости | `notification_channel` | select | да |
| **Модуль (ID из каталога)** | `module_id` | number | нет* |
| **Период (дата старта)** | `chosen_stage` | hidden | нет* |
| **№ сказки (для разового)** | `chosen_tale_number` | hidden | нет* |

**Кнопка:** `Оплатить` — в Zero Block открывает корзину ST100; оплата картой через **Т‑Банк**. См. `docs/TILDA_PAYMENT_TBANK.md`.

\* `module_id` — номер модуля из `catalog/modules.json` (1–18). Без него — режим пилота (только legacy-уроки).

Для **любого тарифа** передайте `chosen_stage` — `1` (6 июля) или `2` (27 июля). На сайте родитель видит даты, не «этап».

Для **разового занятия** дополнительно:
- `chosen_tale_number` — `1`, `2`, `3` или `4` (сказка выбранного периода)

Пример ID модулей 1 класса: `1` разовое, `2` индивидуальное, `3` с преподавателем.

**На лендинге каждого тарифа** добавьте скрытое поле `module_id` с нужным числом (см. `catalog/modules.json`). Для разового — ещё поля выбора этапа и сказки (select или radio).

| Группа | Разовое | Индивидуальное | С преподавателем |
|--------|---------|----------------|------------------|
| 1 класс | 1 | 2 | 3 |
| 2 класс | 4 | 5 | 6 |
| 3 класс | 7 | 8 | 9 |
| 4 класс | 10 | 11 | 12 |
| 6–8 лет (внешкольники) | 13 | 14 | 15 |
| 9–11 лет (внешкольники) | 16 | 17 | 18 |

> **База данных:** на сервере один раз выполните `db/migrations/001_enrollments.sql` (или разверните свежий `db/schema.sql`).

### Значения select `notification_channel`

```
email — на email
telegram — в Telegram (после привязки бота)
both — email и Telegram
web — только личная страница (без писем)
```

В Tilda для select отправляйте **код**, не подпись. Пример опций:

| Подпись для родителя | Значение (value) |
|----------------------|------------------|
| На email | `email` |
| В Telegram | `telegram` |
| Email и Telegram | `both` |
| Только личная страница | `web` |

### Webhook

- **URL:** `https://ВАШ_ДОМЕН/webhook/register`
- **Метод:** POST
- **Content-Type:** application/json (если Tilda отдаёт JSON) или form-urlencoded — API принимает оба через FastAPI body parsing; для Tilda Zero Block используйте встроенный webhook с полями 1:1.

### После успешной регистрации

API возвращает:

```json
{
  "child_id": "uuid — сохраните для форм уроков",
  "module_id": 2,
  "module_title": "Индивидуальное обучение, 1 класс",
  "progress_url": "личная страница родителя",
  "link_telegram_page": "страница привязки Telegram",
  "telegram_deep_link": "ссылка t.me/bot?start=..."
}
```

**На странице «Спасибо» в Tilda** покажите родителю:
1. Ссылку на `progress_url` (кнопка «Мой прогресс»)
2. Если выбран telegram/both — кнопку «Привязать Telegram» → `link_telegram_page`

Готовые тексты для всех страниц: **`docs/TILDA_TEXTS.md`**

**Пошагово по каждому модулю и уроку:** **`docs/TILDA_SETUP_FULL.md`**

**Готовая первая страница (1 класс · индивидуальное):** **`docs/TILDA_PAGE_1_KLASS_INDIVIDUALNOE.md`**

---

## 2. Урок в Читательстве — плеер (баллы автоматически)

Видео и квизы засчитываются **сами** в плеере — родителю не нужны формы.

| Шаг | Баллы | Как |
|-----|-------|-----|
| Видео ≥80% | +2 | Автоматически |
| Квиз «понимание» | +2 | Автоматически |
| Квиз «смысл» | +2 | Автоматически |
| Творчество | +3 | Кнопка в плеере |
| Встреча | +2 | Кнопка в плеере |

Родитель: страница прогресса → кнопка сказки (например «Колобок»).

На Tilda — кнопка **«Открыть урок»** → страница прогресса. Подробнее: `docs/LESSON_PLAYER.md`, тексты: `docs/TILDA_TEXTS.md`.

---

## 3. Форма «Ручная отметка» (только творчество и встреча)

Опционально на Tilda, если не используете кнопки в плеере.

### URL страницы урока

```
https://school.tilda.ws/urok-kolobok?child=UUID_РЕБЁНКА
```

Параметр `child` передаётся из письма после регистрации или из личного кабинета.

### Скрытые поля (Hidden)

| Variable name | Откуда взять значение |
|---------------|----------------------|
| `child_id` | из URL `?child=...` (Tilda: JS или Zero Block) |
| `tale_title` | константа страницы, напр. `Колобок` |
| `module_week` | константа, напр. `1` |
| `lesson_date` | константа или сегодня |

### Видимые поля

| Поле | Variable name | Тип |
|------|---------------|-----|
| Тип задания | `event_type` | select |
| Комментарий / ответ | `notes` | textarea |

### Значения `event_type`

| Подпись | value |
|---------|-------|
| Первое задание | `first_task` |
| Урок + рабочий лист | `lesson_complete` |
| Понимание текста | `comprehension` |
| Анализ смысла | `meaning_analysis` |
| Творческое задание | `creative_task` |
| Пересказ | `retelling` |
| Мини-проверка | `mini_check` |
| Живая встреча | `live_meeting` |
| Вопрос / инициатива | `initiative` |

### Webhook

- **URL:** `https://ВАШ_ДОМЕН/webhook/event`
- **Метод:** POST
- **Заголовок:** `X-Webhook-Secret`

### Страница «Спасибо»

Текст: «Задание принято! Награда появится через минуту на личной странице и в выбранном канале связи.»

---

## 3. Подстановка child_id из URL в Tilda (Zero Block)

В блоке формы добавьте перед отправкой:

```html
<script>
(function () {
  var params = new URLSearchParams(window.location.search);
  var childId = params.get('child');
  if (!childId) return;
  var input = document.querySelector('input[name="child_id"]');
  if (input) input.value = childId;
})();
</script>
```

Скрытое поле: `<input type="hidden" name="child_id" value="">`

---

## 4. Запасной вариант без child_id в URL

Если скрытое поле недоступно, добавьте в форму:

| Variable name | Пример |
|---------------|--------|
| `child_name` | Маша |
| `parent_email` | anna@example.com |

API найдёт ребёнка по паре имя + email родителя.

---

## 5. Привязка Telegram (без полей в Tilda)

После регистрации родитель:

1. Открывает `progress_url`
2. Нажимает **«Привязать Telegram»**
3. В боте жмёт **Start** — `chat_id` сохраняется автоматически

Или сразу с страницы «Спасибо» — ссылка `link_telegram_page` из ответа API.

### Настройка бота (один раз)

```powershell
# В .env: TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_USERNAME, TELEGRAM_WEBHOOK_SECRET, PUBLIC_BASE_URL
python scripts/set_telegram_webhook.py
```

---

## 6. Чеклист перед запуском

- [ ] `WEBHOOK_SECRET` в `.env` и в заголовке Tilda
- [ ] `PUBLIC_BASE_URL` — реальный домен API
- [ ] Форма регистрации → `/webhook/register`
- [ ] Форма задания → `/webhook/event` + `child_id` в URL
- [ ] Страница «Спасибо» со ссылкой на прогресс
- [ ] Для Telegram: бот создан, webhook установлен
- [ ] Для email: SMTP в `.env`

---

## 7. Тестовые запросы (curl)

**Регистрация:**

```powershell
curl -X POST "http://localhost:8000/webhook/register" `
  -H "Content-Type: application/json" `
  -H "X-Webhook-Secret: ваш_секрет" `
  -d "@examples/webhook_register.json"
```

**Задание:**

```powershell
curl -X POST "http://localhost:8000/webhook/event" `
  -H "Content-Type: application/json" `
  -H "X-Webhook-Secret: ваш_секрет" `
  -d "@examples/webhook_event.json"
```
