# Промпты на генерацию трофеев (early-курсы)

**Для кого:** генерация PNG-бейджей → положить в `docs/images/` с именами из таблицы → задеплоить на CDN (`/assets/…`).

**Дата:** 22.08.2026

---

## 0. Общий стиль (как у существующих бейджей Читательства)

**Формат:** квадрат **512×512 px**, PNG, **прозрачный фон** вокруг медали.

**Композиция:** круглая детская медаль / трофей в центре кадра. Мягкая тень под медалью. Внутри медали — один понятный символ, без мелких деталей.

**Стиль:** тёплая детская книжная иллюстрация, мягкая акварельно-плоская заливка, лёгкая зернистость бумаги. Без неона, без глянцевого 3D, без фотореализма.

**Палитра бренда:**
- голубой `#5B7FA6`
- лавандовый `#8F7DA3`
- золото звезды `#E9B85B`
- крем `#F6F4F9`, тёплый текст `#3D5266`

**Эталоны существующих бейджей:**  
`docs/images/gamify-badge-first-step.png`, `gamify-badge-reader.png`, `gamify-badge-tracker.png`

**Эталон искорки (символ, не весь бейдж):** `docs/images/ИСКОРКА.PNG` — капля света с сердечком внутри, золотое свечение.

**Negative (всегда):**  
`text, letters, alphabet, numbers, watermark, logo, neon, scary, photorealistic, cluttered, low quality, extra objects, frame border, square background`

**После генерации:** сохранить под именем из таблицы → `python -m gamification.badge_assets` (или `sync_badge_assets` при деплое).

---

## 1. Новые трофеи — пробный кабинет

| Бейдж | Файл | Когда выдаётся |
|-------|------|----------------|
| Искатель искорок | `gamify-badge-spark-hunter.png` | Собраны все искорки квеста |
| Хранитель сундука | `gamify-badge-chest-keeper.png` | Открыт сундук урока |
| Слоговик | `gamify-badge-syllable-master.png` | Прочитан слог МА («Буквы оживают») |

Уже есть картинки (не генерировать): **Первый шаг**, **Читатель**.

---

## 2. Промпты по одному

### 2.1 Искатель искорок · `gamify-badge-spark-hunter.png`

**Идея:** медаль за сбор волшебных искорок в квесте. Центр — одна крупная искорка (капля света), вокруг — 2–3 маленькие искорки по дуге, как собранная коллекция.

**Prompt:**
```
Children's round achievement medal icon, soft watercolor flat illustration, warm storybook style. Center: one large golden spark droplet with tiny heart glow inside (magical light particle, amber and cream). Two smaller matching sparks orbit nearby like a collected set. Round medal rim in soft blue #5B7FA6 and gold #E9B85B, subtle paper texture. Gentle drop shadow. Isolated on transparent background, 512x512, single trophy, no text, no letters.
```

**Negative:** `character, Slovik, face, book, chest, sword, crown, realistic metal`

---

### 2.2 Хранитель сундука · `gamify-badge-chest-keeper.png`

**Идея:** медаль с маленьким деревянным сундуком (как в уроке), крышка приоткрыта, из щели мягкий золотой свет. Не пугающий, уютный «клад».

**Prompt:**
```
Children's round achievement medal icon, soft watercolor flat illustration, warm storybook style. Center: small friendly wooden treasure chest, lid slightly open, soft golden glow from inside, tiny sparkles. Medal border in lavender #8F7DA3 and gold #E9B85B, cozy children's literary school mood. Gentle shadow under medal. Transparent background, 512x512, no text, no letters, no coins pile clutter.
```

**Negative:** `pirate, skull, dark cave, scary, photorealistic wood, large character, Slovik`

**Референс сундука в UI:** `docs/images/slovik-chest.PNG` (только настроение, не копировать 1:1).

---

### 2.3 Слоговик · `gamify-badge-syllable-master.png`

**Идея:** медаль за первый прочитанный слог. Два мягких звуковых «пузыря» или полукруглых капли сливаются в один слог — **без букв М и А на картинке** (буквы в игре рисуются отдельно). Можно: два цветных полушария (голубой + лавандовый) + маленькая золотая звезда между ними.

**Prompt:**
```
Children's round achievement medal icon, soft watercolor flat illustration. Center: two soft rounded sound bubbles merging into one syllable shape, left bubble blue #5B7FA6, right bubble lavender #8F7DA3, small gold star #E9B85B where they meet — abstract phonics symbol, NO letters, NO alphabet. Warm medal rim, paper texture, gentle shadow. Transparent background 512x512, no text.
```

**Negative:** `letters, alphabet, Cyrillic, MA text, words, numbers, mouth, realistic lips`

---

## 3. Закрытые тизеры полного модуля (пока без картинок в кабинете)

Генерировать позже, когда понадобятся в UI. Имена файлов уже зарезервированы в `gamification/badge_assets.py`.

| Бейдж | Файл | Курс |
|-------|------|------|
| Знаю букву М | `gamify-badge-letter-m.png` | Буквы оживают |
| Словарик | `gamify-badge-word-book.png` | Первые истории |
| Друг Словика | `gamify-badge-slovik-friend.png` | оба модуля, финал |

### 3.1 Знаю букву М (шаблон для серии букв)

**Prompt:**
```
Children's round achievement medal icon, soft watercolor style. Center: one large friendly letter M shape made of soft rounded ribbons in blue and gold — stylized, chunky, child-friendly, NOT typed font. Small star accent. Medal rim cream and gold. Transparent 512x512. Only one letter M, no other text.
```

*Для У, О, С, Р — тот же промпт, заменить букву и имя файла (`gamify-badge-letter-u.png` и т.д.).*

### 3.2 Словарик

**Prompt:**
```
Children's round achievement medal icon, soft watercolor flat illustration. Center: small open picture dictionary book with one simple icon on the page (house or cat silhouette, no text). Warm blue and lavender medal border, gold star clasp. Cozy literary school mood. Transparent 512x512, no letters, no words.
```

### 3.3 Друг Словика

**Prompt:**
```
Children's round achievement medal icon, soft watercolor style. Center: two small friendly figures holding hands — simplified child reader silhouette and small blue book-mascot silhouette (round head, tiny cape hint), warm friendship mood, NOT detailed character portrait. Gold medal rim, soft shadow. Transparent 512x512, no text.
```

**Референс Словика (настроение):** `docs/images/slovik-main.png` — не копировать целиком, только силуэт/цвет.

---

## 4. Чеклист после генерации

1. PNG 512×512, прозрачный фон, имя файла из таблицы.
2. Положить в `docs/images/`.
3. Проверить в кабинете `/progress/…` — вместо ✨ должна появиться картинка.
4. При деплое: `cp docs/images/gamify-badge-* /var/www/chitatelstvo-assets/`.
5. Обновить `?v=` в `templates/progress.html` при необходимости.

---

## 5. Связанные файлы

- Каталог пробных бейджей: `gamification/cabinet_ui.py` → `TRIAL_BADGE_CATALOG`
- Маппинг имён → файлов: `gamification/badge_assets.py` → `BADGE_ASSET_FILES`
- Отображение в кабинете: `templates/progress.html` → блок «Трофеи»
- Дизайн модулей: `docs/early-courses/09-stories-module1.md`, `10-letters-module1.md`
