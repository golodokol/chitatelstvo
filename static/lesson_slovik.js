(function (global) {
  var STEP_HINTS = {
    reads: 'Смотрим видео-урок',
    emotion: 'Изучаем эмоциональный интеллект',
    reading: 'Практика чтения',
    writes: 'Мини-тест по сказке',
    dreams: 'Выполняем задания',
    retelling: 'Пробуем пересказать сказку',
    grows: 'Творчество и встреча — по желанию',
    victory: 'Ура! Урок почти пройден!',
    reward: 'Молодец!',
  };

  var EVENT_POINTS = {
    lesson_complete: 2,
    emotion_quiz: 1,
    reading_practice: 2,
    comprehension: 2,
    meaning_analysis: 2,
    retelling: 2,
    creative_task: 3,
    live_meeting: 2,
    streak_3: 3,
  };

  var EVENT_BADGES = {
    lesson_complete: 'Читатель',
    reading_practice: 'Читатель',
    comprehension: 'Следопыт',
    meaning_analysis: 'Ловец смысла',
    creative_task: 'Сказочник',
    retelling: 'Мастер пересказа',
    live_meeting: 'Слушатель',
    streak_3: 'Непрерывная серия',
    module_complete: 'Исследователь сказки',
    first_task: 'Первый шаг',
  };

  var BADGE_IMAGES = {
    'Первый шаг': '/assets/gamify-badge-first-step.png',
    'Читатель': '/assets/gamify-badge-reader.png',
    'Слушатель': '/assets/gamify-badge-listener.png',
    'Следопыт': '/assets/gamify-badge-tracker.png',
    'Ловец смысла': '/assets/gamify-badge-meaning.png',
    'Мастер пересказа': '/assets/gamify-badge-retelling.png',
    'Сказочник': '/assets/gamify-badge-storyteller.png',
    'Исследователь сказки': '/assets/gamify-badge-module-explorer.png',
    'Непрерывная серия': '/assets/gamify-badge-streak.png',
    'Путешественник по сказке': '/assets/gamify-badge-tale-traveler.png',
  };

  var EVENT_SLOVIK = {
    lesson_complete: 'reads',
    emotion_quiz: 'emotion',
    reading_practice: 'reading',
    comprehension: 'writes',
    meaning_analysis: 'dreams',
    retelling: 'retelling',
    creative_task: 'writes',
    live_meeting: 'grows',
  };

  function rewardParts(eventType) {
    var pts = EVENT_POINTS[eventType] || 0;
    var badge = EVENT_BADGES[eventType] || null;
    return { points: pts, badge: badge };
  }

  function rewardMessage(eventType, status) {
    if (status !== 'accepted') return status === 'duplicate' ? 'Уже было засчитано ранее' : '';
    var parts = rewardParts(eventType);
    if (parts.badge && parts.points) {
      return '+' + parts.points + ' Словиков · бейдж «' + parts.badge + '»';
    }
    if (parts.points) return '+' + parts.points + ' Словиков!';
    if (parts.badge) return 'Бейдж «' + parts.badge + '»!';
    return 'Задание засчитано!';
  }

  function ensureToast() {
    var toast = document.getElementById('slovik-toast');
    if (toast) return toast;
    toast = document.createElement('div');
    toast.id = 'slovik-toast';
    toast.className = 'chit-reward-toast';
    toast.hidden = true;
    toast.setAttribute('aria-live', 'polite');
    toast.innerHTML =
      '<div class="chit-reward-toast__backdrop" data-reward-dismiss></div>' +
      '<div class="chit-reward-toast__card" role="status">' +
      '<p class="chit-reward-toast__kicker"></p>' +
      '<div class="chit-reward-toast__hero">' +
      '<img class="chit-reward-toast__badge" alt="" width="120" height="120" hidden>' +
      '<img class="chit-reward-toast__slovik" alt="Словик" width="84" height="84">' +
      '</div>' +
      '<p class="chit-reward-toast__title"></p>' +
      '<p class="chit-reward-toast__sub"></p>' +
      '</div>';
    document.body.appendChild(toast);
    toast.querySelector('[data-reward-dismiss]')?.addEventListener('click', hideToast);
    return toast;
  }

  function hideToast() {
    var toast = document.getElementById('slovik-toast');
    if (!toast) return;
    toast.classList.remove('is-visible');
    clearTimeout(hideToast._timer);
    hideToast._timer = setTimeout(function () { toast.hidden = true; }, 280);
  }

  function showReward(opts) {
    opts = opts || {};
    var toast = ensureToast();
    var kicker = toast.querySelector('.chit-reward-toast__kicker');
    var badgeImg = toast.querySelector('.chit-reward-toast__badge');
    var slovikImg = toast.querySelector('.chit-reward-toast__slovik');
    var title = toast.querySelector('.chit-reward-toast__title');
    var sub = toast.querySelector('.chit-reward-toast__sub');

    var eventType = opts.eventType || '';
    var parts = rewardParts(eventType);
    // null с сервера = «бейджа нет» (напр. урок букв). Не подменять на EVENT_BADGES.
    var badge = Object.prototype.hasOwnProperty.call(opts, 'badge') ? opts.badge : parts.badge;
    var points = opts.points != null ? opts.points : parts.points;
    var slovikKey = opts.slovikKey || EVENT_SLOVIK[eventType] || 'reward';
    var urls = opts.urls || {};
    var slovikUrl = opts.slovikUrl || (urls && urls[slovikKey]) || (urls && urls.reward) || '/static/sloviki/slovik-reward.png';
    var badgeImage = opts.badgeImage || (badge && BADGE_IMAGES[badge]) || '';

    if (kicker) {
      kicker.textContent = badge ? 'Новый бейдж!' : 'Молодец!';
    }

    if (badgeImg) {
      if (badge && badgeImage) {
        badgeImg.src = badgeImage;
        badgeImg.alt = badge;
        badgeImg.hidden = false;
      } else {
        badgeImg.removeAttribute('src');
        badgeImg.hidden = true;
      }
    }

    if (slovikImg) {
      if (badge && badgeImage) {
        slovikImg.hidden = true;
      } else {
        slovikImg.src = slovikUrl;
        slovikImg.hidden = false;
      }
    }

    if (title) {
      if (badge) {
        title.textContent = '«' + badge + '»';
      } else if (points) {
        title.textContent = '+' + points + ' Словиков!';
      } else {
        title.textContent = opts.message || 'Отличная работа!';
      }
    }

    if (sub) {
      if (badge && points) {
        sub.textContent = '+' + points + ' Словиков';
      } else if (!badge && opts.message && opts.message !== title.textContent) {
        sub.textContent = opts.message;
      } else {
        sub.textContent = '';
      }
    }

    toast.hidden = false;
    requestAnimationFrame(function () {
      toast.classList.add('is-visible');
    });

    clearTimeout(showReward._timer);
    var duration = badge ? 4800 : 3600;
    showReward._timer = setTimeout(hideToast, duration);
  }

  function showToast(urls, key, message, extra) {
    showReward({
      urls: urls,
      slovikKey: key,
      message: message,
      eventType: extra && extra.eventType,
      badge: extra && extra.badge,
      badgeImage: extra && extra.badgeImage,
      points: extra && extra.points,
      slovikUrl: extra && extra.url,
    });
  }

  var STEP_TARGETS = {
    reads: 'step-video',
    emotion: 'step-emotion',
    reading: 'step-reading',
    writes: 'step-comprehension',
    dreams: 'step-meaning',
    retelling: 'step-retelling',
    grows: 'step-creative',
    victory: 'step-rating',
  };

  var companionLinkBound = false;

  function resolveStepTarget(key) {
    var id = STEP_TARGETS[key];
    if (!id) return null;
    if (id === 'step-creative' && !document.getElementById('step-creative')) {
      if (document.getElementById('step-live-lesson')) return 'step-live-lesson';
      if (document.getElementById('step-rating')) return 'step-rating';
    }
    return document.getElementById(id) ? id : null;
  }

  function bindCompanionLink() {
    if (companionLinkBound) return;
    companionLinkBound = true;
    document.addEventListener('click', function (e) {
      var link = e.target.closest('[data-lesson-companion]');
      if (!link) return;
      var href = link.getAttribute('href') || '';
      if (href.charAt(0) !== '#') return;
      var el = document.getElementById(href.slice(1));
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  function updateCompanion(urls, key, hint, stepLabels) {
    bindCompanionLink();
    var img = document.querySelector('[data-lesson-companion-img]');
    var hintEl = document.querySelector('[data-lesson-companion-hint]');
    var companion = document.querySelector('[data-lesson-companion]');
    if (img && urls && urls[key]) img.src = urls[key];
    var resolved = hint;
    if (!resolved && stepLabels) {
      var map = {
        reads: 'video',
        emotion: 'emotion_quiz',
        reading: 'reading_practice',
        writes: 'comprehension_quiz',
        dreams: 'tasks',
        retelling: 'retelling',
        grows: 'creative',
      };
      resolved = stepLabels[map[key]] || '';
    }
    resolved = resolved || STEP_HINTS[key] || '';
    if (hintEl) hintEl.textContent = resolved;
    var targetId = resolveStepTarget(key);
    if (companion) {
      if (targetId) {
        companion.href = '#' + targetId;
        companion.setAttribute('aria-label', 'Перейти к заданию: ' + resolved);
        companion.classList.remove('is-disabled');
      } else {
        companion.removeAttribute('href');
        companion.setAttribute('aria-label', resolved);
        companion.classList.add('is-disabled');
      }
    }
  }

  function afterEvent(urls, eventType, status) {
    var key = EVENT_SLOVIK[eventType] || 'reward';
    if (status === 'accepted') {
      showReward({ urls: urls, eventType: eventType, slovikKey: key });
    }
    updateCompanion(urls, key, STEP_HINTS[key]);
    return key;
  }

  function nextStepKey(cfg, state) {
    state = state || {};
    cfg = cfg || {};
    if (
      state.retellingDone
      || (state.meaningDone && !cfg.hasRetelling)
      || (state.videoUnlocked && !cfg.hasEmotion && !cfg.hasComprehension && !cfg.hasMeaning && !cfg.hasRetelling)
    ) {
      return 'grows';
    }
    if (state.meaningDone && cfg.hasRetelling) return 'retelling';
    if (state.comprehensionDone && !cfg.hasMeaning) return 'grows';
    if (state.comprehensionDone) return 'dreams';
    if (state.readingDone && cfg.hasComprehension) return 'writes';
    if (state.readingDone) return 'grows';
    if (state.emotionDone && (cfg.hasReading || cfg.hasComprehension)) {
      return cfg.hasReading ? 'reading' : 'writes';
    }
    if (state.emotionDone) return 'grows';
    if (state.videoUnlocked && cfg.hasEmotion) return 'emotion';
    if (state.videoUnlocked && cfg.hasReading) return 'reading';
    if (state.videoUnlocked && cfg.hasComprehension) return 'writes';
    if (state.videoUnlocked) return 'grows';
    return 'reads';
  }

  global.ChitSlovik = {
    showToast: showToast,
    showReward: showReward,
    hideToast: hideToast,
    updateCompanion: updateCompanion,
    afterEvent: afterEvent,
    nextStepKey: nextStepKey,
    STEP_HINTS: STEP_HINTS,
    rewardMessage: rewardMessage,
    BADGE_IMAGES: BADGE_IMAGES,
  };
})(window);
