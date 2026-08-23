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
    try { sessionStorage.setItem('chit_enroll_group', course.group); } catch (e) {}
    return D.MAIN_URL;
  }

  var home = D.HOME_URL || 'https://chitatelstvo.ru';
  var enroll = enrollHref();

  var lessons = course.lessons.map(function (title, i) {
    return '<li><span class="ccl-lesson__n">' + (i + 1) + '</span> ' + esc(title) + '</li>';
  }).join('');

  var chips = course.chips.map(function (c) {
    return '<span class="ccl-chip">' + esc(c) + '</span>';
  }).join('');

  var outcomeItems = (course.outcome || []).map(function (t) {
    return '<li>' + esc(t) + '</li>';
  }).join('');

  root.innerHTML =
    '<header class="ccl-header">' +
      '<div class="ccl-header__inner">' +
        '<a class="ccl-logo" href="' + esc(home) + '"><img src="' + D.ASSETS + '/logo-chitatelstvo.png" alt="Читательство" width="180" height="48"></a>' +
        '<nav class="ccl-nav" aria-label="Разделы">' +
          '<a href="#program">Программа</a>' +
          '<a href="#outcome">После курса</a>' +
          '<a href="#enroll">Запись</a>' +
        '</nav>' +
        '<a class="ccl-header-cta" href="' + esc(enroll) + '">Записаться</a>' +
      '</div>' +
    '</header>' +

    '<section class="ccl-hero">' +
      '<div class="ccl-hero__grid">' +
        '<div class="ccl-hero__copy">' +
          '<span class="ccl-badge">' + esc(course.badge) + '</span>' +
          '<span class="ccl-age">' + esc(course.age) + '</span>' +
          '<h1>' + esc(course.h1) + '</h1>' +
          '<p class="ccl-lead">' + esc(course.lead) + '</p>' +
          '<p class="ccl-intro">' + esc(course.intro) + '</p>' +
          '<div class="ccl-chips">' + chips + '</div>' +
          '<div class="ccl-actions">' +
            '<a class="ccl-btn ccl-btn--primary" href="' + esc(enroll) + '">Выбрать тариф</a>' +
            '<a class="ccl-btn ccl-btn--ghost" href="' + esc(home) + '">На главную</a>' +
          '</div>' +
        '</div>' +
        '<div class="ccl-hero__media">' +
          '<img src="' + D.ASSETS + '/' + esc(course.cover) + '" alt="" width="800" height="500" loading="eager">' +
        '</div>' +
      '</div>' +
    '</section>' +

    '<section class="ccl-program" id="program">' +
      '<div class="ccl-program__inner">' +
        '<p class="ccl-chapter"><em>программа</em></p>' +
        '<h2>Что будем проходить</h2>' +
        '<ol class="ccl-lessons">' + lessons + '</ol>' +
      '</div>' +
    '</section>' +

    '<section class="ccl-outcome" id="outcome">' +
      '<div class="ccl-outcome__inner">' +
        '<p class="ccl-chapter"><em>итог</em></p>' +
        '<h2>' + esc(course.outcomeTitle || 'После курса') + '</h2>' +
        '<p class="ccl-outcome__lead">' + esc(course.outcomeLead || '') + '</p>' +
        '<ul class="ccl-outcome__list">' + outcomeItems + '</ul>' +
      '</div>' +
    '</section>' +

    '<section class="ccl-enroll" id="enroll">' +
      '<div class="ccl-enroll__inner">' +
        '<p class="ccl-chapter"><em>запись</em></p>' +
        '<h2>Выберите тариф и запишитесь</h2>' +
        '<p class="ccl-note">Разовое — 799 ₽ · Индивидуальное — 1 990 ₽ (499 ₽ за сказку) · С преподавателем — 4 990 ₽ (1 248 ₽ за сказку). Оплата и запись — на главной.</p>' +
        '<a class="ccl-btn ccl-btn--primary ccl-btn--block" href="' + esc(enroll) + '">Записаться на курс</a>' +
      '</div>' +
    '</section>' +

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

  root.querySelectorAll('a[href="' + D.MAIN_URL + '"]').forEach(function (a) {
    a.addEventListener('click', function () {
      try { sessionStorage.setItem('chit_enroll_group', course.group); } catch (e) {}
    });
  });

  activateLiteApp();
})();
