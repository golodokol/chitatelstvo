/**
 * chitatelstvo.ru/oplata — вставить в HTML-блок на странице оплаты:
 * <script src="https://api.chitatelstvo.ru/assets/chit-pay-page.js?v=7"></script>
 */
(function () {
  var STORAGE_KEY = 'chit_checkout';
  var ST100_RECID = '2379461281';

  function resolveSt100Recid() {
    var rec = document.querySelector('#allrecords .t-rec[data-record-type="706"], .t-rec[data-record-type="706"]');
    if (rec && rec.id && rec.id.indexOf('rec') === 0) {
      return rec.id.slice(3);
    }
    return ST100_RECID;
  }

  function getSt100Root() {
    var recid = resolveSt100Recid();
    return document.getElementById('rec' + recid) || document.querySelector('.t706') || document.body;
  }

  function promoControlsAvailable() {
    return !!findPromoControls();
  }
  var HOME_URL = 'https://chitatelstvo.ru/#program';
  var STORE_REC_TYPES = ['762', '205', '200', '210', '215', '405'];
  var ORDER_PRODUCTS = {
    single: { uid: '797131986522', lid: '863983274147', sku: 'SKU0001-2', title: 'Читательство · Разовое', price: 1490 },
    self_paced: { uid: '206548598642', lid: '205285061796', sku: 'SKU0002', title: 'Читательство · Индивидуальное', price: 1990 },
    with_teacher: { uid: '956231952022', lid: '776534181255', sku: 'SKU0003', title: 'Читательство · С преподавателем', price: 4990 },
    meeting_addon: { uid: '168614126213', lid: '168614126213', sku: 'SKU0004', title: 'Читательство · Занятие с преподавателем', price: 799 }
  };

  var PAY_CSS = [
    'html.chit-pay-mode, body.chit-pay-mode { background:#F6F4F9 !important; }',
    'body.chit-pay-mode #allrecords .t-rec[data-record-type="762"],',
    'body.chit-pay-mode #allrecords .t-rec[data-record-type="205"],',
    'body.chit-pay-mode #allrecords .t-rec[data-record-type="200"],',
    'body.chit-pay-mode #allrecords .t-rec[data-record-type="210"],',
    'body.chit-pay-mode #allrecords .t-rec[data-record-type="215"],',
    'body.chit-pay-mode #allrecords .t-rec[data-record-type="405"],',
    'body.chit-pay-mode #allrecords .chit-pay-hidden,',
    'body.chit-pay-mode #allrecords .t-store {',
    'display:none!important;height:0!important;max-height:0!important;',
    'overflow:hidden!important;visibility:hidden!important;opacity:0!important;',
    'pointer-events:none!important;position:absolute!important;left:-99999px!important;',
    '}',
    'body.chit-pay-mode .t706__carticon { opacity:0!important;pointer-events:none!important; }',
    '#chit-pay-shell {',
    'position:fixed;inset:0;z-index:9998;display:flex;align-items:center;justify-content:center;',
    'background:#F6F4F9;font-family:Nunito,system-ui,sans-serif;color:#2B2140;',
    '}',
    '#chit-pay-shell__box { text-align:center;padding:32px 24px;max-width:360px; }',
    '#chit-pay-shell__title { font-size:22px;font-weight:800;margin:0 0 8px; }',
    '#chit-pay-shell__text { font-size:15px;line-height:1.5;margin:0;color:#5E5670; }'
  ].join('');

  function injectPayStyles() {
    if (document.getElementById('chit-pay-hide')) return;
    var style = document.createElement('style');
    style.id = 'chit-pay-hide';
    style.textContent = PAY_CSS;
    (document.head || document.documentElement).appendChild(style);
    document.documentElement.classList.add('chit-pay-mode');
    if (document.body) document.body.classList.add('chit-pay-mode');
  }

  injectPayStyles();
  document.addEventListener('DOMContentLoaded', function () {
    document.documentElement.classList.add('chit-pay-mode');
    document.body.classList.add('chit-pay-mode');
  });

  function hideStoreRec(rec) {
    if (!rec || rec.getAttribute('data-record-type') === '706') return;
    if (rec.querySelector('.t706') && !rec.querySelector('.js-store-product, .t-store__card-one')) return;
    rec.classList.add('chit-pay-hidden');
    rec.setAttribute('aria-hidden', 'true');
    rec.style.setProperty('display', 'none', 'important');
    rec.style.setProperty('position', 'absolute', 'important');
    rec.style.setProperty('left', '-99999px', 'important');
    rec.style.setProperty('height', '0', 'important');
    rec.style.setProperty('overflow', 'hidden', 'important');
    rec.style.setProperty('visibility', 'hidden', 'important');
    rec.style.setProperty('opacity', '0', 'important');
    rec.style.setProperty('pointer-events', 'none', 'important');
  }

  function isStoreRec(rec) {
    if (!rec || !rec.classList.contains('t-rec')) return false;
    if (rec.getAttribute('data-record-type') === '706') return false;
    var recType = rec.getAttribute('data-record-type');
    if (recType && STORE_REC_TYPES.indexOf(recType) >= 0) return true;
    if (rec.querySelector('.js-store-product, .js-product[data-product-gen-uid], .t-store__card-one, .t-store')) return true;
    var text = rec.textContent || '';
    return /SKU0001|SKU0002|SKU0003|SKU0004/i.test(text) && /Артикул/i.test(text);
  }

  function hideStoreBlocks() {
    document.querySelectorAll('#allrecords .t-rec, .t-rec').forEach(function (rec) {
      if (isStoreRec(rec)) hideStoreRec(rec);
    });
    document.querySelectorAll('.t-store, .t-store__prod-popup').forEach(hideStoreRec);
  }

  function watchStoreBlocks() {
    hideStoreBlocks();
    var root = document.getElementById('allrecords') || document.body;
    if (root._chitPayWatch) return;
    root._chitPayWatch = true;
    new MutationObserver(hideStoreBlocks).observe(root, { childList: true, subtree: true });
    setInterval(hideStoreBlocks, 400);
  }

  function showPayShell(title, text) {
    if (document.getElementById('chit-pay-shell')) return;
    var shell = document.createElement('div');
    shell.id = 'chit-pay-shell';
    shell.innerHTML =
      '<div id="chit-pay-shell__box">' +
      '<p id="chit-pay-shell__title">' + (title || 'Оплата') + '</p>' +
      '<p id="chit-pay-shell__text">' + (text || 'Открываем корзину…') + '</p>' +
      '</div>';
    (document.body || document.documentElement).appendChild(shell);
  }

  function hidePayShell() {
    var shell = document.getElementById('chit-pay-shell');
    if (shell) shell.remove();
    document.querySelectorAll('.t706__carticon').forEach(function (icon) {
      icon.style.removeProperty('opacity');
      icon.style.removeProperty('pointer-events');
    });
  }

  function cartIsOpen() {
    return !!document.querySelector('.t706__cartwin_showed, .t706__cartwin_active, .t706__cartwin-wrapper_showed');
  }

  function readCheckoutFromUrl() {
    try {
      var params = new URLSearchParams(window.location.search);
      var tariff = params.get('tariff');
      if (!tariff || !ORDER_PRODUCTS[tariff]) return null;
      var data = { tariff: tariff };
      [
        'module_id', 'chosen_stage', 'chosen_tale_number', 'lesson_slug',
        'group_code', 'group', 'parent_name', 'parent_email', 'parent_telegram',
        'child_name', 'child_birth_date', 'child_age', 'promo_code', 'notification_channel'
      ].forEach(function (name) {
        var val = params.get(name);
        if (val !== null && val !== '') data[name] = val;
      });
      if (data.group && !data.group_code) data.group_code = data.group;
      if (data.group_code && !data.group) data.group = data.group_code;
      return data;
    } catch (e) {
      return null;
    }
  }

  function readCheckout() {
    try {
      var raw = sessionStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) {}
    var fromUrl = readCheckoutFromUrl();
    if (fromUrl) {
      try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(fromUrl)); } catch (e2) {}
    }
    return fromUrl;
  }

  function setField(name, value) {
    if (value === undefined || value === null) return;
    var v = String(value);
    var aliases = {
      parent_name: ['parent_name', 'Name', 'name', 'nm'],
      parent_email: ['parent_email', 'Email', 'email'],
      parent_telegram: ['parent_telegram', 'Phone', 'phone', 'tel'],
      child_name: ['child_name'],
      child_birth_date: ['child_birth_date', 'birth_date'],
      child_age: ['child_age'],
      promo_code: ['promo_code', 'promocode', 'promo'],
      notification_channel: ['notification_channel'],
      module_id: ['module_id'],
      chosen_stage: ['chosen_stage', 'stage'],
      chosen_tale_number: ['chosen_tale_number', 'tale'],
      lesson_slug: ['lesson_slug'],
      group_code: ['group_code', 'group']
    };
    var names = aliases[name] || [name];
    names.forEach(function (fieldName) {
      document.querySelectorAll(
        '.t706 input[name="' + fieldName + '"], .t706 textarea[name="' + fieldName + '"], .t706 select[name="' + fieldName + '"], form[data-formcart="y"] [name="' + fieldName + '"]'
      ).forEach(function (el) {
        el.value = v;
        try { el.dispatchEvent(new Event('input', { bubbles: true })); } catch (err) {}
        try { el.dispatchEvent(new Event('change', { bubbles: true })); } catch (err) {}
      });
    });
  }

  function waitFor(fn, cb, attempt) {
    if (fn()) { cb(); return; }
    if ((attempt || 0) >= 50) return;
    setTimeout(function () { waitFor(fn, cb, (attempt || 0) + 1); }, 200);
  }

  function resetTcartPromoState() {
    if (!window.tcart) return;
    delete window.tcart.promocode;
    delete window.tcart.prodamount_withdiscount;
    delete window.tcart.prodamount_discountsum;
  }

  function clearTcart() {
    if (!window.tcart) window.tcart = { products: [], amount: 0, total: 0, prodamount: 0 };
    window.tcart.products = [];
    window.tcart.amount = 0;
    window.tcart.total = 0;
    window.tcart.prodamount = 0;
    resetTcartPromoState();
  }

  function refreshTcartTotals() {
    if (typeof window.tcart__updateTotalProductsinCartObj === 'function') {
      window.tcart__updateTotalProductsinCartObj();
    }
    if (typeof window.tcart__calcPromocode === 'function' && window.tcart && typeof window.tcart.amount === 'number') {
      window.tcart.amount = window.tcart__calcPromocode(window.tcart.amount);
    }
    if (typeof window.tcart__reDrawTotal === 'function') {
      window.tcart__reDrawTotal();
    }
    if (typeof window.tcart__reDrawProducts === 'function') {
      window.tcart__reDrawProducts();
    }
    if (typeof window.tcart__saveLocalObj === 'function') {
      window.tcart__saveLocalObj();
    }
  }

  function addProduct(tariff) {
    var p = ORDER_PRODUCTS[tariff];
    if (!p || typeof window.tcart__addProduct !== 'function') return false;
    clearTcart();
    window.tcart__addProduct({
      name: p.title,
      price: p.price,
      amount: p.price,
      quantity: 1,
      recid: resolveSt100Recid(),
      sku: p.sku || '',
      uid: p.uid,
      lid: p.lid || p.uid
    });
    refreshTcartTotals();
    return !!(window.tcart.products && window.tcart.products.length);
  }

  function triggerUidHash(uid) {
    var root = getSt100Root();
    var link = document.createElement('a');
    link.href = '#order:::uid=' + uid;
    link.style.cssText = 'position:absolute;left:-9999px;width:1px;height:1px;opacity:0;';
    root.appendChild(link);
    link.click();
    root.removeChild(link);
    try { window.dispatchEvent(new HashChangeEvent('hashchange')); } catch (e) { window.dispatchEvent(new Event('hashchange')); }
  }

  function findPromoControls() {
    var input = document.querySelector('.t706 .t-inputpromocode, .t706__orderform .t-inputpromocode, .t706__cartwin .t-inputpromocode');
    if (!input) return null;
    var wrapper = input.closest('.t-inputpromocode__wrapper');
    var btn = wrapper
      ? wrapper.querySelector('.t-inputpromocode__btn')
      : document.querySelector('.t706 .t-inputpromocode__btn');
    return btn ? { input: input, btn: btn } : null;
  }

  function promoAppliedOk(code) {
    code = String(code || '').trim();
    if (!code || !window.tcart || typeof window.tcart.promocode !== 'object') return !code;
    var promo = window.tcart.promocode;
    if (promo.message !== 'OK') return false;
    return String(promo.code || promo.promocode || '').trim().toLowerCase() === code.toLowerCase();
  }

  function applyPromoCode(code, cb) {
    code = String(code || '').trim();
    if (!code) {
      if (cb) cb(true);
      return;
    }
    if (promoAppliedOk(code)) {
      refreshTcartTotals();
      if (cb) cb(true);
      return;
    }
    var controls = findPromoControls();
    if (!controls) {
      if (cb) cb(false);
      return;
    }
    setField('promo_code', code);
    controls.input.value = code;
    controls.btn.style.display = 'table-cell';
    try { controls.input.dispatchEvent(new Event('input', { bubbles: true })); } catch (e) {}
    try { controls.input.dispatchEvent(new Event('change', { bubbles: true })); } catch (e) {}
    try { controls.btn.click(); } catch (e) {}

    var attempts = 0;
    (function poll() {
      attempts += 1;
      refreshTcartTotals();
      if (promoAppliedOk(code)) {
        if (cb) cb(true);
        return;
      }
      if (window.tcart && window.tcart.promocode && window.tcart.promocode.message && window.tcart.promocode.message !== 'OK') {
        if (cb) cb(false);
        return;
      }
      if (attempts >= 35) {
        if (cb) cb(false);
        return;
      }
      setTimeout(poll, 200);
    })();
  }

  function openCart() {
    hideStoreBlocks();
    refreshTcartTotals();
    if (typeof window.tcart__openCart === 'function') window.tcart__openCart();
    else {
      var icon = document.querySelector('.t706__carticon');
      if (icon) icon.click();
    }
    setTimeout(function () {
      if (cartIsOpen()) hidePayShell();
    }, 300);
    setTimeout(hidePayShell, 2500);
  }

  function runCheckout() {
    var data = readCheckout();
    if (!data || !data.tariff || !ORDER_PRODUCTS[data.tariff]) {
      showPayShell('Запись на занятие', 'Сначала заполните форму на главной странице.');
      setTimeout(function () { window.location.href = HOME_URL; }, 2200);
      return;
    }

    showPayShell('Оплата', data.promo_code ? 'Проверяем промокод…' : 'Открываем корзину…');
    watchStoreBlocks();

    waitFor(function () {
      return typeof window.tcart__addProduct === 'function' && document.querySelector('.t706');
    }, function () {
      if (!data.notification_channel) data.notification_channel = 'email';
      ['module_id', 'chosen_stage', 'chosen_tale_number', 'lesson_slug', 'group_code', 'parent_name', 'parent_email', 'parent_telegram', 'child_name', 'child_birth_date', 'child_age', 'promo_code', 'notification_channel'].forEach(function (name) {
        setField(name, data[name]);
      });

      var uid = ORDER_PRODUCTS[data.tariff].uid;
      var tries = 0;

      function finishCheckout() {
        if (data.promo_code && !promoControlsAvailable()) {
          showPayShell(
            'Промокод не применился',
            'В блоке ST100 на странице /oplata не включены промокоды. Tilda → ST100 → Настройки → «Промокоды». Оплата откроется по полной цене.'
          );
        }
        applyPromoCode(data.promo_code, function (ok) {
          refreshTcartTotals();
          openCart();
          if (data.promo_code && !ok && promoControlsAvailable()) {
            showPayShell('Промокод', 'Код не принят — проверьте написание или срок действия в Tilda.');
            setTimeout(hidePayShell, 3500);
          }
          if (data.promo_code) {
            [500, 1400].forEach(function (ms) {
              setTimeout(function () {
                applyPromoCode(data.promo_code, refreshTcartTotals);
              }, ms);
            });
          }
        });
      }

      function tryOpen() {
        hideStoreBlocks();
        if (!addProduct(data.tariff)) triggerUidHash(uid);
        tries += 1;
        if ((window.tcart && window.tcart.products && window.tcart.products.length) || tries >= 8) {
          finishCheckout();
          return;
        }
        setTimeout(tryOpen, 400);
      }

      tryOpen();
    });
  }

  watchStoreBlocks();

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runCheckout);
  } else {
    runCheckout();
  }
})();
