(function () {
  'use strict';

  var API_BASE = window.CHIT_QUIZ_API || 'https://api.chitatelstvo.ru';
  var CHECKLIST_URL = API_BASE + '/quiz/checklist';

  var QUESTIONS = [
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

  function showError(msg) {
    if (!elError) return;
    elError.textContent = msg;
    elError.classList.add('is-visible');
  }

  function hideError() {
    if (!elError) elError.classList.remove('is-visible');
  }

  function updateProgress() {
    var pct;
    if (stepIndex < QUESTIONS.length) {
      pct = Math.round(((stepIndex + 1) / QUESTIONS.length) * 80);
    } else if (stepIndex === QUESTIONS.length) {
      pct = 92;
    } else {
      pct = 100;
    }
    if (elProgressFill) elProgressFill.style.width = pct + '%';
    if (elProgressPct) elProgressPct.textContent = pct + '%';
    if (elProgressLabel) {
      if (stepIndex < QUESTIONS.length) {
        elProgressLabel.textContent = 'Вопрос ' + (stepIndex + 1) + ' из ' + QUESTIONS.length;
      } else if (stepIndex === QUESTIONS.length) {
        elProgressLabel.textContent = 'Подборка готова';
      } else {
        elProgressLabel.textContent = 'Готово';
      }
    }
  }

  function refreshSteps() {
    elSteps = root.querySelectorAll('.qz-step');
  }

  function showStep(index) {
    stepIndex = index;
    refreshSteps();
    elSteps.forEach(function (step, i) {
      step.classList.toggle('is-active', i === index);
    });
    updateProgress();
    hideError();
    var dialog = root.closest('.qz-modal__dialog');
    if (dialog) dialog.scrollTop = 0;
  }

  function resetQuiz() {
    answers = {};
    if (form) {
      form.reset();
      var btn = form.querySelector('.qz-btn--submit');
      if (btn) {
        btn.disabled = false;
        btn.textContent = 'Получить подборку + сказку';
      }
    }
    renderQuestions();
    showStep(0);
  }

  function renderQuestions() {
    var container = root.querySelector('#qz-questions');
    if (!container) return;
    container.innerHTML = QUESTIONS.map(function (q, qi) {
      var opts = q.options.map(function (opt, oi) {
        return '<button type="button" class="qz-option" data-q="' + qi + '" data-v="' + oi + '">' + opt + '</button>';
      }).join('');
      return (
        '<section class="qz-step' + (qi === 0 ? ' is-active' : '') + '" data-step="' + qi + '">' +
          '<h2 class="qz-title">' + q.title + '</h2>' +
          '<p class="qz-sub">Выберите один вариант — так мы соберём персональную подборку</p>' +
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

  function openQuizModal() {
    var modal = document.getElementById('qz-modal');
    if (!modal) return;
    resetQuiz();
    modal.classList.add('is-open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('qz-modal-open');
    var closeBtn = modal.querySelector('.qz-modal__close');
    if (closeBtn) closeBtn.focus();
  }

  function closeQuizModal() {
    var modal = document.getElementById('qz-modal');
    if (!modal) return;
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
    window.chitQuizOpen = openQuizModal;
    window.chitQuizClose = closeQuizModal;
    document.querySelectorAll('[href="#quiz"], [data-qz-open]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        openQuizModal();
      });
    });
    modal.querySelectorAll('[data-qz-close]').forEach(function (el) {
      el.addEventListener('click', closeQuizModal);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modal.classList.contains('is-open')) closeQuizModal();
    });
    window.addEventListener('hashchange', function () {
      if (window.location.hash === '#quiz') openQuizModal();
    });
    if (window.location.hash === '#quiz') openQuizModal();
  }

  function normalizePhone(raw) {
    var digits = String(raw || '').replace(/\D/g, '');
    if (digits.length === 11 && digits.charAt(0) === '8') digits = '7' + digits.slice(1);
    if (digits.length === 10) digits = '7' + digits;
    return digits;
  }

  function validateForm() {
    var parentName = form.parent_name.value.trim();
    var phone = normalizePhone(form.phone.value);
    var childName = form.child_name.value.trim();
    var childAge = form.child_age.value.trim();
    if (!parentName) return 'Укажите имя родителя';
    if (phone.length < 11) return 'Укажите корректный телефон';
    if (!childName) return 'Укажите имя ребёнка';
    if (!childAge || isNaN(Number(childAge)) || Number(childAge) < 4 || Number(childAge) > 18) {
      return 'Укажите возраст ребёнка (4–18)';
    }
    return '';
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
      phone: form.phone.value.trim(),
      child_name: form.child_name.value.trim(),
      child_age: Number(form.child_age.value.trim()),
      answers: QUESTIONS.map(function (q) {
        return { question: q.title, answer: answers[q.id] || '' };
      })
    };
    fetch(API_BASE + '/api/quiz/lead', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function (r) {
        if (!r.ok) throw new Error('submit failed');
        return r.json();
      })
      .then(function () {
        showStep(QUESTIONS.length + 1);
      })
      .catch(function () {
        showError('Не удалось отправить. Проверьте связь и попробуйте ещё раз.');
        if (btn) {
          btn.disabled = false;
          btn.textContent = 'Получить подборку + сказку';
        }
      });
  }

  renderQuestions();
  bindModal();

  root.addEventListener('click', function (e) {
    var opt = e.target.closest('.qz-option');
    if (opt) {
      var qi = Number(opt.getAttribute('data-q'));
      var q = QUESTIONS[qi];
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
      if (ni < QUESTIONS.length - 1) showStep(ni + 1);
      else showStep(QUESTIONS.length);
      return;
    }
    var back = e.target.closest('[data-back]');
    if (back) showStep(Number(back.getAttribute('data-back')) - 1);
  });

  if (form) form.addEventListener('submit', submitForm);

  updateProgress();
})();
