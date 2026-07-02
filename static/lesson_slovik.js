(function (global) {
  var STEP_HINTS = {
    reads: 'Смотрим видео-урок',
    emotion: 'Изучаем эмоциональный интеллект',
    writes: 'Мини-тест по сказке',
    dreams: 'Выполняем задания',
    grows: 'Творчество и встреча — по желанию',
    victory: 'Ура! Урок почти пройден!',
    reward: 'Молодец!',
  };

  var EVENT_POINTS = {
    lesson_complete: 2,
    emotion_quiz: 1,
    comprehension: 2,
    meaning_analysis: 2,
    creative_task: 3,
    live_meeting: 2,
  };

  var EVENT_SLOVIK = {
    lesson_complete: 'reads',
    emotion_quiz: 'emotion',
    comprehension: 'writes',
    meaning_analysis: 'dreams',
    creative_task: 'writes',
    live_meeting: 'grows',
  };

  function ensureToast() {
    var toast = document.getElementById('slovik-toast');
    if (toast) return toast;
    toast = document.createElement('div');
    toast.id = 'slovik-toast';
    toast.className = 'chit-slovik-toast';
    toast.hidden = true;
    toast.setAttribute('aria-live', 'polite');
    toast.innerHTML =
      '<img class="chit-slovik-toast__img" src="" alt="" width="56" height="56">' +
      '<p class="chit-slovik-toast__text"></p>';
    document.body.appendChild(toast);
    return toast;
  }

  function showToast(urls, key, message) {
    var toast = ensureToast();
    var img = toast.querySelector('.chit-slovik-toast__img');
    var text = toast.querySelector('.chit-slovik-toast__text');
    var url = (urls && urls[key]) || (urls && urls.reward) || '/static/sloviki/slovik-reward.png';
    if (img) img.src = url;
    if (text) text.textContent = message || '';
    toast.hidden = false;
    toast.classList.add('is-visible');
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(function () {
      toast.classList.remove('is-visible');
      setTimeout(function () { toast.hidden = true; }, 300);
    }, 4200);
  }

  function updateCompanion(urls, key, hint, stepLabels) {
    var img = document.querySelector('[data-lesson-companion-img]');
    var hintEl = document.querySelector('[data-lesson-companion-hint]');
    if (img && urls && urls[key]) img.src = urls[key];
    if (hintEl) {
      var resolved = hint;
      if (!resolved && stepLabels) {
        var map = {
          reads: 'video',
          emotion: 'emotion_quiz',
          writes: 'comprehension_quiz',
          dreams: 'tasks',
          grows: 'creative',
        };
        resolved = stepLabels[map[key]] || '';
      }
      hintEl.textContent = resolved || STEP_HINTS[key] || '';
    }
  }

  function rewardMessage(eventType, status) {
    if (status !== 'accepted') return status === 'duplicate' ? 'Уже было засчитано ранее' : '';
    var pts = EVENT_POINTS[eventType];
    if (pts) return '+' + pts + ' Словиков!';
    return 'Задание засчитано!';
  }

  function afterEvent(urls, eventType, status) {
    var key = EVENT_SLOVIK[eventType] || 'reward';
    if (status === 'accepted') {
      showToast(urls, key, rewardMessage(eventType, status));
    }
    updateCompanion(urls, key, STEP_HINTS[key]);
    return key;
  }

  function nextStepKey(cfg, state) {
    state = state || {};
    cfg = cfg || {};
    if (state.meaningDone || (state.videoDone && !cfg.hasEmotion && !cfg.hasComprehension && !cfg.hasMeaning)) {
      return 'grows';
    }
    if (state.comprehensionDone && !cfg.hasMeaning) return 'grows';
    if (state.comprehensionDone) return 'dreams';
    if (state.emotionDone && cfg.hasComprehension) return 'writes';
    if (state.emotionDone) return 'grows';
    if (state.videoDone && cfg.hasEmotion) return 'emotion';
    if (state.videoDone) return 'writes';
    return 'reads';
  }

  global.ChitSlovik = {
    showToast: showToast,
    updateCompanion: updateCompanion,
    afterEvent: afterEvent,
    nextStepKey: nextStepKey,
    STEP_HINTS: STEP_HINTS,
    rewardMessage: rewardMessage,
  };
})(window);
