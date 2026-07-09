# Страницы курсов на основном сайте (Tilda + оплата)

Как вынести лендинги из `docs/course-pages/` на прод и связать с **Zero Block** главной и страницей **`chitatelstvo.ru/oplata`**.

---

## Схема (как это работает)

```
Главная (Zero Block)          Страница курса (API)              Оплата (Tilda)
chitatelstvo.ru/        →     api…/course-pages/grade-1.html  →  chitatelstvo.ru/oplata
  #programs — обзор              #enroll — форма записи            ST100 + ST205 (скрыты)
  #program — быстрая запись      «Записаться»                      chit-pay-page.js
```

**Оплата одна на весь сайт** — на `/oplata`. На страницах курсов **нет** ST100.

При нажатии «Записаться» страница курса:

1. кладёт данные в `sessionStorage` (`chit_checkout`);
2. дублирует их в query-string;
3. открывает `https://chitatelstvo.ru/oplata?...`

Скрипт `chit-pay-page.js` на `/oplata` читает эти данные, подставляет в скрытые поля ST100, применяет промокод и открывает корзину Tilda.

**Класс и тариф** для API — не отдельные товары в каталоге, а поле **`module_id` (1–18)**. Цена — одна из трёх услуг (990 / 1990 / 4990 ₽).

---

## Шаг 1. Выложить файлы на сервер

Папка в репозитории: `docs/course-pages/`

| Файл | Назначение |
|------|------------|
| `grade-1.html` … `extra-9-11.html` | 6 страниц курсов |
| `index.html` | хаб «все программы» |
| `chit-course-data.js` | программы, `module_id`, цены |
| `chit-course-page.js` | вёрстка + форма + редирект на оплату |
| `chit-course-page.css` | стили |

### Куда копировать

На сервере (рядом с `chit-zero.js`):

```text
/var/www/chitatelstvo-assets/course-pages/
```

Публичные URL:

```text
https://api.chitatelstvo.ru/assets/course-pages/grade-1.html
https://api.chitatelstvo.ru/assets/course-pages/index.html
…
```

### Команда на сервере (после `git pull`)

```bash
mkdir -p /var/www/chitatelstvo-assets/course-pages
cp -r docs/course-pages/* /var/www/chitatelstvo-assets/course-pages/
```

Имеет смысл добавить эту строку в `scripts/deploy_quick.ps1` рядом с копированием `chit-zero.js`.

### Проверка

Откройте в браузере:

- `https://api.chitatelstvo.ru/assets/course-pages/grade-1.html`
- баннер, программа, форма «Записаться» без ошибок в консоли (F12)

---

## Шаг 2. Страница оплаты `/oplata` (если ещё не настроена)

Подробно: `docs/tilda-zero-main/PAY-PAGE.md` и `ST100_SETUP.md`.

### Минимальный набор на `chitatelstvo.ru/oplata`

| Блок | Зачем |
|------|--------|
| **ST100** «Корзина с формой» | оплата + webhook |
| **ST205** × 3 | привязка каталога (товары можно скрыть скриптом) |
| **HTML (T123)** внизу | скрипт оплаты |

В HTML-блоке **только**:

```html
<script src="https://api.chitatelstvo.ru/assets/chit-pay-page.js?v=8"></script>
```

### Три услуги в каталоге Tilda (названия **точно** так)

| Название | Цена | Product ID |
|----------|------|------------|
| Читательство · Разовое | 1 490 ₽ | `797131986522` |
| Читательство · Индивидуальное | 1 990 ₽ | `206548598642` |
| Читательство · С преподавателем | 4 990 ₽ | `956231952022` |

Символ **`·`** (средняя точка) обязателен.

### Скрытые поля в ST100 на `/oplata`

Variable name **латиницей, с подчёркиваниями**:

| Variable name | Откуда берётся |
|---------------|----------------|
| `parent_name` | форма на странице курса (или главной) |
| `parent_email` | то же |
| `parent_telegram` | то же |
| `child_name` | то же |
| `child_birth_date` | страница курса (ISO `YYYY-MM-DD`) |
| `child_age` | считает `chit-pay-page.js` из даты рождения |
| `module_id` | **1–18** — см. таблицу ниже |
| `chosen_stage` | `1` = 6 июля, `2` = 3 августа |
| `chosen_tale_number` | `1`–`4`, только для тарифа «Разовое» |
| `promo_code` | промокод из формы |
| `notification_channel` | на курсе всегда `email` |
| `legal_consent` | checkbox в ST100 (если есть) |

**Webhook:** `POST https://api.chitatelstvo.ru/webhook/register`  
Заголовок: `X-Webhook-Secret` = значение из `.env` на сервере.  
**Success URL:** `https://api.chitatelstvo.ru/spasibo`  
Отправка **только после оплаты**.

### Промокод

Скидку считает **Tilda**, не наш API.

1. Настройки сайта → Платёжные системы → **Промокоды** — создать код.
2. ST100 на **`/oplata`** → Настройки → включить **«Промокоды»** → Опубликовать.
3. Скрытое поле `promo_code` в ST100 (без второго видимого поля «Промокод»).

Проверка: ввести код на странице курса → на `/oplata` сумма в корзине со скидкой.

---

## Шаг 3. Таблица `module_id` (должна совпадать везде)

И в `chit-course-data.js`, и в `chit-zero.src.js`, и в webhook:

| Программа | Разовое | Индивидуальное | С преподавателем |
|-----------|---------|----------------|------------------|
| 1 класс | 1 | 2 | 3 |
| 2 класс | 4 | 5 | 6 |
| 3 класс | 7 | 8 | 9 |
| 4 класс | 10 | 11 | 12 |
| 6–8 лет | 13 | 14 | 15 |
| 9–11 лет | 16 | 17 | 18 |

`chosen_stage`: **1** = старт 6 июля, **2** = старт 3 августа.  
`chosen_tale_number`: только для **Разового** (нечётные `module_id`: 1, 4, 7…).

---

## Шаг 4. Ссылки с главной (Zero Block)

Главная по-прежнему: Zero Block + (опционально) ST100.  
Страницы курсов — **отдельные URL**, не вставляются внутрь Zero Block целиком (слишком тяжёлый HTML).

### Вариант A — красивые URL на `chitatelstvo.ru` (рекомендуется)

Для каждого курса — **новая страница Tilda** без меню:

| Страница в Tilda | URL (slug) | Куда ведёт |
|------------------|------------|------------|
| Летний курс · 1 класс | `1-klass` | редирект на API |
| … | `2-klass` … | … |
| Внеклассное 6–8 | `6-8-let` | … |
| Внеклассное 9–11 | `9-11-let` | … |
| Все программы | `programmy` | `…/course-pages/index.html` |

Блок **T123 HTML** на каждой странице (пример для 1 класса):

```html
<meta http-equiv="refresh" content="0;url=https://api.chitatelstvo.ru/assets/course-pages/grade-1.html">
<script>location.replace('https://api.chitatelstvo.ru/assets/course-pages/grade-1.html');</script>
<p style="font-family:sans-serif;text-align:center;padding:40px">
  <a href="https://api.chitatelstvo.ru/assets/course-pages/grade-1.html">Открыть программу 1 класса →</a>
</p>
```

В итоге в меню и на главной ссылка: `https://chitatelstvo.ru/1-klass`.

### Вариант B — прямые ссылки на API

Без отдельных страниц Tilda:

```text
https://api.chitatelstvo.ru/assets/course-pages/grade-1.html
```

Подходит для кнопок «Подробнее» в аккордеоне программ.

### Что добавить в Zero Block (`00-tilda-zero-upload.html`)

**1. Ссылки в секции `#programs`** — под заголовком аккордеона или в `buildAccordion` в `chit-zero.src.js`:

```javascript
var COURSE_PAGES = {
  'grade-1': 'https://chitatelstvo.ru/1-klass',
  'grade-2': 'https://chitatelstvo.ru/2-klass',
  'grade-3': 'https://chitatelstvo.ru/3-klass',
  'grade-4': 'https://chitatelstvo.ru/4-klass',
  'extra-6-8': 'https://chitatelstvo.ru/6-8-let',
  'extra-9-11': 'https://chitatelstvo.ru/9-11-let'
};
```

В `buildAccordion` после заголовка класса:

```html
<p class="prog-course-link">
  <a href="…">Подробнее о курсе →</a>
</p>
```

**2. Кнопка в hero** «Смотреть программы» может вести на:

- `https://chitatelstvo.ru/programmy` или
- `https://api.chitatelstvo.ru/assets/course-pages/index.html`

**3. Главная запись `#program`** — можно **оставить** (быстрый путь) или убрать и вести всех на страницы курсов. Оба варианта ведут на **тот же** `/oplata` и те же `module_id`.

После правок Zero Block: пересобрать `00-tilda-zero-upload.html` (`python scripts/build_tilda_upload.py`) → вставить в Tilda → **Опубликовать**.

---

## Шаг 5. Проверка оплаты со страницы курса

1. Откройте `…/course-pages/grade-1.html`.
2. Тарифы → **Индивидуальное** → **Старт 6 июля**.
3. Заполните контакты, при желании промокод.
4. **Записаться** → переход на `chitatelstvo.ru/oplata`.
5. На `/oplata`: корзина **1 990 ₽**, товар «Читательство · Индивидуальное».
6. В CRM Tilda после тестовой оплаты: `module_id=2`, `chosen_stage=1`.

Тест API без Tilda:

```powershell
curl -X POST "https://api.chitatelstvo.ru/webhook/register" `
  -H "Content-Type: application/json" `
  -H "X-Webhook-Secret: ВАШ_СЕКРЕТ" `
  -d "{\"parent_name\":\"Тест\",\"parent_email\":\"test@example.com\",\"child_name\":\"Маша\",\"child_age\":7,\"notification_channel\":\"email\",\"module_id\":2,\"chosen_stage\":\"1\"}"
```

---

## Частые ошибки

| Симптом | Причина | Решение |
|---------|---------|---------|
| Пустая страница курса, 404 на `.css` / `.js` | файлы не скопированы на сервер | шаг 1 |
| «Товар не в корзине» | нет ST205 или неверный Product ID | `PAY-PAGE.md`, каталог |
| Полная цена с промокодом | в ST100 выключены «Промокоды» | `ST100_SETUP.md` |
| В CRM пустой `module_id` | нет hidden-поля или не нажали «Записаться» после выбора | поля ST100 |
| Разный класс в письме и в корзине | рассинхрон `MODULES` в `chit-course-data.js` и `chit-zero.src.js` | сверить таблицу module_id |
| Два раза форма контактов | видимые поля и в Zero Block, и в ST100 | в ST100 только **Hidden** для контактов |

---

## Чеклист перед запуском

- [ ] `course-pages/*` на `api.chitatelstvo.ru/assets/course-pages/`
- [ ] `/oplata`: ST100 + 3×ST205 + `chit-pay-page.js`
- [ ] Каталог: 3 услуги с точными названиями и ценами
- [ ] Webhook + Success URL + Т‑Банк
- [ ] Промокоды: созданы в Tilda, включены в ST100 на `/oplata`
- [ ] Ссылки с главной на 6 курсов (редиректы или прямые URL)
- [ ] Тестовая оплата с `grade-1` → письмо + `progress_url`

---

## Связанные файлы

| Документ | О чём |
|----------|--------|
| `docs/tilda-zero-main/INSTALL.md` | установка Zero Block на главную |
| `docs/tilda-zero-main/ST100_SETUP.md` | поля, webhook, промокод, module_id |
| `docs/tilda-zero-main/PAY-PAGE.md` | страница `/oplata` |
| `docs/course-pages/chit-course-data.js` | данные курсов и `PAY_PAGE_URL` |
