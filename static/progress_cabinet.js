(function () {
  var tabs = document.querySelectorAll('.chit-tabs__btn');
  var views = document.querySelectorAll('.chit-view');

  function showTab(name) {
    tabs.forEach(function (btn) {
      var active = btn.getAttribute('data-tab') === name;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    views.forEach(function (view) {
      var show = view.getAttribute('data-view') === name;
      view.hidden = !show;
    });
    document.body.classList.toggle('chit-cabinet--parent', name === 'parent');
    try {
      history.replaceState(null, '', name === 'parent' ? '#parent' : '#');
    } catch (e) {}
  }

  tabs.forEach(function (btn) {
    btn.addEventListener('click', function () {
      showTab(btn.getAttribute('data-tab') || 'child');
    });
  });

  if (location.hash === '#parent') {
    showTab('parent');
  }

  function showRoomToast(data) {
    if (!data || !data.toast_id) return;
    var key = 'chit-slovik-toast-' + data.toast_id;
    if (sessionStorage.getItem(key)) return;
    sessionStorage.setItem(key, '1');
    if (!window.ChitSlovik || !window.ChitSlovik.showReward) return;
    window.ChitSlovik.showReward({
      eventType: data.event_type,
      slovikKey: data.key,
      slovikUrl: data.url,
      message: data.message,
      badge: data.badge,
      badgeImage: data.badge_image,
      points: data.points,
    });
  }

  document.querySelectorAll('.chit-room-toast-data').forEach(function (node) {
    try {
      showRoomToast(JSON.parse(node.textContent || ''));
    } catch (e) {}
  });

  var toast = document.getElementById('slovik-toast');
  if (toast) {
    toast.querySelector('[data-reward-dismiss]')?.addEventListener('click', function () {
      if (window.ChitSlovik && window.ChitSlovik.hideToast) {
        window.ChitSlovik.hideToast();
      }
    });
  }

  document.querySelectorAll('button[data-chest-open]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (btn.disabled) return;
      var panel = btn.closest('.chit-panel--chest');
      if (!panel || !window.ChitChest) return;
      window.ChitChest.openFromPanel(panel);
    });
  });

  document.querySelectorAll('.chit-panel--chest[data-auto-open="1"]').forEach(function (panel) {
    if (window.ChitChest) {
      setTimeout(function () { window.ChitChest.openFromPanel(panel); }, 400);
    }
  });

  var TREASURY_MAX_ROWS = 3;

  function treasuryColumnCount(grid) {
    var style = window.getComputedStyle(grid);
    var cols = style.gridTemplateColumns;
    if (!cols || cols === 'none') return 4;
    return cols.split(' ').filter(function (part) { return part && part !== '0px'; }).length || 4;
  }

  function initTreasuryPager(root) {
    var grid = root.querySelector('.chit-treasury-grid');
    var pager = root.querySelector('[data-treasury-pager]');
    if (!grid || !pager) return;

    var prevBtn = pager.querySelector('[data-treasury-prev]');
    var nextBtn = pager.querySelector('[data-treasury-next]');
    var label = pager.querySelector('[data-treasury-label]');

    function items() {
      return Array.prototype.slice.call(grid.querySelectorAll('.chit-treasury-item'));
    }

    function pageSize() {
      return Math.max(1, treasuryColumnCount(grid) * TREASURY_MAX_ROWS);
    }

    function getPage() {
      return Number(root.getAttribute('data-treasury-page') || '0') || 0;
    }

    function setPage(page) {
      root.setAttribute('data-treasury-page', String(page));
    }

    function render() {
      var list = items();
      if (!list.length) {
        pager.hidden = true;
        return;
      }
      var size = pageSize();
      var pages = Math.max(1, Math.ceil(list.length / size));
      var page = getPage();
      if (page >= pages) page = pages - 1;
      if (page < 0) page = 0;
      setPage(page);
      var start = page * size;
      var end = start + size;
      list.forEach(function (item, index) {
        item.hidden = index < start || index >= end;
      });
      pager.hidden = pages <= 1;
      if (label) label.textContent = (page + 1) + ' / ' + pages;
      if (prevBtn) prevBtn.disabled = page <= 0;
      if (nextBtn) nextBtn.disabled = page >= pages - 1;
    }

    root._chitTreasuryRender = render;

    if (!root.getAttribute('data-treasury-ready')) {
      root.setAttribute('data-treasury-ready', '1');
      if (prevBtn) {
        prevBtn.addEventListener('click', function () {
          setPage(getPage() - 1);
          render();
        });
      }
      if (nextBtn) {
        nextBtn.addEventListener('click', function () {
          setPage(getPage() + 1);
          render();
        });
      }
      var resizeTimer = null;
      window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(render, 120);
      });
    }

    render();
  }

  document.querySelectorAll('[data-treasury]').forEach(initTreasuryPager);

  window.ChitTreasury = {
    refresh: function (root) {
      if (root) {
        initTreasuryPager(root);
        return;
      }
      document.querySelectorAll('[data-treasury]').forEach(initTreasuryPager);
    },
  };

  var modal = document.getElementById('badge-modal');
  var titleEl = document.getElementById('badge-modal-title');
  var textEl = document.getElementById('badge-modal-text');
  var imgWrap = document.getElementById('badge-modal-img-wrap');
  var imgEl = document.getElementById('badge-modal-img');

  function clearPressedBadges(except) {
    document.querySelectorAll('.chit-badge-card.is-pressed').forEach(function (card) {
      if (card !== except) card.classList.remove('is-pressed');
    });
  }

  function clearActiveLevels(except) {
    document.querySelectorAll('.chit-level-step.is-active').forEach(function (step) {
      if (step !== except) step.classList.remove('is-active');
    });
  }

  document.querySelectorAll('.chit-level-step').forEach(function (step) {
    step.addEventListener('click', function () {
      var active = step.classList.contains('is-active');
      clearActiveLevels(step);
      if (!active) step.classList.add('is-active');
    });
  });

  document.querySelectorAll('[data-badge-name]').forEach(function (card) {
    card.addEventListener('click', function () {
      clearPressedBadges(card);
      card.classList.add('is-pressed');
      if (!modal) return;
      var badgeName = card.getAttribute('data-badge-name') || '';
      titleEl.textContent = badgeName;
      textEl.textContent = card.getAttribute('data-badge-condition') || '';
      var imgUrl = card.getAttribute('data-badge-image') || '';
      var cardImg = card.querySelector('.chit-badge-card__img img');
      if (imgEl && imgWrap) {
        var src = imgUrl || (cardImg ? cardImg.src : '');
        if (src) {
          imgEl.src = src;
          imgEl.alt = badgeName;
          imgWrap.hidden = false;
        } else {
          imgEl.removeAttribute('src');
          imgWrap.hidden = true;
        }
      }
      modal.hidden = false;
    });
  });

  if (modal) {
    function closeModal() {
      modal.hidden = true;
      clearPressedBadges(null);
    }
    modal.querySelector('.chit-modal__close')?.addEventListener('click', closeModal);
    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeModal();
    });
  }

  var feedbackForm = document.getElementById('chit-parent-feedback');
  if (feedbackForm) {
    var statusEl = document.getElementById('chit-feedback-status');
    var submitBtn = document.getElementById('chit-feedback-submit');
    var messageEl = document.getElementById('chit-feedback-message');
    var childEl = document.getElementById('chit-feedback-child');
    var token = feedbackForm.getAttribute('data-token') || '';

    function setStatus(text, ok) {
      if (!statusEl) return;
      statusEl.hidden = !text;
      statusEl.textContent = text || '';
      statusEl.classList.toggle('is-ok', !!ok);
      statusEl.classList.toggle('is-err', !!text && !ok);
    }

    feedbackForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var message = (messageEl && messageEl.value || '').trim();
      if (message.length < 5) {
        setStatus('Напишите вопрос чуть подробнее (хотя бы несколько слов).', false);
        if (messageEl) messageEl.focus();
        return;
      }
      if (!token) {
        setStatus('Не удалось отправить: обновите страницу.', false);
        return;
      }
      if (submitBtn) submitBtn.disabled = true;
      setStatus('Отправляем…', true);

      fetch('/progress/' + encodeURIComponent(token) + '/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          message: message,
          child_name: childEl ? (childEl.value || '') : '',
        }),
      })
        .then(function (res) {
          return res.json().then(function (data) {
            return { ok: res.ok, status: res.status, data: data };
          }).catch(function () {
            return { ok: res.ok, status: res.status, data: {} };
          });
        })
        .then(function (result) {
          if (!result.ok) {
            var detail = (result.data && (result.data.detail || result.data.message)) || '';
            if (Array.isArray(detail)) detail = detail.map(function (d) { return d.msg || d; }).join(' ');
            setStatus(detail || 'Не удалось отправить. Попробуйте позже или напишите на info@chitatelstvo.ru', false);
            return;
          }
          setStatus('Отправлено. Мы ответим на почту, которую указывали при записи.', true);
          if (messageEl) messageEl.value = '';
        })
        .catch(function () {
          setStatus('Сеть недоступна. Попробуйте позже или напишите на info@chitatelstvo.ru', false);
        })
        .finally(function () {
          if (submitBtn) submitBtn.disabled = false;
        });
    });
  }
})();
