(function () {
  if (window.__chitQzFit) return;
  window.__chitQzFit = 1;
  var css = document.createElement('style');
  css.id = 'chit-qz-fit';
  css.textContent =
    '@media(max-width:720px){' +
    '#qz-modal.is-open .qz-logo,#qz-modal.is-open .qz-intro-gift,#qz-modal.is-open #qz-questions .qz-sub{display:none!important;height:0!important;margin:0!important;padding:0!important;overflow:hidden!important;border:0!important}' +
    '#qz-modal.is-open .qz-card{padding-bottom:88px!important}' +
    '#qz-modal.is-open .qz-btn--next{position:fixed!important;left:16px!important;right:16px!important;bottom:calc(12px + env(safe-area-inset-bottom,0px))!important;z-index:10070!important;width:auto!important;max-width:none!important}' +
    '#qz-modal.is-open .qz-btn--back{position:fixed!important;left:16px!important;bottom:calc(64px + env(safe-area-inset-bottom,0px))!important;z-index:10070!important}' +
    '}';
  (document.documentElement || document.body).appendChild(css);

  function phone() {
    return (window.innerWidth || 0) <= 720;
  }
  function hideIntro() {
    if (!phone()) return;
    var modal = document.getElementById('qz-modal');
    if (!modal || !modal.classList.contains('is-open')) return;
    var logo = modal.querySelector('.qz-logo');
    var gift = modal.querySelector('.qz-intro-gift');
    if (logo) logo.style.setProperty('display', 'none', 'important');
    if (gift) gift.style.setProperty('display', 'none', 'important');
    var subs = modal.querySelectorAll('#qz-questions .qz-sub');
    var i;
    for (i = 0; i !== subs.length; i += 1) {
      subs[i].style.setProperty('display', 'none', 'important');
    }
  }
  setInterval(hideIntro, 300);

  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var opt = t.closest('#qz-modal .qz-option');
    if (!opt) return;
    if (!phone()) return;
    hideIntro();
    setTimeout(function () {
      var step = opt.closest('.qz-step');
      var next = step && step.querySelector('.qz-btn--next');
      if (next && !next.disabled) next.click();
    }, 80);
  }, true);
})();
