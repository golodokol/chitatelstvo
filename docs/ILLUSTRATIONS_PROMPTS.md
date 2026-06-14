# Промты для иллюстраций в стиле «Пеппи» / Astrid Lindgren

Стиль-референс: [astridli.tilda.ws](https://astridli.tilda.ws/) — Ingrid Vang Nyman, свободная линия, акварель, скандинавская детская книга. Не Disney, не 3D.

**Палитра сайта:** пыльно-синий `#5B7FA6`, лиловый `#8F7DA3`, голубой `#88A9D1`, крем `#F6F4F9`, тёплые акценты (оранжевый, зелёный) — умеренно.

**Технические требования для обложек книг в hero:**
- Формат: **вертикаль 3:4** (например 600×800 px или 768×1024 px)
- **Без текста** на обложке — только иллюстрация
- Края: можно слегка «рваные» или с мягкой тенью — обложка ляжет поверх CSS-кнопки книги
- Сохранить в `docs/images/` с именами из таблицы ниже

---

## Обложки для интерактивной полки (hero)

| Файл | Книга | Смысл |
|------|-------|--------|
| `hero-book-single.png` | Левая | Разовое — одна сказка |
| `hero-book-full.png` | Центральная | 8 сказок, полная программа |
| `hero-book-block.png` | Правая | Блок из 4 сказок |

### 1. Разовое — `hero-book-single.png`

```
Children's book cover illustration, Scandinavian whimsical style like Pippi Longstocking by Ingrid Vang Nyman. One small open fairy-tale book on a wooden table, a curious child peeking over the pages with wide eyes, a single golden path winding into the book like a invitation. Loose ink outlines, soft watercolor washes. Palette: dusty blue #5B7FA6, soft lilac #8F7DA3, cream background #F6F4F9, tiny warm orange accent. Vertical 3:4 ratio, no text, no logo, warm playful mood, hand-drawn children's literature aesthetic.
```

**Negative prompt:** `3D render, Disney, Pixar, photorealistic, text, letters, watermark, dark horror, anime`

### 2. Полная программа — `hero-book-full.png`

```
Whimsical Scandinavian children's illustration for a book cover, Pippi Longstocking / Astrid Lindgren museum style. A tall wooden bookshelf with exactly eight colorful fairy-tale spines, summer sunlight through a round window, a small red-haired girl in mismatched socks sitting on the floor reading. Loose ink line art, soft watercolor, cozy Nordic room. Colors harmonize with dusty blue #5B7FA6 and lilac #8F7DA3, cream walls. Vertical 3:4, no text on cover, joyful adventurous mood, Ingrid Vang Nyman inspired.
```

**Negative prompt:** `3D, Disney princess, realistic photo, text, title, barcode, scary`

### 3. Блок из 4 — `hero-book-block.png`

```
Playful children's book cover illustration, Scandinavian picture book style like Pippi Longstocking. Four slim fairy-tale books tied together with a ribbon bow, calendar pages fluttering with sun and moon hints (summer start), a friendly horse or monkey companion peeking from behind (subtle Lindgren nod, not literal Pippi portrait). Soft watercolor and ink, palette blue #88A9D1 and lilac #A896B8 on cream #F6F4F9. Vertical 3:4, no text, lighthearted hand-drawn feel.
```

**Negative prompt:** `3D render, corporate, text, logo, photorealistic, cluttered`

---

## Куда ещё вставить иллюстрации

| Место на сайте | Файл (предложение) | Зачем |
|----------------|-------------------|--------|
| Угол блока «О школе» (pull-quote) | `vignette-reading-corner.png` | Живость рядом с цитатой, не перегружая текст |
| Шапка аккордеона «Программы по классам» | `programs-shelf-strip.png` | Горизонтальная полоска-разделитель |
| Пустое состояние на странице прогресса родителя | `empty-no-lessons-yet.png` | Мягкое «ещё не начали» вместо сухой иконки |
| Финальный CTA перед футером | `cta-wave-goodbye.png` | Персонаж машет рукой — призыв записаться |
| Карточки «Для кого» (4 мини-иконки) | `audience-kids.png`, `audience-family.png`, … | По одной маленькой сцене на карточку |
| Письма FAQ (угловой штамп) | `faq-wax-seal.png` | Декоративная «печать» на конверте |

---

## Промты для дополнительных мест

### Pull-quote — угол «читательского уголка»

```
Small corner vignette illustration, Scandinavian children's book style, Ingrid Vang Nyman watercolor. Cozy reading nook: armchair, stack of books, cat sleeping, window with birch trees. Soft blues and lilacs matching #5B7FA6 and #8F7DA3, cream paper texture background. Square 800×800, transparent or cream edges, no text, decorative spot illustration for website margin.
```

### Полоска над программами

```
Wide horizontal banner illustration, whimsical Nordic children's art. Wooden shelf with fairy-tale books, summer garland, small figure on tiptoes reaching for a book. Aspect ratio 3:1 (e.g. 1200×400), soft watercolor and ink, palette dusty blue and lilac, no text, seamless calm composition for website section header.
```

### Пустое состояние (страница прогресса)

```
Gentle children's illustration, Pippi Longstocking aesthetic but original character. A closed book waiting on a desk, pencil and bookmark ready, morning light — mood "adventure hasn't started yet". Soft watercolor, encouraging not sad. Square 600×600, no text, minimal background #F6F4F9.
```

### Финальный CTA — персонаж машет

```
Whimsical Scandinavian child character (original, not Pippi copy) waving hello from behind an open book, summer sky, playful ink and watercolor. Small illustration for call-to-action block, roughly 400×500 vertical, palette site blues and lilacs, warm smile, no text.
```

### «Для кого» — 4 мини-сцены (256×256 каждая)

**Дети 6–11:**
```
Tiny square spot illustration: child reading fairy tale with magnifying glass, discovering hero's feelings. Nordic watercolor, blue-lilac, playful, 256×256, no text.
```

**Семьи:**
```
Tiny square: parent and child on sofa sharing one book, cozy evening lamp. Scandinavian picture book style, soft colors, 256×256, no text.
```

**Тем, кому скучно в школе:**
```
Tiny square: bored desk transforms into magical forest emerging from open book. Whimsical ink watercolor, 256×256, no text.
```

**Родители:**
```
Tiny square: parent looking at tablet/phone with child's progress stars, proud smile, books on shelf behind. Warm Nordic illustration, 256×256, no text.
```

### FAQ — декоративная печать на «конверте»

```
Small circular wax seal illustration with open book and star motif, hand-drawn Scandinavian style, lilac and gold tones, 200×200, transparent background, no letters or words, decorative stamp for FAQ letter cards.
```

---

## Как подключить на preview-странице

1. Сгенерировать изображения и положить в `docs/images/`.
2. Hero уже ждёт три файла: `hero-book-single.png`, `hero-book-full.png`, `hero-book-block.png`.
3. Для pull-quote можно добавить в CSS:

```css
.about-pullquote::before {
  content: '';
  background: url('images/vignette-reading-corner.png') no-repeat;
  /* … */
}
```

4. На Tilda: загрузить в «Файлы», в Zero Block — `<img>` или фон блока.

---

## Единый «мастер-промт» (скопировать в начало любого запроса)

```
Style lock: Original Scandinavian children's book illustration inspired by Astrid Lindgren and illustrator Ingrid Vang Nyman (Pippi Longstocking books). Loose confident ink outlines, soft translucent watercolor, slightly imperfect hand-drawn charm, warm humor, NOT Disney/Pixar/3D/anime. Color harmony with website: dusty blue #5B7FA6, lilac #8F7DA3, light blue #88A9D1, cream #F6F4F9. No text, no watermark, no logos.
```
