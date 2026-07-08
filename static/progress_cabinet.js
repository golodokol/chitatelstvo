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
})();
