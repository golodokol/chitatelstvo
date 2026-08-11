#!/usr/bin/env python3
"""Дожать evergreen: 2 шага записи, отзывы, meta, кабинет-превью."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TILDA = ROOT / "docs" / "tilda-zero-main"
COURSES = ROOT / "docs" / "course-pages"


def patch_enroll_two_steps() -> None:
    path = TILDA / "01-html.txt"
    text = path.read_text(encoding="utf-8")
    old = """      <div class="step-block date-box is-visible" id="chit-date-box">
        <div class="step-label"><em>шаг 3</em> · блок программы</div>
        <p class="step-hint" id="chit-step3-hint" hidden>Для «Разового» выберите блок, затем нажмите на одну сказку в списке ниже.</p>
        <p class="step-hint" id="chit-stage1-closed-note" hidden>На тарифе «С преподавателем» сейчас открыт блок 2 — сказки 5–8 и живые встречи по четвергам.</p>
        <p class="step-hint step-hint--always" id="chit-step3-guide">Список сказок ниже — программа блока; выбирать их не нужно (кроме «Разового»).</p>
        <div class="stage-row" id="chit-stages">
          <button type="button" class="pill" data-stage="1">Блок 1 · сказки 1–4</button>
          <button type="button" class="pill is-active" data-stage="2">Блок 2 · сказки 5–8</button>
        </div>
        <div class="tales" id="chit-tales"></div>
        <div class="block-preview" id="chit-block-preview" style="display:none"></div>
      </div>"""
    new = """      <div class="step-block date-box is-visible" id="chit-date-box">
        <div class="step-label">блок программы</div>
        <p class="step-hint" id="chit-step3-hint" hidden>Для «Разового» выберите блок и нажмите на одну сказку ниже.</p>
        <p class="step-hint" id="chit-stage1-closed-note" hidden>На тарифе «С преподавателем» сейчас открыт блок 2 — сказки 5–8 и живые встречи по четвергам.</p>
        <p class="step-hint step-hint--always" id="chit-step3-guide">В тарифе уже все 4 сказки блока — выбирать сказки не нужно (кроме «Разового»).</p>
        <div class="stage-row" id="chit-stages">
          <button type="button" class="pill" data-stage="1">Блок 1 · сказки 1–4</button>
          <button type="button" class="pill is-active" data-stage="2">Блок 2 · сказки 5–8</button>
        </div>
        <div class="tales" id="chit-tales"></div>
        <div class="block-preview" id="chit-block-preview" style="display:none"></div>
      </div>"""
    if old not in text:
        raise SystemExit("enroll block not found")
    text = text.replace(old, new, 1)
    text = text.replace(
        '<p class="step-hint step-hint--always">Платный формат на 4 недели. Бесплатный урок — выше, это не то же самое, что «Разовое»</p>',
        '<p class="step-hint step-hint--always">Два шага: возраст и формат. Ниже выберите блок из 4 сказок. Бесплатный урок — выше, это не «Разовое»</p>',
        1,
    )
    path.write_text(text, encoding="utf-8")
    print("enroll: 2-step wording")


PROOF_REVIEWS = """
    <div class="proof-reviews" aria-label="Отзывы родителей">
      <article class="proof-review">
        <p class="proof-review__text">«Наконец-то ребёнок не просто „прочитал для галочки“ — он рассказывает, что понял, и сам просит следующую сказку.»</p>
        <cite class="proof-review__author">Мария, мама ученика 2 класса</cite>
      </article>
      <article class="proof-review">
        <p class="proof-review__text">«Удобно, что всё на личной странице: видно баллы, открытые уроки — не нужно ничего отмечать вручную.»</p>
        <cite class="proof-review__author">Ольга, тариф «Индивидуальное»</cite>
      </article>
      <article class="proof-review">
        <p class="proof-review__text">«Ребёнку было интересно в „Читательстве“ — настоящее книжное королевство: живые иллюстрации, музыка и задания. Каждый раз ждёт „открытие сундука“.»</p>
        <cite class="proof-review__author">Николай, старший брат</cite>
      </article>
    </div>
"""

CABINET_MOCK = """
    <div class="proof-product">
      <div class="proof-product__text">
        <h3>Личная страница ребёнка</h3>
        <p>После оплаты на email приходит ссылка на кабинет: открытые сказки, Словики, уровни и сундук после урока. Ребёнок видит свой путь — вы понимаете, что происходит на каждом занятии.</p>
        <a class="btn btn--outline" href="#program">Начать с бесплатного урока</a>
      </div>
      <figure class="cabinet-mock" aria-label="Как выглядит кабинет">
        <div class="cabinet-mock__chrome">
          <span></span><span></span><span></span>
          <em>комната приключений</em>
        </div>
        <div class="cabinet-mock__body">
          <div class="cabinet-mock__hi">
            <strong>Привет, Даниил!</strong>
            <span>Ты уже на уровне Юный читатель</span>
          </div>
          <div class="cabinet-mock__stats">
            <div>
              <img src="https://api.chitatelstvo.ru/assets/gamify-level-young-reader.png" alt="" width="56" height="56" loading="lazy">
              <b>Уровень</b>
              <span>Юный читатель</span>
            </div>
            <div>
              <img src="https://api.chitatelstvo.ru/assets/gamify-badge-meaning.png" alt="" width="48" height="48" loading="lazy">
              <b>Словики</b>
              <span>9</span>
            </div>
          </div>
          <div class="cabinet-mock__bar" aria-hidden="true"><i style="width:78%"></i></div>
          <p class="cabinet-mock__note">До следующего уровня осталось 1 Словик · сундук совсем близко</p>
        </div>
        <figcaption>Так выглядит комната приключений после урока</figcaption>
      </figure>
    </div>
"""


def patch_proof() -> None:
    path = TILDA / "01-html.txt"
    text = path.read_text(encoding="utf-8")
    old_product = """    <div class="proof-product">
      <div class="proof-product__text">
        <h3>Личная страница ребёнка</h3>
        <p>После оплаты на email приходит ссылка на кабинет: открытые сказки, Словики, уровни и сундук после урока. Ребёнок видит свой путь — вы понимаете, что происходит на каждом занятии.</p>
        <a class="btn btn--outline" href="#program">Начать с бесплатного урока</a>
      </div>
      <div class="proof-product__visual" aria-hidden="true">
        <img src="https://api.chitatelstvo.ru/assets/gamify-level-young-reader.png" alt="" width="120" height="120" loading="lazy">
        <img src="https://api.chitatelstvo.ru/assets/gamify-badge-meaning.png" alt="" width="88" height="88" loading="lazy">
        <img src="https://api.chitatelstvo.ru/assets/gamify-badge-storyteller.png" alt="" width="88" height="88" loading="lazy">
      </div>
    </div>
  </div>
</section>"""
    if "proof-reviews" not in text:
        if old_product not in text:
            raise SystemExit("proof product block not found")
        text = text.replace(
            old_product,
            PROOF_REVIEWS + "\n" + CABINET_MOCK + "\n  </div>\n</section>",
            1,
        )
    # chapter title
    text = text.replace(
        "<span class=\"section__chapter\"><em>глава 7½</em> · как это выглядит</span>\n    <h2 class=\"section__title\">Школа уже работает</h2>",
        "<span class=\"section__chapter\"><em>глава 7½</em> · отзывы и кабинет</span>\n    <h2 class=\"section__title\">Школа уже работает</h2>",
        1,
    )
    path.write_text(text, encoding="utf-8")
    print("proof: reviews + cabinet mock")


CSS_EXTRA = """
#chit-main .proof-reviews {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin: 8px 0 28px;
}
#chit-main .proof-review {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px 18px;
}
#chit-main .proof-review__text {
  margin: 0 0 14px;
  font-size: 15px;
  line-height: 1.55;
  color: var(--text);
}
#chit-main .proof-review__author {
  display: block;
  font-style: normal;
  font-size: 13px;
  font-weight: 700;
  color: var(--muted);
}
#chit-main .cabinet-mock {
  margin: 0;
  background: linear-gradient(180deg, #EDF3F9 0%, #F7F5FA 100%);
  border: 1.5px solid var(--border);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: var(--shadow);
}
#chit-main .cabinet-mock__chrome {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  background: rgba(255,255,255,.85);
  border-bottom: 1px solid var(--border);
}
#chit-main .cabinet-mock__chrome span {
  width: 8px; height: 8px; border-radius: 50%;
  background: #D4E2EF;
}
#chit-main .cabinet-mock__chrome em {
  margin-left: 8px;
  font-style: normal;
  font-size: 12px;
  font-weight: 800;
  color: var(--blue);
  letter-spacing: .02em;
}
#chit-main .cabinet-mock__body { padding: 18px 16px 16px; }
#chit-main .cabinet-mock__hi strong {
  display: block;
  font-size: 18px;
  color: var(--blue);
}
#chit-main .cabinet-mock__hi span {
  display: block;
  margin-top: 2px;
  font-size: 13px;
  color: var(--muted);
  font-weight: 600;
}
#chit-main .cabinet-mock__stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin: 16px 0 12px;
}
#chit-main .cabinet-mock__stats > div {
  background: #fff;
  border-radius: 14px;
  padding: 12px 10px;
  text-align: center;
  border: 1px solid var(--border);
}
#chit-main .cabinet-mock__stats img {
  display: block;
  margin: 0 auto 6px;
  width: 48px;
  height: 48px;
  object-fit: contain;
}
#chit-main .cabinet-mock__stats b {
  display: block;
  font-size: 11px;
  letter-spacing: .04em;
  text-transform: uppercase;
  color: var(--accent);
}
#chit-main .cabinet-mock__stats span {
  display: block;
  margin-top: 2px;
  font-size: 14px;
  font-weight: 800;
  color: var(--blue);
}
#chit-main .cabinet-mock__bar {
  height: 10px;
  border-radius: 999px;
  background: #D8E5F1;
  overflow: hidden;
}
#chit-main .cabinet-mock__bar i {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #5B7FA6, #8F7DA3);
  border-radius: inherit;
}
#chit-main .cabinet-mock__note {
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--muted);
  font-weight: 600;
}
#chit-main .cabinet-mock figcaption {
  padding: 10px 14px 12px;
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
  background: rgba(255,255,255,.7);
  border-top: 1px solid var(--border);
}
@media (max-width: 900px) {
  #chit-main .proof-reviews { grid-template-columns: 1fr; }
}
"""


def patch_css() -> None:
    css_path = TILDA / "chit-zero.css"
    css = css_path.read_text(encoding="utf-8")
    marker = "/* ===== proof reviews + cabinet mock ===== */"
    if marker in css:
        css = css[: css.index(marker)].rstrip() + "\n"
    css = css.rstrip() + "\n\n" + marker + "\n" + CSS_EXTRA + "\n"
    css_path.write_text(css, encoding="utf-8")
    (TILDA / "02-css.txt").write_text(css, encoding="utf-8")
    print("css: reviews + cabinet")


def patch_meta() -> None:
    metas = {
        "grade-1.html": (
            "Курс литературного чтения · 1 класс — Читательство",
            "Онлайн-школа литературного чтения для 1 класса: 8 сказок, видеоуроки, задания на смысл и личная страница прогресса.",
        ),
        "grade-2.html": (
            "Курс литературного чтения · 2 класс — Читательство",
            "Онлайн-школа литературного чтения для 2 класса: 8 сказок, видеоуроки, задания на смысл и личная страница прогресса.",
        ),
        "grade-3.html": (
            "Курс литературного чтения · 3 класс — Читательство",
            "Онлайн-школа литературного чтения для 3 класса: 8 произведений, видеоуроки и личная страница прогресса.",
        ),
        "grade-4.html": (
            "Курс литературного чтения · 4 класс — Читательство",
            "Онлайн-школа литературного чтения для 4 класса: 8 книг, видеоуроки и личная страница прогресса.",
        ),
        "extra-6-8.html": (
            "Внеклассное чтение 6–8 лет — Читательство",
            "Онлайн-школа литературного чтения для детей 6–8 лет: 8 книг, видеоуроки и личная страница прогресса.",
        ),
        "extra-9-11.html": (
            "Внеклассное чтение 9–11 лет — Читательство",
            "Онлайн-школа литературного чтения для детей 9–11 лет: 8 повестей, видеоуроки и личная страница прогресса.",
        ),
        "index.html": (
            "Программы по возрастам — Читательство",
            "Онлайн-школа литературного чтения: программы для 1–4 класса и внеклассное чтение 6–11 лет. Видеоуроки, задания и личная страница прогресса.",
        ),
    }
    for name, (title, desc) in metas.items():
        path = COURSES / name
        path.write_text(
            f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="chit-course-page.css?v=20260812b">
</head>
<body class="chit-course-page" data-{"page=\"hub\"" if name == "index.html" else f'group="{name.replace(".html", "")}"'}>
  <div id="chit-course"></div>
  <script src="https://api.chitatelstvo.ru/static/chit-image-guard.js?v=20260812b"></script>
  <script src="chit-course-data.js?v=20260812b"></script>
  <script src="chit-course-page.js?v=20260812b"></script>
</body>
</html>
""",
            encoding="utf-8",
        )
    # bump data version
    data = COURSES / "chit-course-data.js"
    t = data.read_text(encoding="utf-8")
    t = t.replace("PAGES_VERSION = '20260812a'", "PAGES_VERSION = '20260812b'")
    data.write_text(t, encoding="utf-8")
    print("meta: course pages fixed")


def patch_js_show_date_copy() -> None:
    path = TILDA / "chit-zero.src.js"
    text = path.read_text(encoding="utf-8")
    # ensure guides don't say "шаг 3" / date
    text = text.replace(
        "guide.textContent = 'Выберите блок программы. Список ниже — все 4 сказки уже входят в тариф, выбирать не нужно.';",
        "guide.textContent = 'Выберите блок. Список ниже — все 4 сказки уже входят в тариф.';",
    )
    path.write_text(text, encoding="utf-8")
    print("js: guide copy")


def write_video_tz() -> None:
    path = ROOT / "docs" / "VIDEO_SCHOOL_TOUR_TZ.md"
    path.write_text(
        """# ТЗ: видео «Школа изнутри» для главной Читательства

**Формат:** горизонталь 16:9 + вертикальный crop 9:16 для Reels/Stories  
**Хронометраж:** 60–75 секунд (основная версия) + нарезка 20–25 сек  
**Стиль:** спокойный product-tour как у Skyeng / Фоксфорд / Reading Eggs — экран продукта + короткий голос родителя/основателя, без кликбейта  
**Цель:** показать, что это уже работающая онлайн-школа, а не «набор на лето»

---

## Что снять (материалы)

1. **Кабинет ребёнка** (`/progress/...`) — уровни, Словики, прогресс-бар, сундук, список сказок.
2. **Урок на платформе** — 1 сказка целиком по шагам: видео → эмоциометр/вопросы → задание → сундук.
3. **Каталог программ** на сайте — 6 карточек по возрастам.
4. **Лицо/голос** — Ольга или Анастасия, 1–2 фразы в начале и в конце (можно off-screen).
5. **Живая встреча (если есть запись)** — 5–8 сек лица детей/преподавателя без лиц крупно, или только экран Zoom с никами.

Разрешение экрана: **1920×1080**, курсор крупный, без лишних вкладок и уведомлений. Имя ребёнка — вымышленное (например «Даниил»).

---

## Сценарий 70 секунд (тайминг + текст)

| Время | Кадр | Что на экране | Текст (голос / супер) |
|------:|------|---------------|------------------------|
| 0:00–0:05 | Intro | Логотип Читательство + мягкий фон луга/книг | **«Это Читательство — онлайн-школа литературного чтения для детей 6–11 лет.»** |
| 0:05–0:12 | Каталог | Главная → блок «Выберите программу», наведение на 2 класс | **«Шесть программ по возрастам. Можно начать в любой день.»** Супер: `6 программ · от 799 ₽` |
| 0:12–0:20 | Кабинет | Комната приключений: «Привет, Даниил», уровень, Словики | **«У ребёнка — своя комната приключений: уровни, баллы-Словики и прогресс.»** |
| 0:20–0:28 | Кабинет | Сундук / бейджи / полка сказок | **«После урока открывается сундук. Родитель видит, что уже пройдено.»** |
| 0:28–0:38 | Урок | Старт сказки, фрагмент видео 4–5 сек | **«Одна сказка — как мини-курс: короткое видео…»** |
| 0:38–0:48 | Урок | Вопросы / эмоциометр / карточки | **«…вопросы на понимание и задания на смысл — не пересказ наизусть.»** |
| 0:48–0:55 | Урок → сундук | Успех задания, анимация сундука | **«Словики начисляются сразу. Так чтение удерживает внимание лучше гаджетов.»** |
| 0:55–1:03 | Форматы | Тарифы: Разовое / Индивидуальное / С преподавателем | **«Можно взять одну сказку, блок из четырёх или заниматься с преподавателем по четвергам.»** |
| 1:03–1:10 | CTA | Кнопка «Попробовать бесплатно» / Словик | **«Начните с бесплатного урока — без карты. Ссылка в описании.»** Супер: `Попробуйте бесплатно` |

Музыка: лёгкая acoustic/folk без вокала, −18…−22 LUFS под голос.  
Субтитры: обязательны, крупные, без emoji-спама.

---

## Версия 20–25 секунд (Reels)

1. 0–3 сек — лого + «онлайн-школа чтения»  
2. 3–8 — кабинет (уровень + Словики)  
3. 8–16 — урок: вопрос → верный ответ → сундук  
4. 16–25 — CTA «Бесплатный урок» + URL

Текст суперкороткий: **«Не списки на лето — школа, где ребёнок понимает книги»**

---

## Чего не делать

- Не обещать «за 2 недели научим читать»  
- Не показывать даты стартов и «осталось N мест»  
- Не снимать реальные ФИО/лица детей без согласия  
- Не растягивать демо дольше 15 сек без смены кадра  

---

## Готовые фразы для супер

- Онлайн-школа литературного чтения  
- 6 программ по возрасту  
- Свой темп или с преподавателем  
- Личная страница прогресса  
- Бесплатный урок без карты  

---

## Сдача

- master 16:9, H.264, 1080p, до 80 МБ  
- vertical 9:16, 1080×1920  
- файл субтитров `.srt`  
- 3 стоп-кадра для обложки: кабинет / сундук / каталог программ  
""",
        encoding="utf-8",
    )
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    patch_enroll_two_steps()
    patch_proof()
    patch_css()
    patch_meta()
    patch_js_show_date_copy()
    write_video_tz()


if __name__ == "__main__":
    main()
