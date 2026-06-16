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

  document.querySelectorAll('[data-chest-open]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (btn.disabled) return;
      var panel = btn.closest('.chit-panel--chest');
      if (!panel) return;
      panel.classList.add('is-opened');
      var reveal = panel.querySelector('.chit-chest-reveal');
      if (reveal) reveal.hidden = false;
      btn.textContent = 'Забрать награду';
      btn.disabled = true;
    });
  });

  var modal = document.getElementById('badge-modal');
  var titleEl = document.getElementById('badge-modal-title');
  var textEl = document.getElementById('badge-modal-text');

  document.querySelectorAll('[data-badge-name]').forEach(function (card) {
    card.addEventListener('click', function () {
      if (!modal) return;
      titleEl.textContent = card.getAttribute('data-badge-name') || '';
      textEl.textContent = card.getAttribute('data-badge-condition') || '';
      modal.hidden = false;
    });
  });

  if (modal) {
    modal.querySelector('.chit-modal__close')?.addEventListener('click', function () {
      modal.hidden = true;
    });
    modal.addEventListener('click', function (e) {
      if (e.target === modal) modal.hidden = true;
    });
  }
})();
