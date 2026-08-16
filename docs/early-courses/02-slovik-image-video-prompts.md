# Промпты: изображения и видео Словика для вступительных роликов

**Для кого:** ты (генерация картинок → оживление → склейка)  
**Курсы:** пробные «Буквы оживают» и «Первые истории»  
**AI только для intro-роликов** (30–45 сек). Короткие реплики в станциях — без lip sync.  
**Дата фиксации:** 16.08.2026

**Стек:** картинка (с reference Словика) → Kling / Hedra (оживление + lip sync) → CapCut (склейка под VO актёра).

**Эталон персонажа:** `https://api.chitatelstvo.ru/static/sloviki/slovik-main.png`  
Всегда загружай reference и пиши `same character as reference`.

**Аудио от чтеца:** `bo-trial-intro.wav`, `ph-trial-intro.wav`  
(тексты — в `01-voice-actor-intro.md`)

---

## 0. Порядок работы

1. Зафиксировать эталон `slovik-ref-hero` (максимально похож на `slovik-main.png`).
2. Сгенерировать все кадры **только** от этого эталона (character / image reference).
3. Оживить кадры в video **из готовых картинок** (не text-to-video с нуля).
4. В CapCut склеить под полный VO; музыка тише речи (−18…−22 dB) или без музыки.
5. Экспорт: mp4 H.264, 1080p; желательно 16:9 (+ 9:16 по желанию).

Если лицо «плывёт»: меньше motion, Static brush на лицо (Kling), короче клип.

---

## 1. CHARACTER LOCK (вставлять в КАЖДЫЙ image-промпт)

```text
CHARACTER LOCK (keep identical in every image):
Same mascot as reference image — Slovik, a soft friendly storybook companion for kids 4–7.
Cute rounded proportions, big expressive eyes, gentle smile, soft fabric/plush-like texture,
warm cream and soft terracotta/coral accents, simple clean design, no scary teeth, no neon,
no glossy 3D plastic look. Recognizable face and silhouette must stay consistent.
Style: warm children's book illustration, soft watercolor-flat shading, high readability,
centered character, plain or softly blurred background unless scene is specified.
No text, no letters, no watermark, no logo, no UI.
```

### Negative prompt

```text
blurry, deformed face, extra limbs, text, letters, alphabet overlay, watermark, logo,
photorealistic human, horror, scary, neon, cyberpunk, cluttered background, low quality
```

### Формат картинок

- Для оживления с губами: **1:1 или 4:5**, персонаж крупно.
- Для широких сцен: **16:9**, но лицо Словика всё равно читаемое.

---

## 2. Базовые позы Словика (общие)

| ID файла | Назначение | Prompt |
|---|---|---|
| `slovik-ref-hero` | эталон | `CHARACTER LOCK. Full body or 3/4 portrait of Slovik facing camera, friendly hello pose, one hand raised in a soft wave, warm soft background gradient cream to peach, storybook illustration` |
| `slovik-wave` | привет | `CHARACTER LOCK. Slovik waving hello, cheerful eyes, soft smile, looking at viewer, clean warm background` |
| `slovik-talk` | говорит | `CHARACTER LOCK. Slovik mid-speech, mouth slightly open naturally, attentive friendly expression, looking at viewer, clean warm background` |
| `slovik-listen` | ждёт | `CHARACTER LOCK. Slovik listening pose, head slightly tilted, eyes curious, closed gentle smile, clean warm background` |
| `slovik-hint` | подсказка | `CHARACTER LOCK. Slovik encouraging hint pose, one finger softly raised, kind eyes, reassuring smile, clean warm background` |
| `slovik-joy` | радость | `CHARACTER LOCK. Slovik celebrating softly, small happy jump or clasped hands, bright eyes, big warm smile, clean warm background` |
| `slovik-worry` | беда / квест | `CHARACTER LOCK. Slovik mildly worried but brave, eyebrows up, holding empty hands as if something is missing, soft dramatic lighting, clean warm background` |
| `slovik-invite` | «помоги мне» | `CHARACTER LOCK. Slovik extending an open hand toward the viewer invitingly, hopeful smile, eye contact, clean warm background` |
| `slovik-chest` | награда | `CHARACTER LOCK. Slovik beside a small magical wooden chest with soft glow, proud happy expression, clean warm background` |

---

## 3. Кадры intro — Буквы оживают  
Квест: «Словик и пропавшие звуки»

| ID | Кадр | Prompt |
|---|---|---|
| `bo-intro-01-gate` | Врата страны звуков | `CHARACTER LOCK. Slovik standing at a whimsical wooden gate to the Land of Sounds, morning light, soft meadow, magical but calm atmosphere, storybook wide scene, character clearly visible in center-left` |
| `bo-intro-02-missing` | искорки пропали | `CHARACTER LOCK. Slovik in a quiet empty sound meadow looking around worried, faint empty sparkle outlines where magic sparks disappeared, soft mist, storybook illustration` |
| `bo-intro-03-sparks` | три искорки (без букв) | `CHARACTER LOCK. Slovik presenting three glowing quest sparks: hearing spark, shape spark, friendship-pair spark, floating above his paws, clear icons, no text, storybook illustration` |
| `bo-intro-04-invite` | зовёт на квест | `CHARACTER LOCK. Slovik at the gate extending hand to viewer, determined kind smile, soft sparkles returning behind him, storybook illustration` |

### Раскадровка под VO (~40 сек)

| Сек | Кадр | Смысл речи |
|---:|---|---|
| 0–8 | `bo-intro-01-gate` | Привет, Словик |
| 8–18 | `bo-intro-02-missing` | Пропали искорки |
| 18–30 | `bo-intro-03-sparks` | Три искорки: звук, буква, сочетание |
| 30–40 | `bo-intro-04-invite` | Помоги вернуть звуки |
| конец | freeze | Кнопка в уроке: «Помочь Словику» |

---

## 4. Кадры intro — Первые истории  
Квест: «Спаси первую историю»

| ID | Кадр | Prompt |
|---|---|---|
| `ph-intro-01-closed-book` | закрытая книжка | `CHARACTER LOCK. Slovik kneeling beside a large closed magical storybook sealed with a soft lock of light, worried brave expression, dusk-warm storybook lighting` |
| `ph-intro-02-empty-path` | слоги убежали | `CHARACTER LOCK. Slovik on a winding reading path where glowing syllable-stones are missing, empty sockets in the path, leaves and soft wind, urgent but child-friendly adventure mood` |
| `ph-intro-03-call-home` | вернуть слоги | `CHARACTER LOCK. Slovik gently guiding two glowing sound beads along a shining path toward the closed book in the distance, hopeful expression, magical trail of light, storybook illustration` |
| `ph-intro-04-save-invite` | помоги спасти | `CHARACTER LOCK. Slovik turning to viewer with open hand invitation, closed magical book behind him starting to glimmer faintly, heroic soft smile, help-me-save-the-first-story mood without any text` |

### Раскадровка под VO (~40 сек)

| Сек | Кадр | Смысл речи |
|---:|---|---|
| 0–8 | `ph-intro-01-closed-book` | Беда: книжка не открывается |
| 8–18 | `ph-intro-02-empty-path` | Слоги убежали |
| 18–28 | `ph-intro-03-call-home` | Вернуть: м→а, ма, слово, история |
| 28–40 | `ph-intro-04-save-invite` | Помоги спасти первую историю |
| конец | freeze | Кнопка в уроке: «Пройти тропу» / «Спасти историю» |

---

## 5. Общие VIDEO-промпты

Вставлять в каждый image-to-video:

```text
Gentle subtle animation only. Keep character face and body identical to the input image.
Soft head nod, natural blink, slight breathing motion, calm storybook camera, no morphing,
no face distortion, no extra fingers, no zoom chaos, no scene change, high consistency.
Kids content, warm lighting.
```

Если есть lip sync / audio:

```text
Mouth moves naturally in sync with the provided speech audio.
Keep lip motion gentle and readable, not exaggerated.
Eyes stay alive with soft blinks. Head moves slightly while talking.
Identity lock to reference frame.
```

Промпт-ориентир (короткий):

```text
warm storybook mascot character talking gently, soft head movement, blink, mouth synced to speech, kids illustration, stable face, calm camera
```

---

## 6. Клипы оживления — Буквы оживают

| Клип | Картинка-вход | Длит. | Video prompt |
|---|---|---:|---|
| `bo-v01` | `bo-intro-01-gate` | 6–8с | `Slovik waves hello softly at the gate, gentle blink, slight body sway, morning sparkles drift slowly. GENERAL VIDEO RULES.` |
| `bo-v02` | `bo-intro-02-missing` | 8–10с | `Slovik looks left and right searching for missing sparks, worried then brave, soft wind in grass, tiny empty sparkle outlines flicker. GENERAL VIDEO RULES.` |
| `bo-v03` | `bo-intro-03-sparks` | 8–10с | `Three quest sparks glow and pulse gently as Slovik presents them, soft magical shimmer, character talks with subtle mouth motion. GENERAL + LIP SYNC.` |
| `bo-v04` | `bo-intro-04-invite` | 6–8с | `Slovik extends hand toward camera invitingly, hopeful smile, sparks slowly return in background. GENERAL + LIP SYNC.` |

---

## 7. Клипы оживления — Первые истории

| Клип | Картинка-вход | Длит. | Video prompt |
|---|---|---:|---|
| `ph-v01` | `ph-intro-01-closed-book` | 7–9с | `Slovik looks at the sealed magical book with concern, book lock glows faintly, soft dramatic light. GENERAL + LIP SYNC.` |
| `ph-v02` | `ph-intro-02-empty-path` | 8–10с | `Camera gently pushes along the empty path, Slovik turns searching for missing syllable-lights, leaves move softly. GENERAL VIDEO RULES.` |
| `ph-v03` | `ph-intro-03-call-home` | 8–10с | `Glowing beads travel along the shining path toward the distant book, Slovik guides them kindly. GENERAL + LIP SYNC.` |
| `ph-v04` | `ph-intro-04-save-invite` | 6–8с | `Slovik reaches hand to viewer, book behind him glimmers stronger as if almost waking. GENERAL + LIP SYNC.` |

---

## 8. Склейка в CapCut (памятка)

- Переходы: crossfade 8–12 кадров.
- Один полный VO-файл на ролик поверх клипов.
- Субтитры крупно, 1 строка (тексты из `01-voice-actor-intro.md`).
- В конце 0,5 сек тишины / freeze перед кнопкой урока.
- Имена финалов: `bo-trial-intro.mp4`, `ph-trial-intro.mp4`.

---

## 9. Станции после intro (названия зафиксированы; картинки станций — отдельным пакетом)

### Буквы оживают · «Словик и пропавшие звуки»

0. Врата страны звуков (этот intro)  
1. Поляна шёпотов  
2. Пещера эха  
3. Мастерская буквы  
4. Охота на А  
5. Корзина слов  
6. Мост дружбы  
7. Пауза в траве  
8. Финишный сундук  
9. Награда Словика  

### Первые истории · «Спаси первую историю»

0. Закрытая книжка (этот intro)  
1. Камни букв  
2. Звуковая тропа  
3. Поляна слогов  
4. Пауза на тропе  
5. Домик слов  
6. Окно истории  
7. Ключ от книжки  
8. Награда Словика  

---

## 10. Чеклист готовности intro

- [ ] Эталон `slovik-ref-hero` похож на `slovik-main.png`
- [ ] 4 кадра BO + 4 кадра PH
- [ ] 4+4 видеоклипа без морфинга лица
- [ ] VO актёра наложено, губы только во intro
- [ ] Финалы `bo-trial-intro.mp4`, `ph-trial-intro.mp4`
