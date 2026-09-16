(function () {
  if (window.__chitQzPhone) return;
  window.__chitQzPhone = 1;
  var A = 'https://api.chitatelstvo.ru/assets/';
  var V = '20260909e';
  if (!document.querySelector('link[href*="chit-qz-phone.css"]')) {
    var l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = A + 'chit-qz-phone.css?v=' + V;
    (document.head || document.documentElement).appendChild(l);
  }
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var opt = t.closest('#qz-modal .qz-option');
    if (!opt) return;
    if ((window.innerWidth || 0) > 720) return;
    setTimeout(function () {
      var step = opt.closest('.qz-step');
      var next = step && step.querySelector('.qz-btn--next');
      if (next && !next.disabled) next.click();
    }, 40);
  });
})();
