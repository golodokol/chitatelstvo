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

  function showSlovikToast(url, message) {
    var toast = document.getElementById('slovik-toast');
    if (!toast || !url) return;
    var img = toast.querySelector('.chit-slovik-toast__img');
    var text = toast.querySelector('.chit-slovik-toast__text');
    if (img) img.src = url;
    if (text) text.textContent = message || '';
    toast.hidden = false;
    toast.classList.add('is-visible');
    clearTimeout(showSlovikToast._timer);
    showSlovikToast._timer = setTimeout(function () {
      toast.classList.remove('is-visible');
      setTimeout(function () { toast.hidden = true; }, 300);
    }, 4200);
  }

  document.querySelectorAll('.chit-room-toast-data').forEach(function (node) {
    try {
      var data = JSON.parse(node.textContent || '');
      if (!data || !data.toast_id) return;
      var key = 'chit-slovik-toast-' + data.toast_id;
      if (sessionStorage.getItem(key)) return;
      sessionStorage.setItem(key, '1');
      showSlovikToast(data.url, data.message);
    } catch (e) {}
  });

  document.querySelectorAll('[data-chest-open]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (btn.disabled) return;
      var panel = btn.closest('.chit-panel--chest');
      if (!panel) return;
      panel.classList.add('is-opened');
      var reveal = panel.querySelector('.chit-chest-reveal');
      if (reveal) reveal.hidden = false;
      var victoryUrl = panel.getAttribute('data-chest-victory');
      var chestImg = panel.querySelector('[data-chest-slovik-img]');
      if (chestImg && victoryUrl) chestImg.src = victoryUrl;
      showSlovikToast(victoryUrl || '/static/sloviki/slovik-victory.png', 'Сундук открыт! Новая награда ждёт в уроке.');
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
