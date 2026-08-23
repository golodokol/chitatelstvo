(function () {
  var ROOT_IDS = ['chit-course-root', 'chit-course-lite'];

  function getRoot() {
    for (var i = 0; i < ROOT_IDS.length; i++) {
      var el = document.getElementById(ROOT_IDS[i]);
      if (el) return el;
    }
    return null;
  }

  function setImp(el, props) {
    if (!el) return;
    Object.keys(props).forEach(function (k) {
      if (props[k] != null) el.style.setProperty(k, props[k], 'important');
    });
  }

  function patchRecStyles(rec) {
    if (!rec) return;
    rec.querySelectorAll('style').forEach(function (s) {
      var t = s.textContent || '';
      if (t.indexOf('t396__artboard') < 0 && t.indexOf('tn-elem') < 0) return;
      var n = t
        .replace(/left:\s*calc\([^)]+\)/gi, 'left:0')
        .replace(/width:\s*(?:1200|960|640|480|320)px/gi, 'width:100%')
        .replace(/height:\s*35000px/gi, 'height:auto')
        .replace(/height:\s*100vh/gi, 'height:auto')
        .replace(/display:\s*table/gi, 'display:block');
      if (n !== t) s.textContent = n;
    });
  }

  function syncTildaLayout() {
    var m = getRoot();
    if (!m) return;

    var rec = m.closest('.t-rec');
    patchRecStyles(rec);

    if (rec) {
      setImp(rec, {
        width: '100%',
        'max-width': '100%',
        height: 'auto',
        'max-height': 'none',
        overflow: 'visible',
        'padding-top': '0',
        'margin-top': '0'
      });
    }

    var chain = [
      m.closest('.t396'),
      m.closest('.t396__artboard'),
      m.closest('.tn-elem'),
      m.closest('.tn-atom'),
      m.closest('.tn-atom__html'),
      m
    ];

    chain.forEach(function (el) {
      if (!el) return;
      setImp(el, {
        display: 'block',
        position: 'relative',
        left: '0',
        top: '0',
        width: '100%',
        'max-width': '100%',
        'min-width': '0',
        transform: 'none',
        'min-height': '0',
        'max-height': 'none',
        overflow: 'visible',
        height: 'auto'
      });
    });

    ['.t396__carrier', '.t396__filter'].forEach(function (sel) {
      var el = rec && rec.querySelector(sel);
      if (!el) return;
      setImp(el, {
        height: '0',
        'max-height': '0',
        overflow: 'hidden',
        position: 'absolute',
        left: '0',
        top: '0',
        width: '100%',
        'pointer-events': 'none'
      });
    });

    var h = Math.ceil(m.getBoundingClientRect().height);
    if (h > 0) {
      var ab = m.closest('.t396__artboard');
      if (ab) {
        setImp(ab, { height: h + 'px' });
        ab.setAttribute('data-artboard-height', String(h));
      }
    }
  }

  window.chitSyncTildaLayout = syncTildaLayout;

  function hookT396() {
    if (window._chitCourseT396Hook) return;
    var orig = window.t396_init;
    if (typeof orig !== 'function') return;
    window._chitCourseT396Hook = 1;
    window.t396_init = function () {
      var out = orig.apply(this, arguments);
      syncTildaLayout();
      setTimeout(syncTildaLayout, 50);
      return out;
    };
  }

  syncTildaLayout();
  hookT396();
  setTimeout(syncTildaLayout, 80);
  setTimeout(syncTildaLayout, 300);
  setTimeout(syncTildaLayout, 1200);
  window.addEventListener('load', syncTildaLayout);

  var n = 0;
  var poll = setInterval(function () {
    syncTildaLayout();
    hookT396();
    if (++n > 80) clearInterval(poll);
  }, 250);

  var root = getRoot();
  if (root && window.ResizeObserver) {
    new ResizeObserver(syncTildaLayout).observe(root);
  }
})();
