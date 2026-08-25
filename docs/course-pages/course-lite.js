(function () {
  var D = window.CHIT_COURSE_LITE;
  if (!D) return;

  var group = document.body.getAttribute('data-group')
    || (document.getElementById('chit-course-lite') && document.getElementById('chit-course-lite').getAttribute('data-group'));
  var course = group && D.courses[group];
  var rootHost = document.getElementById('chit-course-lite');
  var root = document.getElementById('chit-course-lite-app') || rootHost;
  if (!course || !root) {
    if (root) root.innerHTML = '<p style="padding:40px;text-align:center">Страница не найдена</p>';
    return;
  }

  document.title = course.h1 + ' — Читательство';

  function activateLiteApp() {
    var staticEl = document.getElementById('chit-course-static');
    var appWrap = document.getElementById('chit-course-lite-app');
    if (staticEl) {
      staticEl.setAttribute('hidden', '');
      staticEl.setAttribute('aria-hidden', 'true');
    }
    if (appWrap) appWrap.removeAttribute('hidden');
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function enrollHref() {
    return D.MAIN_URL;
  }

  function rememberEnroll(tariff) {
    try {
      sessionStorage.setItem('chit_enroll_group', course.group);
      if (tariff) sessionStorage.setItem('chit_enroll_tariff', tariff);
      else sessionStorage.removeItem('chit_enroll_tariff');
    } catch (e) {}
  }

  function imgUrl(src) {
    if (!src) return '';
    if (/^https?:\/\//i.test(src)) return src;
    if (src.indexOf('/early/') === 0) return (D.STATIC || 'https://api.chitatelstvo.ru/static') + src;
    return D.ASSETS + '/' + src.replace(/^\//, '');
  }

  function lessonTitle(item) {
    return typeof item === 'string' ? item : (item && item.title) || '';
  }

  function lessonBlurb(item) {
    return typeof item === 'string' ? '' : (item && item.blurb) || '';
  }

  var home = D.HOME_URL || 'https://chitatelstvo.ru';
  var enroll = enrollHref();
  var quiz = D.QUIZ_URL || home + '#quiz';
  var isEarly = group.indexOf('early-') === 0;
  var isRich = !!(course.why || course.inside || course.gallery || course.faq || course.nextLinks);
  var tariffsHref = isEarly ? '#tariffs' : enroll;

  function pricingNote() {
    if (isEarly) {
      return 'Разовое — 799 ₽ за 1 урок · самостоятельное прохождение — 1 990 ₽ за 8 уроков модуля.\nС преподавателем — 4 990 ₽ (8 уроков + 4 встречи). Оплата — на главной.';
    }
    var vol = '4 урока';
    return 'Разовое — 799 ₽ · самостоятельное прохождение курса — 1 990 ₽ за ' + vol + '.\nС преподавателем — 4 990 ₽. Оплата и запись — на главной.';
  }

  function earlyFareCardsHtml() {
    function card(opts) {
      return (
        '<article class="ccl-fare' + (opts.rec ? ' ccl-fare--rec' : '') + '">' +
          (opts.rec ? '<span class="ccl-fare__badge">Рекомендуем</span>' : '') +
          '<h3 class="ccl-fare__name">' + esc(opts.name) + '</h3>' +
          '<p class="ccl-fare__price">' + esc(opts.price) + '</p>' +
          (opts.delta ? '<p class="ccl-fare__delta">' + esc(opts.delta) + '</p>' : '') +
          '<p class="ccl-fare__sub">' + esc(opts.sub) + '</p>' +
          '<ul class="ccl-fare__feats">' +
            opts.feats.map(function (f) {
              return '<li class="' + (f.yes ? 'is-yes' : 'is-no') + '">' + esc(f.text) + '</li>';
            }).join('') +
          '</ul>' +
          '<a class="ccl-fare__cta" href="' + esc(enroll) + '" data-enroll-tariff="' + esc(opts.tariff) + '">' +
            esc(opts.cta || 'Записаться') +
          '</a>' +
        '</article>'
      );
    }
    return (
      card({
        tariff: 'single',
        name: 'Разовое',
        price: '799 ₽',
        sub: '1 урок',
        feats: [
          { yes: true, text: '1 урок модуля на платформе' },
          { yes: true, text: 'Квест и задания' },
          { yes: true, text: 'Личная страница прогресса' },
          { yes: false, text: 'Модуль из 8 уроков' },
          { yes: false, text: 'Живые встречи' }
        ]
      }) +
      card({
        tariff: 'self_paced',
        name: 'Индивидуальное',
        price: '1 990 ₽',
        delta: '1 990 ₽ за модуль',
        sub: '8 уроков модуля · свой темп',
        rec: true,
        feats: [
          { yes: true, text: '8 уроков модуля на платформе' },
          { yes: true, text: 'Квест и задания' },
          { yes: true, text: 'Личная страница прогресса' },
          { yes: true, text: 'Модуль целиком' },
          { yes: false, text: 'Живые встречи' }
        ]
      }) +
      card({
        tariff: 'with_teacher',
        name: 'С преподавателем',
        price: '4 990 ₽',
        delta: '4 990 ₽ за модуль',
        sub: '8 уроков модуля + 4 встречи',
        feats: [
          { yes: true, text: '8 уроков модуля на платформе' },
          { yes: true, text: 'Квест и задания' },
          { yes: true, text: 'Личная страница прогресса' },
          { yes: true, text: 'Модуль целиком' },
          { yes: true, text: 'Живые встречи' }
        ]
      })
    );
  }

  var lessons = (course.lessons || []).map(function (item, i) {
    var title = lessonTitle(item);
    var blurb = lessonBlurb(item);
    return (
      '<li>' +
        '<span class="ccl-lesson__n">' + (i + 1) + '</span>' +
        '<div class="ccl-lesson__body">' +
          '<strong class="ccl-lesson__title">' + esc(title) + '</strong>' +
          (blurb ? '<span class="ccl-lesson__blurb">' + esc(blurb) + '</span>' : '') +
        '</div>' +
      '</li>'
    );
  }).join('');

  var chips = (course.chips || []).map(function (c) {
    return '<span class="ccl-chip">' + esc(c) + '</span>';
  }).join('');

  function listBlock(items, className) {
    return (items || []).map(function (t) {
      return '<li class="' + className + '">' + esc(t) + '</li>';
    }).join('');
  }

  function cardsBlock(items, cardClass) {
    return (items || []).map(function (it) {
      return (
        '<article class="' + cardClass + '">' +
          '<h3>' + esc(it.title) + '</h3>' +
          '<p>' + esc(it.text) + '</p>' +
        '</article>'
      );
    }).join('');
  }

  var navExtra = '';
  if (course.why) navExtra += '<a href="#why">Почему мы</a>';
  if (course.gallery) navExtra += '<a href="#look">Как выглядит</a>';
  navExtra += '<a href="#program">Программа</a><a href="#outcome">После курса</a>';
  if (course.faq) navExtra += '<a href="#faq">Вопросы</a>';
  navExtra += '<a href="' + (isEarly ? '#tariffs' : '#enroll') + '">Запись</a>';
  if (isEarly && course.trialSlug) navExtra += '<a href="#trial">Пробный</a>';

  var trialHref = (isEarly && course.trialSlug) ? '#trial' : quiz;
  var useBrandHero = isEarly;
  var heroCtas =
    '<div class="ccl-actions">' +
      '<a class="ccl-btn ccl-btn--primary" href="' + esc(tariffsHref) + '">' +
        (useBrandHero ? 'Выбрать формат' : 'Выбрать тариф') +
      '</a>' +
      (isEarly
        ? '<a class="ccl-btn ccl-btn--accent" href="' + esc(trialHref) + '">Пробный урок бесплатно</a>'
        : '<a class="ccl-btn ccl-btn--ghost" href="' + esc(home) + '">На главную</a>') +
    '</div>';

  var html = '';

  html +=
    '<header class="ccl-header">' +
      '<div class="ccl-header__inner">' +
        '<a class="ccl-logo" href="' + esc(home) + '"><img src="' + D.ASSETS + '/logo-chitatelstvo.png" alt="Читательство" width="180" height="48"></a>' +
        '<nav class="ccl-nav" aria-label="Разделы">' + navExtra + '</nav>' +
        '<a class="ccl-header-cta" href="' + esc(isEarly ? '#tariffs' : enroll) + '">Записаться</a>' +
      '</div>' +
    '</header>';

  var heroTags = '';
  if (useBrandHero) {
    heroTags =
      '<div class="ccl-hero__tags">' +
        '<span class="ccl-badge">' + esc(course.badge) + '</span>' +
        (course.age ? '<span class="ccl-age">' + esc(course.age) + '</span>' : '') +
      '</div>';
  } else {
    heroTags =
      '<span class="ccl-badge">' + esc(course.badge) + '</span>' +
      (course.age ? '<span class="ccl-age">' + esc(course.age) + '</span>' : '');
  }

  var heroMediaHtml;
  if (course.coverVideo) {
    var poster = course.coverPoster || course.cover;
    heroMediaHtml =
      '<video class="ccl-hero__video" src="' + esc(imgUrl(course.coverVideo)) + '"' +
        (poster ? ' poster="' + esc(imgUrl(poster)) + '"' : '') +
        ' width="800" height="500" autoplay muted loop playsinline preload="metadata"' +
        ' aria-label="' + esc(course.h1) + '"></video>';
  } else {
    heroMediaHtml =
      '<img src="' + esc(imgUrl(course.cover)) + '" alt="' + esc(course.h1) + '" width="800" height="500" loading="eager">';
  }

  var heroInner =
    '<div class="ccl-hero__grid">' +
      '<div class="ccl-hero__copy">' +
        heroTags +
        '<h1>' + esc(course.h1) + '</h1>' +
        (course.subtitle ? '<p class="ccl-subtitle">' + esc(course.subtitle) + '</p>' : '') +
        '<p class="ccl-lead">' + esc(course.lead) + '</p>' +
        (useBrandHero ? '' : '<p class="ccl-intro">' + esc(course.intro) + '</p>') +
        (useBrandHero ? heroCtas + '<div class="ccl-chips">' + chips + '</div>'
                      : '<div class="ccl-chips">' + chips + '</div>' + heroCtas) +
      '</div>' +
      '<div class="ccl-hero__media">' +
        heroMediaHtml +
      '</div>' +
    '</div>';

  html +=
    '<section class="ccl-hero' + (useBrandHero ? ' ccl-hero--brand' : '') + '" id="about">' +
      (useBrandHero
        ? '<div class="ccl-hero__frame">' +
            '<div class="ccl-hero__pattern" aria-hidden="true"></div>' +
            heroInner +
          '</div>'
        : heroInner) +
    '</section>';

  if (course.promise) {
    html +=
      '<section class="ccl-promise">' +
        '<div class="ccl-promise__inner">' +
          '<p class="ccl-chapter"><em>итог для семьи</em></p>' +
          '<p class="ccl-promise__text">' + esc(course.promise) + '</p>' +
        '</div>' +
      '</section>';
  }

  if (course.slogan) {
    html +=
      '<section class="ccl-slogan" aria-label="Слоган">' +
        '<div class="ccl-slogan__inner">' +
          '<p class="ccl-slogan__text">' + esc(course.slogan) + '</p>' +
        '</div>' +
      '</section>';
  }

  if (course.why && course.why.length) {
    html +=
      '<section class="ccl-why" id="why">' +
        '<div class="ccl-why__inner">' +
          '<p class="ccl-chapter"><em>для родителей</em></p>' +
          '<h2>' + esc(course.whyTitle || 'Почему выбирают этот курс') + '</h2>' +
          '<div class="ccl-why__grid">' + cardsBlock(course.why, 'ccl-why-card') + '</div>' +
        '</div>' +
      '</section>';
  }

  if (course.inside && course.inside.length) {
    html +=
      '<section class="ccl-inside" id="inside">' +
        '<div class="ccl-inside__inner">' +
          '<p class="ccl-chapter"><em>на курсе</em></p>' +
          '<h2>' + esc(course.insideTitle || 'Что будет на курсе') + '</h2>' +
          '<div class="ccl-inside__grid">' + cardsBlock(course.inside, 'ccl-inside-card') + '</div>' +
        '</div>' +
      '</section>';
  }

  if (course.gallery && course.gallery.length) {
    html +=
      '<section class="ccl-gallery" id="look">' +
        '<div class="ccl-gallery__inner">' +
          '<p class="ccl-chapter"><em>из уроков</em></p>' +
          '<h2>' + esc(course.galleryTitle || 'Как выглядит урок') + '</h2>' +
          '<div class="ccl-gallery__grid">' +
            course.gallery.map(function (g) {
              return (
                '<figure class="ccl-gallery__item">' +
                  '<img src="' + esc(imgUrl(g.src)) + '" alt="' + esc(g.alt || '') + '" width="640" height="400" loading="lazy">' +
                  (g.caption ? '<figcaption>' + esc(g.caption) + '</figcaption>' : '') +
                '</figure>'
              );
            }).join('') +
          '</div>' +
        '</div>' +
      '</section>';
  }

  html +=
    '<section class="ccl-program" id="program">' +
      '<div class="ccl-program__inner">' +
        '<p class="ccl-chapter"><em>программа</em></p>' +
        '<h2>Что будем проходить</h2>' +
        (course.programLead ? '<p class="ccl-program__lead">' + esc(course.programLead) + '</p>' : '') +
        '<ol class="ccl-lessons">' + lessons + '</ol>' +
      '</div>' +
    '</section>';

  if ((course.childGets && course.childGets.length) || (course.parentGets && course.parentGets.length)) {
    html +=
      '<section class="ccl-gets" id="gets">' +
        '<div class="ccl-gets__inner">' +
          '<p class="ccl-chapter"><em>результат</em></p>' +
          '<div class="ccl-gets__grid">' +
            (course.childGets && course.childGets.length
              ? '<div class="ccl-gets__col">' +
                  '<h2>' + esc(course.childGetsTitle || 'Что получит ребёнок') + '</h2>' +
                  '<ul class="ccl-gets__list">' + listBlock(course.childGets, '') + '</ul>' +
                '</div>'
              : '') +
            (course.parentGets && course.parentGets.length
              ? '<div class="ccl-gets__col">' +
                  '<h2>' + esc(course.parentGetsTitle || 'Что получите вы') + '</h2>' +
                  '<ul class="ccl-gets__list">' + listBlock(course.parentGets, '') + '</ul>' +
                '</div>'
              : '') +
          '</div>' +
        '</div>' +
      '</section>';
  }

  html +=
    '<section class="ccl-outcome" id="outcome">' +
      '<div class="ccl-outcome__inner">' +
        '<p class="ccl-chapter"><em>итог</em></p>' +
        '<h2>' + esc(course.outcomeTitle || 'После курса') + '</h2>' +
        '<p class="ccl-outcome__lead">' + esc(course.outcomeLead || '') + '</p>' +
        '<ul class="ccl-outcome__list">' + listBlock(course.outcome || [], '') + '</ul>' +
      '</div>' +
    '</section>';

  html +=
    '<section class="ccl-enroll' + (isEarly ? ' ccl-enroll--fares' : '') + '" id="' + (isEarly ? 'tariffs' : 'enroll') + '">' +
      '<div class="ccl-enroll__inner">' +
        '<p class="ccl-chapter"><em>' + (isEarly ? 'тариф' : 'запись') + '</em></p>' +
        '<h2>' + (isEarly ? 'Выберите формат' : 'Выберите тариф и запишитесь') + '</h2>' +
        '<p class="ccl-note">' +
          (isEarly
            ? 'Форматы этого модуля · 1 990 ₽ — за 8 уроков'
            : esc(pricingNote())) +
        '</p>' +
        (isEarly
          ? '<div class="ccl-fares" role="list">' + earlyFareCardsHtml() + '</div>' +
            (course.trialSlug
              ? '<p class="ccl-enroll__trial"><a class="ccl-btn ccl-btn--ghost" href="#trial">Пробный урок бесплатно</a></p>'
              : '')
          : '<div class="ccl-actions ccl-actions--enroll">' +
              '<a class="ccl-btn ccl-btn--primary ccl-btn--block" href="' + esc(enroll) + '">Записаться на курс</a>' +
            '</div>') +
      '</div>' +
    '</section>';

  if (isEarly) {
    html += '<div id="enroll" hidden aria-hidden="true"></div>';
  }

  if (isEarly && course.trialSlug) {
    var ageDef = course.trialAgeDefault || 5;
    html +=
      '<section class="ccl-trial" id="trial">' +
        '<div class="ccl-trial__inner">' +
          '<p class="ccl-chapter"><em>бесплатно</em></p>' +
          '<h2>Запись на пробный урок</h2>' +
          '<p class="ccl-note">Откроем «' + esc(course.trialTitle || course.h1) +
            '» прямо на этой странице. Ссылка придёт на email в течение минуты.</p>' +
          '<form class="ccl-trial__form" id="ccl-trial-form" novalidate>' +
            '<label class="ccl-trial__field">' +
              '<span>Имя родителя</span>' +
              '<input name="parent_name" type="text" autocomplete="name" required maxlength="200" placeholder="Как к вам обращаться">' +
            '</label>' +
            '<label class="ccl-trial__field">' +
              '<span>Email</span>' +
              '<input name="parent_email" type="email" autocomplete="email" required maxlength="200" placeholder="name@email.com">' +
            '</label>' +
            '<label class="ccl-trial__field">' +
              '<span>Имя ребёнка</span>' +
              '<input name="child_name" type="text" autocomplete="off" required maxlength="100" placeholder="Имя">' +
            '</label>' +
            '<label class="ccl-trial__field ccl-trial__field--age">' +
              '<span>Возраст ребёнка</span>' +
              '<input name="child_age" type="number" min="1" max="99" required value="' + ageDef + '">' +
            '</label>' +
            '<div class="ccl-trial__consents">' +
              '<label class="ccl-trial__check">' +
                '<input type="checkbox" name="consent_privacy" required>' +
                '<span>Соглашаюсь с <a href="https://api.chitatelstvo.ru/legal/politika" target="_blank" rel="noopener">политикой конфиденциальности</a></span>' +
              '</label>' +
              '<label class="ccl-trial__check">' +
                '<input type="checkbox" name="consent_offer" required>' +
                '<span>Соглашаюсь с <a href="https://api.chitatelstvo.ru/legal/oferta" target="_blank" rel="noopener">публичной офертой</a></span>' +
              '</label>' +
              '<label class="ccl-trial__check">' +
                '<input type="checkbox" name="consent_marketing">' +
                '<span>Соглашаюсь получать полезные письма и новости Читательства</span>' +
              '</label>' +
            '</div>' +
            '<button class="ccl-btn ccl-btn--primary ccl-btn--block" type="submit">Получить пробный урок</button>' +
            '<p class="ccl-trial__msg" id="ccl-trial-msg" hidden></p>' +
          '</form>' +
        '</div>' +
      '</section>';
  }

  if (course.faq && course.faq.length) {
    html +=
      '<section class="ccl-faq" id="faq">' +
        '<div class="ccl-faq__inner">' +
          '<p class="ccl-chapter"><em>вопросы</em></p>' +
          '<h2>' + esc(course.faqTitle || 'Частые вопросы') + '</h2>' +
          '<div class="ccl-faq__list">' +
            course.faq.map(function (item) {
              return (
                '<details class="ccl-faq__item">' +
                  '<summary>' + esc(item.q) + '</summary>' +
                  '<p>' + esc(item.a) + '</p>' +
                '</details>'
              );
            }).join('') +
          '</div>' +
        '</div>' +
      '</section>';
  }

  if (course.nextLinks && course.nextLinks.length) {
    html +=
      '<section class="ccl-next" id="next">' +
        '<div class="ccl-next__inner">' +
          '<p class="ccl-chapter"><em>если уже легко</em></p>' +
          '<h2>' + esc(course.nextTitle || 'Следующий шаг') + '</h2>' +
          (course.nextText ? '<p class="ccl-next__text">' + esc(course.nextText) + '</p>' : '') +
          '<div class="ccl-next__links">' +
            course.nextLinks.map(function (link) {
              return (
                '<a class="ccl-next__card" href="' + esc(link.href) + '">' +
                  '<strong>' + esc(link.label) + '</strong>' +
                  (link.meta ? '<span>' + esc(link.meta) + '</span>' : '') +
                '</a>'
              );
            }).join('') +
          '</div>' +
        '</div>' +
      '</section>';
  }

  html +=
    '<footer class="ccl-footer">' +
      '<div class="ccl-footer__inner">' +
        '<img class="ccl-footer__logo" src="' + D.ASSETS + '/logo-chitatelstvo.png" alt="Читательство" width="180" height="48">' +
        '<p class="ccl-footer__warm">С теплом, команда Читательства</p>' +
        '<nav class="ccl-footer__legal" aria-label="Юридическая информация">' +
          '<a href="https://api.chitatelstvo.ru/legal/politika" target="_blank" rel="noopener">Политика</a>' +
          '<a href="https://api.chitatelstvo.ru/legal/oferta" target="_blank" rel="noopener">Оферта</a>' +
          '<a href="https://api.chitatelstvo.ru/legal/rekvizity" target="_blank" rel="noopener">Реквизиты</a>' +
        '</nav>' +
        '<p class="ccl-footer__contact">' +
          '<a href="mailto:info@chitatelstvo.ru">info@chitatelstvo.ru</a> · ' +
          '<a href="' + esc(home) + '">chitatelstvo.ru</a>' +
        '</p>' +
        '<p class="ccl-footer__seller">ИП Рощина Ольга Владимировна · ИНН 231150315327</p>' +
        '<p class="ccl-footer__copy">© Читательство</p>' +
      '</div>' +
    '</footer>';

  root.innerHTML = html;
  void isRich;
  void quiz;

  root.querySelectorAll('a[href="' + D.MAIN_URL + '"]').forEach(function (a) {
    a.addEventListener('click', function () {
      rememberEnroll(a.getAttribute('data-enroll-tariff') || '');
    });
  });

  function scrollToHashTarget() {
    var id = (location.hash || '').replace(/^#/, '');
    if (!id || !/^[A-Za-z][\w:-]*$/.test(id)) return;
    if (id === 'enroll' && isEarly) id = 'tariffs';
    var el = root.querySelector('#' + id) || document.getElementById(id);
    if (!el || (el.closest && el.closest('#chit-course-static'))) return;
    if (el.hasAttribute('hidden')) {
      el = root.querySelector('#tariffs') || el;
    }
    requestAnimationFrame(function () {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  root.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a) return;
    var id = (a.getAttribute('href') || '').slice(1);
    if (!id || !/^[A-Za-z][\w:-]*$/.test(id)) return;
    if (id === 'enroll' && isEarly) id = 'tariffs';
    var el = root.querySelector('#' + id);
    if (!el || el.hasAttribute('hidden')) return;
    e.preventDefault();
    if (history.replaceState) history.replaceState(null, '', '#' + id);
    else location.hash = id;
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  var trialForm = root.querySelector('#ccl-trial-form');
  if (trialForm && course.trialSlug) {
    var trialMsg = root.querySelector('#ccl-trial-msg');
    trialForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var fd = new FormData(trialForm);
      var parentName = String(fd.get('parent_name') || '').trim();
      var parentEmail = String(fd.get('parent_email') || '').trim();
      var childName = String(fd.get('child_name') || '').trim();
      var childAge = parseInt(String(fd.get('child_age') || ''), 10);
      var btn = trialForm.querySelector('button[type="submit"]');
      function showMsg(text, isHtml) {
        if (!trialMsg) return;
        trialMsg.hidden = false;
        if (isHtml) trialMsg.innerHTML = text;
        else trialMsg.textContent = text;
      }
      if (!parentName || !parentEmail || !childName || !Number.isFinite(childAge) || childAge < 1) {
        showMsg('Заполните все поля формы.');
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(parentEmail)) {
        showMsg('Укажите корректный email.');
        return;
      }
      var consentPrivacy = !!(trialForm.consent_privacy && trialForm.consent_privacy.checked);
      var consentOffer = !!(trialForm.consent_offer && trialForm.consent_offer.checked);
      var consentMarketing = !!(trialForm.consent_marketing && trialForm.consent_marketing.checked);
      if (!consentPrivacy || !consentOffer) {
        showMsg('Отметьте согласие с политикой конфиденциальности и офертой.');
        return;
      }
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Открываем урок…';
      }
      fetch('https://api.chitatelstvo.ru/api/early/trial', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parent_name: parentName,
          parent_email: parentEmail,
          phone: '',
          child_name: childName,
          child_age: childAge,
          trial_slug: course.trialSlug,
          trial_title: course.trialTitle || course.h1,
          consent_privacy: consentPrivacy,
          consent_offer: consentOffer,
          consent_marketing: consentMarketing
        })
      })
        .then(function (r) {
          return r.json().then(function (j) {
            return { ok: r.ok, j: j };
          });
        })
        .then(function (res) {
          if (!res.ok) {
            var detail = res.j && res.j.detail;
            throw new Error(typeof detail === 'string' ? detail : 'Не удалось открыть пробный урок.');
          }
          var msg = (res.j && res.j.message) || 'Пробный урок открыт. Проверьте email.';
          if (res.j && res.j.lesson_url) {
            showMsg(
              esc(msg) +
                ' <a class="ccl-trial__link" href="' + esc(res.j.lesson_url) + '" target="_blank" rel="noopener">Открыть урок</a>',
              true
            );
          } else {
            showMsg(msg);
          }
          trialForm.reset();
          if (trialForm.child_age) trialForm.child_age.value = String(course.trialAgeDefault || 5);
        })
        .catch(function (err) {
          showMsg((err && err.message) || 'Не удалось отправить. Напишите на info@chitatelstvo.ru');
        })
        .finally(function () {
          if (btn) {
            btn.disabled = false;
            btn.textContent = 'Получить пробный урок';
          }
        });
    });
  }

  activateLiteApp();
  setTimeout(scrollToHashTarget, 60);
  setTimeout(scrollToHashTarget, 400);
})();
