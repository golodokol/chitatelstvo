/**
 * chitatelstvo.ru/oplata — вставить в HTML-блок на странице оплаты (один раз):
 * <script src="https://api.chitatelstvo.ru/assets/chit-pay-page.js?v=24"></script>
 * Важно: только ОДИН HTML-блок со скриптом на странице /oplata (удалить старые v=6, v=16).
 */
(function () {
  if (window._chitPayPageInited) return;
  window._chitPayPageInited = true;

  var STORAGE_KEY = 'chit_checkout';
  var ST100_RECID = '2380214471';
  var payShellTimer = null;
  var safetyTimer = null;
  var checkoutStarted = false;
  var checkoutFinished = false;

  var HOME_URL = 'https://chitatelstvo.ru/#program';
  var ORDER_PRODUCTS = {
    single: { uid: '797131986522', lid: '863983274147', sku: 'SKU0001-2', title: 'Читательство · Разовое', price: 799 },
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
    'body.chit-pay-mode #allrecords .t-store {',
    'display:none!important;visibility:hidden!important;height:0!important;overflow:hidden!important;',
    '}',
    'body.chit-pay-mode .t706__carticon { opacity:0!important;pointer-events:none!important; }',
    'body.chit-pay-mode .t706 .t-input-group_pc .chit-promo-label {',
    'display:block;margin:0 0 8px;font-size:16px;line-height:1.3;color:#000;',
    '}',
    '#chit-pay-shell {',
    'position:fixed;inset:0;z-index:9998;display:flex;align-items:center;justify-content:center;',
    'background:rgba(246,244,249,0.92);font-family:Nunito,system-ui,sans-serif;color:#2B2140;',
    'pointer-events:none;',
    '}',
    '#chit-pay-shell__box { text-align:center;padding:32px 24px;max-width:360px; }',
    '#chit-pay-shell__title { font-size:22px;font-weight:800;margin:0 0 8px; }',
    '#chit-pay-shell__text { font-size:15px;line-height:1.5;margin:0;color:#5E5670; }'
  ].join('');

  function ageFromBirthDate(isoDate) {
    if (!isoDate) return '';
    var parts = String(isoDate).split('-');
    if (parts.length !== 3) return '';
    var birth = new Date(+parts[0], +parts[1] - 1, +parts[2]);
    if (isNaN(birth.getTime())) return '';
    var today = new Date();
    var age = today.getFullYear() - birth.getFullYear();
    var m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age -= 1;
    return age >= 0 ? String(age) : '';
  }

  function birthDateToDmy(isoDate) {
    if (!isoDate) return '';
    var p = String(isoDate).split('-');
    if (p.length !== 3) return String(isoDate);
    return p[2] + '.' + p[1] + '.' + p[0];
  }

  function sanitizeTelegram(value) {
    if (value === undefined || value === null) return value;
    var v = String(value).trim().replace(/["']/g, '').replace(/\s+/g, ' ');
    var digits = v.replace(/\D/g, '');
    if (digits.length === 11 && (digits.charAt(0) === '7' || digits.charAt(0) === '8')) {
      return '+7' + digits.slice(-10);
    }
    return v;
  }

  function normalizeCheckout(data) {
    if (!data) return data;
    if (data.parent_telegram) data.parent_telegram = sanitizeTelegram(data.parent_telegram);
    if (data.child_birth_date && !data.child_age) {
      data.child_age = ageFromBirthDate(data.child_birth_date);
    }
    return data;
  }

  function resolveSt100Recid() {
    var rec = document.querySelector('.t-rec[data-record-type="706"]');
    if (rec && rec.id && rec.id.indexOf('rec') === 0) return rec.id.slice(3);
    return ST100_RECID;
  }

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

  function showPayShell(title, text) {
    var shell = document.getElementById('chit-pay-shell');
    if (!shell) {
      shell = document.createElement('div');
      shell.id = 'chit-pay-shell';
      shell.innerHTML =
        '<div id="chit-pay-shell__box"><p id="chit-pay-shell__title"></p><p id="chit-pay-shell__text"></p></div>';
      (document.body || document.documentElement).appendChild(shell);
    }
    var t = document.getElementById('chit-pay-shell__title');
    var x = document.getElementById('chit-pay-shell__text');
    if (t) t.textContent = title || 'Оплата';
    if (x) x.textContent = text || 'Открываем корзину…';
    if (payShellTimer) clearTimeout(payShellTimer);
    payShellTimer = setTimeout(hidePayShell, 4000);
  }

  function hidePayShell() {
    if (payShellTimer) { clearTimeout(payShellTimer); payShellTimer = null; }
    var shell = document.getElementById('chit-pay-shell');
    if (shell) shell.remove();
  }

  function resolveTariffFromParams(params) {
    var tariff = params.get('tariff');
    if (tariff && ORDER_PRODUCTS[tariff]) return tariff;
    var keys = [];
    params.forEach(function (val, key) { keys.push(key); });
    for (var i = 0; i < keys.length; i++) {
      var key = keys[i];
      if (key.indexOf('tariff-') === 0) {
        var t = key.slice(7);
        if (ORDER_PRODUCTS[t]) return t;
      }
    }
    var raw = window.location.search || '';
    var m = raw.match(/(?:\?|&)tariff-([a-z_]+)(?:&|$)/i);
    if (m && ORDER_PRODUCTS[m[1]]) return m[1];
    return null;
  }

  function readCheckoutFromUrl() {
    try {
      var params = new URLSearchParams(window.location.search);
      var tariff = resolveTariffFromParams(params);
      if (!tariff) return null;
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
    } catch (e) { return null; }
  }

  function readCheckout() {
    try {
      var raw = sessionStorage.getItem(STORAGE_KEY);
      if (raw) return normalizeCheckout(JSON.parse(raw));
    } catch (e) {}
    var fromUrl = readCheckoutFromUrl();
    if (fromUrl) {
      fromUrl = normalizeCheckout(fromUrl);
      try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(fromUrl)); } catch (e2) {}
    }
    return fromUrl;
  }

  function setField(name, value) {
    if (value === undefined || value === null) return;
    var v = String(value);
    var aliases = {
      parent_name: ['parent_name'],
      parent_email: ['parent_email', 'email', 'Email'],
      parent_telegram: ['parent_telegram'],
      child_name: ['child_name'],
      child_birth_date: ['child_birth_date'],
      child_age: ['child_age'],
      promo_code: ['promo_code'],
      notification_channel: ['notification_channel'],
      module_id: ['module_id'],
      chosen_stage: ['chosen_stage'],
      chosen_tale_number: ['chosen_tale_number'],
      lesson_slug: ['lesson_slug'],
      group_code: ['group_code', 'group']
    };
    var names = aliases[name] || [name];
    var values = name === 'child_birth_date' ? [v, birthDateToDmy(v)] : [v];
    names.forEach(function (fieldName) {
      values.forEach(function (fieldValue) {
        document.querySelectorAll(
          '.t706 [name="' + fieldName + '"], form[data-formcart="y"] [name="' + fieldName + '"]'
        ).forEach(function (el) {
          if (el.type === 'checkbox' || el.type === 'radio') return;
          el.value = fieldValue;
        });
      });
    });
  }

  function ensureLegalConsent() {
    document.querySelectorAll('.t706 input[name="legal_consent"]').forEach(function (el) {
      if (el.type === 'checkbox') el.checked = true;
      else if (!el.value) el.value = 'yes';
    });
  }

  function configurePromoField(data) {
    document.querySelectorAll('.t706 .t-input-group_pc').forEach(function (group) {
      if (group.getAttribute('data-chit-promo-ui')) return;
      group.setAttribute('data-chit-promo-ui', '1');
      if (!group.querySelector('.t-input-title')) {
        var label = document.createElement('div');
        label.className = 't-input-title t-descr t-descr_md chit-promo-label';
        label.textContent = 'Промокод';
        var block = group.querySelector('.t-input-block');
        if (block) block.insertAdjacentElement('beforebegin', label);
      }
      var input = group.querySelector('.t-inputpromocode');
      if (input) {
        input.setAttribute('placeholder', 'Промокод');
        input.setAttribute('aria-label', 'Промокод');
      }
      var btn = group.querySelector('.t-inputpromocode__btn');
      if (btn && !btn.textContent.trim()) btn.textContent = 'Применить';
    });
    var code = data && String(data.promo_code || '').trim();
    if (!code) return;
    setField('promo_code', code);
    var input = document.querySelector('.t706 .t-inputpromocode');
    var btn = document.querySelector('.t706 .t-inputpromocode__btn');
    if (input) input.value = code;
    if (btn) btn.style.display = 'table-cell';
  }

  function fixFormLayout() {
    var root = document.querySelector('.t706');
    if (!root) return;
    var success = root.querySelector('.js-successbox');
    if (success) {
      success.style.display = 'none';
      success.textContent = '';
    }
    ['.t706__orderform', '.t-form__inputsbox', '.t706__cartwin-products', '.t706__cartwin-bottom'].forEach(function (sel) {
      var el = root.querySelector(sel);
      if (!el) return;
      el.style.removeProperty('display');
      el.style.removeProperty('height');
      el.style.removeProperty('overflow');
    });
  }

  function applyCheckoutFields(data) {
    if (!data) return;
    normalizeCheckout(data);
    if (!data.notification_channel) data.notification_channel = 'email';
    [
      'module_id', 'chosen_stage', 'chosen_tale_number', 'lesson_slug', 'group_code',
      'parent_name', 'parent_email', 'parent_telegram', 'child_name',
      'child_birth_date', 'child_age', 'promo_code', 'notification_channel'
    ].forEach(function (name) { setField(name, data[name]); });
    mirrorEmailForKassa(data);
    ensureLegalConsent();
    configurePromoField(data);
    fixFormLayout();
  }

  function syncPaymentSystem() {
    var checked = document.querySelector('.t706 .t-radio_payment[name="paymentsystem"]:checked');
    if (!checked) return;
    var system = checked.getAttribute('data-payment-variant-system') || checked.value || '';
    var root = document.querySelector('.t706');
    if (root && system) {
      root.setAttribute('data-payment-variant-system', system);
      root.setAttribute('data-payment-system', system);
    }
    if (!window.tcart) window.tcart = { products: [], amount: 0, total: 0, prodamount: 0 };
    if (system) window.tcart.system = system;
  }

  function mirrorEmailForKassa(data) {
    if (!data || !data.parent_email) return;
    var email = String(data.parent_email).trim();
    if (!email) return;
    document.querySelectorAll('.t706 .t-input-group_em input[type="email"]').forEach(function (el) {
      if (!el.value) el.value = email;
    });
  }

  function clearTcart() {
    try { window.localStorage.removeItem('tcart'); } catch (e) {}
    if (!window.tcart) window.tcart = { products: [], amount: 0, total: 0, prodamount: 0 };
    window.tcart.products = [];
    window.tcart.amount = 0;
    window.tcart.total = 0;
    window.tcart.prodamount = 0;
    delete window.tcart.promocode;
    window.tcart.updated = Math.floor(Date.now() / 1000);
    if (typeof window.tcart__saveLocalObj === 'function') window.tcart__saveLocalObj();
  }

  function refreshTcartTotals() {
    if (typeof window.tcart__updateTotalProductsinCartObj === 'function') {
      window.tcart__updateTotalProductsinCartObj();
    }
    if (typeof window.tcart__reDrawTotal === 'function') window.tcart__reDrawTotal();
    if (typeof window.tcart__reDrawProducts === 'function') window.tcart__reDrawProducts();
    if (typeof window.tcart__saveLocalObj === 'function') window.tcart__saveLocalObj();
  }

  function addProduct(tariff) {
    var p = ORDER_PRODUCTS[tariff];
    if (!p || typeof window.tcart__addProduct !== 'function') return false;
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
    window.tcart.updated = Math.floor(Date.now() / 1000);
    normalizeCartItem(tariff);
    refreshTcartTotals();
    return !!(window.tcart.products && window.tcart.products.length);
  }

  function triggerUidHash(uid) {
    var root = document.getElementById('rec' + resolveSt100Recid()) || document.querySelector('.t706') || document.body;
    var link = document.createElement('a');
    link.href = '#order:::uid=' + uid;
    link.style.cssText = 'position:absolute;left:-9999px;opacity:0;';
    root.appendChild(link);
    link.click();
    root.removeChild(link);
  }

  function openCartModal() {
    if (typeof window.tcart__openCart === 'function') {
      window.tcart__openCart();
      return;
    }
    var icon = document.querySelector('.t706__carticon');
    if (icon) icon.click();
  }

  function hasActivePromo() {
    return !!(window.tcart && window.tcart.promocode && window.tcart.promocode.message === 'OK');
  }

  function catalogBasePrice(tariff) {
    var p = ORDER_PRODUCTS[tariff];
    return p ? p.price : null;
  }

  function recalcPromoTotals(tariff) {
    if (!window.tcart) return null;
    var base = catalogBasePrice(tariff);
    if (typeof base !== 'number') base = window.tcart.prodamount;
    if (typeof base !== 'number') base = window.tcart.amount;
    if (typeof base !== 'number') return null;
    window.tcart.prodamount = base;
    if (hasActivePromo() && typeof window.tcart__calcPromocode === 'function') {
      window.tcart.total = window.tcart__calcPromocode(base);
      window.tcart.amount = window.tcart.total;
    } else {
      window.tcart.total = base;
      window.tcart.amount = base;
    }
    return window.tcart.total;
  }

  function syncCartForPayment(tariff) {
    if (!window.tcart) return;
    var p = ORDER_PRODUCTS[tariff];
    if (!p) return;
    normalizeCartItem(tariff);
    var total = p.price;
    if (hasActivePromo() && typeof window.tcart__calcPromocode === 'function') {
      total = window.tcart__calcPromocode(p.price);
    }
    var products = window.tcart.products || [];
    if (products.length === 1) {
      var item = products[0];
      item.quantity = 1;
      item.price = total;
      item.amount = total;
      window.tcart.products = [item];
    }
    window.tcart.amount = total;
    window.tcart.total = total;
    window.tcart.prodamount = total;
    window.tcart.updated = Math.floor(Date.now() / 1000);
    syncPaymentSystem();
    if (typeof window.tcart__saveLocalObj === 'function') window.tcart__saveLocalObj();
  }

  function cartReady(tariff) {
    if (!window.tcart || !window.tcart.products || !window.tcart.products.length) return false;
    var p = ORDER_PRODUCTS[tariff];
    if (!p) return false;
    var item = window.tcart.products[0];
    if (String(item.uid) !== String(p.uid)) return false;
    if (parseInt(item.quantity, 10) !== 1) return false;
    if (!hasActivePromo() && parseInt(item.price, 10) !== parseInt(p.price, 10)) return false;
    return true;
  }

  function normalizeCartItem(tariff, options) {
    options = options || {};
    var p = ORDER_PRODUCTS[tariff];
    if (!p || !window.tcart) return;
    var items = (window.tcart.products || []).filter(function (it) {
      return String(it.uid) === String(p.uid);
    });
    if (!items.length) return;
    var item = items[0];
    item.quantity = 1;
    window.tcart.products = [item];
    var keepPricing = options.keepPricing || hasActivePromo();
    if (!keepPricing) {
      item.price = p.price;
      item.amount = p.price;
      window.tcart.amount = p.price;
      window.tcart.prodamount = p.price;
      window.tcart.total = p.price;
    } else {
      item.price = p.price;
      item.amount = p.price;
      recalcPromoTotals(tariff);
    }
    window.tcart.updated = Math.floor(Date.now() / 1000);
    if (typeof window.tcart__saveLocalObj === 'function') window.tcart__saveLocalObj();
  }

  function applyPromoCode(code, cb) {
    code = String(code || '').trim();
    if (!code) { if (cb) cb(); return; }
    var input = document.querySelector('.t706 .t-inputpromocode');
    var btn = document.querySelector('.t706 .t-inputpromocode__btn');
    if (!input || !btn) { if (cb) cb(); return; }
    setField('promo_code', code);
    input.value = code;
    btn.style.display = 'table-cell';
    try { btn.click(); } catch (e) {}
    setTimeout(function () { refreshTcartTotals(); if (cb) cb(); }, 600);
  }

  function bindPayHandlers(tariff) {
    if (window._chitPayGuard) return;
    window._chitPayGuard = true;
    function onPayAttempt() {
      var checkout = readCheckout();
      if (checkout && checkout.tariff) syncCartForPayment(checkout.tariff);
      applyCheckoutFields(checkout);
    }
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.t706 .t-submit, .t706 button[type="submit"]')) return;
      onPayAttempt();
    }, true);
    document.addEventListener('submit', function (e) {
      if (!e.target || !e.target.closest || !e.target.closest('.t706')) return;
      onPayAttempt();
    }, true);
    document.addEventListener('change', function (e) {
      if (!e.target.matches || !e.target.matches('.t706 .t-radio_payment[name="paymentsystem"]')) return;
      syncPaymentSystem();
    }, true);
  }

  function waitForSt100(cb, attempt) {
    var n = attempt || 0;
    if (document.querySelector('.t706')) { cb(); return; }
    if (n >= 40) { cb(); return; }
    setTimeout(function () { waitForSt100(cb, n + 1); }, 250);
  }

  function waitForTcart(cb, attempt) {
    var n = attempt || 0;
    if (typeof window.tcart__addProduct === 'function' || typeof window.tcart__openCart === 'function') {
      cb();
      return;
    }
    if (n >= 30) { cb(); return; }
    setTimeout(function () { waitForTcart(cb, n + 1); }, 250);
  }

  function clearSafetyTimer() {
    if (!safetyTimer) return;
    clearTimeout(safetyTimer);
    safetyTimer = null;
  }

  function finishOnce(data) {
    if (checkoutFinished) return;
    checkoutFinished = true;
    clearSafetyTimer();
    applyPromoCode(data.promo_code, function () {
      normalizeCartItem(data.tariff);
      applyCheckoutFields(data);
      refreshTcartTotals();
      openCartModal();
      hidePayShell();
      setTimeout(function () { applyCheckoutFields(data); fixFormLayout(); }, 500);
    });
  }

  function prepareCart(data) {
    var uid = ORDER_PRODUCTS[data.tariff].uid;
    clearTcart();
    if (typeof window.tcart__addProduct === 'function') {
      addProduct(data.tariff);
    } else {
      triggerUidHash(uid);
    }
    setTimeout(function () {
      normalizeCartItem(data.tariff);
      refreshTcartTotals();
      finishOnce(data);
    }, 700);
  }

  function runCheckout() {
    if (checkoutStarted) return;
    checkoutStarted = true;

    var data = readCheckout();
    if (!data || !data.tariff || !ORDER_PRODUCTS[data.tariff]) {
      showPayShell('Запись на занятие', 'Сначала заполните форму на главной странице.');
      setTimeout(function () { window.location.href = HOME_URL; }, 2200);
      return;
    }

    bindPayHandlers(data.tariff);
    showPayShell('Оплата', 'Открываем корзину…');

    safetyTimer = setTimeout(function () {
      if (checkoutFinished) return;
      finishOnce(data);
    }, 10000);

    waitForSt100(function () {
      applyCheckoutFields(data);
      waitForTcart(function () {
        prepareCart(data, 0);
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runCheckout);
  } else {
    runCheckout();
  }
})();
