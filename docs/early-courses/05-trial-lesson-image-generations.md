# Список картинок — пробный урок «Буквы оживают»

**Урок:** Словик и пропавшие звуки (`early-letters-trial-lesson-01`)  
**Дата:** 18.08.2026  
**Для кого:** генерация картинок → класть в `static/early/letters/` с именами из таблиц

Это **итоговый** список по текущему уроку. Не генерировать буквы О/М/У/И как отдельные картинки — в игре они рисуются как UI. Не генерировать змейку: в уроке её нет.

---

## 0. Стиль

Тёплая детская книжная иллюстрация, мягкая акварельно-плоская заливка, читается с телефона. Без неона, без глянцевого 3D, без водяных знаков, без подписей на картинке.

**Эталон Словика:** `https://api.chitatelstvo.ru/static/sloviki/slovik-main.png`  
Словик уже в шапке урока — **на фонах его не рисовать**.

**Фоны:** 16:9, пустой центр (туда ляжет игра).  
**Предметы и буква-герой:** 1:1, PNG, прозрачный фон, один объект.

**Negative:** `blurry, text, watermark, logo, neon, scary, photorealistic human, cluttered background, extra limbs, low quality`  
Для фонов и предметов ещё: `letters, alphabet`.  
Для буквы-героя А буквы в negative **нет**.

---

## 1. Маршрут урока — что на экране

| № | Станция | Что видит ребёнок | Картинки |
|---|---|---|---|
| 1 | Врата | видео, постер | `scene-gate.png` |
| 2 | **Буква А** | первая встреча: большая красивая А, нажать — услышать а-а-а | **`letter-a-hero.png`** + фон `scene-missing.png` |
| 3 | Поляна шёпотов | найти, что шумит | фон `scene-missing.png` + 9 предметов |
| 4 | Пещера эха | ловить вспышки А среди О И У | фон `scene-sparks.png` (буквы — UI) |
| 5 | Мастерская | найти три А среди других букв | фон `scene-sparks.png` (буквы — UI) |
| 6 | Собери букву | две ножки + перекладина | фон `scene-sparks.png` (детали — UI; кусочки можно нарисовать, см. §5) |
| 7 | Большая и маленькая | разложить А / а | фон `scene-invite.png` (буквы — UI) |
| 8 | Поймать на поляне | бегают А и а | фон `scene-sparks.png` (буквы — UI) |
| 9 | Лабиринт | идти по А | фон `scene-sparks.png` (буквы — UI) |
| 10 | Слова на А | аист и арбуз | фон `scene-sparks.png` + 6 предметов |
| 11 | Мост | слог ма | фон `scene-invite.png` + `mama.png` |
| 12 | Слог МА | мама / мяч / кот / сыр | фон `scene-invite.png` + 4 предмета |
| 13 | Награда | искорки, сундук Словика | фон `scene-invite.png` + `spark.png` |

Словик в шапке: позы `wave`, `invite`, `listen`, `talk`, `hint`, `joy`, `chest`, `worry` — уже есть, не генерировать.

---

## 2. Уже есть — не генерировать, если качество устраивает

**Фоны** в `static/early/letters/`: `scene-gate.png`, `scene-missing.png`, `scene-sparks.png`, `scene-invite.png`.

**Предметы:** `rain.png`, `ball.png`, `house.png`, `bird.png`, `motor.png`, `tree.png`, `drum.png`, `cup.png`, `bell.png`, `aist.png`, `arbuz.png`, `mama.png`, `kot.png`, `syr.png`, `spark.png`.

**Словик** в `static/early/slovik/`: wave, talk, listen, hint, joy, worry, invite, chest.

**Не используется в этом уроке:** `snake.png`, `hero.png`.

---

## 3. Генерировать в первую очередь

### 3.1. Буква-герой А (новая, обязательная)

Первый раз ребёнок **знакомится** с А. Не плоская кнопка-шрифт, а красивая живая буква: крупная, тёплая, как персонаж страны звуков.

| Файл | Куда | Prompt |
|---|---|---|
| `letter-a-hero.png` | станция «Буква А», кнопка по центру | `A single beautiful hero Cyrillic letter А as a friendly storybook character-object for kids 4–7, tall printed capital A, bold rounded strokes, warm navy-blue with soft terracotta glow, tiny warm sparkles around, children's book illustration, watercolor-flat shading, centered, high readability on phone, transparent background, no other letters, no mascot, no text, no watermark` |

Дубль B, если слишком «игрушечно»:

`Elegant friendly Cyrillic letter А, printed schoolbook shape with soft rounded corners, deep ink-blue, gentle gold rim light, standing on a hint of cream glow, storybook, transparent background, one letter only`

---

### 3.2. Кусочки А для «Собери букву» (желательно)

Сейчас ножки и перекладина — схематичный UI. Если рисовать — три куска в том же стиле, что герой-А.

| Файл | Что | Prompt |
|---|---|---|
| `letter-a-piece-left.png` | левая ножка | `Puzzle piece: left diagonal stroke of Cyrillic letter А, same style as hero letter A, bold rounded navy shape, children's book, transparent background, no extra marks` |
| `letter-a-piece-right.png` | правая ножка | `Puzzle piece: right diagonal stroke of Cyrillic letter А, same style, bold rounded navy, transparent background` |
| `letter-a-piece-bar.png` | перекладина | `Puzzle piece: horizontal crossbar of Cyrillic letter А, same style, bold rounded navy, transparent background` |

---

## 4. Фоны — только если перерисовываем текущие 4

Центр пустой. Без Словика, без букв, без текста.

| Файл | Станции | Что нарисовать | Prompt |
|---|---|---|---|
| `scene-gate.png` | 1 Врата (постер видео) | ворота страны звуков | `Whimsical wooden gate to the Land of Sounds, morning soft light, meadow edges, empty lower-center for UI, no character, no text, no letters, storybook, 16:9` |
| `scene-missing.png` | 2 встреча А, 3 шёпоты | тихая поляна, «звуки пропали» | `Quiet magical sound meadow, cream-green ground, sparse bushes at edges, empty center, faint missing-sparkle dust far away, no character, no letters, no text, storybook, 16:9` |
| `scene-sparks.png` | эхо, мастерская, сборка, охота, лабиринт, слова | поляна с мягким светом искорок | `Soft meadow with distant tiny warm sparkles, empty center for game UI, calm cream light, no character, no letters, no text, storybook, 16:9` |
| `scene-invite.png` | сортировка, мост, сундук, награда | тёплая поляна-приглашение | `Warm inviting meadow clearing, evening cream light, empty center, gentle sparkle dust far away, no character, no letters, no text, storybook, 16:9` |

---

## 5. Предметы — только если перерисовываем

По одному объекту, прозрачный фон, без букв на картинке.

| Файл | Подпись | Где в уроке | Prompt |
|---|---|---|---|
| `rain.png` | Дождь | шёпоты (шумит) | `Single cute rain cloud with soft raindrops, children's book icon, transparent background, centered, no text` |
| `motor.png` | Мотор | шёпоты (шумит) | `Single cute toy motor, children's book icon, transparent background, no text` |
| `drum.png` | Барабан | шёпоты (шумит) | `Single cute toy drum, children's book icon, transparent background, no text` |
| `bell.png` | Колокольчик | шёпоты (шумит) | `Single cute small bell, children's book icon, transparent background, no text` |
| `ball.png` | Мяч | шёпоты, слова, сундук | `Single cute colorful ball, children's book icon, transparent background, no text` |
| `house.png` | Дом | шёпоты, слова | `Single cute small house, children's book icon, transparent background, no text` |
| `bird.png` | Птица | шёпоты | `Single cute small bird, children's book icon, transparent background, no text` |
| `tree.png` | Дерево | шёпоты | `Single cute simple tree, children's book icon, transparent background, no text` |
| `cup.png` | Чашка | шёпоты, слова | `Single cute cup, children's book icon, transparent background, no text` |
| `aist.png` | Аист | слова на А | `Single cute stork standing, children's book icon, transparent background, no text, no letters` |
| `arbuz.png` | Арбуз | слова на А | `Single cute watermelon, children's book icon, transparent background, no text, no letters` |
| `mama.png` | Мама | мост, сундук (слог ма) | `Warm gentle mother figure icon for kids 4–6, soft storybook, transparent background, no text, no letters` |
| `kot.png` | Кот | сундук | `Single cute cat, children's book icon, transparent background, no text, no letters` |
| `syr.png` | Сыр | сундук | `Single cute piece of cheese, children's book icon, transparent background, no text, no letters` |
| `spark.png` | Искорка | награда, полёт искорки | `Single glowing quest spark teardrop of light, warm amber-peach, soft magical, transparent background, no icons inside, no text` |

---

## 6. Не генерировать

- буквы О, И, У, М, Д, П и слоги МА/АМ/МО/СА — это кнопки в игре;
- змейку;
- отдельные «корзина» и «сундук» как предметы (сундук — поза Словика);
- новые позы Словика;
- три типа искорок с иконками внутри — в уроке одна `spark.png`.

---

## 7. Порядок генерации

1. **`letter-a-hero.png`** — первая встреча с А.  
2. Кусочки А (если рисуем сборку).  
3. Фоны — только если текущие `scene-*` слабые.  
4. Предметы — только те, что хочется заменить. Сначала шумные: rain, motor, drum, bell; потом aist, arbuz, mama, kot, syr.

Имена файлов — **точно как в таблицах**, иначе не подключится.

---

## 8. Куда класть

| Папка | Файлы |
|---|---|
| `static/early/letters/` | `letter-a-hero.png`, кусочки, `scene-*.png`, предметы, `spark.png` |
| `static/early/slovik/` | позы — уже лежат |
