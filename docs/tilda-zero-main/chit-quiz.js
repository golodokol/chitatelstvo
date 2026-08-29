(function () {
  'use strict';

  // Починка «Дальше»: старый inline CSS давал width:100% всем .qz-btn — кнопка сжималась
  if (!document.getElementById('chit-qz-nav-fix')) {
    var navFix = document.createElement('style');
    navFix.id = 'chit-qz-nav-fix';
    navFix.textContent =
      '#qz-modal .qz-modal__dialog .qz-nav{display:flex!important;flex-wrap:nowrap!important;gap:10px!important;width:100%!important;box-sizing:border-box!important}' +
      '#qz-modal .qz-modal__dialog .qz-nav .qz-btn{width:auto!important;max-width:none!important;box-sizing:border-box!important}' +
      '#qz-modal .qz-modal__dialog .qz-nav .qz-btn--back{flex:0 0 auto!important;min-width:96px!important}' +
      '#qz-modal .qz-modal__dialog .qz-nav .qz-btn--next{flex:1 1 auto!important;min-width:0!important}' +
      '@media(max-width:480px){#qz-modal .qz-modal__dialog .qz-nav{flex-direction:column!important}' +
      '#qz-modal .qz-modal__dialog .qz-nav .qz-btn--back,#qz-modal .qz-modal__dialog .qz-nav .qz-btn--next{width:100%!important;min-width:0!important}}';
    (document.head || document.documentElement).appendChild(navFix);
  }

  var API_BASE = window.CHIT_QUIZ_API || 'https://api.chitatelstvo.ru';
  var CHECKLIST_URL = API_BASE + '/quiz/checklist.pdf?v=20260615b';
  var AUTO_CFG = window.CHIT_QUIZ_AUTO || {};
  var AUTO_ENABLED = AUTO_CFG.enabled === true;
  var AUTO_DELAY_MS = Number(AUTO_CFG.delayMs) > 0 ? Number(AUTO_CFG.delayMs) : 12000;
  var AUTO_ONCE_PER_SESSION = AUTO_CFG.oncePerSession !== false;
  var AUTO_STORAGE_KEY = 'chit_quiz_popup';
  var autoOpenTimer = null;
  var activeVariant = 'reading';

  var QUESTIONS_READING = [
    {
      id: 'frequency',
      title: 'Как часто ребёнок читает дома?',
      options: [
        'Почти каждый день',
        'Несколько раз в неделю',
        'Редко, по настроению',
        'Почти не читает сам'
      ]
    },
    {
      id: 'hard',
      title: 'Что самое сложное в чтении для ребёнка?',
      options: [
        'Понять, о чём текст',
        'Дочитать до конца',
        'Пересказать своими словами',
        'Начать читать без напоминаний'
      ]
    },
    {
      id: 'format',
      title: 'Какой формат лучше?',
      options: [
        'Видео и задания в своём темпе',
        'С живым преподавателем в группе',
        'Короткие уроки по одной сказке',
        'Пока сложно сказать — хочу подборку'
      ]
    },
    {
      id: 'blocker',
      title: 'Что больше всего мешает ребёнку читать?',
      options: [
        'Гаджеты и экраны',
        '«Скучно» или неинтересно',
        'Сложные слова и длинные тексты',
        'Нет привычки читать дома'
      ]
    },
    {
      id: 'priority',
      title: 'Что для вас важнее сейчас?',
      options: [
        'Чтобы ребёнок полюбил чтение',
        'Чтобы понимал прочитанное',
        'Чтобы был план и структура',
        'Попробовать без давления'
      ]
    }
  ];

  var QUESTIONS_EARLY = [
    {
      id: 'readiness',
      title: 'Как ребёнок сейчас с буквами и чтением?',
      options: [
        'Ещё почти не знает буквы',
        'Знает некоторые буквы',
        'Складывает слоги или короткие слова',
        'Уже читает простые тексты'
      ]
    },
    {
      id: 'sounds',
      title: 'Что получается легче всего?',
      options: [
        'Слушать и повторять звуки',
        'Узнавать буквы на картинках',
        'Складывать слоги в слова',
        'Пока всё в новинку'
      ]
    },
    {
      id: 'interest',
      title: 'Что ребёнку сейчас интереснее?',
      options: [
        'Игры со звуками и буквами',
        'Короткие истории и картинки',
        'Сказки вслух вместе со взрослым',
        'Пока неясно — хотим попробовать'
      ]
    },
    {
      id: 'format_early',
      title: 'Какой формат вам удобнее?',
      options: [
        'Короткие квесты дома в своём темпе',
        'С педагогом в мини-группе',
        'Сначала один бесплатный урок',
        'Нужна подсказка, что выбрать'
      ]
    },
    {
      id: 'goal_early',
      title: 'Что важнее сейчас?',
      options: [
        'Мягко подготовить к школе',
        'Чтобы полюбил буквы и истории',
        'Уверенность в первых словах',
        'Попробовать без давления'
      ]
    }
  ];

  var COPY = {
    reading: {
      introBadge: 'Бесплатный доступ к платформе и один урок-сказка!',
      introSub: 'Ответьте на 5 вопросов — получите чек-лист «10 признаков, что ребёнок не понимает прочитанное» на email. А чуть позже откроем доступ к платформе и бесплатному полноценному уроку, чтобы вы прошли одно книжное приключение вместе с ребёнком.',
      formSub: 'Оставьте контакты — пришлём PDF-чек-лист «10 признаков, что ребёнок не понимает прочитанное» на email.',
      giftNow: '<strong>Сейчас:</strong> PDF-чек-лист на email — проверить понимание текста вместе с ребёнком.',
      giftLater: '<strong>Чуть позже:</strong> бесплатный доступ к платформе, один полноценный урок-сказка и личное письмо от основателя с рекомендациями.',
      ageNote: 'Наши программы для читающих детей — примерно 6–11 лет',
      submit: 'Получить PDF-чек-лист',
      successPdf: '<strong>PDF-чек-лист уже на вашем email.</strong>',
      successDefaultGift: 'Личное письмо от основателя с рекомендациями и подарком придёт чуть позже.',
      successTrialGift: function (title) {
        return 'Бесплатный урок «' + title + '» откроем чуть позже — ссылка придёт отдельным письмом.';
      },
      showChecklistLink: true,
      checklistUrl: CHECKLIST_URL,
      questionSub: 'Ответьте честно — так мы точнее подстроим рекомендации в письме'
    },
    early: {
      introBadge: 'Бесплатный пробный квест со Словиком!',
      introSub: '5 коротких вопросов — откроем пробный урок и пришлём PDF-чек-лист «10 признаков, что ребёнку нужен мягкий старт чтения».',
      formSub: 'Оставьте контакты — пришлём ссылку на пробный урок и PDF-чек-лист на email.',
      giftNow: '<strong>Сейчас:</strong> PDF-чек-лист и доступ к пробному квесту на платформе (ссылка в письме).',
      giftLater: '<strong>В письме:</strong> подсказка, с чего начать — «Буквы оживают» или «Первые истории».',
      ageNote: 'Этот квиз — для детей, которые ещё не читают сами или только начинают (примерно 4–7 лет)',
      submit: 'Получить урок и PDF',
      successPdf: '<strong>Письмо с PDF и ссылкой на урок уже уходит на ваш email.</strong>',
      successDefaultGift: 'Откройте письмо — там PDF-чек-лист и ссылка на пробный квест со Словиком.',
      successTrialGift: function (title) {
        return 'Пробный урок «' + title + '» и PDF уже открываем — письмо придёт в течение минуты.';
      },
      showChecklistLink: true,
      checklistUrl: API_BASE + '/quiz/checklist-early.pdf?v=20260827a',
      questionSub: 'Ответьте честно — так мы подскажем, с какого курса начать'
    }
  };

  var root = document.getElementById('chit-quiz');
  if (!root) return;

  var answers = {};
  var stepIndex = 0;

  var elProgressFill = root.querySelector('.qz-progress__fill');
  var elProgressLabel = root.querySelector('.qz-progress__label');
  var elProgressPct = root.querySelector('.qz-progress__pct');
  var elSteps = root.querySelectorAll('.qz-step');
  var elError = root.querySelector('.qz-error');
  var form = root.querySelector('#qz-form');

  function questions() {
    return activeVariant === 'early' ? QUESTIONS_EARLY : QUESTIONS_READING;
  }

  function copy() {
    return COPY[activeVariant] || COPY.reading;
  }

  function showError(msg) {
    if (!elError) return;
    elError.textContent = msg;
    elError.classList.add('is-visible');
  }

  function hideError() {
    if (!elError) return;
    elError.classList.remove('is-visible');
  }

  function updateProgress() {
    var qs = questions();
    var pct;
    if (stepIndex < qs.length) {
      pct = Math.round(((stepIndex + 1) / qs.length) * 100);
    } else {
      pct = 100;
    }
    if (elProgressFill) elProgressFill.style.width = pct + '%';
    if (elProgressPct) elProgressPct.textContent = pct + '%';
    if (elProgressLabel) {
      if (stepIndex < qs.length) {
        elProgressLabel.textContent = 'Вопрос ' + (stepIndex + 1) + ' из ' + qs.length;
      } else if (stepIndex === qs.length) {
        elProgressLabel.textContent = activeVariant === 'early' ? 'Почти готово' : 'Подборка готова';
      } else {
        elProgressLabel.textContent = 'Готово';
      }
    }
  }

  function refreshSteps() {
    elSteps = root.querySelectorAll('.qz-step');
  }

  function fitDialogHeight() {
    var dialog = root.closest('.qz-modal__dialog');
    var modal = dialog && dialog.closest('.qz-modal');
    if (!dialog || !modal || !modal.classList.contains('is-open')) return;
    dialog.style.height = 'auto';
    dialog.style.maxHeight = '';
    dialog.classList.remove('qz-modal--tight', 'qz-modal--form-compact');
    var card = dialog.querySelector('.qz-card');
    if (!card) return;
    var pad = window.innerWidth <= 720 ? 24 : 32;
    var max = Math.max(280, window.innerHeight - pad);
    var isForm = root.classList.contains('qz-form-step');
    var h = card.offsetHeight;
    if (h > max) {
      dialog.classList.add('qz-modal--tight');
      if (isForm) dialog.classList.add('qz-modal--form-compact');
      h = card.offsetHeight;
    }
    if (isForm) {
      dialog.style.overflow = 'hidden';
      var fit = Math.min(Math.max(h, 280), max);
      dialog.style.height = fit + 'px';
      dialog.style.maxHeight = fit + 'px';
      return;
    }
    dialog.style.overflow = '';
    var fit2 = Math.min(h, max);
    dialog.style.height = fit2 + 'px';
    dialog.style.maxHeight = fit2 + 'px';
  }

  function showStep(index) {
    var qs = questions();
    stepIndex = index;
    refreshSteps();
    elSteps.forEach(function (step, i) {
      step.classList.toggle('is-active', i === index);
    });
    root.classList.toggle('qz-phase-questions', index >= 0 && index < qs.length);
    root.classList.toggle('qz-intro-collapsed', index > 0 && index < qs.length);
    root.classList.toggle('qz-form-step', index === qs.length);
    root.classList.toggle('qz-success-step', index > qs.length);
    updateProgress();
    hideError();
    window.setTimeout(fitDialogHeight, 40);
  }

  function applyVariantCopy() {
    var c = copy();
    root.setAttribute('data-quiz-variant', activeVariant);
    var badge = root.querySelector('.qz-intro-gift__badge');
    var introSub = root.querySelector('.qz-intro-gift__sub');
    var formStep = root.querySelector('[data-step="form"]');
    var formSub = formStep && formStep.querySelector('.qz-sub');
    var giftPs = formStep && formStep.querySelectorAll('.qz-gift p:not(.qz-gift__label)');
    var ageNote = root.querySelector('.qz-age-note');
    var submitBtn = form && form.querySelector('.qz-btn--submit');
    var successPdf = root.querySelector('[data-qz-success-pdf]');
    var checklistLink = root.querySelector('[data-qz-checklist-link]');

    if (badge) badge.textContent = c.introBadge;
    if (introSub) introSub.textContent = c.introSub;
    if (formSub) formSub.textContent = c.formSub;
    if (giftPs && giftPs.length >= 2) {
      giftPs[0].innerHTML = c.giftNow;
      giftPs[1].innerHTML = c.giftLater;
    }
    if (ageNote) ageNote.textContent = c.ageNote;
    if (submitBtn && !submitBtn.disabled) submitBtn.textContent = c.submit;
    if (successPdf) successPdf.innerHTML = c.successPdf;
    if (checklistLink) {
      checklistLink.hidden = !c.showChecklistLink;
      checklistLink.style.display = c.showChecklistLink ? '' : 'none';
      if (c.checklistUrl) checklistLink.setAttribute('href', c.checklistUrl);
    }
  }

  function detectVariantFromTrial(trial) {
    if (!trial || typeof trial !== 'object') return 'reading';
    if (trial.quiz === 'early' || trial.quiz === 'reading') return trial.quiz;
    var age = String(trial.age || '');
    var slug = String(trial.slug || '');
    if (age === '4-6' || age === '5-7') return 'early';
    if (slug.indexOf('early-') === 0) return 'early';
    return 'reading';
  }

  function resolveVariant(el) {
    if (el && el.getAttribute) {
      var fromEl = el.getAttribute('data-quiz');
      if (fromEl === 'early' || fromEl === 'reading') return fromEl;
    }
    try {
      var raw = sessionStorage.getItem('chit_trial');
      if (raw) return detectVariantFromTrial(JSON.parse(raw));
    } catch (err) {}
    return 'reading';
  }

  function resetQuiz() {
    answers = {};
    if (form) {
      form.reset();
      var btn = form.querySelector('.qz-btn--submit');
      if (btn) {
        btn.disabled = false;
        btn.textContent = copy().submit;
      }
    }
    applyVariantCopy();
    renderQuestions();
    showStep(0);
  }

  function renderQuestions() {
    var container = root.querySelector('#qz-questions');
    if (!container) return;
    var qs = questions();
    var sub = copy().questionSub;
    container.innerHTML = qs.map(function (q, qi) {
      var opts = q.options.map(function (opt, oi) {
        return '<button type="button" class="qz-option" data-q="' + qi + '" data-v="' + oi + '">' + opt + '</button>';
      }).join('');
      return (
        '<section class="qz-step' + (qi === 0 ? ' is-active' : '') + '" data-step="' + qi + '">' +
          '<h2 class="qz-title">' + q.title + '</h2>' +
          '<p class="qz-sub">' + sub + '</p>' +
          '<div class="qz-options">' + opts + '</div>' +
          '<div class="qz-nav">' +
            (qi > 0 ? '<button type="button" class="qz-btn qz-btn--back" data-back="' + qi + '">Назад</button>' : '') +
            '<button type="button" class="qz-btn qz-btn--next" data-next="' + qi + '" disabled>Дальше</button>' +
          '</div>' +
        '</section>'
      );
    }).join('');
    refreshSteps();
  }

  function quizStorageGet() {
    if (!AUTO_ONCE_PER_SESSION) return null;
    try {
      return sessionStorage.getItem(AUTO_STORAGE_KEY);
    } catch (err) {
      return null;
    }
  }

  function quizStorageSet(value) {
    if (!AUTO_ONCE_PER_SESSION) return;
    try {
      sessionStorage.setItem(AUTO_STORAGE_KEY, value);
    } catch (err) {
      /* ignore */
    }
  }

  function quizPopupSeen() {
    return !!quizStorageGet();
  }

  function markQuizPopup(reason) {
    quizStorageSet(reason || 'seen');
  }

  function cancelAutoOpen() {
    if (autoOpenTimer) {
      clearTimeout(autoOpenTimer);
      autoOpenTimer = null;
    }
  }

  function shouldAutoOpen() {
    if (!AUTO_ENABLED) return false;
    if (!document.getElementById('qz-modal')) return false;
    if (window.location.hash === '#quiz') return false;
    if (quizPopupSeen()) return false;
    return true;
  }

  function scheduleAutoOpen() {
    cancelAutoOpen();
    if (!shouldAutoOpen()) return;
    autoOpenTimer = window.setTimeout(function () {
      autoOpenTimer = null;
      if (!shouldAutoOpen()) return;
      if (document.hidden) {
        document.addEventListener('visibilitychange', function onVisible() {
          if (document.hidden) return;
          document.removeEventListener('visibilitychange', onVisible);
          if (!shouldAutoOpen()) return;
          openQuizModal('auto');
        });
        return;
      }
      var modal = document.getElementById('qz-modal');
      if (modal && modal.classList.contains('is-open')) return;
      openQuizModal('auto');
    }, AUTO_DELAY_MS);
  }

  function applyTrialAgeHint() {
    if (!form || !form.child_age) return;
    try {
      var hint = sessionStorage.getItem('chit_trial_age_hint');
      if (hint && !form.child_age.value) form.child_age.value = hint;
    } catch (err) {}
  }

  function rememberTrialFromEl(el) {
    if (!el || !el.getAttribute) return;
    var quizAttr = el.getAttribute('data-quiz') || '';
    var slug = el.getAttribute('data-trial-slug') || '';
    var age = el.getAttribute('data-trial-age') || '';
    var title = el.getAttribute('data-trial-title') || '';
    var quiz = quizAttr === 'early' || quizAttr === 'reading'
      ? quizAttr
      : (age === '4-6' || age === '5-7' || slug.indexOf('early-') === 0 ? 'early' : 'reading');

    if (!slug && !quizAttr) {
      try {
        sessionStorage.removeItem('chit_trial');
        sessionStorage.removeItem('chit_trial_age_hint');
      } catch (err) {}
      return;
    }

    try {
      sessionStorage.setItem('chit_trial', JSON.stringify({
        age: age,
        slug: slug,
        title: title,
        quiz: quiz
      }));
      var hintAge = age === '4-6' ? '5' : (age === '5-7' ? '6' : (age === '6-8' ? '7' : (age === '9-11' ? '10' : '')));
      if (hintAge) sessionStorage.setItem('chit_trial_age_hint', hintAge);
      else sessionStorage.removeItem('chit_trial_age_hint');
    } catch (err) {}
  }

  function updateSuccessForTrial(apiData) {
    var success = root.querySelector('[data-step="success"]');
    if (!success) return;
    var giftLine = success.querySelector('[data-qz-gift-line]');
    var slot = success.querySelector('[data-qz-trial-slot]');
    var enroll = success.querySelector('[data-qz-enroll]');
    var pdf = success.querySelector('[data-qz-checklist-link]');
    var c = copy();
    var title = '';
    try {
      var raw = sessionStorage.getItem('chit_trial');
      if (raw) {
        var trial = JSON.parse(raw);
        if (trial && trial.title) title = String(trial.title);
      }
    } catch (err) {}
    if (giftLine) {
      giftLine.textContent = title ? c.successTrialGift(title) : c.successDefaultGift;
    }
    var oldLink = success.querySelector('.qz-success-trial-link');
    if (oldLink) oldLink.remove();
    var lessonUrl = apiData && apiData.trial_lesson_url;
    if (slot) {
      if (lessonUrl) {
        slot.hidden = false;
        slot.innerHTML =
          '<a class="qz-success-btn qz-success-btn--primary" href="' + lessonUrl +
          '" target="_blank" rel="noopener">Открыть пробный урок</a>';
        if (enroll) {
          enroll.className = 'qz-success-btn qz-success-btn--secondary';
        }
        if (pdf) {
          pdf.className = 'qz-success-btn qz-success-btn--ghost';
        }
      } else {
        slot.hidden = true;
        slot.innerHTML = '';
        if (enroll) {
          enroll.className = 'qz-success-btn qz-success-btn--primary';
        }
        if (pdf) {
          pdf.className = c.showChecklistLink
            ? 'qz-success-btn qz-success-btn--secondary'
            : 'qz-success-btn qz-success-btn--ghost';
        }
      }
    }
  }

  function openQuizModal(source, fromEl) {
    var modal = document.getElementById('qz-modal');
    if (!modal) return;
    cancelAutoOpen();
    markQuizPopup(source || 'open');
    activeVariant = resolveVariant(fromEl);
    resetQuiz();
    applyTrialAgeHint();
    updateSuccessForTrial();
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('qz-modal-open');
    var closeBtn = modal.querySelector('.qz-modal__close');
    if (closeBtn) closeBtn.focus();
    window.setTimeout(fitDialogHeight, 60);
  }

  function closeQuizModal() {
    var modal = document.getElementById('qz-modal');
    if (!modal) return;
    markQuizPopup('dismissed');
    modal.classList.remove('is-open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('qz-modal-open');
    if (window.location.hash === '#quiz') {
      try {
        history.replaceState(null, '', window.location.pathname + window.location.search);
      } catch (err) {
        window.location.hash = '';
      }
    }
  }

  function bindModal() {
    var modal = document.getElementById('qz-modal');
    if (!modal) return;
    window.chitQuizOpen = function () { openQuizModal('manual'); };
    window.chitQuizOpenWithEl = function (fromEl) {
      if (fromEl) rememberTrialFromEl(fromEl);
      openQuizModal('manual', fromEl);
    };
    window.chitQuizClose = closeQuizModal;
    document.querySelectorAll('[href="#quiz"], [data-qz-open]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        rememberTrialFromEl(el);
        openQuizModal('manual', el);
      });
    });
    modal.querySelectorAll('[data-qz-close]').forEach(function (el) {
      el.addEventListener('click', closeQuizModal);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modal.classList.contains('is-open')) closeQuizModal();
    });
    window.addEventListener('hashchange', function () {
      if (window.location.hash === '#quiz') {
        rememberTrialFromUrl();
        openQuizModal('hash');
      }
    });
    rememberTrialFromUrl();
    if (window.location.hash === '#quiz') {
      window.setTimeout(function () { openQuizModal('hash'); }, 120);
    }
  }

  function rememberTrialFromUrl() {
    try {
      var params = new URLSearchParams(window.location.search || '');
      var slug = params.get('trial') || params.get('trial_slug') || '';
      if (!slug) return;
      var age = params.get('age') || params.get('trial_age') || '';
      var title = params.get('title') || params.get('trial_title') || '';
      var quiz = params.get('quiz') || '';
      if (!quiz) {
        quiz = (age === '4-6' || age === '5-7' || slug.indexOf('early-') === 0) ? 'early' : 'reading';
      }
      sessionStorage.setItem('chit_trial', JSON.stringify({
        age: age,
        slug: slug,
        title: title,
        quiz: quiz
      }));
      var hintAge = age === '4-6' ? '5' : (age === '5-7' ? '6' : (age === '6-8' ? '7' : (age === '9-11' ? '10' : '')));
      if (hintAge) sessionStorage.setItem('chit_trial_age_hint', hintAge);
    } catch (err) {}
  }

  function allQuestionsAnswered() {
    var qs = questions();
    for (var i = 0; i < qs.length; i++) {
      if (!answers[qs[i].id]) return false;
    }
    return true;
  }

  function validateForm() {
    var parentName = form.parent_name.value.trim();
    var parentEmail = form.parent_email.value.trim();
    var childName = form.child_name.value.trim();
    var childAgeRaw = form.child_age ? form.child_age.value.trim() : '';
    var childAge = childAgeRaw === '' ? NaN : parseInt(childAgeRaw, 10);
    if (!parentName) return 'Укажите имя родителя';
    if (!parentEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(parentEmail)) {
      return 'Укажите корректный email';
    }
    if (!childName) return 'Укажите имя ребёнка';
    if (!childAgeRaw || !Number.isFinite(childAge) || childAge < 1) {
      return 'Укажите возраст ребёнка от 1 года';
    }
    if (!allQuestionsAnswered()) {
      return 'Ответьте на все вопросы квиза — нажмите «Назад» и выберите варианты';
    }
    return '';
  }

  function buildAnswersPayload() {
    return questions().map(function (q) {
      return { id: q.id, question: q.title, answer: answers[q.id] || '' };
    }).filter(function (item) {
      return item.answer && item.answer.trim();
    });
  }

  function submitForm(e) {
    e.preventDefault();
    hideError();
    var err = validateForm();
    if (err) {
      showError(err);
      return;
    }
    var btn = form.querySelector('.qz-btn--submit');
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Отправляем…';
    }
    var payload = {
      parent_name: form.parent_name.value.trim(),
      parent_email: form.parent_email.value.trim(),
      phone: '',
      child_name: form.child_name.value.trim(),
      child_age: parseInt(form.child_age.value.trim(), 10),
      answers: buildAnswersPayload(),
      quiz_variant: activeVariant
    };
    try {
      var trialRaw = sessionStorage.getItem('chit_trial');
      if (trialRaw) {
        var trial = JSON.parse(trialRaw);
        if (trial && typeof trial === 'object') {
          if (trial.age) payload.trial_age = String(trial.age);
          if (trial.slug) payload.trial_slug = String(trial.slug);
          if (trial.title) payload.trial_title = String(trial.title);
          if (trial.quiz && !payload.quiz_variant) payload.quiz_variant = String(trial.quiz);
        }
      }
    } catch (err2) {}
    fetch(API_BASE + '/api/quiz/lead', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function (r) {
        if (r.ok) return r.json();
        return r.json().catch(function () { return {}; }).then(function (data) {
          var msg = 'Не удалось отправить. Проверьте связь и попробуйте ещё раз.';
          if (data && data.detail) {
            if (typeof data.detail === 'string') msg = data.detail;
            else if (Array.isArray(data.detail) && data.detail[0] && data.detail[0].msg) {
              msg = 'Проверьте ответы квиза и данные формы, затем попробуйте снова.';
            }
          }
          throw new Error(msg);
        });
      })
      .then(function (data) {
        markQuizPopup('done');
        updateSuccessForTrial(data);
        showStep(questions().length + 1);
      })
      .catch(function (err3) {
        showError(err3 && err3.message ? err3.message : 'Не удалось отправить. Проверьте связь и попробуйте ещё раз.');
        if (btn) {
          btn.disabled = false;
          btn.textContent = copy().submit;
        }
      });
  }

  renderQuestions();
  bindModal();

  root.addEventListener('click', function (e) {
    var qs = questions();
    var opt = e.target.closest('.qz-option');
    if (opt) {
      var qi = Number(opt.getAttribute('data-q'));
      var q = qs[qi];
      if (!q) return;
      answers[q.id] = q.options[Number(opt.getAttribute('data-v'))];
      opt.closest('.qz-options').querySelectorAll('.qz-option').forEach(function (b) {
        b.classList.toggle('is-selected', b === opt);
      });
      var nextBtn = opt.closest('.qz-step').querySelector('.qz-btn--next');
      if (nextBtn) nextBtn.disabled = false;
      return;
    }
    var next = e.target.closest('[data-next]');
    if (next && !next.disabled) {
      var ni = Number(next.getAttribute('data-next'));
      if (ni < qs.length - 1) showStep(ni + 1);
      else showStep(qs.length);
      return;
    }
    var back = e.target.closest('[data-back]');
    if (back) showStep(Number(back.getAttribute('data-back')) - 1);
  });

  if (form) form.addEventListener('submit', submitForm);

  var ageInput = form && form.child_age;
  if (ageInput) {
    ageInput.setAttribute('min', '1');
    ageInput.setAttribute('max', '99');
    ageInput.addEventListener('input', function () {
      if (this.value === '' || this.value === '-') {
        if (this.value === '-') this.value = '';
        return;
      }
      var n = parseInt(this.value, 10);
      if (!Number.isFinite(n) || n < 1) this.value = '';
      else if (n > 99) this.value = '99';
    });
    ageInput.addEventListener('focus', function () {
      var self = this;
      window.setTimeout(function () {
        self.scrollIntoView({ block: 'center', behavior: 'smooth' });
      }, 320);
    });
  }

  updateProgress();
  window.addEventListener('resize', fitDialogHeight);
})();
