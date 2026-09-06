/**
 * chitatelstvo.ru/oplata — вставить в HTML-блок на странице оплаты (один раз):
 * <script src="https://api.chitatelstvo.ru/assets/chit-pay-page.js?v=20260906b"></script>
 * Важно: только ОДИН HTML-блок со скриптом на странице /oplata (удалить старые версии).
 */
(function () {
  var PAY_PAGE_VER = '20260906b';
  if (window._chitPayPageVersion === PAY_PAGE_VER) return;
  window._chitPayPageVersion = PAY_PAGE_VER;
  var alreadyStarted = !!window._chitPayPageInited;
  window._chitPayPageInited = true;

  // Старый chit-zero.js на /oplata падает (classList на null) и оставлял белый экран.
  // Замораживаем chitReady до загрузки отложенного chit-zero — homepage-init не стартует.
  try {
    if (String(location.pathname || '').indexOf('/oplata') >= 0) {
      Object.defineProperty(window, 'chitReady', {
        value: function () {},
        writable: false,
        configurable: false
      });
    }
  } catch (e) {}

  var STORAGE_KEY = 'chit_checkout';
  var PROMO_FAIL_KEY = 'chit_promo_failed';
  var ST100_RECID = '2380214471';
  var payShellTimer = null;
  var safetyTimer = null;
  var checkoutStarted = false;
  var checkoutFinished = false;

  var HOME_URL = 'https://chitatelstvo.ru/#program';
  var PRODUCT_IMG = 'https://api.chitatelstvo.ru/assets/logo-chitatelstvo.png';
  var ORDER_PRODUCTS = {
    single: { uid: '797131986522', lid: '863983274147', sku: 'SKU0001-2', title: 'Читательство · Разовое', price: 799 },
    self_paced: { uid: '206548598642', lid: '205285061796', sku: 'SKU0002', title: 'Читательство · Индивидуальное', price: 1990 },
    with_teacher: { uid: '956231952022', lid: '776534181255', sku: 'SKU0003', title: 'Читательство · С преподавателем', price: 4990 },
    meeting_addon: { uid: '168614126213', lid: '168614126213', sku: 'SKU0004', title: 'Читательство · Занятие с преподавателем', price: 799 }
  };

  var PAY_CSS = [
    'html.chit-pay-mode, body.chit-pay-mode { background:#F6F4F9 !important; }',
    'html.chit-pay-mode, body.chit-pay-mode.t706__body_cartwinshowed {',
    'height:auto!important;max-height:none!important;overflow:auto!important;',
    '-webkit-overflow-scrolling:touch!important;',
    '}',
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
    'body.chit-pay-mode .t706,',
    'body.chit-pay-mode .t-rec[data-record-type="706"] {',
    'display:block!important;visibility:visible!important;opacity:1!important;',
    'height:auto!important;position:relative!important;left:auto!important;overflow:visible!important;',
    'pointer-events:auto!important;',
    '}',
    'body.chit-pay-mode .t706__cartwin,',
    'body.chit-pay-mode .t706__cartwin.t706__cartwin_showed {',
    'display:block!important;visibility:visible!important;opacity:1!important;',
    'pointer-events:auto!important;',
    'position:fixed!important;inset:0!important;top:0!important;left:0!important;right:0!important;bottom:0!important;',
    'width:100%!important;height:100%!important;max-height:100vh!important;max-height:100dvh!important;',
    'overflow-x:hidden!important;overflow-y:scroll!important;-webkit-overflow-scrolling:touch!important;',
    'touch-action:pan-y!important;overscroll-behavior:contain!important;',
    'padding-bottom:48px!important;z-index:100000!important;',
    '}',
    'body.chit-pay-mode .t706__cartwin-content {',
    'display:flex!important;flex-direction:column!important;',
    'height:auto!important;max-height:none!important;overflow:visible!important;min-height:100%;',
    '}',
    'body.chit-pay-mode .t706__orderform { order:1!important; }',
    'body.chit-pay-mode .t706__cartwin-products { order:2!important; }',
    'body.chit-pay-mode .t706__cartwin-bottom { order:3!important; }',
    'body.chit-pay-mode .t706 .t-input-group_cb[data-field-name="legal_consent"],',
    'body.chit-pay-mode .t706 .t-input-group_cb:has(input[name="legal_consent"]) {',
    'display:block!important;visibility:visible!important;opacity:1!important;',
    'height:auto!important;overflow:visible!important;margin:12px 0!important;',
    '}',
    'body.chit-pay-mode .t706 .t-input-group_cb input[name="legal_consent"] {',
    'position:static!important;opacity:1!important;width:18px!important;height:18px!important;',
    '}',
    'body.chit-pay-mode .t706 .t-input-group_cb .t-checkbox__control {',
    'display:flex!important;align-items:flex-start!important;gap:10px!important;',
    'font-size:14px!important;line-height:1.45!important;color:#2B2140!important;',
    '}',
    'body.chit-pay-mode .t706 .t-input-group_cb .t-checkbox__control span {',
    'display:inline!important;white-space:normal!important;font-size:14px!important;line-height:1.45!important;',
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

  function readPhone(data) {
    if (!data) return '';
    return String(data.parent_phone || data.parent_telegram || '').trim();
  }

  function normalizeCheckout(data) {
    if (!data) return data;
    var phone = sanitizeTelegram(readPhone(data));
    if (phone) {
      data.parent_phone = phone;
      data.parent_telegram = phone;
    }
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
    var style = document.getElementById('chit-pay-hide');
    if (!style) {
      style = document.createElement('style');
      style.id = 'chit-pay-hide';
      (document.head || document.documentElement).appendChild(style);
    }
    style.textContent = PAY_CSS;
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
        'group_code', 'group', 'parent_name', 'parent_email', 'parent_phone', 'parent_telegram',
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
    if (!v.trim() && (
      name === 'parent_phone' || name === 'parent_telegram' ||
      name === 'parent_name' || name === 'parent_email' || name === 'child_name' ||
      name === 'child_birth_date' || name === 'child_age'
    )) return;
    var aliases = {
      parent_name: ['parent_name'],
      parent_email: ['parent_email', 'email', 'Email'],
      parent_phone: ['parent_phone', 'parent_telegram', 'Phone', 'phone', 'tel', 'Telegram'],
      parent_telegram: ['parent_telegram', 'parent_phone', 'Phone', 'phone', 'tel', 'Telegram'],
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

  function clearJunkFormFields() {
    document.querySelectorAll(
      '.t706 [name="form-spec-comments"], .t706 [name="Comments"], .t706 [name="Comment"], .t706 [name="comments"], .t706 textarea'
    ).forEach(function (el) {
      var v = String(el.value || '').trim();
      if (!v) return;
      if (/^its\s*good\.?$/i.test(v)) el.value = '';
    });
  }

  function phoneFieldNodes() {
    return document.querySelectorAll(
      '.t706 input[type="tel"],' +
      '.t706 input[name="parent_phone"], .t706 input[name="parent_telegram"],' +
      '.t706 input[name="Phone"], .t706 input[name="phone"], .t706 input[name="tel"],' +
      '.t706 .t-input-phonemask__value, .t706 .t-input-phonemask input,' +
      '.t706 .t-input-group_ph input, .t706 [data-field-type="ph"] input'
    );
  }

  function readPhoneFromForm() {
    var best = '';
    phoneFieldNodes().forEach(function (el) {
      if (el.type === 'checkbox' || el.type === 'radio') return;
      var v = sanitizeTelegram(el.value || '');
      if (v.replace(/\D/g, '').length >= 10 && v.replace(/\D/g, '').length > best.replace(/\D/g, '').length) {
        best = v;
      }
    });
    return best;
  }

  function writePhoneToForm(phone) {
    phone = sanitizeTelegram(phone || '');
    if (!phone) return;
    var digits = digits11(phone);
    var pretty = prettyRuPhone(digits || phone);
    phoneFieldNodes().forEach(function (el) {
      if (el.type === 'checkbox' || el.type === 'radio') return;
      var isHiddenMask = (el.className || '').indexOf('t-input-phonemask__value') >= 0 ||
        el.classList.contains('js-phonemask-result') ||
        el.type === 'hidden';
      el.value = isHiddenMask && digits.length >= 10 ? digits : pretty;
    });
    exposePhoneForTilda(pretty);
  }

  function digits11(phone) {
    var d = String(phone || '').replace(/\D/g, '');
    if (d.length === 11 && (d.charAt(0) === '8' || d.charAt(0) === '7')) d = '7' + d.slice(1);
    else if (d.length === 10) d = '7' + d;
    return d;
  }

  function prettyRuPhone(phone) {
    var d = digits11(phone);
    if (d.length === 11 && d.charAt(0) === '7') {
      return '+7 (' + d.slice(1, 4) + ') ' + d.slice(4, 7) + '-' + d.slice(7, 9) + '-' + d.slice(9, 11);
    }
    return String(phone || '').trim();
  }

  function ensureHiddenInput(form, name, value) {
    if (!form || !name) return null;
    var vis = form.querySelector('input.t-input[name="' + name + '"], .t-input[name="' + name + '"]');
    var hidden = null;
    form.querySelectorAll('input[name="' + name + '"]').forEach(function (el) {
      if (el !== vis && el.type !== 'checkbox' && el.type !== 'radio') hidden = el;
    });
    if (!hidden) {
      hidden = document.createElement('input');
      hidden.type = 'hidden';
      hidden.name = name;
      form.appendChild(hidden);
    }
    if (value) hidden.value = value;
    return hidden;
  }

  function exposePhoneForTilda(phone) {
    var form = document.querySelector('.t706 form, form[data-formcart="y"]');
    if (!form) return;
    var d = digits11(phone || readPhoneFromForm());
    if (d.length < 10) return;
    var pretty = prettyRuPhone(d);
    var vis = form.querySelector(
      'input.t-input[name="Phone"], input.t-input[name="parent_phone"], input.t-input[name="parent_telegram"], input[type="tel"].js-tilda-rule'
    );
    if (vis) {
      vis.setAttribute('name', 'Phone');
      vis.setAttribute('autocomplete', 'tel');
      vis.setAttribute('data-tilda-rule', 'phone');
      vis.value = pretty;
      var group = vis.closest('[data-field-name]');
      if (group) group.setAttribute('data-field-name', 'Phone');
    }
    ensureHiddenInput(form, 'parent_phone', pretty);
    ensureHiddenInput(form, 'parent_telegram', pretty);
    form.querySelectorAll('input[name="Phone"]').forEach(function (el) {
      if (el === vis) return;
      if (el.type === 'hidden' || el.classList.contains('js-phonemask-result') || (el.className || '').indexOf('phonemask') >= 0) {
        el.value = d;
      }
    });
  }

  function syncPhoneFields(data) {
    var phone = readPhone(data) || readPhoneFromForm();
    writePhoneToForm(phone);
  }

  function renamePhoneField() {
    document.querySelectorAll(
      '.t706 [name="parent_telegram"], .t706 [name="parent_phone"], form[data-formcart="y"] [name="parent_telegram"], form[data-formcart="y"] [name="parent_phone"]'
    ).forEach(function (el) {
      el.setAttribute('name', 'Phone');
      el.setAttribute('autocomplete', 'tel');
      if (el.getAttribute('type') === 'text') el.setAttribute('type', 'tel');
      var group = el.closest('[data-field-name]');
      if (group) group.setAttribute('data-field-name', 'Phone');
      var label = group && group.querySelector('label, .t-input-title');
      if (label && /telegram/i.test(label.textContent || '')) {
        label.textContent = (label.textContent || '').replace(/telegram/ig, 'Телефон');
        if (!/\S/.test(label.textContent)) label.textContent = 'Телефон';
      }
    });
  }

  function dedupeFormServices() {
    document.querySelectorAll('.t706 form, form[data-formcart="y"]').forEach(function (form) {
      var seen = {};
      form.querySelectorAll('input[name="formservices[]"]').forEach(function (el) {
        var v = String(el.value || '');
        if (seen[v]) el.parentNode.removeChild(el);
        else seen[v] = true;
      });
    });
  }

  function injectLegalConsent(form) {
    if (!form || form.querySelector('input[name="legal_consent"]')) return;
    var wrap = document.createElement('div');
    wrap.className = 't-input-group t-input-group_cb';
    wrap.setAttribute('data-field-name', 'legal_consent');
    wrap.setAttribute('data-field-type', 'cb');
    wrap.innerHTML =
      '<label class="t-checkbox__control">' +
      '<input type="checkbox" name="legal_consent" value="yes" data-tilda-req="1" aria-required="true">' +
      '<div class="t-checkbox__indicator"></div>' +
      '<span>Я соглашаюсь с <a href="https://api.chitatelstvo.ru/legal/politika" target="_blank" rel="noopener">Политикой конфиденциальности</a> и <a href="https://api.chitatelstvo.ru/legal/oferta" target="_blank" rel="noopener">публичной офертой</a></span>' +
      '</label>';
    var submit = form.querySelector('.t-submit, button[type="submit"]');
    var box = form.querySelector('.t-form__inputsbox') || form;
    if (submit && submit.parentNode) submit.parentNode.insertBefore(wrap, submit);
    else box.appendChild(wrap);
  }

  function ensureLegalConsent(opts) {
    var forceUnchecked = !opts || opts.forceUnchecked !== false;
    var CONSENT_HTML =
      'Я соглашаюсь с <a href="https://api.chitatelstvo.ru/legal/politika" target="_blank" rel="noopener">Политикой конфиденциальности</a> и <a href="https://api.chitatelstvo.ru/legal/oferta" target="_blank" rel="noopener">публичной офертой</a>';
    document.querySelectorAll('.t706 form, form[data-formcart="y"]').forEach(function (form) {
      injectLegalConsent(form);
    });
    document.querySelectorAll('.t706 input[name="legal_consent"]').forEach(function (el) {
      if (el.type !== 'checkbox') {
        if (el.parentNode) el.parentNode.removeChild(el);
        return;
      }
      if (forceUnchecked && !window._chitConsentTouched) {
        el.checked = false;
        el.removeAttribute('checked');
      }
      el.setAttribute('data-tilda-req', '1');
      el.setAttribute('aria-required', 'true');
      el.required = true;
      if (!el._chitConsentBound) {
        el._chitConsentBound = true;
        el.addEventListener('change', function () {
          window._chitConsentTouched = true;
        });
      }
      var group = el.closest('.t-input-group');
      if (group) {
        group.style.setProperty('display', 'block', 'important');
        group.style.setProperty('visibility', 'visible', 'important');
        group.style.setProperty('opacity', '1', 'important');
        group.style.setProperty('height', 'auto', 'important');
        group.style.setProperty('overflow', 'visible', 'important');
        group.style.setProperty('position', 'static', 'important');
      }
      var label = el.closest('label');
      var span = label && label.querySelector('span');
      if (span) {
        var text = (span.textContent || '').replace(/\s+/g, ' ').trim();
        if (!text || text.length < 8) span.innerHTML = CONSENT_HTML;
      } else if (label && !(label.textContent || '').replace(/\s+/g, ' ').trim()) {
        var s = document.createElement('span');
        s.innerHTML = CONSENT_HTML;
        label.appendChild(s);
      }
    });
    clearJunkFormFields();
    renamePhoneField();
    dedupeFormServices();
  }

  function hasLegalConsent() {
    var boxes = document.querySelectorAll('.t706 input[name="legal_consent"][type="checkbox"]');
    if (!boxes.length) return true;
    for (var i = 0; i < boxes.length; i++) {
      if (boxes[i].checked) return true;
    }
    return false;
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
    if (!code || isPromoBlocked(code)) return;
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
    hoistOrderForm();
  }

  function hoistOrderForm() {
    var content = document.querySelector('.t706__cartwin-content') || document.querySelector('.t706__cartwin');
    if (!content) return;
    var form = document.querySelector('.t706__orderform') || document.querySelector('.t706 form[data-formcart="y"]');
    var products = document.querySelector('.t706__cartwin-products');
    if (!form || !products || !products.parentNode) return;
    if (products.compareDocumentPosition(form) & Node.DOCUMENT_POSITION_FOLLOWING) {
      products.parentNode.insertBefore(form, products);
    }
  }

  function captureFormIntoCheckout() {
    var data = readCheckout() || {};
    ['parent_name', 'parent_email', 'parent_phone', 'child_name', 'child_birth_date', 'child_age', 'promo_code'].forEach(function (name) {
      var el = document.querySelector('.t706 [name="' + name + '"]');
      if (!el || el.type === 'checkbox' || el.type === 'radio') return;
      var v = String(el.value || '').trim();
      if (v) data[name] = v;
    });
    var phone = readPhoneFromForm();
    if (phone) {
      data.parent_phone = phone;
      data.parent_telegram = phone;
    }
    var emailEl = document.querySelector('.t706 input[type="email"]');
    if (emailEl && String(emailEl.value || '').trim()) data.parent_email = String(emailEl.value).trim();
    saveCheckout(data);
    return data;
  }

  function fieldLabel(el) {
    var n = (el && el.getAttribute && el.getAttribute('name')) || '';
    var map = {
      parent_name: 'имя родителя',
      parent_email: 'email',
      Email: 'email',
      email: 'email',
      parent_phone: 'телефон',
      parent_telegram: 'телефон',
      Phone: 'телефон',
      phone: 'телефон',
      child_name: 'имя ребёнка',
      legal_consent: 'согласие с офертой'
    };
    if (map[n]) return map[n];
    var g = el && el.closest && el.closest('.t-input-group');
    var t = g && g.querySelector('.t-input-title, .t-input-subtitle, label');
    var text = t && String(t.textContent || '').replace(/\s+/g, ' ').trim();
    return text || n || 'обязательное поле';
  }

  function isPhoneInput(el) {
    if (!el) return false;
    if (el.type === 'tel') return true;
    var n = el.name || '';
    return /phone|Phone|tel|telegram/i.test(n) || (el.className || '').indexOf('phonemask') >= 0;
  }

  function requiredEmptyFields() {
    var empty = [];
    var phoneOk = (readPhoneFromForm() || '').replace(/\D/g, '').length >= 10;
    var consentOk = hasLegalConsent();
    document.querySelectorAll('.t706 .js-tilda-rule[data-tilda-req="1"], .t706 input[data-tilda-req="1"]').forEach(function (el) {
      if (el.disabled) return;
      if (el.type === 'checkbox' || el.type === 'radio') {
        if (el.name === 'legal_consent' && consentOk) return;
        if (!el.checked) empty.push(el);
        return;
      }
      if (isPhoneInput(el)) {
        if (!phoneOk) empty.push(el);
        return;
      }
      if (!String(el.value || '').trim()) empty.push(el);
    });
    return empty;
  }

  function scrollCartTo(el) {
    var win = document.querySelector('.t706__cartwin');
    if (el && typeof el.focus === 'function') {
      try { el.focus({ preventScroll: true }); } catch (err) { try { el.focus(); } catch (err2) {} }
    }
    if (win && el) {
      var wr = win.getBoundingClientRect();
      var er = el.getBoundingClientRect();
      win.scrollTop = Math.max(0, win.scrollTop + (er.top - wr.top) - 72);
    }
    if (el && el.scrollIntoView) {
      try { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (err3) {}
    }
  }

  function showRequiredError(fields) {
    var names = [];
    (fields || []).forEach(function (el) {
      var l = fieldLabel(el);
      if (names.indexOf(l) < 0) names.push(l);
    });
    var msg = names.length
      ? ('Заполните: ' + names.join(', '))
      : 'Пожалуйста, заполните все обязательные поля';
    document.querySelectorAll(
      '.t706 .js-errorbox-all, .t706 .t-form__errorbox-text, .t706 .t-form__errorbox-middle, .t706 .t-form__errorbox-wrapper'
    ).forEach(function (box) {
      box.style.display = 'block';
      box.textContent = msg;
    });
  }

  function syncLegalConsentFromUi() {
    document.querySelectorAll('.t706 input[name="legal_consent"][type="checkbox"]').forEach(function (el) {
      var group = el.closest('.t-input-group');
      var control = el.closest('.t-checkbox__control') || el.parentElement;
      var looksChecked = !!(
        el.checked ||
        el.getAttribute('checked') ||
        (control && /checked/i.test(control.className || '')) ||
        (group && /checked/i.test(group.className || ''))
      );
      if (looksChecked) el.checked = true;
    });
  }

  function applyCheckoutFields(data) {
    if (!data) return;
    normalizeCheckout(data);
    if (!data.notification_channel) data.notification_channel = 'email';
    [
      'module_id', 'chosen_stage', 'chosen_tale_number', 'lesson_slug', 'group_code',
      'parent_name', 'parent_email', 'parent_phone', 'parent_telegram', 'child_name',
      'child_birth_date', 'child_age', 'promo_code', 'notification_channel'
    ].forEach(function (name) { setField(name, data[name]); });
    mirrorEmailForKassa(data);
    ensureLegalConsent({ forceUnchecked: false });
    syncPhoneFields(data);
    exposePhoneForTilda(readPhone(data) || readPhoneFromForm());
    configurePromoField(data);
    fixFormLayout();
    hoistOrderForm();
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
      lid: p.lid || p.uid,
      img: PRODUCT_IMG
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
    revealPaymentUi();
    if (typeof window.tcart__openCart === 'function') {
      window.tcart__openCart();
      return;
    }
    var icon = document.querySelector('.t706__carticon');
    if (icon) icon.click();
  }

  function revealPaymentUi() {
    document.documentElement.classList.add('chit-pay-mode');
    if (document.body) document.body.classList.add('chit-pay-mode');
    document.querySelectorAll('.t-rec[data-record-type="706"], .t-rec:has(.t706), .t706').forEach(function (el) {
      var rec = el.classList.contains('t-rec') ? el : el.closest('.t-rec');
      if (rec) {
        rec.classList.remove('chit-store-hidden');
        rec.removeAttribute('aria-hidden');
        ['display', 'position', 'left', 'height', 'min-height', 'max-height', 'padding', 'margin', 'overflow', 'visibility', 'opacity', 'pointer-events'].forEach(function (prop) {
          rec.style.removeProperty(prop);
        });
      }
    });
    var win = document.querySelector('.t706__cartwin');
    if (win) {
      win.classList.add('t706__cartwin_showed');
      win.classList.add('t706__cartwin_opened');
      win.style.setProperty('display', 'block', 'important');
      win.style.setProperty('visibility', 'visible', 'important');
      win.style.setProperty('opacity', '1', 'important');
      win.style.setProperty('pointer-events', 'auto', 'important');
      win.style.setProperty('position', 'fixed', 'important');
      win.style.setProperty('inset', '0', 'important');
      win.style.setProperty('top', '0', 'important');
      win.style.setProperty('left', '0', 'important');
      win.style.setProperty('width', '100%', 'important');
      win.style.setProperty('height', '100%', 'important');
      win.style.setProperty('max-height', '100vh', 'important');
      win.style.setProperty('overflow-x', 'hidden', 'important');
      win.style.setProperty('overflow-y', 'scroll', 'important');
      win.style.setProperty('z-index', '100000', 'important');
    }
    var cart = document.querySelector('.t706');
    if (cart) {
      cart.style.setProperty('display', 'block', 'important');
      cart.style.setProperty('visibility', 'visible', 'important');
      cart.style.setProperty('opacity', '1', 'important');
    }
    hoistOrderForm();
  }

  function hasActivePromo() {
    return !!(window.tcart && window.tcart.promocode && window.tcart.promocode.message === 'OK');
  }

  function promoAlreadyApplied(code) {
    if (!code || !hasActivePromo()) return false;
    var promo = window.tcart.promocode;
    var saved = String(promo.code || promo.promocode || '').trim();
    return saved.toLowerCase() === String(code).trim().toLowerCase();
  }

  function isPromoBlocked(code) {
    code = String(code || '').trim().toLowerCase();
    if (!code) return false;
    try {
      var raw = sessionStorage.getItem(PROMO_FAIL_KEY);
      var list = raw ? JSON.parse(raw) : [];
      return list.indexOf(code) >= 0;
    } catch (e) {
      return false;
    }
  }

  function markPromoBlocked(code) {
    code = String(code || '').trim().toLowerCase();
    if (!code) return;
    try {
      var raw = sessionStorage.getItem(PROMO_FAIL_KEY);
      var list = raw ? JSON.parse(raw) : [];
      if (list.indexOf(code) < 0) list.push(code);
      sessionStorage.setItem(PROMO_FAIL_KEY, JSON.stringify(list));
    } catch (e) {}
  }

  function clearCheckoutPromo(data) {
    if (data) delete data.promo_code;
    try {
      var stored = readCheckout();
      if (stored) {
        delete stored.promo_code;
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
      }
    } catch (e) {}
    setField('promo_code', '');
    var input = document.querySelector('.t706 .t-inputpromocode');
    var btn = document.querySelector('.t706 .t-inputpromocode__btn');
    if (input) input.value = '';
    if (btn) btn.style.display = 'none';
    if (window.tcart) delete window.tcart.promocode;
  }

  function saveCheckout(data) {
    if (!data) return;
    try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data)); } catch (e) {}
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

  function normalizeCartItem(tariff) {
    var p = ORDER_PRODUCTS[tariff];
    if (!p || !window.tcart) return;
    var items = (window.tcart.products || []).filter(function (it) {
      return String(it.uid) === String(p.uid);
    });
    if (!items.length) return;
    var item = items[0];
    item.quantity = 1;
    item.price = p.price;
    item.amount = p.price;
    window.tcart.products = [item];
    window.tcart.prodamount = p.price;
    recalcPromoTotals(tariff);
    window.tcart.updated = Math.floor(Date.now() / 1000);
    if (typeof window.tcart__saveLocalObj === 'function') window.tcart__saveLocalObj();
  }

  function prepareCartForPayment(tariff) {
    if (!window.tcart) return;
    normalizeCartItem(tariff);
    syncPaymentSystem();
    if (typeof window.tcart__saveLocalObj === 'function') window.tcart__saveLocalObj();
  }

  function applyPromoCode(code, cb) {
    code = String(code || '').trim();
    if (!code) { if (cb) cb(false); return; }
    if (isPromoBlocked(code)) { if (cb) cb(false); return; }
    if (promoAlreadyApplied(code)) { if (cb) cb(true); return; }
    var input = document.querySelector('.t706 .t-inputpromocode');
    var btn = document.querySelector('.t706 .t-inputpromocode__btn');
    if (!input || !btn) { if (cb) cb(false); return; }
    setField('promo_code', code);
    input.value = code;
    btn.style.display = 'table-cell';
    try { btn.click(); } catch (e) {}
    setTimeout(function () {
      refreshTcartTotals();
      var ok = promoAlreadyApplied(code);
      if (!ok) {
        markPromoBlocked(code);
      }
      if (cb) cb(ok);
    }, 900);
  }

  function bindPayHandlers(tariff) {
    if (window._chitPayGuard === PAY_PAGE_VER) return;
    window._chitPayGuard = PAY_PAGE_VER;
    function onPayAttempt(e) {
      var checkout = captureFormIntoCheckout();
      if (checkout && checkout.tariff) prepareCartForPayment(checkout.tariff);
      if (checkout) {
        normalizeCheckout(checkout);
        if (!checkout.notification_channel) checkout.notification_channel = 'email';
        [
          'module_id', 'chosen_stage', 'chosen_tale_number', 'lesson_slug', 'group_code',
          'parent_name', 'parent_email', 'parent_phone', 'parent_telegram', 'child_name',
          'child_birth_date', 'child_age', 'promo_code', 'notification_channel'
        ].forEach(function (name) { setField(name, checkout[name]); });
        var phone = readPhone(checkout) || readPhoneFromForm();
        if (phone) {
          setField('parent_phone', phone);
          writePhoneToForm(phone);
        }
        mirrorEmailForKassa(checkout);
        ensureLegalConsent({ forceUnchecked: false });
        syncPhoneFields(checkout);
        exposePhoneForTilda(readPhone(checkout) || readPhoneFromForm());
        configurePromoField(checkout);
        fixFormLayout();
      }
      clearJunkFormFields();
      syncLegalConsentFromUi();
      hoistOrderForm();
      var missing = requiredEmptyFields();
      if (missing.length || !hasLegalConsent()) {
        if (e) {
          e.preventDefault();
          if (e.stopImmediatePropagation) e.stopImmediatePropagation();
          else e.stopPropagation();
        }
        ensureLegalConsent({ forceUnchecked: false });
        if (!hasLegalConsent()) {
          var box = document.querySelector('.t706 input[name="legal_consent"][type="checkbox"]');
          if (box) missing.unshift(box);
        }
        showRequiredError(missing);
        scrollCartTo(missing[0]);
        return false;
      }
      return true;
    }
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.t706 .t-submit, .t706 button[type="submit"]')) return;
      onPayAttempt(e);
    }, true);
    document.addEventListener('pointerdown', function (e) {
      if (!e.target.closest('.t706 .t-submit, .t706 button[type="submit"]')) return;
      syncPhoneFields(readCheckout());
    }, true);
    document.addEventListener('submit', function (e) {
      if (!e.target || !e.target.closest || !e.target.closest('.t706')) return;
      onPayAttempt(e);
    }, true);
    document.addEventListener('change', function (e) {
      if (!e.target.matches || !e.target.matches('.t706 .t-radio_payment[name="paymentsystem"]')) return;
      syncPaymentSystem();
    }, true);
    document.addEventListener('change', function (e) {
      if (!e.target.closest || !e.target.closest('.t706')) return;
      if (e.target.name === 'legal_consent') window._chitConsentTouched = true;
      captureFormIntoCheckout();
    }, true);
    document.addEventListener('input', function (e) {
      if (!e.target.closest || !e.target.closest('.t706')) return;
      captureFormIntoCheckout();
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
    applyPromoCode(data.promo_code, function (ok) {
      if (!ok && data.promo_code) {
        clearCheckoutPromo(data);
        saveCheckout(data);
      }
      normalizeCartItem(data.tariff);
      applyCheckoutFields(data);
      refreshTcartTotals();
      openCartModal();
      hidePayShell();
      setTimeout(function () { applyCheckoutFields(data); fixFormLayout(); revealPaymentUi(); }, 500);
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
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }

  function start() {
    revealPaymentUi();
    waitForSt100(function () {
      revealPaymentUi();
      ensureLegalConsent();
      renamePhoneField();
      dedupeFormServices();
      if (alreadyStarted) {
        var data = readCheckout();
        if (data && data.tariff) {
          bindPayHandlers(data.tariff);
          applyCheckoutFields(data);
        }
        openCartModal();
        hidePayShell();
        setTimeout(revealPaymentUi, 400);
        return;
      }
      runCheckout();
    });
  }
})();
