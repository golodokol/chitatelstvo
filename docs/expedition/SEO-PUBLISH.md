# Публикация: Читательская экспедиция

Организация: **Читательство** · https://chitatelstvo.ru  
Контакт: info@chitatelstvo.ru · ИП Рощина Ольга Владимировна · ИНН 231150315327  
Ольга Рощина · 8 905 473-83-70 · тг [@olgaroshchina](https://t.me/olgaroshchina)

Раздел живёт внутри школы, не как отдельный бренд.

## Как добавить страницу в Tilda

1. **Страницы** → **Добавить страницу**.
2. Заполнить поля ниже (SEO + Social + адрес).
3. Удалить стандартные блоки Tilda на странице.
4. **Настройки страницы** → не показывать **шапку и подвал сайта** (у экспедиции свои).
5. **Zero Block** → HTML-элемент `</>` → вставить **весь** файл `docs/tilda-zero-pages/expedition.html`.
6. Артборд **1200**, высота **авто**, выравнивание **сверху**.
7. **Опубликовать**.

Вложенные экраны (карта, паспорт, библиотекам) открываются хешем:  
`https://chitatelstvo.ru/expedition#/map`

---

## Данные для Tilda — копировать как есть

| Поле в Tilda | Значение |
|---|---|
| **Название страницы** (в списке) | Читательская экспедиция |
| **Адрес страницы** (URL) | `expedition` |
| **Полный URL** | https://chitatelstvo.ru/expedition |
| **Title** (SEO) | Читательская экспедиция — литературная школа «Читательство» |
| **Description** (SEO) | Карта сказок народов России для детей 6–11 лет. Игровой маршрут и бесплатный вход на платформу школы «Читательство». Для семей и библиотек. |
| **Keywords** | читательская экспедиция, сказки народов России, литературная школа, Читательство, библиотеки, карта сказок, чтение для детей 6-11 |
| **Canonical** | https://chitatelstvo.ru/expedition |
| **og:title** | то же, что Title |
| **og:description** | то же, что Description |
| **og:url** | https://chitatelstvo.ru/expedition |
| **og:image** | https://api.chitatelstvo.ru/static/expedition/images/hero-map.png |
| **og:type** | website |
| **twitter:card** | summary_large_image |
| **H1** | Читательская экспедиция |
| **Robots** | index, follow |
| **Sitemap** | включить страницу |
| **Шапка / подвал сайта** | скрыть на этой странице |
| **Файл Zero Block** | `docs/tilda-zero-pages/expedition.html` |

### Title

```text
Читательская экспедиция — литературная школа «Читательство»
```

### Description

```text
Карта сказок народов России для детей 6–11 лет. Игровой маршрут и бесплатный вход на платформу школы «Читательство». Для семей и библиотек.
```

### Адрес

```text
expedition
```

### Canonical / og:url

```text
https://chitatelstvo.ru/expedition
```

### Keywords

```text
читательская экспедиция, сказки народов России, литературная школа, Читательство, библиотеки, карта сказок, чтение для детей 6-11
```

### og:image

```text
https://api.chitatelstvo.ru/static/expedition/images/hero-map.png
```

### Дополнительный HTML в Head (если есть поле)

```html
<link rel="canonical" href="https://chitatelstvo.ru/expedition">
<meta property="og:type" content="website">
<meta property="og:url" content="https://chitatelstvo.ru/expedition">
<meta property="og:title" content="Читательская экспедиция — литературная школа «Читательство»">
<meta property="og:description" content="Карта сказок народов России для детей 6–11 лет. Игровой маршрут и бесплатный вход на платформу школы «Читательство». Для семей и библиотек.">
<meta property="og:image" content="https://api.chitatelstvo.ru/static/expedition/images/hero-map.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Читательская экспедиция — литературная школа «Читательство»">
<meta name="twitter:description" content="Карта сказок народов России для детей 6–11 лет. Игровой маршрут и бесплатный вход на платформу школы «Читательство». Для семей и библиотек.">
<meta name="twitter:image" content="https://api.chitatelstvo.ru/static/expedition/images/hero-map.png">
```

JSON-LD уже лежит внутри файла Zero Block — отдельно в Head дублировать не нужно.

---

## Zero Block

- Элемент: **HTML** `</>`
- Вставить **целиком** `docs/tilda-zero-pages/expedition.html`
- Артборд: **1200**
- Высота: **авто**
- Выравнивание: **сверху**
- Отступы секции: **0**
- Фон секции: `#FAF7F2`

---

## После публикации

- Страница: https://chitatelstvo.ru/expedition
- Карта: https://chitatelstvo.ru/expedition#/map
- Библиотекам: https://chitatelstvo.ru/expedition#/libraries
- По желанию: ссылка в меню / на главной.

Заявки библиотек пишутся в `data/expedition/` на API. SQL: `db/migrations/004_expedition.sql`.
