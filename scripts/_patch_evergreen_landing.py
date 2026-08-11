#!/usr/bin/env python3
"""Перевод главной и страниц курсов на evergreen-модель школы."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TILDA = ROOT / "docs" / "tilda-zero-main"
COURSES = ROOT / "docs" / "course-pages"


def replace_all(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        if old not in text:
            raise SystemExit(f"Missing expected string:\n---\n{old[:180]}\n---")
        text = text.replace(old, new)
    return text


def patch_html_txt() -> None:
    path = TILDA / "01-html.txt"
    text = path.read_text(encoding="utf-8")

    text = replace_all(
        text,
        [
            (
                """    <nav class="site-nav" aria-label="Разделы страницы">
      <a href="#how-it-works">Как устроено</a>
      <a href="#programs">Программы</a>
      <a href="#tariffs">Тарифы</a>
      <a href="#quiz">Подарок</a>
      <a href="#faq">Вопросы</a>
    </nav>
    <div class="site-header__right">
      <a class="header-cta" href="#program">Записаться</a>
    </div>""",
                """    <nav class="site-nav" aria-label="Разделы страницы">
      <a href="#programs">Программы</a>
      <a href="#how-it-works">Как проходит</a>
      <a href="#tariffs">Тарифы</a>
      <a href="#proof">О школе</a>
      <a href="#faq">Вопросы</a>
    </nav>
    <div class="site-header__right">
      <a class="header-cta" href="#programs">Выбрать программу</a>
    </div>""",
            ),
            (
                """      <h1>Понимать книги — с удовольствием</h1>
      <p class="hero__lead">Онлайн-школа литературного чтения: видео, вопросы на понимание и задания на смысл — ребёнок погружается в сказку, а вы видите прогресс на личной странице</p>
      <p class="hero__price"><strong>от 799 ₽</strong> за одну сказку на платформе</p>
      <div class="hero__cta">
        <div class="hero__actions">
          <a class="btn btn--hero" href="#program">Записаться на курс</a>
          <a class="btn btn--outline" href="https://chitatelstvo.ru/programmy">Смотреть программы</a>
        </div>
      </div>""",
                """      <h1>Понимать книги — с удовольствием</h1>
      <p class="hero__lead">Онлайн-школа литературного чтения для детей 6–11 лет: 6 программ по возрасту, видео и задания на смысл, личный кабинет с прогрессом. Начать можно в любой день</p>
      <p class="hero__price"><strong>от 799 ₽</strong> за одну сказку · запись открыта</p>
      <div class="hero__cta">
        <div class="hero__actions">
          <a class="btn btn--hero" href="#programs">Выбрать программу</a>
          <a class="btn btn--outline" href="#quiz">Попробовать бесплатно</a>
        </div>
      </div>""",
            ),
            (
                """        <p id="hero-book-text"><strong style="color:var(--blue)">8 сказок</strong> на полке каждого класса. Два старта: <span class="hero-book-text__nb"><strong>15&nbsp;июля</strong> и <strong>10&nbsp;августа</strong></span>, но присоединиться можно в любой момент</p>""",
                """        <p id="hero-book-text"><strong style="color:var(--blue)">8 сказок</strong> в каждой программе · <span class="hero-book-text__nb">свой темп или с преподавателем</span> · начать можно с любой сказки</p>""",
            ),
            (
                """      <p><strong>Базовый курс</strong> — для 1–4 класса, <strong>внеклассное чтение</strong> — для детей 6–11 лет. <strong>12 сказок за лето</strong> — три блока по 4: старт <strong>15 июля</strong>, продолжение <strong>10 августа</strong> и <strong>внеклассная программа</strong>. Оплата — за блок из 4 сказок или за одну, если хотите попробовать.</p>
    </div>
    <div class="summer-timeline" id="timeline">
      <div class="summer-timeline__track">
        <div class="summer-timeline__node">
          <span class="summer-timeline__date">15 июля</span>
          <span class="summer-timeline__label">4 сказки · 4 недели</span>
        </div>
        <span class="summer-timeline__arrow" aria-hidden="true">→</span>
        <div class="summer-timeline__node">
          <span class="summer-timeline__date">10 августа</span>
          <span class="summer-timeline__label">ещё 4 сказки · 4 недели</span>
        </div>
        <span class="summer-timeline__arrow" aria-hidden="true">→</span>
        <div class="summer-timeline__node summer-timeline__node--extra">
          <span class="summer-timeline__date">внеклассное</span>
          <span class="summer-timeline__label">ещё 4 сказки · 6–11 лет</span>
        </div>
        <span class="summer-timeline__total">= 12 сказок за лето</span>
      </div>
    </div>""",
                """      <p><strong>6 программ</strong> для детей 6–11 лет: школьное чтение (1–4 класс) и внеклассное. В каждой — <strong>8 сказок</strong> с видео, заданиями и личным прогрессом. Можно взять одну сказку, блок из 4 или всю программу.</p>
    </div>
    <div class="school-pillars" id="timeline" aria-label="Как устроена школа">
      <article class="school-pillars__item">
        <h3 class="school-pillars__title">Программы по возрасту</h3>
        <p class="school-pillars__text">Шесть направлений — своя полка книг для каждого класса и возраста</p>
      </article>
      <article class="school-pillars__item">
        <h3 class="school-pillars__title">Свой темп</h3>
        <p class="school-pillars__text">Уроки на платформе без опозданий: присоединиться можно в любой день</p>
      </article>
      <article class="school-pillars__item">
        <h3 class="school-pillars__title">Живые встречи</h3>
        <p class="school-pillars__text">Опционально — квест в мини-группе 4–6 детей по четвергам</p>
      </article>
    </div>""",
            ),
            (
                """            <span class="tariff-card__meet-line tariff-card__meet-line--muted">Живые занятия-квесты с преподавателем — со старта 10 августа (поток 15 июля — только онлайн)</span>""",
                """            <span class="tariff-card__meet-line tariff-card__meet-line--muted">Живые занятия-квесты — на тарифе «С преподавателем», встречи по четвергам</span>""",
            ),
            (
                """    <span class="section__chapter"><em>глава 6</em> · полка сказок</span>
    <h2 class="section__title">Сказки по классам</h2>
    <p class="section__lead">Полная программа — 8 сказок. Оплата — за блок из 4 или за одну сказку</p>
    <div class="prog-shelf" aria-hidden="true"><img src="https://api.chitatelstvo.ru/assets/programs-shelf-strip.png" alt="" width="900" height="300"></div>

    <div class="prog-block">
      <h3 class="prog-block__title">Базовый курс</h3>
      <p class="prog-block__sub">Для учеников 1–4 класса</p>
      <p class="prog-block__note">Эти сказки чаще всего встречаются в летних списках обязательного чтения — мы поможем ребёнку разобрать и понять каждую.</p>
      <div class="acc" id="acc-basic"></div>
    </div>
    <div class="prog-block">
      <h3 class="prog-block__title">Внеклассное чтение</h3>
      <p class="prog-block__sub">Для детей 6–8 и 9–11 лет</p>
      <div class="acc" id="acc-extra"></div>
    </div>""",
                """    <span class="section__chapter"><em>глава 6</em> · программы</span>
    <h2 class="section__title">Выберите программу по возрасту</h2>
    <p class="section__lead">6 курсов · в каждом 8 сказок · начать можно сегодня</p>

    <div class="course-catalog" id="course-catalog" aria-label="Каталог программ">
      <a class="course-card" href="https://chitatelstvo.ru/1-klass">
        <span class="course-card__badge">Базовый курс</span>
        <strong class="course-card__title">1 класс</strong>
        <span class="course-card__meta">7–8 лет · 8 сказок</span>
        <span class="course-card__status">Доступно · старт в любой день</span>
        <span class="course-card__price">от 799 ₽</span>
        <span class="course-card__cta">Смотреть программу →</span>
      </a>
      <a class="course-card" href="https://chitatelstvo.ru/2-klass">
        <span class="course-card__badge">Базовый курс</span>
        <strong class="course-card__title">2 класс</strong>
        <span class="course-card__meta">8–9 лет · 8 сказок</span>
        <span class="course-card__status">Доступно · старт в любой день</span>
        <span class="course-card__price">от 799 ₽</span>
        <span class="course-card__cta">Смотреть программу →</span>
      </a>
      <a class="course-card" href="https://chitatelstvo.ru/3-klass">
        <span class="course-card__badge">Базовый курс</span>
        <strong class="course-card__title">3 класс</strong>
        <span class="course-card__meta">9–10 лет · 8 сказок</span>
        <span class="course-card__status">Доступно · старт в любой день</span>
        <span class="course-card__price">от 799 ₽</span>
        <span class="course-card__cta">Смотреть программу →</span>
      </a>
      <a class="course-card" href="https://chitatelstvo.ru/4-klass">
        <span class="course-card__badge">Базовый курс</span>
        <strong class="course-card__title">4 класс</strong>
        <span class="course-card__meta">10–11 лет · 8 сказок</span>
        <span class="course-card__status">Доступно · старт в любой день</span>
        <span class="course-card__price">от 799 ₽</span>
        <span class="course-card__cta">Смотреть программу →</span>
      </a>
      <a class="course-card course-card--extra" href="https://chitatelstvo.ru/6-8-let">
        <span class="course-card__badge">Внеклассное</span>
        <strong class="course-card__title">6–8 лет</strong>
        <span class="course-card__meta">Вне школьной программы · 8 сказок</span>
        <span class="course-card__status">Доступно · старт в любой день</span>
        <span class="course-card__price">от 799 ₽</span>
        <span class="course-card__cta">Смотреть программу →</span>
      </a>
      <a class="course-card course-card--extra" href="https://chitatelstvo.ru/9-11-let">
        <span class="course-card__badge">Внеклассное</span>
        <strong class="course-card__title">9–11 лет</strong>
        <span class="course-card__meta">Вне школьной программы · 8 сказок</span>
        <span class="course-card__status">Доступно · старт в любой день</span>
        <span class="course-card__price">от 799 ₽</span>
        <span class="course-card__cta">Смотреть программу →</span>
      </a>
    </div>
    <p class="course-catalog__hub"><a href="https://chitatelstvo.ru/programmy">Все программы на одной странице →</a></p>

    <div class="prog-shelf" aria-hidden="true"><img src="https://api.chitatelstvo.ru/assets/programs-shelf-strip.png" alt="" width="900" height="300"></div>

    <div class="prog-block">
      <h3 class="prog-block__title">Базовый курс · список сказок</h3>
      <p class="prog-block__sub">Для учеников 1–4 класса</p>
      <p class="prog-block__note">Сказки из школьных списков чтения — помогаем разобрать и понять каждую.</p>
      <div class="acc" id="acc-basic"></div>
    </div>
    <div class="prog-block">
      <h3 class="prog-block__title">Внеклассное чтение · список сказок</h3>
      <p class="prog-block__sub">Для детей 6–8 и 9–11 лет</p>
      <div class="acc" id="acc-extra"></div>
    </div>""",
            ),
            (
                """      <div class="step-block date-box is-visible" id="chit-date-box">
        <div class="step-label"><em>шаг 3</em> · дата старта</div>
        <p class="step-hint" id="chit-step3-hint" hidden>Для «Разового» после даты нажмите на одну сказку в списке ниже.</p>
        <p class="step-hint" id="chit-stage1-closed-note" hidden>Набор на этап 1 с преподавателем закрыт — доступна запись на старт 10 августа.</p>
        <p class="step-hint step-hint--always" id="chit-step3-guide">Список сказок ниже — программа блока; выбирать их не нужно (кроме «Разового»).</p>
        <div class="stage-row" id="chit-stages">
          <button type="button" class="pill" data-stage="1">Старт курса 15 июля</button>
          <button type="button" class="pill is-active" data-stage="2">Старт 10 августа</button>
        </div>""",
                """      <div class="step-block date-box is-visible" id="chit-date-box">
        <div class="step-label"><em>шаг 3</em> · блок программы</div>
        <p class="step-hint" id="chit-step3-hint" hidden>Для «Разового» выберите блок, затем нажмите на одну сказку в списке ниже.</p>
        <p class="step-hint" id="chit-stage1-closed-note" hidden>На тарифе «С преподавателем» сейчас открыт блок 2 — сказки 5–8 и живые встречи по четвергам.</p>
        <p class="step-hint step-hint--always" id="chit-step3-guide">Список сказок ниже — программа блока; выбирать их не нужно (кроме «Разового»).</p>
        <div class="stage-row" id="chit-stages">
          <button type="button" class="pill" data-stage="1">Блок 1 · сказки 1–4</button>
          <button type="button" class="pill is-active" data-stage="2">Блок 2 · сказки 5–8</button>
        </div>""",
            ),
            (
                """          <span class="faq-q__text">Когда начинается курс?</span>
        </button>
        <p class="faq-a"><span class="faq-a__sign">Читательство отвечает:</span>Два старта: <strong>15 июля</strong> и <strong>10 августа</strong>. Каждый — блок из 4 сказок (4 недели). При записи вы выбираете один период. Полная программа класса — 8 сказок, если пройти оба блока.</p>""",
                """          <span class="faq-q__text">Когда можно начать?</span>
        </button>
        <p class="faq-a"><span class="faq-a__sign">Читательство отвечает:</span>В любой день. Уроки открываются по расписанию платформы — присоединиться можно и с середины программы. В каждой программе 8 сказок (2 блока по 4). Можно взять одну сказку, один блок или всю программу.</p>""",
            ),
            (
                """        <p class="faq-a"><span class="faq-a__sign">Читательство отвечает:</span>Да. Можно <a href="#program">пройти урок бесплатно</a>: для 6–8 лет — «Сказка о рыбаке и рыбке», для 9–11 лет — «Сказка о царе Салтане». Или тариф «Разовое» — 799 ₽ за одну сказку онлайн. Живые занятия-квесты — со старта 10 августа.</p>""",
                """        <p class="faq-a"><span class="faq-a__sign">Читательство отвечает:</span>Да. Можно <a href="#program">пройти урок бесплатно</a>: для 6–8 лет — «Сказка о рыбаке и рыбке», для 9–11 лет — «Сказка о царе Салтане». Или тариф «Разовое» — 799 ₽ за одну сказку онлайн. Живые занятия-квесты — на тарифе «С преподавателем», по четвергам.</p>""",
            ),
            (
                """        <p class="faq-a"><span class="faq-a__sign">Читательство отвечает:</span><strong>Индивидуальное</strong> — 4 сказки в своём темпе, без живых встреч (1 990 ₽): видео, квизы и сундук после каждого урока. <strong>С преподавателем</strong> — та же основа плюс расширенная программа и квест по сказке в мини-группе 4–6 детей, 4 живые встречи со старта 10 августа (4 990 ₽). <strong>Разовое</strong> — 1 сказка онлайн (799 ₽); поток 15 июля — только онлайн, живые занятия — со старта 10 августа.</p>""",
                """        <p class="faq-a"><span class="faq-a__sign">Читательство отвечает:</span><strong>Индивидуальное</strong> — 4 сказки в своём темпе, без живых встреч (1 990 ₽): видео, квизы и сундук после каждого урока. <strong>С преподавателем</strong> — та же основа плюс расширенная программа и квест по сказке в мини-группе 4–6 детей, 4 живые встречи по четвергам (4 990 ₽). <strong>Разовое</strong> — 1 сказка онлайн (799 ₽).</p>""",
            ),
            (
                """      <h2>Почему бы не открыть первую сказку?</h2>
      <p>Школа только начинает путь — поэтому даём бесплатный доступ к платформе и одному полноценному уроку. Пройдите одно книжное приключение вместе с ребёнком, а если понравится — запись займёт пару минут.</p>""",
                """      <h2>Почему бы не открыть первую сказку?</h2>
      <p>Даём бесплатный доступ к платформе и одному полноценному уроку. Пройдите книжное приключение вместе с ребёнком — если понравится, запись на программу займёт пару минут.</p>""",
            ),
        ],
    )

    # Social proof before FAQ
    proof = """
<!-- PROOF -->
<section class="section section--cream reveal" id="proof">
  <div class="section__inner">
    <span class="section__chapter"><em>глава 7½</em> · как это выглядит</span>
    <h2 class="section__title">Школа уже работает</h2>
    <p class="section__lead">Не календарный набор, а постоянная платформа чтения с программами по возрастам</p>
    <div class="proof-stats" aria-label="О школе в цифрах">
      <div class="proof-stats__item">
        <strong class="proof-stats__num">6</strong>
        <span class="proof-stats__label">программ по возрасту</span>
      </div>
      <div class="proof-stats__item">
        <strong class="proof-stats__num">48</strong>
        <span class="proof-stats__label">сказок на полках</span>
      </div>
      <div class="proof-stats__item">
        <strong class="proof-stats__num">5</strong>
        <span class="proof-stats__label">уровней прогресса</span>
      </div>
      <div class="proof-stats__item">
        <strong class="proof-stats__num">9</strong>
        <span class="proof-stats__label">бейджей в коллекции</span>
      </div>
    </div>
    <div class="proof-product">
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
</section>

"""
    if 'id="proof"' not in text:
        text = text.replace("<!-- FAQ -->", proof + "<!-- FAQ -->", 1)

    # chapter numbers after inserting proof - FAQ stays 8, founder 9 - ok
    # Update section lead under tariffs
    text = text.replace(
        '<p class="section__lead">Самостоятельно в своём темпе или с преподавателем в мини-группе — выберите, как удобнее семье</p>',
        '<p class="section__lead">Запись открыта · доступ сразу после оплаты. Самостоятельно или с преподавателем — как удобнее семье</p>',
        1,
    )

    path.write_text(text, encoding="utf-8")
    print(f"Updated {path.relative_to(ROOT)}")


CSS_ADDON = """

/* ===== Evergreen school: pillars, catalog, proof ===== */
#chit-main .school-pillars {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  max-width: 960px;
  margin: 36px auto 0;
}
#chit-main .school-pillars__item {
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 22px 20px;
  box-shadow: var(--shadow);
}
#chit-main .school-pillars__title {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 800;
  color: var(--blue);
}
#chit-main .school-pillars__text {
  margin: 0;
  font-size: 15px;
  line-height: 1.5;
  color: var(--muted);
}
#chit-main .course-catalog {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin: 28px 0 12px;
}
#chit-main .course-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 22px 20px 20px;
  background: var(--white);
  border: 1.5px solid var(--border);
  border-radius: 18px;
  text-decoration: none;
  color: inherit;
  box-shadow: var(--shadow);
  transition: border-color .2s, transform .15s, box-shadow .2s;
}
#chit-main .course-card:hover {
  border-color: #A8C4DD;
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(61, 82, 102, .1);
}
#chit-main .course-card--extra {
  background: linear-gradient(180deg, #FBF8FC 0%, #fff 70%);
}
#chit-main .course-card__badge {
  display: inline-flex;
  align-self: flex-start;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--blue-pale, #E8F1F8);
  color: var(--blue);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .02em;
}
#chit-main .course-card--extra .course-card__badge {
  background: var(--accent-pale, #F0EAF5);
  color: var(--accent);
}
#chit-main .course-card__title {
  font-size: 24px;
  font-weight: 800;
  color: var(--blue);
  margin-top: 4px;
}
#chit-main .course-card__meta,
#chit-main .course-card__status {
  font-size: 14px;
  color: var(--muted);
  font-weight: 600;
}
#chit-main .course-card__status {
  color: #5A8F6D;
}
#chit-main .course-card__price {
  margin-top: 8px;
  font-size: 18px;
  font-weight: 800;
  color: var(--text);
}
#chit-main .course-card__cta {
  margin-top: auto;
  padding-top: 12px;
  font-size: 14px;
  font-weight: 800;
  color: var(--accent);
}
#chit-main .course-catalog__hub {
  text-align: center;
  margin: 8px 0 28px;
}
#chit-main .course-catalog__hub a {
  color: var(--blue);
  font-weight: 700;
  text-decoration: none;
}
#chit-main .course-catalog__hub a:hover { text-decoration: underline; }
#chit-main .proof-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin: 28px 0 32px;
}
#chit-main .proof-stats__item {
  text-align: center;
  padding: 20px 12px;
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 16px;
}
#chit-main .proof-stats__num {
  display: block;
  font-size: 34px;
  font-weight: 800;
  color: var(--blue);
  line-height: 1.1;
}
#chit-main .proof-stats__label {
  display: block;
  margin-top: 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--muted);
}
#chit-main .proof-product {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, .8fr);
  gap: 28px;
  align-items: center;
  padding: 28px;
  background: var(--white);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow);
}
#chit-main .proof-product h3 {
  margin: 0 0 10px;
  font-size: 22px;
  color: var(--blue);
}
#chit-main .proof-product p {
  margin: 0 0 18px;
  color: var(--muted);
  line-height: 1.55;
}
#chit-main .proof-product__visual {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}
#chit-main .proof-product__visual img {
  width: 96px;
  height: 96px;
  object-fit: contain;
}
@media (max-width: 900px) {
  #chit-main .school-pillars,
  #chit-main .course-catalog { grid-template-columns: 1fr 1fr; }
  #chit-main .proof-stats { grid-template-columns: 1fr 1fr; }
  #chit-main .proof-product { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  #chit-main .school-pillars,
  #chit-main .course-catalog { grid-template-columns: 1fr; }
}
"""


def patch_css() -> None:
    # Prefer newer chit-zero.css as base; keep 02-css in sync for build
    css_path = TILDA / "chit-zero.css"
    css = css_path.read_text(encoding="utf-8")
    marker = "/* ===== Evergreen school: pillars, catalog, proof ===== */"
    if marker in css:
        start = css.index(marker)
        css = css[:start].rstrip() + "\n"
    css = css.rstrip() + "\n" + CSS_ADDON
    css_path.write_text(css + "\n", encoding="utf-8")
    (TILDA / "02-css.txt").write_text(css + "\n", encoding="utf-8")
    print("Updated chit-zero.css and 02-css.txt")


def patch_zero_src() -> None:
    path = TILDA / "chit-zero.src.js"
    text = path.read_text(encoding="utf-8")
    text = replace_all(
        text,
        [
            (
                "        renderPeriod('Старт курса 15 июля', item.june, '1', item.group) +\n"
                "        renderPeriod('Старт 10 августа', item.july, '2', item.group) +",
                "        renderPeriod('Блок 1 · сказки 1–4', item.june, '1', item.group) +\n"
                "        renderPeriod('Блок 2 · сказки 5–8', item.july, '2', item.group) +",
            ),
            (
                "  var STAGE_LABEL = { '1': 'Старт курса 15 июля', '2': 'Старт 10 августа' };",
                "  var STAGE_LABEL = { '1': 'Блок 1 · сказки 1–4', '2': 'Блок 2 · сказки 5–8' };",
            ),
            (
                "    return 'Только онлайн. Занятия с преподавателем по сказкам потока 15 июля не проводятся — со старта 10 августа';",
                "    return 'Только онлайн. Живые занятия по сказкам блока 1 сейчас не проводятся — выберите блок 2';",
            ),
            (
                "/** Можно ли ещё докупить встречу. Поток 15 июля закрыт; со старта 10 августа — если дата в будущем. */",
                "/** Можно ли ещё докупить встречу. Блок 1 с преподавателем закрыт; блок 2 — если дата в будущем. */",
            ),
            (
                "    // Класс и основной тариф; старт — 10 августа (этап 1 с преподавателем закрыт).\n",
                "    // Класс и основной тариф; для «С преподавателем» — блок 2.\n",
            ),
            (
                "    if (!state.stage) {\n"
                "      state.stage = '2';\n"
                "      document.querySelectorAll('#chit-stages .pill').forEach(function(p) {\n"
                "        p.classList.toggle('is-active', p.getAttribute('data-stage') === '2');\n"
                "      });\n"
                "    }",
                "    if (!state.stage) {\n"
                "      state.stage = (state.tariff === 'with_teacher' && WITH_TEACHER_STAGE1_CLOSED) ? '2' : '1';\n"
                "      document.querySelectorAll('#chit-stages .pill').forEach(function(p) {\n"
                "        p.classList.toggle('is-active', p.getAttribute('data-stage') === state.stage);\n"
                "      });\n"
                "    }",
            ),
            (
                "        html += '<br><span class=\"summary-empty\">Выберите дату и сказку</span>';",
                "        html += '<br><span class=\"summary-empty\">Выберите блок и сказку</span>';",
            ),
            (
                "      html += '<br><span class=\"summary-empty\">Выберите дату старта</span>';",
                "      html += '<br><span class=\"summary-empty\">Выберите блок программы</span>';",
            ),
            (
                "        '<div class=\"block-preview__title\">Программа этого старта' +",
                "        '<div class=\"block-preview__title\">Программа этого блока' +",
            ),
            (
                "          : 'Выберите дату, затем нажмите на одну сказку в списке — её и оплатите.';",
                "          : 'Выберите блок, затем нажмите на одну сказку в списке — её и оплатите.';",
            ),
            (
                "        guide.textContent = 'Выберите дату старта. Список ниже — программа блока: все 4 сказки уже входят в тариф, выбирать не нужно.';",
                "        guide.textContent = 'Выберите блок программы. Список ниже — все 4 сказки уже входят в тариф, выбирать не нужно.';",
            ),
            (
                "      stage1.title = closed ? 'Набор на этап 1 с преподавателем закрыт' : '';",
                "      stage1.title = closed ? 'Блок 1 с преподавателем сейчас недоступен' : '';",
            ),
            (
                "      alert('Набор на этап 1 с преподавателем закрыт. Выберите старт 10 августа.');",
                "      alert('На тарифе «С преподавателем» блок 1 сейчас недоступен. Выберите блок 2.');",
            ),
            (
                "    { q: '«Лето — это маленькая жизнь»', c: '8 сказок — целое летнее путешествие в книгу' }",
                "    { q: '«Лето — это маленькая жизнь»', c: '8 сказок — целое путешествие в книгу' }",
            ),
            (
                "    '<strong style=\"color:var(--blue)\">8 сказок</strong> на полке каждого класса. Два старта: <span class=\"hero-book-text__nb\"><strong>15&nbsp;июля</strong> и <strong>10&nbsp;августа</strong></span>, но присоединиться можно в любой момент',",
                "    '<strong style=\"color:var(--blue)\">8 сказок</strong> в каждой программе · <span class=\"hero-book-text__nb\">свой темп или с преподавателем</span> · начать можно с любой сказки',",
            ),
        ],
    )
    # Second alert occurrence
    text = text.replace(
        "alert('Набор на этап 1 с преподавателем закрыт. Выберите старт 10 августа.');",
        "alert('На тарифе «С преподавателем» блок 1 сейчас недоступен. Выберите блок 2.');",
    )
    path.write_text(text, encoding="utf-8")
    print(f"Updated {path.relative_to(ROOT)}")


def patch_sync_schedule() -> None:
    path = ROOT / "scripts" / "sync_chit_schedule.py"
    text = path.read_text(encoding="utf-8")
    text = replace_all(
        text,
        [
            (
                "/** Можно ли ещё докупить встречу. Поток 15 июля закрыт; со старта 10 августа — если дата в будущем. */",
                "/** Можно ли ещё докупить встречу. Блок 1 с преподавателем закрыт; блок 2 — если дата в будущем. */",
            ),
            (
                "    return 'Только онлайн. Занятия с преподавателем по сказкам потока 15 июля не проводятся — со старта 10 августа';",
                "    return 'Только онлайн. Живые занятия по сказкам блока 1 сейчас не проводятся — выберите блок 2';",
            ),
        ],
    )
    path.write_text(text, encoding="utf-8")
    print(f"Updated {path.relative_to(ROOT)}")


def patch_build_version() -> None:
    path = ROOT / "scripts" / "build_tilda_upload.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace('VERSION = "20260728e"', 'VERSION = "20260812a"', 1)
    text = text.replace(
        'f"<!-- CHIT VERSION {VERSION} · даты 15 июля / 10 августа, пояснения в карточках формата -->\\n"',
        'f"<!-- CHIT VERSION {VERSION} · evergreen школа, программы по возрастам -->\\n"',
        1,
    )
    path.write_text(text, encoding="utf-8")
    print(f"Updated {path.relative_to(ROOT)}")


def patch_course_data() -> None:
    path = COURSES / "chit-course-data.js"
    text = path.read_text(encoding="utf-8")
    text = replace_all(
        text,
        [
            (
                "  var STAGE_LABEL = { '1': 'Старт курса 15 июля', '2': 'Старт 10 августа' };",
                "  var STAGE_LABEL = { '1': 'Блок 1 · сказки 1–4', '2': 'Блок 2 · сказки 5–8' };",
            ),
            (
                "      meetNote: 'Только онлайн. Живые занятия-квесты — со старта 10 августа',",
                "      meetNote: 'Только онлайн. Живые занятия-квесты — на тарифе «С преподавателем»',",
            ),
            (
                "    return 'Только онлайн. Занятия с преподавателем по сказкам потока 15 июля не проводятся — со старта 10 августа';",
                "    return 'Только онлайн. Живые занятия по сказкам блока 1 сейчас не проводятся — выберите блок 2';",
            ),
            (
                "      h1: 'Летний курс по школьной программе 1 класса',\n"
                "      lead: '8 сказок из школьных списков — видео, задания на понимание и личная страница прогресса. Ребёнок читает с удовольствием, вы видите результат.',\n"
                "      intro: 'Эти сказки чаще всего встречаются в летних списках обязательного чтения — мы поможем ребёнку разобрать и понять каждую.',",
                "      h1: 'Курс литературного чтения · 1 класс',\n"
                "      lead: '8 сказок из школьных списков — видео, задания на понимание и личная страница прогресса. Ребёнок читает с удовольствием, вы видите результат.',\n"
                "      intro: 'Сказки из школьных списков чтения — помогаем ребёнку разобрать и понять каждую.',",
            ),
            (
                "      h1: 'Летний курс по школьной программе 2 класса',\n"
                "      lead: '8 сказок и повестей — от Пушкина до Андерсена. Видеоуроки, вопросы на смысл и баллы на личной странице.',\n"
                "      intro: 'Программа подобрана под летние списки чтения для 2 класса — с акцентом на понимание героя и сюжета.',",
                "      h1: 'Курс литературного чтения · 2 класс',\n"
                "      lead: '8 сказок и повестей — от Пушкина до Андерсена. Видеоуроки, вопросы на смысл и баллы на личной странице.',\n"
                "      intro: 'Программа для 2 класса — с акцентом на понимание героя и сюжета.',",
            ),
            (
                "        'Хотите закрепить навык осмысленного чтения за лето',",
                "        'Хотите закрепить навык осмысленного чтения',",
            ),
            (
                "      h1: 'Летний курс по школьной программе 3 класса',\n"
                "      lead: '8 произведений — от пушкинских сказок до «Королевства кривых зеркал». Глубокое изучение книги: герои, замысел, эмоции.',\n"
                "      intro: 'Тексты соответствуют программе внеклассного и летнего чтения для 3 класса.',",
                "      h1: 'Курс литературного чтения · 3 класс',\n"
                "      lead: '8 произведений — от пушкинских сказок до «Королевства кривых зеркал». Глубокое изучение книги: герои, замысел, эмоции.',\n"
                "      intro: 'Тексты соответствуют программе чтения для 3 класса.',",
            ),
            (
                "        'Семья ищет структурированное летнее чтение',",
                "        'Семья ищет структурированное чтение дома',",
            ),
            (
                "      h1: 'Летний курс по школьной программе 4 класса',\n"
                "      lead: '8 книг — от бажовских сказов до «Пеппи» и Гулливера. Видео, задания и прогресс на пути к истинному пониманию текста.',\n"
                "      intro: 'Произведения из типичных списков летнего чтения для 4 класса — с разбором смысла и героев.',",
                "      h1: 'Курс литературного чтения · 4 класс',\n"
                "      lead: '8 книг — от бажовских сказов до «Пеппи» и Гулливера. Видео, задания и прогресс на пути к истинному пониманию текста.',\n"
                "      intro: 'Произведения из типичных списков чтения для 4 класса — с разбором смысла и героев.',",
            ),
            (
                "        'Можно пройти оба блока по 4 сказки за лето'",
                "        'Можно пройти оба блока по 4 сказки'",
            ),
            (
                "    'Летняя программа собрана из сказок школьных списков — с заданиями на истинное понимание каждой истории.';",
                "    'Программы собраны из сказок школьных и внеклассных списков — с заданиями на истинное понимание каждой истории.';",
            ),
            (
                "  var PAGES_VERSION = '20260728e';",
                "  var PAGES_VERSION = '20260812a';",
            ),
        ],
    )
    path.write_text(text, encoding="utf-8")
    print(f"Updated {path.relative_to(ROOT)}")


def patch_course_page_js() -> None:
    path = COURSES / "chit-course-page.js"
    text = path.read_text(encoding="utf-8")
    text = replace_all(
        text,
        [
            (
                "        '<p class=\"cc-hero__lead\">Шесть программ летнего чтения — выберите свою и запишитесь на курс.</p></div>' +",
                "        '<p class=\"cc-hero__lead\">Шесть программ по возрастам — выберите свою и начните в любой день.</p></div>' +",
            ),
            (
                "    var gradeMatch = h1.match(/^(Летний курс по школьной программе)\\s+(\\d+\\s+класса)$/);",
                "    var gradeMatch = h1.match(/^(Курс литературного чтения)\\s+·\\s+(\\d+\\s+класс)$/);",
            ),
            (
                "              '<span class=\"cc-banner__chip\">8 сказок · 15 июля / 10 августа</span>' +",
                "              '<span class=\"cc-banner__chip\">8 сказок · старт в любой день</span>' +",
            ),
            (
                "      '<strong>Живые встречи</strong> — на тарифе «С преподавателем» со старта 10 августа; поток 15 июля — только онлайн'",
                "      '<strong>Живые встречи</strong> — на тарифе «С преподавателем», по четвергам в мини-группе'",
            ),
            (
                "      '<strong>Даты:</strong> старт 15 июля или 10 августа, блок из 4 сказок (4 недели)',",
                "      '<strong>Старт:</strong> в любой день; программа — 2 блока по 4 сказки',",
            ),
            (
                "          '<p class=\"cc-section__lead\">Два старта на выбор. Каждую неделю открывается новая сказка.</p>' +\n"
                "          '<div class=\"cc-program-block\">' +\n"
                "            '<h3 class=\"cc-program-block__title\">Старт 15 июля</h3>' +\n"
                "            '<div class=\"cc-tale-list cc-tale-list--program\">' + taleRowsHtml(program.june, '1', 1, true) + '</div>' +\n"
                "          '</div>' +\n"
                "          '<div class=\"cc-program-block\">' +\n"
                "            '<h3 class=\"cc-program-block__title\">Старт 10 августа</h3>' +",
                "          '<p class=\"cc-section__lead\">Два блока по 4 сказки. Можно начать с любого блока.</p>' +\n"
                "          '<div class=\"cc-program-block\">' +\n"
                "            '<h3 class=\"cc-program-block__title\">Блок 1 · сказки 1–4</h3>' +\n"
                "            '<div class=\"cc-tale-list cc-tale-list--program\">' + taleRowsHtml(program.june, '1', 1, true) + '</div>' +\n"
                "          '</div>' +\n"
                "          '<div class=\"cc-program-block\">' +\n"
                "            '<h3 class=\"cc-program-block__title\">Блок 2 · сказки 5–8</h3>' +",
            ),
            (
                "            tariffCard('self_paced', 'Индивидуальное', '4 сказки — целое летнее путешествие',",
                "            tariffCard('self_paced', 'Индивидуальное', '4 сказки — путешествие в книгу',",
            ),
            (
                "              '<div class=\"cc-step-label\">шаг 2 · когда начать</div>' +\n"
                "              '<p class=\"cc-step-hint\" id=\"cc-step-hint\" hidden>799 ₽ — урок на платформе. Живые занятия-квесты — со старта 10 августа.</p>' +\n"
                "              '<p class=\"cc-step-hint\" id=\"cc-stage1-closed-note\" hidden>Набор на этап 1 с преподавателем закрыт — доступна запись на старт 10 августа.</p>' +\n"
                "              '<div class=\"cc-pills\" id=\"cc-stages\">' +\n"
                "                '<button type=\"button\" class=\"cc-pill\" data-stage=\"1\">Старт курса 15 июля</button>' +\n"
                "                '<button type=\"button\" class=\"cc-pill\" data-stage=\"2\">Старт 10 августа</button>' +",
                "              '<div class=\"cc-step-label\">шаг 2 · блок программы</div>' +\n"
                "              '<p class=\"cc-step-hint\" id=\"cc-step-hint\" hidden>799 ₽ — урок на платформе. Живые занятия — на тарифе «С преподавателем».</p>' +\n"
                "              '<p class=\"cc-step-hint\" id=\"cc-stage1-closed-note\" hidden>На тарифе «С преподавателем» сейчас открыт блок 2 — сказки 5–8 и встречи по четвергам.</p>' +\n"
                "              '<div class=\"cc-pills\" id=\"cc-stages\">' +\n"
                "                '<button type=\"button\" class=\"cc-pill\" data-stage=\"1\">Блок 1 · сказки 1–4</button>' +\n"
                "                '<button type=\"button\" class=\"cc-pill\" data-stage=\"2\">Блок 2 · сказки 5–8</button>' +",
            ),
            (
                "            faqItem('Когда начинается курс?', 'Два старта: <strong>15 июля</strong> и <strong>10 августа</strong>. Каждый — блок из 4 сказок (4 недели).') +",
                "            faqItem('Когда можно начать?', 'В любой день. В программе 8 сказок (2 блока по 4). Можно взять одну сказку, блок или всю программу.') +",
            ),
            (
                "            faqItem('Можно ли начать с одной сказки?', 'Да. Тариф «Разовое» — ' + D.formatPrice(D.TARIFF_PRICE.single) + ': одна сказка на платформе, без встречи в цене. Живые занятия-квесты — со старта 10 августа.') +",
                "            faqItem('Можно ли начать с одной сказки?', 'Да. Тариф «Разовое» — ' + D.formatPrice(D.TARIFF_PRICE.single) + ': одна сказка на платформе, без встречи в цене. Живые занятия — на тарифе «С преподавателем».') +",
            ),
            (
                "            faqItem('Чем отличаются тарифы?', 'Разовое — 1 сказка онлайн (' + D.formatPrice(D.TARIFF_PRICE.single) + '). Индивидуальное — 4 сказки без встреч (' + D.formatPrice(D.TARIFF_PRICE.self_paced) + '). С преподавателем — 4 сказки + 4 встречи со старта 10 августа (' + D.formatPrice(D.TARIFF_PRICE.with_teacher) + ').') +",
                "            faqItem('Чем отличаются тарифы?', 'Разовое — 1 сказка онлайн (' + D.formatPrice(D.TARIFF_PRICE.single) + '). Индивидуальное — 4 сказки без встреч (' + D.formatPrice(D.TARIFF_PRICE.self_paced) + '). С преподавателем — 4 сказки + 4 встречи по четвергам (' + D.formatPrice(D.TARIFF_PRICE.with_teacher) + ').') +",
            ),
            (
                "        alert('Набор на этап 1 с преподавателем закрыт. Выберите старт 10 августа.');",
                "        alert('На тарифе «С преподавателем» блок 1 сейчас недоступен. Выберите блок 2.');",
            ),
            (
                "    // По умолчанию: основной тариф + старт 10 августа",
                "    // По умолчанию: основной тариф + блок 1 (для with_teacher — блок 2)",
            ),
        ],
    )
    text = text.replace(
        "alert('Набор на этап 1 с преподавателем закрыт. Выберите старт 10 августа.');",
        "alert('На тарифе «С преподавателем» блок 1 сейчас недоступен. Выберите блок 2.');",
    )
    # bump cache on html files
    for html in COURSES.glob("*.html"):
        h = html.read_text(encoding="utf-8")
        h2 = h.replace("?v=20260727f", "?v=20260812a").replace("?v=20260728e", "?v=20260812a")
        if h2 != h:
            html.write_text(h2, encoding="utf-8")
            print(f"Bumped {html.relative_to(ROOT)}")
    path.write_text(text, encoding="utf-8")
    print(f"Updated {path.relative_to(ROOT)}")


def main() -> None:
    patch_html_txt()
    patch_css()
    patch_zero_src()
    patch_sync_schedule()
    patch_build_version()
    patch_course_data()
    patch_course_page_js()
    print("All patches applied.")


if __name__ == "__main__":
    main()
