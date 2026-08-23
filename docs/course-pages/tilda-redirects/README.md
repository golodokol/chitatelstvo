# Страницы курсов в Tilda (Zero Block)

**Версия ассетов:** `20260822l`

Это уже **не редиректы** на API. Вставляете HTML в Zero Block — лендинг открывается на `chitatelstvo.ru/...`.

## Как поставить / обновить страницу

1. **Страницы** → нужная страница (или **+ Новая**)
2. SEO: заголовок и **slug** из таблицы
3. Снять «Показывать в меню» (по желанию)
4. **+ Блок** → **Zero Block** (T123) → HTML-элемент на всю ширину
5. Артборд: ширина **1200**, высота **авто**, выравнивание **сверху**
6. Ctrl+A → вставить **весь** файл из этой папки → **Опубликовать**

## Таблица

| Файл | Slug | Тип |
|------|------|-----|
| `bukvy-ozhivayut.html` | `bukvy-ozhivayut` | lite |
| `pervye-istorii.html` | `pervye-istorii` | lite |
| `1-klass.html` | `1-klass` | полный |
| `2-klass.html` | `2-klass` | полный |
| `3-klass.html` | `3-klass` | полный |
| `4-klass.html` | `4-klass` | полный |
| `6-8-let.html` | `6-8-let` | полный |
| `9-11-let.html` | `9-11-let` | полный |
| `veter-v-ivah.html` | `veter-v-ivah` | lite |
| `tainstvenny-sad.html` | `tainstvenny-sad` | lite |
| `russkie-skazki-6-9.html` | `russkie-skazki-6-9` | lite |
| `russkie-skazki-10-12.html` | `russkie-skazki-10-12` | lite |
| `programmy.html` | `programmy` | хаб |

## Если страница уже была редиректом

Откройте Zero Block → замените старый HTML на новый файл целиком → Опубликовать.  
URL (`/1-klass` и т.д.) не меняется.

## Проверка

1. `https://chitatelstvo.ru/1-klass` — полный лендинг **на домене сайта** (адрес в браузере не прыгает на api…)
2. Главная → **Подробнее** → та же страница
3. **Записаться** → `/oplata` с нужным `module_id`

CSS/JS лежат на `api.chitatelstvo.ru/assets/course-pages/` — после правок контента их нужно задеплоить на сервер.
