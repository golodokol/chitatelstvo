# Электронная книжка «Дома» — финальные промпты на развороты

**Формат:** цельный горизонтальный разворот (картинка слева + текст справа)  
**Соотношение:** **16:9** (рекомендуется 1920×1080 или 2560×1440)  
**Стиль:** детская книжная иллюстрация, мягкий storybook digital painting, тёплый свет, без водяных знаков  

После генерации файлы кладём так:

```
static/early/stories/book-home-01.jpg
static/early/stories/book-home-02.jpg
static/early/stories/book-home-03.jpg
static/early/stories/book-home-04.jpg
static/early/stories/book-home-05.jpg
```

В JSON у каждой страницы:

```json
{
  "text": "ВОТ МОЙ ДОМ.",
  "spread_image": "/static/early/stories/book-home-01.jpg",
  "alt": "Дом"
}
```

Пока `spread_image` нет — показывается старый режим (отдельная картинка + текст в интерфейсе).

---

## Общий шаблон (добавляйте к каждому промпту)

```
Open children's picture book double-page spread, landscape 16:9, viewed flat from above.
LEFT PAGE: full-bleed illustration (scene described below), soft painted edges.
RIGHT PAGE: cream paper page with clear open space in the center for one short Russian sentence.
On the right page, render the exact sentence in large bold dark navy serif capital letters, centered, readable for children age 5–7:
"[SENTENCE]"
Keep a soft book gutter / spine shadow in the middle. Cozy, warm, whimsical storybook style.
No UI, no buttons, no arrows, no page numbers, no watermark, no English text.
```

**Negative prompt:**

```
English text, UI, buttons, arrows, page numbers, watermark, logo, photorealistic photo, cluttered right page, tiny unreadable text, horror, scary
```

---

## Разворот 1 — ВОТ МОЙ ДОМ.

**Файл:** `book-home-01.jpg`  
**Текст на правой странице:** `ВОТ МОЙ ДОМ.`

```
Open children's picture book double-page spread, landscape 16:9, viewed flat from above.
LEFT PAGE: cozy little wooden house with warm windows, evening golden light, soft garden path, gentle trees, inviting home atmosphere, cute storybook illustration.
RIGHT PAGE: cream paper page with clear open space in the center for one short Russian sentence.
On the right page, render the exact sentence in large bold dark navy serif capital letters, centered, readable for children age 5–7:
"ВОТ МОЙ ДОМ."
Keep a soft book gutter / spine shadow in the middle. Cozy, warm, whimsical storybook style.
No UI, no buttons, no arrows, no page numbers, no watermark, no English text.
```

---

## Разворот 2 — ВОТ МОЙ КОТ.

**Файл:** `book-home-02.jpg`  
**Текст:** `ВОТ МОЙ КОТ.`

```
Open children's picture book double-page spread, landscape 16:9, viewed flat from above.
LEFT PAGE: cute ginger tabby kitten sitting happily near a doorway or on a soft rug at home, friendly big eyes, warm indoor light, children's storybook illustration.
RIGHT PAGE: cream paper page with clear open space in the center for one short Russian sentence.
On the right page, render the exact sentence in large bold dark navy serif capital letters, centered, readable for children age 5–7:
"ВОТ МОЙ КОТ."
Keep a soft book gutter / spine shadow in the middle. Cozy, warm, whimsical storybook style.
No UI, no buttons, no arrows, no page numbers, no watermark, no English text.
```

---

## Разворот 3 — КОТ ЕСТ СЫР.

**Файл:** `book-home-03.jpg`  
**Текст:** `КОТ ЕСТ СЫР.`

```
Open children's picture book double-page spread, landscape 16:9, viewed flat from above.
LEFT PAGE: adorable ginger kitten holding and nibbling a big yellow Swiss cheese wedge with holes, playful and cute, soft warm light, children's storybook illustration, clean background.
RIGHT PAGE: cream paper page with clear open space in the center for one short Russian sentence.
On the right page, render the exact sentence in large bold dark navy serif capital letters, centered, readable for children age 5–7:
"КОТ ЕСТ СЫР."
Keep a soft book gutter / spine shadow in the middle. Cozy, warm, whimsical storybook style.
No UI, no buttons, no arrows, no page numbers, no watermark, no English text.
```

---

## Разворот 4 — НОЧЬ, КОТ СПИТ.

**Файл:** `book-home-04.jpg`  
**Текст:** `НОЧЬ, КОТ СПИТ.`

```
Open children's picture book double-page spread, landscape 16:9, viewed flat from above.
LEFT PAGE: peaceful magical night forest, deep navy starry sky, thin crescent moon, autumn leaves, cute ginger kitten curled up sleeping on the forest floor in soft warm light, calm cozy mood, children's storybook illustration, leave some open space near center for composition.
RIGHT PAGE: cream paper page with clear open space in the center for one short Russian sentence.
On the right page, render the exact sentence in large bold dark navy serif capital letters, centered, readable for children age 5–7:
"НОЧЬ, КОТ СПИТ."
Keep a soft book gutter / spine shadow in the middle. Cozy, warm, whimsical storybook style.
No UI, no buttons, no arrows, no page numbers, no watermark, no English text.
```

---

## Разворот 5 — МАМА СПИТ.

**Файл:** `book-home-05.jpg`  
**Текст:** `МАМА СПИТ.`

```
Open children's picture book double-page spread, landscape 16:9, viewed flat from above.
LEFT PAGE: gentle mother sleeping peacefully in a cozy bed at night, soft moonlight through the window, calm warm bedroom, kind and tender children's storybook illustration (no scary details).
RIGHT PAGE: cream paper page with clear open space in the center for one short Russian sentence.
On the right page, render the exact sentence in large bold dark navy serif capital letters, centered, readable for children age 5–7:
"МАМА СПИТ."
Keep a soft book gutter / spine shadow in the middle. Cozy, warm, whimsical storybook style.
No UI, no buttons, no arrows, no page numbers, no watermark, no English text.
```

---

## Как подключить после генерации

1. Сохранить 5 JPG в `static/early/stories/`.
2. В `lessons/catalog/early-stories-trial-lesson-01.json` у станции `first_book` у каждой строки добавить `spread_image`.
3. Залить файлы на сервер.

Пример одной строки:

```json
{
  "text": "КОТ ЕСТ СЫР.",
  "spread_image": "/static/early/stories/book-home-03.jpg",
  "image": "/static/early/stories/kot-eat.png",
  "alt": "Кот ест сыр"
}
```

`image` можно оставить как запасной вариант; если есть `spread_image`, интерфейс покажет цельный разворот.
