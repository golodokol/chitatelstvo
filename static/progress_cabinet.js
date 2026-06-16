(function () {
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

  document.querySelectorAll('.chit-level-step[data-level-info]').forEach(function (step) {
    step.addEventListener('click', function () {
      var info = step.getAttribute('data-level-info');
      if (info) step.setAttribute('title', info);
    });
  });
})();
