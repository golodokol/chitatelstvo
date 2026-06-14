# ST100 + оплата + webhook — все 18 модулей

Zero Block выбирает **класс + тариф + дату (+ сказку)** → в hidden-поля ST100 попадают `module_id` (1–18), `chosen_stage`, `chosen_tale_number`.

---

## Шаг 1. Три товара в каталоге Tilda

**Каталог** → создайте **3 услуги** (названия **точно** так):

| Название | Цена |
|----------|------|
| Читательство · Разовое | 1 490 ₽ |
| Читательство · Индивидуальное | 1 990 ₽ |
| Читательство · С преподавателем | 4 990 ₽ |

Класс (1–4, 6–8, 9–11) **не** отдельный товар — он в `module_id`.

---

## Шаг 2. Блок ST100 на главной

1. **+ Блок** → **Магазин** → **ST100** «Корзина с формой заказа»
2. Поставьте **внизу страницы** (под Zero Block)
3. **Настройки ST100** → включите **«Открывать корзину после выбора товара»**

### Поля формы в ST100 (Variable name — копируйте точно!)

| Подпись в Tilda | Variable name | Тип | Обяз. |
|-----------------|---------------|-----|-------|
| Имя родителя | `parent_name` | text | да |
| Email | `parent_email` | email | да |
| Telegram | `parent_telegram` | text | нет |
| Имя ребёнка | `child_name` | text | да |
| Возраст ребёнка | `child_age` | number | нет |
| Как присылать новости | `notification_channel` | select | да |
| *(скрыто)* | `module_id` | hidden | — |
| *(скрыто)* | `chosen_stage` | hidden | — |
| *(скрыто)* | `chosen_tale_number` | hidden | — |

### Select `notification_channel` — значения (value)

| Подпись | value |
|---------|-------|
| На email | `email` |
| В Telegram | `telegram` |
| Email и Telegram | `both` |
| Только личная страница | `web` |

Кнопка в корзине: **Оплатить**

---

## Шаг 3. Webhook (после оплаты)

**Настройки сайта** → **Формы** → **Webhook**:

```
URL:    https://api.chitatelstvo.ru/webhook/register
Method: POST
Header: X-Webhook-Secret: <WEBHOOK_SECRET из .env на сервере>
```

В **контенте ST100** подключите этот webhook.

Включите **«Отправлять только после оплаты»** (если есть).

Success URL: страница «Спасибо» (например `/spasibo`).

---

## Шаг 4. Т‑Банк

См. `docs/TILDA_PAYMENT_TBANK.md` — URL уведомлений: `https://forms.tildacdn.com/payment/tinkoff/`

---

## Таблица module_id (все модули)

| Класс / группа | Разовое | Индивидуальное | С преподавателем |
|----------------|---------|----------------|------------------|
| 1 класс | 1 | 2 | 3 |
| 2 класс | 4 | 5 | 6 |
| 3 класс | 7 | 8 | 9 |
| 4 класс | 10 | 11 | 12 |
| 6–8 лет | 13 | 14 | 15 |
| 9–11 лет | 16 | 17 | 18 |

**chosen_stage:** `1` = 22 июня, `2` = 20 июля — для **всех** тарифов.

**chosen_tale_number:** `1`–`4` — **только** для разового (module_id нечётные: 1,4,7…).

Zero Block заполняет эти поля автоматически при нажатии «Записаться».

---

## Шаг 5. Проверка

1. На сайте: 2 класс → Индивидуальное → 22 июня → **Записаться**
2. Корзина: **1 990 ₽**, поля контактов
3. Оплата (тестовая карта Т‑Банка)
4. Письмо на email + `progress_url` в webhook-ответе
5. В CRM Tilda в заявке: `module_id=5`, `chosen_stage=1`

Тест API без Tilda:

```powershell
curl -X POST "https://api.chitatelstvo.ru/webhook/register" `
  -H "Content-Type: application/json" `
  -H "X-Webhook-Secret: ВАШ_СЕКРЕТ" `
  -d "{\"parent_name\":\"Тест\",\"parent_email\":\"test@example.com\",\"child_name\":\"Маша\",\"child_age\":8,\"notification_channel\":\"email\",\"module_id\":2,\"chosen_stage\":\"1\"}"
```

Ответ: `"module_id": 2`, `"module_title": "Индивидуальное обучение, 1 класс"`.

---

## Если hidden-поля пустые в CRM

1. В ST100 есть 3 hidden с **точными** именами `module_id`, `chosen_stage`, `chosen_tale_number`
2. В Zero Block вставлен актуальный JS (`03-js.txt` или `00-all-in-one.html`)
3. Родитель нажал «Записаться» **после** выбора класса и даты
4. Опубликована **новая** версия страницы
