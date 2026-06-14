# Страницы Tilda: /zapis и /spasibo (опционально)

Запись и оплата сейчас на **главной** `chitatelstvo.ru/` (блок «Выберите свой путь»).

---

## Уже работает на API (без Tilda)

| URL | Назначение |
|-----|------------|
| `https://api.chitatelstvo.ru/spasibo` | **Success URL** после оплаты в ST100 |
| `https://api.chitatelstvo.ru/zapis` | редирект на `https://chitatelstvo.ru/#program` |

**В ST100 → Success page** укажите: `https://api.chitatelstvo.ru/spasibo`

---

## Если нужны URL на chitatelstvo.ru

### Страница `zapis` (редирект на главную)

1. Tilda → **+ Страница** → пустая
2. SEO → **Page URL:** `zapis`
3. Блок **T123 HTML** → вставьте:

```html
<meta http-equiv="refresh" content="0;url=https://chitatelstvo.ru/#program">
<script>location.replace('https://chitatelstvo.ru/#program');</script>
<p style="font-family:sans-serif;text-align:center;padding:40px">
  <a href="https://chitatelstvo.ru/#program">Перейти к записи на курс →</a>
</p>
```

4. **Опубликовать**

### Страница `spasibo` (на домене сайта, опционально)

Можно не создавать — достаточно `https://api.chitatelstvo.ru/spasibo`.

Если нужна на `chitatelstvo.ru/spasibo`: блок T123 с редиректом:

```html
<meta http-equiv="refresh" content="0;url=https://api.chitatelstvo.ru/spasibo">
<script>location.replace('https://api.chitatelstvo.ru/spasibo');</script>
```

---

## Каталог 3 товара (обязательно!)

Проверка скриптом: `python scripts/check_tilda_catalog.py`

Создайте в **Каталог → Услуги** три позиции **точно** так:

| Название | Цена |
|----------|------|
| Читательство · Разовое | 1 490 ₽ |
| Читательство · Индивидуальное | 1 990 ₽ |
| Читательство · С преподавателем | 4 990 ₽ |

Символ **`·`** (средняя точка) обязателен — так в `chit-zero.js` формируются ссылки `#order:…`.

После создания: **Опубликовать** сайт и снова запустить проверку.
