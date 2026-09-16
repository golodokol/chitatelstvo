# Список картинок для рендеринга · уроки 1–4 (1, 3, 8, 10 сентября)

**Куда класть:**  
- буквы: `static/early/letters/`  
- истории: `static/early/stories/`  
**Стиль:** как пробный урок — тёплая книжная иллюстрация, акварельно-плоская заливка, телефон. Без неона, 3D-глянца, водяных знаков, **без текста на картинке** (буквы и слова рисует UI), кроме разворотов книжек.

**Эталон Словика:** `https://api.chitatelstvo.ru/static/sloviki/slovik-main.png`  
На **фонах игр Словика не рисовать** (он в шапке). Исключение: `word_screen` — Словик рядом с экраном, отдельный персонажный кадр.

**Negative общий:** `blurry, text, watermark, logo, neon, scary, photorealistic human, cluttered, extra limbs, English letters, UI buttons`

Character lock Словика — из `02-slovik-image-video-prompts.md`.

---

## Уже есть — не генерировать

Фоны: `scene-gate`, `scene-missing`, `scene-sparks`, `scene-invite`.  
Предметы: `rain`, `ball`, `house`, `motor`, `tree`, `cup`, `mama`, `kot`, `syr`, `spark`.  
Словик: wave, talk, listen, hint, joy, worry, invite, chest.  
Книжка «Дома»: `book-home-01` … `05`.

---

## Приоритет 1 — общие новые сцены (буквы)

| файл | формат | куда | prompt |
|------|--------|------|--------|
| `scene-trail-path.jpg` | 16:9, пустой центр | hop, intro камня | `Top-down cozy meadow path in the Land of Sounds, grassy trail, round green bushes in a grid, sand edges, turquoise water on sides, morning light, children's storybook, empty center for gameplay, no characters, no letters, no text` |
| `scene-forest-board.jpg` | 16:9 | letter_grid | `Cartoon forest clearing, wooden framed empty beige board in center, pine trees, grassy hills, distant soft mountains, blue sky, storybook, no letters on the board, no mascot, no text` |
| `scene-water-count.jpg` | 16:9 | letter_count | `Calm stylized ocean or wide river in Sound Country, gentle waves, distant purple hills, sky, empty water surface for floating markers, children's book, no numbers, no letters, no UI` |
| `scene-comic-book.jpg` | 16:9 | or_choice | `Open comic-style storybook spread, left page empty yellow frame, right page empty yellow bar at bottom, playful purple soft background with faint shapes not letters, no text, no mascot` |
| `ui-star-board.png` | 1:1 PNG | meet_letter, reward | `Vertical wooden plank with six empty star-shaped slots, three top slots glowing gold stars, three empty, children's book prop, transparent background, no text` |
| `ui-reward-books.png` | PNG | reward историй | `Stack of three colorful children's books on a small stone, rainbow and clouds suggestion, no text on covers, storybook, transparent or simple sky` |
| `bush-green.png` | 1:1 PNG | hop | `Single lush round green bush, top-down, soft shadow, transparent background, no letter, no character` |
| `pebble-hero.png` | 1:1 PNG | hop (фишка) | `Small round orange bird-like pebble companion, cute top-down, friendly, no text, transparent background` *(не Словик; фишка хода)* |

---

## Приоритет 1 — буквы-герои (кириллица)

Как `letter-a-hero.png`. Печатная школьная форма, тёплый тёмно-синий.

| файл | буква | prompt (ядро) |
|------|-------|----------------|
| `letter-m-hero.png` | М | `A single beautiful hero Cyrillic letter М, tall printed capital, bold rounded strokes, warm navy-blue, terracotta glow, tiny sparkles, children's book, transparent background, no other letters, no mascot, no Latin M` |
| `letter-m-small.png` | м | то же, **lowercase Cyrillic м** |
| `letter-u-hero.png` | У | `hero Cyrillic У` |
| `letter-u-small.png` | у | lowercase у |
| `letter-o-hero.png` | О | `hero Cyrillic О, perfectly round` |
| `letter-o-small.png` | о | lowercase о |
| `letter-s-hero.png` | С | `hero Cyrillic С` (не латинская C, если модель путает — `Cyrillic Es С`) |
| `letter-s-small.png` | с | lowercase с |

Куски пазла **М**: две вертикали + перекладина — `m-part-left.png`, `m-part-right.png`, `m-part-bar.png`.  
Куски **О**: один круг / два полукруга — `o-part-arc.png`.

---

## Картинки к станциям букв

| файл | урок | станция | prompt |
|------|------|---------|--------|
| `sun-smile.png` | 1, 2 | or_choice / listen | `Friendly smiling sun, yellow rays, no text on face, children's book, transparent background` |
| `snake-hiss.png` | 4 | listen / or | `Cute small snake in grass, not scary, storybook, no letters, transparent` |
| `wind-howl.png` | 2 | or_choice | `Gentle wind swirl over meadow, no face required, storybook, transparent or simple` |
| `bear-wise.png` | 2 | quest УМ | `Cute brown bear sitting thoughtfully, children's book, no text, transparent` |
| `som-fish.png` | 4 | quest СО | `Friendly catfish / som fish in clear water, storybook, no text` |
| `round-cup.png` | 3 | scene_hunt | уже может быть `cup.png` — проверить круглый силуэт |
| `round-ball.png` | 3 | scene_hunt / spread | использовать `ball.png` |
| `box-square.png` | 3 | дистрактор | `Simple closed cardboard box, square, not round, transparent` |

Развороты `letter_spread` (текст **на картинке**, как книжка):

| файл | текст на правой/в овале | левая сцена |
|------|-------------------------|-------------|
| `spread-m-motor.jpg` | не слово МОТОР; овал пустой — слог рисует UI **или** только картинка мотора | мотор на поляне, крупно |
| `spread-m-mama.jpg` | `МАМА` заглавными, **М** чуть жирнее | мама и ребёнок, тепло, без папы |
| `spread-o-ball.jpg` | `О` крупно | круглый мяч |
| `spread-o-mo.jpg` | `МО` | мотор (тот же персонаж-предмет) |

Промпт разворота — шаблон из `11-ebook-home-spread-prompts.md`, 16:9, кириллица only.

---

## «Первые истории» — новые кадры

### Урок 1 · Кот и коробка

| файл | назначение | prompt |
|------|------------|--------|
| `scene-home-floor.jpg` | intro, короб на полу | `Cozy home interior, wooden floor, closed cardboard box in center, ginger cat nearby curious, warm daylight, storybook 16:9, no text, Slovik not in scene` |
| `slovik-screen.png` | word_screen | `CHARACTER LOCK Slovik standing beside a vintage-friendly boxy TV with blank glowing cream screen (empty for UI word), garden or home, storybook, no letters on screen` |
| `box-closed.png` | предмет | `Closed kraft box, cute, transparent` |
| `box-empty.png` | квест шаг 1 | `Open empty box, transparent` |
| `box-ball.png` | квест шаг 3 | `Open box with a bright ball inside, transparent` |
| `cat-happy.png` | КОТ РАД | `Ginger tabby cat delighted, paws up, storybook, transparent` |
| `cover-box.jpg` | обложка книжки | `Cover illustration: cat and cardboard box, no title text` |

Развороты книжки `book-box-01.jpg` … `05.jpg`:

1. ВОТ КОРОБ. — короб на полу  
2. ЧТО ТАМ? — кот заглядывает  
3. НЕ ТУТ. — пустой короб  
4. ВОТ МЯЧ! — мяч в коробе  
5. КОТ РАД. — кот радуется  

Шаблон — как `11-ebook-home-spread-prompts.md`.

### Урок 2 · Дождь за окном

| файл | назначение | prompt |
|------|------------|--------|
| `scene-window-rain.jpg` | intro | `Cat at rainy window, cozy room, rain streaks, storybook 16:9, no text` |
| `window-frame.png` | слово ОКНО | `Cute house window, rain outside, transparent` |
| `sun-clear.png` | дистрактор солнце | можно `sun-smile.png` |
| `cover-rain.jpg` | обложка | `Cat at window, rain, no title text` |

Развороты `book-rain-01` … `05`: ИДЁТ ДОЖДЬ · КОТ У ОКНА · ТИХО ДОМА · КОТ СПИТ · НОЧЬ.

### Урок 3 · Где мяч?

| файл | назначение | prompt |
|------|------------|--------|
| `scene-kitchen.jpg` | hotspot | `Small cozy kitchen empty of ball, storybook, no text` |
| `scene-room.jpg` | hotspot | `Child room, sofa, no ball` |
| `scene-hall.jpg` | hotspot верный | `Hallway, ball visible under chair` |
| `ball-under-chair.png` | ПОД | `Bright ball under a wooden chair, transparent or simple` |
| `ball-on-sofa.png` | дистрактор | `Ball on sofa` |
| `cat-run.png` | БЕЖИТ | `Ginger cat running after a ball` |
| `cat-catch.png` | ЛОВИТ | `Cat catching a ball` |
| `cover-ball.jpg` | обложка | `Cat looking for a ball, no text` |

Развороты `book-ball-01` … `05`: ГДЕ МЯЧ? · НЕ ТУТ · НЕ ТУТ · ВОТ МЯЧ! · КОТ РАД.

### Урок 4 · Память

| файл | назначение | prompt |
|------|------------|--------|
| `shelf-four.jpg` | 4 обложки | `Wooden shelf with four small children's books standing, covers match box/rain/ball/home, titles not readable or omitted` |
| `scene-wave-stones.jpg` | order_step | `Soft indoor “pond rug” with six empty round stepping stones in two rows, cozy home, no numbers (UI adds 1–6), storybook 16:9` |

---

## UI-пропсы (нейтральные, без копирайта референса)

| файл | зачем |
|------|--------|
| `slot-white.png` | пустой слот фразы |
| `tile-word.png` | жёлтая плитка (слово рисует UI) |
| `heart-bar.png` | не копируем чужой heart UI; у нас **искорки** — использовать `spark.png` |
| `badge-silver.png` | опционально награда урока 4 историй | `Simple silver award badge with ribbon, no English text SILVER` |

---

## Не рендерить

- Муравей, ноутбук, латинские *use / mice / time / men / moss / milk / mop / monkey*  
- Латинские m, n, s на кустах  
- Экран с английским словом  
- Жираф и плитки *I am Sam* — у нас кот и **ВОТ МЯЧ**  
- Отдельная сетка с латинскими буквами

---

## Оценка объёма

| Пачка | шт. ориентир |
|-------|----------------|
| Новые фоны | 6 |
| Буквы-герои + маленькие + куски М/О | ~14 |
| Предметы букв | ~8 |
| Letter spreads | 4 |
| Истории сцены + предметы | ~20 |
| Обложки | 3 (+ «Дома» уже есть) |
| Развороты книжек 3 книжки × 5 | 15 |
| Словик у экрана | 1 |

**Сначала:** фоны hop/grid/water, 4 буквы-героя, `slovik-screen`, короб/кот/мяч, развороты трёх книжек.  
**Потом:** сетка-доска, count, or_choice рамка, полка урока 4.
