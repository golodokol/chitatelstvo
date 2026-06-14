# Примеры Zero Block — Читательство

Префикс классов: `chit-`. Копировать HTML + CSS в соответствующие вкладки Zero Block.

---

## Пример 1: Hero

**HTML:**

```html
<div class="chit-hero">
  <div class="chit-wrap">
    <p class="chit-eyebrow">Литературная школа онлайн</p>
    <h1 class="chit-hero__title">Читательство</h1>
    <p class="chit-hero__lead">Чтение без давления — для детей 7–10 лет. Сказки, задания и маленькие победы каждую неделю.</p>
    <div class="chit-hero__actions">
      <a href="#registration" class="chit-btn chit-btn--primary">Записаться в Читательство</a>
      <a href="#how" class="chit-btn chit-btn--ghost">Как устроен модуль</a>
    </div>
  </div>
</div>
```

**CSS:**

```css
.chit-hero {
  --chit-bg: #FAF7F2;
  --chit-text: #2A2622;
  --chit-primary: #3D4F7C;
  --chit-accent: #C4694A;
  background: linear-gradient(165deg, #FAF7F2 0%, #F0EBE3 100%);
  padding: 96px 20px 80px;
  font-family: 'Inter', system-ui, sans-serif;
  color: var(--chit-text);
}
.chit-wrap { max-width: 1120px; margin: 0 auto; }
.chit-eyebrow {
  font-size: 0.875rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6B6560;
  margin: 0 0 16px;
}
.chit-hero__title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(2.25rem, 5vw, 3.5rem);
  line-height: 1.1;
  color: var(--chit-primary);
  margin: 0 0 20px;
  font-weight: 600;
}
.chit-hero__lead {
  font-size: clamp(1.05rem, 2vw, 1.25rem);
  line-height: 1.6;
  max-width: 560px;
  margin: 0 0 32px;
  color: #4A4540;
}
.chit-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.chit-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 0 28px;
  border-radius: 999px;
  font-size: 1rem;
  font-weight: 600;
  text-decoration: none;
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}
.chit-btn--primary {
  background: #C4694A;
  color: #fff;
  box-shadow: 0 4px 16px rgba(196, 105, 74, 0.25);
}
.chit-btn--primary:hover {
  background: #A85538;
  transform: translateY(-1px);
}
.chit-btn--ghost {
  background: transparent;
  color: #3D4F7C;
  border: 1.5px solid #E5DFD6;
}
.chit-btn--ghost:hover { background: #fff; }
.chit-btn:focus-visible {
  outline: 2px solid #3D4F7C;
  outline-offset: 3px;
}
@media (max-width: 640px) {
  .chit-hero { padding: 64px 20px 48px; }
  .chit-hero__actions { flex-direction: column; }
  .chit-btn { width: 100%; }
}
```

---

## Пример 2: Bento «Как устроен модуль»

**HTML:**

```html
<div class="chit-module" id="how">
  <div class="chit-wrap">
    <h2 class="chit-module__title">Один модуль — четыре недели</h2>
    <div class="chit-bento">
      <article class="chit-card chit-card--wide">
        <span class="chit-card__num">01</span>
        <h3 class="chit-card__h">3–4 сказки</h3>
        <p class="chit-card__p">Каждая — отдельный мини-курс с видео и заданиями.</p>
      </article>
      <article class="chit-card">
        <span class="chit-card__num">02</span>
        <h3 class="chit-card__h">15–20 минут</h3>
        <p class="chit-card__p">Короткий рабочий лист — без марафонов.</p>
      </article>
      <article class="chit-card">
        <span class="chit-card__num">03</span>
        <h3 class="chit-card__h">Баллы сами</h3>
        <p class="chit-card__p">Видео и квиз засчитываются автоматически.</p>
      </article>
      <article class="chit-card chit-card--accent">
        <span class="chit-card__num">04</span>
        <h3 class="chit-card__h">Живая встреча</h3>
        <p class="chit-card__p">Раз в неделю — обсудить сказку и поиграть.</p>
      </article>
    </div>
  </div>
</div>
```

**CSS:**

```css
.chit-module {
  padding: 80px 20px;
  background: #fff;
  font-family: 'Inter', system-ui, sans-serif;
}
.chit-module__title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(1.5rem, 3vw, 2.25rem);
  color: #3D4F7C;
  margin: 0 0 40px;
  text-align: center;
}
.chit-bento {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  max-width: 1120px;
  margin: 0 auto;
}
.chit-card {
  background: #FAF7F2;
  border: 1px solid #E5DFD6;
  border-radius: 16px;
  padding: 28px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.chit-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(42, 38, 34, 0.08);
}
.chit-card--wide { grid-column: span 2; }
.chit-card--accent {
  background: linear-gradient(135deg, #3D4F7C 0%, #4A608F 100%);
  border-color: transparent;
  color: #fff;
}
.chit-card--accent .chit-card__num,
.chit-card--accent .chit-card__p { color: rgba(255,255,255,0.75); }
.chit-card--accent .chit-card__h { color: #fff; }
.chit-card__num {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #C4694A;
  display: block;
  margin-bottom: 12px;
}
.chit-card__h {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.25rem;
  margin: 0 0 8px;
  color: #2A2622;
}
.chit-card__p {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.55;
  color: #6B6560;
}
@media (max-width: 640px) {
  .chit-module { padding: 48px 20px; }
  .chit-bento { grid-template-columns: 1fr; }
  .chit-card--wide { grid-column: span 1; }
}
```

---

## Пример 3: Доверие для родителей

**HTML:**

```html
<div class="chit-trust">
  <div class="chit-wrap chit-trust__grid">
    <div class="chit-trust__copy">
      <h2 class="chit-trust__title">А родителю — спокойствие</h2>
      <p class="chit-trust__text">Прогресс на личной странице. Короткие уведомления — на email, в Telegram или только в браузере.</p>
      <ul class="chit-trust__list">
        <li>Без сравнения с другими детьми</li>
        <li>Без лишних звонков</li>
        <li>Ребёнок идёт в своём темпе</li>
      </ul>
    </div>
    <div class="chit-trust__panel">
      <p class="chit-trust__badge">Личная страница</p>
      <p class="chit-trust__stat">Баллы · бейджи · следующий урок</p>
      <p class="chit-trust__note">Всё в одном месте — сохраните ссылку в закладки.</p>
    </div>
  </div>
</div>
```

**CSS:**

```css
.chit-trust {
  padding: 80px 20px;
  background: #F0EBE3;
  font-family: 'Inter', system-ui, sans-serif;
}
.chit-trust__grid {
  max-width: 1120px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
}
.chit-trust__title {
  font-family: 'Fraunces', Georgia, serif;
  font-size: clamp(1.5rem, 3vw, 2rem);
  color: #3D4F7C;
  margin: 0 0 16px;
}
.chit-trust__text {
  color: #4A4540;
  line-height: 1.6;
  margin: 0 0 20px;
}
.chit-trust__list {
  margin: 0;
  padding: 0;
  list-style: none;
}
.chit-trust__list li {
  padding: 8px 0 8px 28px;
  position: relative;
  color: #2A2622;
}
.chit-trust__list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 14px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #5A7A6A;
}
.chit-trust__panel {
  background: #fff;
  border-radius: 20px;
  padding: 36px;
  box-shadow: 0 4px 24px rgba(42, 38, 34, 0.06);
}
.chit-trust__badge {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #5A7A6A;
  background: #EEF4F0;
  padding: 6px 12px;
  border-radius: 999px;
  margin: 0 0 16px;
}
.chit-trust__stat {
  font-family: 'Fraunces', Georgia, serif;
  font-size: 1.35rem;
  color: #3D4F7C;
  margin: 0 0 12px;
}
.chit-trust__note {
  margin: 0;
  font-size: 0.9rem;
  color: #6B6560;
  line-height: 1.5;
}
@media (max-width: 768px) {
  .chit-trust { padding: 48px 20px; }
  .chit-trust__grid { grid-template-columns: 1fr; }
}
```
