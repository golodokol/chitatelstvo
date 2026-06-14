---
name: tilda-zero-block
description: >-
  Generates HTML, CSS, and JS for Tilda Zero Blocks with modern international
  landing design and Chitatelstvo brand (literary school for children 7-10).
  Use when the user asks for Tilda zero block, custom Tilda section, landing
  block, chitatelstvo.ru design, or HTML/CSS for Tilda editor.
---

# Tilda Zero Block — Читательство

## Когда применять

Пользователь просит сверстать секцию для Tilda, нулевой блок, кастомный дизайн лендинга, hero, bento, карточки, CTA для `chitatelstvo.ru`.

## Формат ответа

Всегда выдавай в таком порядке:

1. **Назначение блока** — 1–2 предложения
2. **HTML** — вкладка HTML в Zero Block
3. **CSS** — вкладка CSS (или `<style>` только если пользователь явно просит)
4. **JS** — только если нужна интерактивность; иначе «не требуется»
5. **Настройки Tilda** — отступы секции, фон, якоря, шрифты
6. **Чеклист** — мобилка, контраст, кнопки, ссылки

## Ограничения Tilda Zero Block

- **Без фреймворков:** не подключать React, Vue, Tailwind CDN, Bootstrap.
- **Префикс классов:** только `chit-` — не конфликтовать с `.t-`, `.tn-`, `.t396`.
- **Шрифты:** Fraunces/Lora + Inter/Source Sans 3 — подключить в Tilda → Настройки сайта → Шрифты.
- **Артборд:** проектировать под ширину **1200px**, контент max **1120px**.
- **Адаптив:** mobile-first; брейкпоинты `640px`, `960px`, `1200px`.
- **Единицы:** `rem`, `%`, `clamp()`, `min()`; избегать фиксированных высот блоков.
- **Кнопки:** `<a href="...">` с классом `chit-btn`; для форм Tilda — ссылка на якорь `#registration` или URL страницы записи.
- **Изображения:** `loading="lazy"`, `alt` обязателен; предпочитать WebP через Tilda CDN.
- **JS:** оборачивать в `document.addEventListener('DOMContentLoaded', ...)`; не трогать глобальные объекты Tilda.

## Бренд

Полная палитра и тон — в [brand.md](brand.md).  
Тексты копировать/адаптировать из `docs/TILDA_TEXTS.md`.

Кратко:
- Тепло, без давления, для родителей
- Не мультяшно, не агрессивно продающе
- CTA: «Записаться в Читательство», «Записать ребёнка»

## Дизайн-правила (международные тренды)

| Принцип | Реализация |
|---------|------------|
| Editorial typography | serif в заголовках, sans в тексте, контраст размеров |
| Bento grid | CSS Grid, карточки 16px radius, лёгкая тень |
| Warm minimalism | кремовый фон `#FAF7F2`, не чистый белый на всей странице |
| Soft depth | тени `rgba(42,38,34,0.06–0.08)`, без neumorphism |
| Micro-interaction | `transition 0.2s`, `translateY(-1px)` на hover |
| Accessibility | контраст ≥ 4.5:1, `focus-visible`, кнопки ≥ 48px |
| Generous spacing | секции 80px / 48px mobile, gap 16–24px |

Избегать: glassmorphism на весь экран, неон, parallax-перегруз, autoplay video, pop-up агрессии.

## Рабочий процесс

1. Уточнить тип блока (hero / features / pricing / trust / FAQ / CTA).
2. Взять тексты из `docs/TILDA_TEXTS.md` или предложить черновик в тоне бренда.
3. Сверстать с префиксом `chit-`, CSS variables из brand.md в корне секции.
4. Проверить: 320px ширина, нет горизонтального скролла, все ссылки осмысленны.
5. Указать якоря (`#registration`, `#how`) для навигации по странице.

## Примеры

Готовые паттерны — [examples.md](examples.md):
- Hero с двумя CTA
- Bento «Как устроен модуль»
- Блок доверия для родителей

Новые блоки **наследуют** те же токены и именование из примеров.

## Чеклист перед выдачей

- [ ] Классы с префиксом `chit-`
- [ ] Адаптив 320 / 640 / 960
- [ ] Шрифты указаны для подключения в Tilda
- [ ] CTA ведёт на форму записи или якорь
- [ ] Нет внешних CDN кроме шрифтов Google (если нужны)
- [ ] Тексты без сравнения детей и без давления

## Дополнительно

- Формы webhook — `docs/TILDA_FORMS.md` (не дублировать логику API в Zero Block).
- Страница прогресса и уроки — на `api.chitatelstvo.ru`, не встраивать iframe без запроса.
