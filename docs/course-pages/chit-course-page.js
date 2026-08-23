(function () {
  var D = window.CHIT_COURSE;
  if (!D) return;

  var pageRoot = document.getElementById('chit-course-root') || document.body;
  var group = pageRoot.getAttribute('data-group') || document.body.getAttribute('data-group');
  var isHub = pageRoot.getAttribute('data-page') === 'hub' || document.body.getAttribute('data-page') === 'hub';
  var HOME_URL = 'https://chitatelstvo.ru/';

  if (isHub) {
    renderHub();
    return;
  }
  if (!group || !D.META[group]) {
    var missing = document.getElementById('chit-course');
    if (missing) missing.innerHTML = '<p style="padding:40px;text-align:center">Страница не найдена</p>';
    return;
  }

  var meta = D.META[group];
  var program = D.PROGRAMS[group];
  var withTeacherClosed = !!(D.NO_WITH_TEACHER_GROUPS && D.NO_WITH_TEACHER_GROUPS.indexOf(group) >= 0);
  document.title = meta.h1 + ' — Читательство';

  function waitlistHref() {
    var label = (D.MODULES[group] && D.MODULES[group].label) || group;
    return 'mailto:info@chitatelstvo.ru?subject=' +
      encodeURIComponent('Жду тариф «С преподавателем» · ' + label) +
      '&body=' + encodeURIComponent(
        'Здравствуйте!\n\nХочу узнать, когда откроется тариф «С преподавателем» для курса «' +
        label + '».\n\nИмя:\nТелефон / Telegram:\n'
      );
  }

  renderPage();
  initEnrollment();
  initFaq();
  initLessonDemoToggle();
  initMobileCta();

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function guillemets(text) {
    var t = String(text || '').replace(/[.!?…]+\s*$/u, '').trim();
    return '«' + esc(t) + '»';
  }

  function renderHub() {
    var root = document.getElementById('chit-course');
    var TILDA = {
      'grade-1': 'https://chitatelstvo.ru/1-klass',
      'grade-2': 'https://chitatelstvo.ru/2-klass',
      'grade-3': 'https://chitatelstvo.ru/3-klass',
      'grade-4': 'https://chitatelstvo.ru/4-klass',
      'extra-6-8': 'https://chitatelstvo.ru/6-8-let',
      'extra-9-11': 'https://chitatelstvo.ru/9-11-let',
      'early-letters': 'https://chitatelstvo.ru/bukvy-ozhivayut',
      'early-stories': 'https://chitatelstvo.ru/pervye-istorii',
      'wind': 'https://chitatelstvo.ru/veter-v-ivah',
      'garden': 'https://chitatelstvo.ru/tainstvenny-sad',
      'rus-6-9': 'https://chitatelstvo.ru/russkie-skazki-6-9',
      'rus-10-12': 'https://chitatelstvo.ru/russkie-skazki-10-12'
    };
    var cards = Object.keys(D.META).map(function (g) {
      var m = D.META[g];
      var href = TILDA[g] || m.file;
      return '<a class="cc-hub-card" href="' + esc(href) + '">' +
        '<span class="cc-badge">' + esc(m.badge) + '</span>' +
        '<h3>' + esc(m.h1) + '</h3>' +
        '<p>' + esc(m.age) + ' · 8 сказок · от ' + D.formatPrice(D.TARIFF_PRICE.single) + '</p>' +
        '</a>';
    }).join('');
    root.innerHTML =
      '<header class="cc-header"><div class="cc-header__inner">' +
        '<a class="cc-logo" href="' + HOME_URL + '"><img src="' + D.ASSETS + '/logo-chitatelstvo.png" alt="Читательство"></a>' +
        '<a class="cc-header-cta" href="' + HOME_URL + '">На главную</a>' +
      '</div></header>' +
      '<section class="cc-hero"><div class="cc-hero__grid" style="grid-template-columns:1fr">' +
        '<div><span class="cc-badge">Программы по возрастам</span>' +
        '<h1>Сказки по классам и возрастам</h1>' +
        '<p class="cc-hero__lead">Шесть программ по возрастам — выберите свою и начните в любой день.</p></div>' +
      '</div></section>' +
      '<section class="cc-section cc-section--white"><div class="cc-section__inner">' +
        '<div class="cc-hub-grid">' + cards + '</div>' +
      '</div></section>' +
      footerHtml();
  }

  function taleAnchorId(stageNum, taleIndex) {
    return D.coverSlug(group, stageNum, taleIndex);
  }

  function bookCoverHtml(title, stageNum, taleIndex, opts) {
    opts = opts || {};
    var url = D.coverUrl(group, stageNum, taleIndex);
    var imgPart = url
      ? '<img src="' + esc(url) + '" alt="' + esc(title) + '" loading="lazy" draggable="false">'
      : '<div class="cc-book__placeholder" aria-hidden="true"></div>';
    var inner = '<div class="cc-book">' +
      '<div class="cc-book__frame">' + imgPart + '</div>' +
    '</div>';
    if (opts.link) {
      return '<a class="cc-book__link" href="#' + esc(opts.link) + '" aria-label="Перейти к описанию: ' + esc(title) + '">' +
        inner + '</a>';
    }
    return inner;
  }

  function heroCoversHtml() {
    var tiles = [];
    for (var i = 1; i <= 4; i++) {
      tiles.push(bookCoverHtml(program.june[i - 1][1], 1, i, {
        link: taleAnchorId(1, i),
      }));
    }
    return '<div class="cc-hero__shelf">' + tiles.join('') + '</div>';
  }

  function formatProgramDate(sched, index, stageKey) {
    if (!sched || !sched.lessons[index]) return '';
    if (stageKey && D.lessonIsOpen(stageKey, index + 1)) {
      return 'Уже доступен для прохождения';
    }
    var raw = sched.lessons[index];
    var parts = raw.trim().split(/\s+/);
    if (parts.length >= 2) {
      return parts[0] + ' ' + parts.slice(1).join(' ').toUpperCase();
    }
    return raw.toUpperCase();
  }

  function taleRowsHtml(rows, stageKey, stageNum, compact) {
    var sched = D.SCHEDULE[stageKey];
    return rows.map(function (row, i) {
      var info = D.taleInfo(row[1]);
      var dateHtml = sched
        ? '<span class="cc-tale-row__date">' + esc(sched.lessons[i]) + '</span>'
        : '';
      var anchorId = taleAnchorId(stageNum, i + 1);
      if (compact) {
        var dateLabel = formatProgramDate(sched, i, stageKey);
        return '<article class="cc-tale-program" id="' + esc(anchorId) + '">' +
          '<div class="cc-tale-program__cover">' + bookCoverHtml(row[1], stageNum, i + 1) + '</div>' +
          '<div class="cc-tale-program__body">' +
            (dateLabel ? '<div class="cc-tale-program__date">' + esc(dateLabel) + '</div>' : '') +
            '<div class="cc-tale-program__title">' + esc(row[1]) + '</div>' +
            '<p class="cc-tale-program__desc">' + esc(D.programTaleDesc(row[1])) + '</p>' +
          '</div></article>';
      }
      var quoteHtml = info.quote ? '<p class="cc-tale-row__quote">' + guillemets(info.quote) + '</p>' : '';
      var open = D.lessonIsOpen(stageKey, i + 1);
      var dateBlock = sched
        ? '<div class="cc-tale-row__date">' + esc(open ? 'Уже доступен для прохождения' : ('Урок откроется: ' + (sched.weekdays[i] || 'пн') + ' ' + sched.lessons[i])) + '</div>'
        : '';
      return '<article class="cc-tale-row" id="' + esc(anchorId) + '">' +
        bookCoverHtml(row[1], stageNum, i + 1) +
        '<div class="cc-tale-row__body">' +
          '<div class="cc-tale-row__week">Сказка ' + esc(row[0]) + '</div>' +
          '<div class="cc-tale-row__title">' + esc(row[1]) + '</div>' +
          '<p class="cc-tale-row__desc">' + esc(info.desc) + '</p>' +
          quoteHtml + dateBlock +
        '</div></article>';
    }).join('');
  }

  function reviewsHtml() {
    return '<div class="cc-reviews cc-reviews--strip">' + D.REVIEWS.map(function (r) {
      return '<blockquote class="cc-review">' +
        '<p class="cc-review__text">' + guillemets(r.text) + '</p>' +
        '<cite class="cc-review__author">' + esc(r.author) + '</cite></blockquote>';
    }).join('') + '</div>';
  }

  function reviewsStripHtml() {
    return '<section class="cc-strip-reviews" id="reviews">' +
      '<div class="cc-strip-reviews__inner">' +
        '<div class="cc-strip-reviews__head">' +
          '<span class="cc-chapter"><em>отзывы</em></span>' +
          '<h2>Что говорят родители</h2>' +
        '</div>' +
        reviewsHtml() +
      '</div>' +
    '</section>';
  }

  function splitListHtml(items, variant) {
    return '<ul class="cc-split-list cc-split-list--' + variant + '">' +
      items.map(function (t) { return '<li>' + t + '</li>'; }).join('') +
    '</ul>';
  }

  function bannerHtml() {
    var img = D.BANNER_URL
      ? '<img class="cc-banner__img" src="' + esc(D.BANNER_URL) + '" alt="">'
      : '';
    return '<section class="cc-banner" id="top" aria-label="Баннер курса">' +
      '<div class="cc-banner__frame">' +
        img +
        '<div class="cc-banner__shade" aria-hidden="true"></div>' +
        '<div class="cc-banner__pattern" aria-hidden="true"></div>' +
        '<div class="cc-banner__layout">' +
          '<div class="cc-banner__content">' +
            '<div class="cc-banner__tags">' +
              '<span class="cc-banner__tag">' + esc(meta.badge) + '</span>' +
              '<span class="cc-banner__tag cc-banner__tag--ghost">' + esc(meta.age) + '</span>' +
            '</div>' +
            '<h1>' + heroTitleHtml() + '</h1>' +
            '<p class="cc-banner__lead">' + esc(meta.lead) + '</p>' +
            '<a class="cc-btn cc-btn--banner" href="#tariffs">Выбрать формат</a>' +
            '<div class="cc-banner__chips">' +
              '<span class="cc-banner__chip">8 сказок · старт в любой день</span>' +
              '<span class="cc-banner__chip cc-banner__chip--price">от ' + D.formatPrice(D.TARIFF_PRICE.single) + '</span>' +
            '</div>' +
          '</div>' +
          '<div class="cc-banner__visual">' + heroCoversHtml() + '</div>' +
        '</div>' +
      '</div>' +
    '</section>';
  }

  function heroTitleHtml() {
    var h1 = meta.h1;
    var gradeMatch = h1.match(/^(Курс литературного чтения)\s+·\s+(\d+\s+класс)$/);
    if (gradeMatch) {
      return esc(gradeMatch[1]) + '<br>' + esc(gradeMatch[2]);
    }
    var extraMatch = h1.match(/^(Курс по внеклассному чтению)\s+(.+)$/);
    if (extraMatch) {
      return esc(extraMatch[1]) + '<br>' + esc(extraMatch[2]);
    }
    return esc(h1);
  }

  function heroTitleShort() {
    return meta.h1;
  }

  function schoolIntroHtml() {
    return '<section class="cc-intro" id="about">' +
      '<div class="cc-section__inner cc-intro__inner">' +
        '<p class="cc-intro__pitch">' + esc(D.SCHOOL_PITCH) + '</p>' +
        '<p class="cc-intro__program"><strong>' + esc(D.MODULES[group].label) + '.</strong> ' + esc(meta.intro) + '</p>' +
        '<p class="cc-intro__quote">' + guillemets(D.PULL_QUOTE.text) + ' <cite>— ' + esc(D.PULL_QUOTE.cite) + '</cite></p>' +
      '</div>' +
    '</section>';
  }

  function whatHowHtml() {
    var what = [
      '<strong>8 видеоуроков</strong> — по одному на каждую сказку программы',
      '<strong>Задания на смысл</strong> — чтение по карточкам, вопросы к тексту, творчество',
      '<strong>Личная страница</strong> — баллы, уровни и бейджи, прогресс виден родителю',
      '<strong>Эмоциометр и игровые задания</strong> — ребёнок думает о героях и их переживаниях',
      '<strong>Живые встречи</strong> — на тарифе «С преподавателем», по четвергам в мини-группе'
    ];
    var how = [
      '<strong>Формат:</strong> онлайн — видео и задания на платформе',
      '<strong>Старт:</strong> в любой день; программа — 2 блока по 4 сказки',
      '<strong>Темп:</strong> одна сказка открывается каждую неделю, внутри недели — свой ритм',
      '<strong>После оплаты</strong> на email приходит ссылка на личную страницу ребёнка'
    ];
    var formats = [
      '<strong>Разовое</strong> — 1 сказка на платформе, без встречи в цене (799 ₽)',
      '<strong>Индивидуальное</strong> — 4 сказки в своём темпе, без живых встреч',
      withTeacherClosed
        ? '<strong>С преподавателем</strong> — пока недоступно, можно подписаться на обновления'
        : '<strong>С преподавателем</strong> — 4 сказки и 4 встречи в мини-группе'
    ];
    return '<section class="cc-strip cc-strip--what-how" id="what">' +
      '<div class="cc-strip__inner">' +
        '<div class="cc-split-panel cc-split-panel--pale">' +
          '<h2>Что будет</h2>' +
          splitListHtml(what, 'dark') +
        '</div>' +
        '<div class="cc-split-panel cc-split-panel--warm">' +
          '<h2>Как будет</h2>' +
          splitListHtml(how, 'light') +
          '<h3 class="cc-split-subhead">Варианты прохождения</h3>' +
          splitListHtml(formats, 'light') +
        '</div>' +
      '</div>' +
    '</section>';
  }

  function skillsWhomHtml(forWhom) {
    var skills = D.SKILLS.map(function (s) { return esc(s); });
    var whom = forWhom.map(function (t) { return esc(t); });
    return '<section class="cc-strip cc-strip--skills" id="skills">' +
      '<div class="cc-strip__inner">' +
        '<div class="cc-split-panel cc-split-panel--violet">' +
          '<h2>Ребёнок научится</h2>' +
          splitListHtml(skills, 'light') +
        '</div>' +
        '<div class="cc-split-panel cc-split-panel--white">' +
          '<h2>Этот курс для вас, если</h2>' +
          splitListHtml(whom, 'dark') +
          '<a class="cc-btn cc-btn--pill" href="#tariffs">Подробно о форматах</a>' +
        '</div>' +
      '</div>' +
    '</section>';
  }

  function stripsHtml(forWhom) {
    return '<div class="cc-strips">' + whatHowHtml() + skillsWhomHtml(forWhom) + '</div>';
  }

  function lessonFlowHtml() {
    return '<section class="cc-section cc-section--pale" id="how">' +
      '<div class="cc-section__inner">' +
        '<span class="cc-chapter"><em>урок</em></span>' +
        '<h2>Одна сказка — один мини-курс</h2>' +
        '<p class="cc-section__lead">Видео, вопросы и творчество — ребёнок проходит в своём темпе за неделю</p>' +
        '<div class="cc-lesson-steps cc-lesson-steps--compact">' +
          ['video', 'quiz-text', 'quiz-meaning', 'creative', 'retell'].map(function (s) {
            return '<figure class="cc-lesson-step"><img src="' + D.ASSETS + '/lesson-step-' + s + '.png" alt="" loading="lazy"></figure>';
          }).join('') +
        '</div>' +
      '</div></section>';
  }

  function outcomeHtml() {
    var items = meta.outcome || [];
    if (!items.length) return '';
    return '<section class="cc-section cc-section--outcome" id="outcome">' +
      '<div class="cc-section__inner">' +
        '<span class="cc-chapter"><em>итог</em></span>' +
        '<h2>' + esc(meta.outcomeTitle || 'После курса') + '</h2>' +
        '<p class="cc-section__lead">' + esc(meta.outcomeLead || '') + '</p>' +
        '<ul class="cc-outcome-list">' +
          items.map(function (t) { return '<li>' + esc(t) + '</li>'; }).join('') +
        '</ul>' +
      '</div>' +
    '</section>';
  }

  function compareTableHtml() {
    return '<div class="cc-compare"><table>' +
      '<thead><tr><th></th><th>Разовое</th><th>Индивидуальное</th><th>С преподавателем</th></tr></thead>' +
      '<tbody>' +
      '<tr><td>Сказки на платформе</td><td>1</td><td>4</td><td>4</td></tr>' +
      '<tr><td>Видео и задания</td><td>✓</td><td>✓</td><td>✓</td></tr>' +
      '<tr><td>Личная страница</td><td>✓</td><td>✓</td><td>✓</td></tr>' +
      '<tr><td>Блок из 4 сказок</td><td>—</td><td>✓</td><td>✓</td></tr>' +
      '<tr><td>Живые встречи</td><td>—</td><td>—</td><td>4</td></tr>' +
      '<tr><td>Цена</td><td>' + D.formatPrice(D.TARIFF_PRICE.single) + '</td><td>' + D.formatPrice(D.TARIFF_PRICE.self_paced) + '</td><td>' + D.formatPrice(D.TARIFF_PRICE.with_teacher) + '</td></tr>' +
      '</tbody></table></div>';
  }

  function lessonDemoHtml() {
    if (group !== D.LESSON_DEMO.group) return '';
    var L = D.LESSON_DEMO;
    var E = L.emotion;
    var chips = L.steps.map(function (s) {
      return '<span class="cc-demo-chip"><b>' + s.n + '</b> ' + esc(s.label) + '</span>';
    }).join('');

    var heroes = L.meaning.pickExtra.heroes.map(function (h) {
      return '<figure class="cc-demo-hero">' +
        '<div class="cc-demo-hero__frame' + (h.inStory ? '' : ' is-extra') + '">' +
        '<img src="' + esc(h.image) + '" alt="" loading="lazy"></div>' +
        '<span>' + esc(h.name) + (h.inStory ? '' : '<em>не в сказке</em>') + '</span></figure>';
    }).join('');

    var pairs = L.meaning.pictureMatch.pairs.map(function (p) {
      return '<figure class="cc-demo-pair">' +
        '<div class="cc-demo-pair__img"><img src="' + esc(p.image) + '" alt="" loading="lazy"></div>' +
        '<span>' + esc(p.label) + '</span></figure>';
    }).join('');

    var events = L.retelling.events.map(function (e) {
      return '<figure class="cc-demo-event">' +
        '<div class="cc-demo-event__img"><img src="' + esc(e.image) + '" alt="" loading="lazy"></div>' +
        '<p>' + esc(e.text) + '</p></figure>';
    }).join('');

    var opts = L.comprehension.options.map(function (o) {
      var cls = o === L.comprehension.correct ? ' cc-demo-quiz__opt is-correct' : ' cc-demo-quiz__opt';
      return '<div class="' + cls.trim() + '">' + esc(o) + '</div>';
    }).join('');

    var creative = L.creative.map(function (c) {
      return '<span>' + esc(c) + '</span>';
    }).join('');

    return '<section class="cc-section cc-section--deep" id="lesson-demo">' +
      '<div class="cc-section__inner">' +
        '<span class="cc-chapter"><em>пример урока</em></span>' +
        '<h2>Внутри урока «' + esc(L.title) + '»</h2>' +
        '<p class="cc-section__lead">Фрагмент реального урока с платформы — чтобы увидеть, как устроены задания</p>' +
        '<div class="cc-lesson-demo">' +
          '<div class="cc-demo-chips">' + chips + '</div>' +
          '<div class="cc-demo-preview">' +
            '<div class="cc-demo-preview__emotion">' +
              '<h4 class="cc-demo-block__title">Эмоциометр</h4>' +
              '<div class="cc-demo-emotion cc-demo-emotion--preview">' +
                '<div class="cc-demo-emotion__wheel">' +
                  '<img src="' + esc(E.image) + '" alt="Эмоциометр — десять эмоций" loading="lazy">' +
                '</div>' +
                '<div class="cc-demo-emotion__copy">' +
                  '<p class="cc-demo-emotion__q">' + esc(E.question) + '</p>' +
                  '<p class="cc-demo-emotion__hint">Выберите ' + E.pick + ' эмоции героя на колесе из 10</p>' +
                '</div>' +
              '</div>' +
            '</div>' +
            '<div class="cc-demo-preview__row">' +
              '<div class="cc-demo-preview__card">' +
                '<h4 class="cc-demo-block__title">Чтение по карточкам</h4>' +
                '<div class="cc-demo-reading cc-demo-reading--preview">' +
                  '<div class="cc-demo-reading__img"><img src="' + esc(L.reading.image) + '" alt="" loading="lazy"></div>' +
                  '<p class="cc-demo-reading__text">' + guillemets(L.reading.text) + '</p>' +
                '</div>' +
              '</div>' +
              '<div class="cc-demo-preview__card">' +
                '<h4 class="cc-demo-block__title">Мини-тест</h4>' +
                '<div class="cc-demo-quiz cc-demo-quiz--preview">' +
                  '<p class="cc-demo-quiz__q">' + esc(L.comprehension.text) + '</p>' +
                  '<div class="cc-demo-quiz__opts">' + opts + '</div>' +
                '</div>' +
              '</div>' +
            '</div>' +
          '</div>' +
          '<button type="button" class="cc-demo-toggle" id="cc-demo-toggle" aria-expanded="false">' +
            'Показать все задания урока' +
          '</button>' +
          '<div class="cc-demo-more" id="cc-demo-more" hidden>' +
            '<div class="cc-demo-block">' +
              '<h4 class="cc-demo-block__title">' + esc(L.meaning.pickExtra.title) + '</h4>' +
              '<p class="cc-demo-block__sub">' + esc(L.meaning.pickExtra.hint) + '</p>' +
              '<div class="cc-demo-heroes">' + heroes + '</div>' +
              '<p class="cc-demo-block__sub" style="margin-top:20px">' + esc(L.meaning.pictureMatch.title) + '</p>' +
              '<div class="cc-demo-pairs">' + pairs + '</div>' +
            '</div>' +
            '<div class="cc-demo-block">' +
              '<h4 class="cc-demo-block__title">' + esc(L.retelling.title) + '</h4>' +
              '<div class="cc-demo-events">' + events + '</div>' +
            '</div>' +
            '<div class="cc-demo-block">' +
              '<h4 class="cc-demo-block__title">Творческие задания</h4>' +
              '<div class="cc-demo-creative">' + creative + '</div>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</div>' +
    '</section>';
  }

  function footerHtml() {
    return '<div class="cc-pattern-strip" aria-hidden="true"></div>' +
      '<footer class="cc-footer">' +
        '<div class="cc-footer__inner">' +
          '<img class="cc-footer__logo" src="' + D.ASSETS + '/logo-chitatelstvo.png" alt="Читательство" width="256" height="256">' +
          '<p class="cc-footer__warm">С теплом, команда Читательства</p>' +
          '<nav class="cc-footer__legal" aria-label="Юридическая информация">' +
            '<a href="https://api.chitatelstvo.ru/legal/politika" target="_blank" rel="noopener">Политика конфиденциальности</a>' +
            '<a href="https://api.chitatelstvo.ru/legal/oferta" target="_blank" rel="noopener">Публичная оферта</a>' +
          '</nav>' +
          '<p class="cc-footer__contact">' +
            '<a href="mailto:info@chitatelstvo.ru">info@chitatelstvo.ru</a> · ' +
            '<a href="tel:+79585000850">+7 (958) 500-08-50</a>' +
          '</p>' +
          '<p class="cc-footer__seller">ИП Рощина Ольга Владимировна · ИНН 231150315327</p>' +
          '<p class="cc-footer__copy">© Читательство · chitatelstvo.ru</p>' +
        '</div>' +
      '</footer>';
  }

  function renderPage() {
    var root = document.getElementById('chit-course');

    root.innerHTML =
      '<header class="cc-header"><div class="cc-header__inner">' +
        '<a class="cc-logo" href="' + HOME_URL + '"><img src="' + D.ASSETS + '/logo-chitatelstvo.png" alt="Читательство"></a>' +
        '<nav class="cc-nav" aria-label="Разделы">' +
          '<a href="#about">О курсе</a>' +
          '<a href="#program-list">Программа</a>' +
          '<a href="#outcome">После курса</a>' +
          '<a href="#tariffs">Тарифы</a>' +
          '<a href="#enroll">Запись</a>' +
        '</nav>' +
        '<a class="cc-header-cta" href="#enroll">Записаться</a>' +
      '</div></header>' +

      bannerHtml() +
      schoolIntroHtml() +
      stripsHtml(forWhomFromMeta()) +

      '<section class="cc-section cc-section--pale" id="program-list">' +
        '<div class="cc-section__inner">' +
          '<span class="cc-chapter"><em>программа</em></span>' +
          '<h2>8 сказок — что читаем</h2>' +
          '<p class="cc-section__lead">Два блока по 4 сказки. Можно начать с любого блока.</p>' +
          '<div class="cc-program-block">' +
            '<h3 class="cc-program-block__title">Блок 1 · сказки 1–4</h3>' +
            '<div class="cc-tale-list cc-tale-list--program">' + taleRowsHtml(program.june, '1', 1, true) + '</div>' +
          '</div>' +
          '<div class="cc-program-block">' +
            '<h3 class="cc-program-block__title">Блок 2 · сказки 5–8</h3>' +
            '<div class="cc-tale-list cc-tale-list--program">' + taleRowsHtml(program.july, '2', 2, true) + '</div>' +
          '</div>' +
          '<p class="cc-program-note">Можно начать с одной сказки на тарифе «Разовое» — от ' + D.formatPrice(D.TARIFF_PRICE.single) + '</p>' +
        '</div>' +
      '</section>' +

      lessonFlowHtml() +
      outcomeHtml() +
      reviewsStripHtml() +

      '<section class="cc-section cc-section--white" id="tariffs">' +
        '<div class="cc-section__inner">' +
          '<span class="cc-chapter"><em>тарифы</em></span>' +
          '<h2>Выберите формат</h2>' +
          '<div class="cc-tariffs">' +
            tariffCard('single', D.TARIFF_COPY.single.name, D.TARIFF_COPY.single.mood,
              D.TARIFF_COPY.single.list,
              D.TARIFF_COPY.single.meetNote, false) +
            tariffCard('self_paced', 'Индивидуальное', '4 сказки — путешествие в книгу',
              ['4 сказки на платформе', 'Видео и задания на смысл', 'Личная страница прогресса', 'Блок из 4 сказок', 'Живые встречи — нет'],
              false, true) +
            tariffCard('with_teacher', 'С преподавателем', '4 сказки и живые разговоры о книге',
              ['4 сказки на платформе', 'Видео и задания на смысл', 'Личная страница прогресса', 'Блок из 4 сказок', 'Живые встречи'],
              true) +
          '</div>' +
          (withTeacherClosed
            ? '<p class="cc-tariff-waitnote">Тариф «С преподавателем» для этой программы сейчас закрыт. Можно оставить заявку — напишем, когда набор откроется.</p>'
            : '') +
          '<details class="cc-compare-details">' +
            '<summary>Сравнить тарифы в таблице</summary>' +
            compareTableHtml() +
          '</details>' +
        '</div>' +
      '</section>' +

      '<section class="cc-section cc-section--deep" id="enroll">' +
        '<div class="cc-section__inner">' +
          '<span class="cc-chapter"><em>запись</em></span>' +
          '<h2>Записаться на курс</h2>' +
          '<div class="cc-enroll" id="cc-enroll-panel">' +
            '<p class="cc-section__lead" style="margin-top:0">Программа: <strong>' + esc(D.MODULES[group].label) + '</strong></p>' +

            '<div class="cc-step-block">' +
              '<div class="cc-step-label">шаг 1 · формат</div>' +
              '<div class="cc-pick-cards" id="cc-tariffs">' +
                pickCard('single', D.TARIFF_COPY.single.pickTag, D.TARIFF_COPY.single.name, D.TARIFF_PRICE.single, D.TARIFF_COPY.single.pickHint) +
                pickCard('self_paced', 'Основной', 'Индивидуальное', 1990, '4 сказки в своём темпе') +
                pickCard('with_teacher', 'С поддержкой', 'С преподавателем', 4990, '4 сказки + встречи') +
              '</div>' +
            '</div>' +

            '<div class="cc-step-block" id="cc-date-box" style="display:none">' +
              '<div class="cc-step-label">шаг 2 · блок программы</div>' +
              '<p class="cc-step-hint" id="cc-step-hint" hidden>799 ₽ — урок на платформе. Живые занятия — на тарифе «С преподавателем».</p>' +
              '<p class="cc-step-hint" id="cc-stage1-closed-note" hidden>На тарифе «С преподавателем» сейчас открыт блок 2 — сказки 5–8 и встречи по четвергам.</p>' +
              '<div class="cc-pills" id="cc-stages">' +
                '<button type="button" class="cc-pill" data-stage="1">Блок 1 · сказки 1–4</button>' +
                '<button type="button" class="cc-pill" data-stage="2">Блок 2 · сказки 5–8</button>' +
              '</div>' +
              '<div class="cc-tales" id="cc-tales"></div>' +
              '<div id="cc-block-preview" style="display:none"></div>' +
            '</div>' +

            '<div class="cc-step-block">' +
              '<div class="cc-step-label">ваш выбор</div>' +
              '<div class="cc-summary is-empty" id="cc-summary">Выберите формат и дату</div>' +
            '</div>' +

            '<input type="hidden" id="module_id" name="module_id" value="">' +
            '<input type="hidden" id="chosen_stage" name="chosen_stage" value="">' +
            '<input type="hidden" id="chosen_tale_number" name="chosen_tale_number" value="">' +

            '<div class="cc-step-block">' +
              '<div class="cc-step-label">контакты</div>' +
              '<div class="cc-form-grid" id="cc-contact-form">' +
                formField('parent_name', 'Имя родителя', 'text', true) +
                formField('parent_email', 'Email', 'email', true) +
                formField('parent_telegram', 'Телефон', 'tel', false) +
                formField('child_name', 'Имя ребёнка', 'text', true) +
                formField('child_birth_date', 'День рождения ребёнка', 'date', true) +
                formField('promo_code', 'Промокод', 'text', false) +
              '</div>' +
              '<button type="button" class="cc-btn cc-btn--block" id="cc-pay-btn" disabled>Записаться</button>' +
              '<p class="cc-form-consent">Нажимая «Записаться», вы соглашаетесь с <a href="https://api.chitatelstvo.ru/legal/politika" target="_blank" rel="noopener">политикой конфиденциальности</a> и <a href="https://api.chitatelstvo.ru/legal/oferta" target="_blank" rel="noopener">офертой</a>. Оплата откроется на защищённой странице chitatelstvo.ru.</p>' +
            '</div>' +
          '</div>' +
        '</div>' +
      '</section>' +

      '<section class="cc-section cc-section--white" id="faq">' +
        '<div class="cc-section__inner">' +
          '<span class="cc-chapter"><em>вопросы</em></span>' +
          '<h2>Частые вопросы</h2>' +
          '<div class="cc-faq" id="cc-faq">' +
            faqItem('Когда можно начать?', 'В любой день. В программе 8 сказок (2 блока по 4). Можно взять одну сказку, блок или всю программу.') +
            faqItem('Что будет после оплаты?', 'На email придёт ссылка на личную страницу — там открытые сказки, баллы и прогресс.') +
            faqItem('Можно ли начать с одной сказки?', 'Да. Тариф «Разовое» — ' + D.formatPrice(D.TARIFF_PRICE.single) + ': одна сказка на платформе, без встречи в цене.' + (withTeacherClosed ? '' : ' Живые занятия — на тарифе «С преподавателем».')) +
            faqItem('Чем отличаются тарифы?', withTeacherClosed
              ? ('Разовое — 1 сказка онлайн (' + D.formatPrice(D.TARIFF_PRICE.single) + '). Индивидуальное — 4 сказки без встреч (' + D.formatPrice(D.TARIFF_PRICE.self_paced) + '). Тариф «С преподавателем» для этой программы пока недоступен — можно подписаться на обновления.')
              : ('Разовое — 1 сказка онлайн (' + D.formatPrice(D.TARIFF_PRICE.single) + '). Индивидуальное — 4 сказки без встреч (' + D.formatPrice(D.TARIFF_PRICE.self_paced) + '). С преподавателем — 4 сказки + 4 встречи по четвергам (' + D.formatPrice(D.TARIFF_PRICE.with_teacher) + ').')) +
          '</div>' +
        '</div>' +
      '</section>' +

      '<div class="cc-mobile-cta" id="cc-mobile-cta" hidden>' +
        '<a class="cc-btn" href="#enroll">Записаться · от ' + D.formatPrice(D.TARIFF_PRICE.single) + '</a>' +
      '</div>' +

      footerHtml();
  }

  function forWhomFromMeta() {
    return meta.forWhom;
  }

  function tariffCard(key, name, mood, items, meet, featured) {
    var closed = key === 'with_teacher' && withTeacherClosed;
    var meetHtml = meet
      ? '<div class="cc-tariff__meet">' + esc(typeof meet === 'string' ? meet : (closed ? 'Набор временно закрыт' : 'Встречи по четвергам')) + '</div>'
      : '<div class="cc-tariff__meet cc-tariff__meet--empty" aria-hidden="true"></div>';
    var cta = closed
      ? '<a class="cc-btn cc-btn--block cc-btn--waitlist" href="' + waitlistHref() + '">Пока недоступно · подписаться</a>'
      : '<a class="cc-btn cc-btn--block" href="#enroll" data-tariff-jump="' + key + '">Выбрать</a>';
    return '<article class="cc-tariff' + (featured ? ' cc-tariff--featured' : '') + (closed ? ' cc-tariff--closed' : '') + '">' +
      (closed ? '<span class="cc-tariff__closed-badge">Набор закрыт</span>' : '') +
      '<h3 class="cc-tariff__name">' + esc(name) + '</h3>' +
      '<p class="cc-tariff__mood">' + esc(mood) + '</p>' +
      '<ul class="cc-tariff__list">' + items.map(function (i) { return '<li>' + esc(i) + '</li>'; }).join('') + '</ul>' +
      meetHtml +
      '<div class="cc-tariff__price">' + D.formatPrice(D.TARIFF_PRICE[key]) + '</div>' +
      '<div class="cc-tariff__note">' + (key === 'single' ? (D.TARIFF_COPY.single.priceNote || 'за 1 занятие') : 'за блок из 4 сказок') + '</div>' +
      cta +
      '</article>';
  }

  function pickCard(key, tag, name, price, hint) {
    var closed = key === 'with_teacher' && withTeacherClosed;
    if (closed) {
      return '<a class="cc-pick-card cc-pick-card--closed" href="' + waitlistHref() + '" data-tariff="' + key + '" aria-disabled="true">' +
        '<div class="cc-pick-card__tag">Пока недоступно</div>' +
        '<div class="cc-pick-card__name">' + esc(name) + '</div>' +
        '<div class="cc-pick-card__price">' + D.formatPrice(price) + '</div>' +
        '<div class="cc-pick-card__hint">Подписаться на обновления</div></a>';
    }
    return '<button type="button" class="cc-pick-card" data-tariff="' + key + '">' +
      '<div class="cc-pick-card__tag">' + esc(tag) + '</div>' +
      '<div class="cc-pick-card__name">' + esc(name) + '</div>' +
      '<div class="cc-pick-card__price">' + D.formatPrice(price) + '</div>' +
      '<div class="cc-pick-card__hint">' + esc(hint) + '</div></button>';
  }

  function formField(name, label, type, req) {
    return '<div class="cc-form-field"><label for="cc_' + name + '">' + esc(label) + '</label>' +
      '<input type="' + type + '" id="cc_' + name + '" name="' + name + '"' + (req ? ' required' : '') + '></div>';
  }

  function faqItem(q, a) {
    return '<div class="cc-faq-item"><button type="button" class="cc-faq-q">' + esc(q) + '</button>' +
      '<p class="cc-faq-a">' + a + '</p></div>';
  }

  function initFaq() {
    var faq = document.getElementById('cc-faq');
    if (!faq) return;
    faq.addEventListener('click', function (e) {
      var q = e.target.closest('.cc-faq-q');
      if (!q) return;
      var a = q.nextElementSibling;
      var open = a.classList.contains('is-open');
      faq.querySelectorAll('.cc-faq-a').forEach(function (x) { x.classList.remove('is-open'); });
      if (!open) a.classList.add('is-open');
    });
  }

  function initLessonDemoToggle() {
    var btn = document.getElementById('cc-demo-toggle');
    var panel = document.getElementById('cc-demo-more');
    if (!btn || !panel) return;
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      panel.hidden = open;
      btn.textContent = open ? 'Показать все задания урока' : 'Свернуть';
    });
  }

  function initMobileCta() {
    var bar = document.getElementById('cc-mobile-cta');
    var enroll = document.getElementById('enroll');
    if (!bar || !enroll || !window.matchMedia) return;
    var mq = window.matchMedia('(max-width: 768px)');
    function update() {
      if (!mq.matches) {
        bar.hidden = true;
        return;
      }
      var rect = enroll.getBoundingClientRect();
      bar.hidden = rect.top < window.innerHeight && rect.bottom > 0;
    }
    window.addEventListener('scroll', update, { passive: true });
    mq.addEventListener('change', update);
    update();
  }

  function initEnrollment() {
    var state = { tariff: '', stage: '', taleNum: 0 };
    var elSummary = document.getElementById('cc-summary');
    var elDateBox = document.getElementById('cc-date-box');
    var elTales = document.getElementById('cc-tales');
    var elPreview = document.getElementById('cc-block-preview');
    var hidMid = document.getElementById('module_id');
    var hidStage = document.getElementById('chosen_stage');
    var hidTale = document.getElementById('chosen_tale_number');
    var payBtn = document.getElementById('cc-pay-btn');

    function ageFromBirthDate(iso) {
      if (!iso) return '';
      var p = String(iso).split('-');
      if (p.length !== 3) return '';
      var birth = new Date(+p[0], +p[1] - 1, +p[2]);
      if (isNaN(birth.getTime())) return '';
      var today = new Date();
      var age = today.getFullYear() - birth.getFullYear();
      var md = today.getMonth() - birth.getMonth();
      if (md < 0 || (md === 0 && today.getDate() < birth.getDate())) age -= 1;
      return age >= 0 ? String(age) : '';
    }

    function isReady() {
      if (!state.tariff) return false;
      if (state.tariff === 'single') return !!(state.stage && state.taleNum);
      return !!state.stage;
    }

    function updatePayBtn() {
      if (!payBtn) return;
      var ready = isReady();
      payBtn.disabled = !ready;
      payBtn.textContent = ready
        ? 'Записаться — ' + D.formatPrice(D.TARIFF_PRICE[state.tariff])
        : 'Записаться';
    }

    function syncHidden() {
      var mods = D.MODULES[group];
      hidMid.value = (state.tariff && mods) ? mods[state.tariff] : '';
      hidStage.value = state.stage || '';
      hidTale.value = (state.tariff === 'single' && state.taleNum) ? String(state.taleNum) : '';
      if (!state.tariff) {
        elSummary.classList.add('is-empty');
        elSummary.textContent = 'Выберите формат и дату';
        updatePayBtn();
        return;
      }
      elSummary.classList.remove('is-empty');
      var html = '<strong>' + esc(D.MODULES[group].label) + '</strong> · ' + esc(D.TARIFF_LABEL[state.tariff]);
      if (state.tariff === 'single') {
        if (state.stage && state.taleNum) {
          html += '<br>' + esc(D.STAGE_LABEL[state.stage]) + ' · ' +
            esc(D.TALES[group][state.stage][state.taleNum - 1]);
          html += '<br>' + esc(D.formatPrice(D.TARIFF_PRICE.single)) + ' · урок на платформе';
          if (D.singleMeetingAddonAvailable(state.stage, state.taleNum)) {
            html += '<br>' + esc(D.singleMeetingLabel(state.stage, state.taleNum).toLowerCase());
          }
        } else {
          html += '<br><em>Выберите дату и сказку</em>';
        }
      } else if (state.stage) {
        html += '<br>' + esc(D.STAGE_LABEL[state.stage]) + ' · 4 сказки';
        if (state.tariff === 'with_teacher') html += ' + 4 встречи';
      } else {
        html += '<br><em>Выберите дату старта</em>';
      }
      elSummary.innerHTML = html;
      updatePayBtn();
    }

    function scheduleHtml(stage, index, tariff) {
      var s = D.SCHEDULE[stage];
      if (!s) return '';
      var mwd = s.meetingWeekdays && s.meetingWeekdays[index] ? s.meetingWeekdays[index] + ' ' : 'чт ';
      var html = '<span style="font-size:13px;color:var(--muted)">';
      if (tariff === 'single') {
        html += esc(D.lessonOpenLabel(stage, index));
      } else if (tariff === 'with_teacher') {
        html += 'Встреча: ' + mwd + s.meetings[index] + '<br>';
        html += esc(D.lessonOpenLabel(stage, index));
      } else {
        html += esc(D.lessonOpenLabel(stage, index));
      }
      html += '</span>';
      return html;
    }

    function renderTales() {
      elTales.innerHTML = '';
      elPreview.style.display = 'none';
      if (!state.stage) return;
      var list = D.TALES[group][state.stage];
      if (state.tariff === 'single') {
        elTales.style.display = 'grid';
        list.forEach(function (title, i) {
          var btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'cc-tale-btn' + (state.taleNum === i + 1 ? ' is-active' : '');
          btn.innerHTML =
            '<span class="cc-tale-btn__num">' + (i + 1) + '</span>' +
            '<span><span class="cc-tale-btn__title">' + esc(title) + '</span>' +
            scheduleHtml(state.stage, i, state.tariff) + '</span>';
          btn.onclick = function () {
            state.taleNum = i + 1;
            renderTales();
            syncHidden();
          };
          elTales.appendChild(btn);
        });
      } else {
        elTales.style.display = 'none';
        elPreview.style.display = 'block';
        elPreview.innerHTML =
          '<p><strong>4 сказки в этом блоке</strong>' +
          (state.tariff === 'with_teacher' ? ' · встречи по четвергам' : '') + '</p>' +
          '<div class="cc-block-preview__cards">' +
          list.map(function (t, i) {
            return '<div class="cc-block-preview__card"><strong>Сказка ' + (i + 1) + '</strong><br>' +
              esc(t) + '<br>' + scheduleHtml(state.stage, i, state.tariff) + '</div>';
          }).join('') + '</div>';
      }
    }

    document.getElementById('cc-tariffs').onclick = function (e) {
      var card = e.target.closest('[data-tariff]');
      if (!card) return;
      if (card.classList.contains('cc-pick-card--closed') || card.getAttribute('aria-disabled') === 'true') {
        return;
      }
      e.preventDefault();
      state.tariff = card.getAttribute('data-tariff');
      if (state.tariff === 'with_teacher' && withTeacherClosed) return;
      if (state.tariff !== 'single') state.taleNum = 0;
      else if (state.stage && !state.taleNum) state.taleNum = 1;
      document.querySelectorAll('#cc-tariffs .cc-pick-card').forEach(function (c) {
        c.classList.toggle('is-active', c === card);
      });
      elDateBox.style.display = 'block';
      var hint = document.getElementById('cc-step-hint');
      if (hint) hint.hidden = state.tariff !== 'single';
      refreshStageAvailability();
      renderTales();
      syncHidden();
    };

    function refreshStageAvailability() {
      var stage1 = document.querySelector('#cc-stages [data-stage="1"]');
      var note = document.getElementById('cc-stage1-closed-note');
      var closed = state.tariff === 'with_teacher' && D.WITH_TEACHER_STAGE1_CLOSED;
      if (stage1) {
        stage1.hidden = closed;
        stage1.style.display = closed ? 'none' : '';
        stage1.classList.toggle('is-disabled', closed);
        stage1.disabled = closed;
        stage1.title = closed ? 'Набор на этап 1 с преподавателем закрыт' : '';
        if (closed) stage1.classList.remove('is-active');
      }
      if (note) note.hidden = !closed;
      if (closed && state.stage !== '2') {
        state.stage = '2';
        state.taleNum = 0;
        document.querySelectorAll('#cc-stages .cc-pill').forEach(function (p) {
          p.classList.toggle('is-active', p.getAttribute('data-stage') === '2');
        });
      }
    }

    document.getElementById('cc-stages').onclick = function (e) {
      var btn = e.target.closest('[data-stage]');
      if (!btn || btn.disabled || btn.classList.contains('is-disabled')) return;
      state.stage = btn.getAttribute('data-stage');
      state.taleNum = 0;
      document.querySelectorAll('#cc-stages .cc-pill').forEach(function (p) {
        p.classList.toggle('is-active', p === btn);
      });
      renderTales();
      syncHidden();
    };

    document.querySelectorAll('[data-tariff-jump]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var tariff = btn.getAttribute('data-tariff-jump');
        if (tariff === 'with_teacher' && withTeacherClosed) return;
        var card = document.querySelector('#cc-tariffs [data-tariff="' + tariff + '"]');
        if (card && !card.classList.contains('cc-pick-card--closed')) card.click();
        document.getElementById('enroll').scrollIntoView({ behavior: 'smooth' });
      });
    });

    function collectPayload() {
      function val(name) {
        var el = document.querySelector('[name="' + name + '"]');
        return el ? el.value : '';
      }
      return {
        tariff: state.tariff,
        module_id: hidMid.value,
        chosen_stage: hidStage.value,
        chosen_tale_number: hidTale.value,
        parent_name: val('parent_name'),
        parent_email: val('parent_email'),
        parent_telegram: val('parent_telegram'),
        child_name: val('child_name'),
        child_birth_date: val('child_birth_date'),
        child_age: ageFromBirthDate(val('child_birth_date')),
        promo_code: val('promo_code'),
        notification_channel: 'email'
      };
    }

    function validate() {
      if (!hidMid.value) {
        alert('Выберите формат и дату.');
        document.getElementById('enroll').scrollIntoView({ behavior: 'smooth' });
        return false;
      }
      if (state.tariff === 'with_teacher' && D.WITH_TEACHER_STAGE1_CLOSED && state.stage === '1') {
        alert('На тарифе «С преподавателем» блок 1 сейчас недоступен. Выберите блок 2.');
        return false;
      }
      if (state.tariff === 'single' && (!hidStage.value || !hidTale.value)) {
        alert('Выберите дату и сказку.');
        return false;
      }
      if (state.tariff !== 'single' && !hidStage.value) {
        alert('Выберите дату старта.');
        return false;
      }
      var fields = [
        ['parent_name', 'Укажите имя родителя.'],
        ['parent_email', 'Укажите email.'],
        ['child_name', 'Укажите имя ребёнка.'],
        ['child_birth_date', 'Укажите день рождения ребёнка.']
      ];
      for (var i = 0; i < fields.length; i++) {
        var el = document.querySelector('[name="' + fields[i][0] + '"]');
        if (el && !String(el.value).trim()) {
          alert(fields[i][1]);
          el.focus();
          return false;
        }
      }
      return true;
    }

    payBtn.addEventListener('click', function () {
      if (!validate()) return;
      var payload = collectPayload();
      try {
        sessionStorage.setItem('chit_checkout', JSON.stringify(payload));
      } catch (err) {}
      var qs = new URLSearchParams();
      Object.keys(payload).forEach(function (key) {
        var v = payload[key];
        if (v !== undefined && v !== null && String(v).trim() !== '') qs.set(key, String(v));
      });
      var url = D.PAY_PAGE_URL;
      var query = qs.toString();
      if (query) url += (url.indexOf('?') >= 0 ? '&' : '?') + query;
      window.location.href = url;
    });

    // По умолчанию: основной тариф + блок 1 (для with_teacher — блок 2)
    state.tariff = 'self_paced';
    state.stage = '2';
    var defTariff = document.querySelector('#cc-tariffs [data-tariff="self_paced"]');
    if (defTariff) {
      document.querySelectorAll('#cc-tariffs .cc-pick-card').forEach(function (c) {
        c.classList.toggle('is-active', c === defTariff);
      });
    }
    document.querySelectorAll('#cc-stages .cc-pill').forEach(function (p) {
      p.classList.toggle('is-active', p.getAttribute('data-stage') === '2');
    });
    elDateBox.style.display = 'block';
    refreshStageAvailability();
    renderTales();
    syncHidden();
  }
})();
