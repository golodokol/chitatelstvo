(function () {
  var modal = document.getElementById('chest-modal');
  if (!modal) return;

  var animateStage = document.getElementById('chest-modal-animate');
  var revealStage = document.getElementById('chest-modal-reveal');
  var chestImg = document.getElementById('chest-modal-img');
  var lightEl = document.getElementById('chest-modal-light');
  var sparksEl = document.getElementById('chest-modal-sparks');
  var rewardsEl = document.getElementById('chest-modal-rewards');
  var subEl = document.getElementById('chest-modal-sub');
  var titleEl = document.getElementById('chest-modal-title');
  var claimBtn = document.getElementById('chest-modal-claim');

  var activePanel = null;
  var activeItems = [];
  var claimDone = false;
  var claimedTreasurySection = null;

  function wait(ms) {
    return new Promise(function (resolve) {
      setTimeout(resolve, ms);
    });
  }

  function resetModal() {
    claimDone = false;
    claimedTreasurySection = null;
    if (chestImg) {
      chestImg.className = 'chit-chest-modal__chest';
      chestImg.src = '/static/chest/chest-closed.png';
    }
    if (lightEl) lightEl.classList.remove('is-on');
    if (sparksEl) sparksEl.innerHTML = '';
    if (rewardsEl) rewardsEl.innerHTML = '';
    if (animateStage) animateStage.hidden = false;
    if (revealStage) revealStage.hidden = true;
    if (titleEl) titleEl.textContent = 'Сундук открыт!';
    if (claimBtn) {
      claimBtn.disabled = false;
      claimBtn.hidden = false;
      claimBtn.textContent = 'Забрать награду';
    }
  }

  function spawnSparks() {
    if (!sparksEl) return;
    sparksEl.innerHTML = '';
    var slovikUrls = [
      '/static/sloviki/slovik-reward.png',
      '/static/sloviki/slovik-victory.png',
      '/static/sloviki/slovik-dreams.png',
    ];
    for (var i = 0; i < 10; i++) {
      var node;
      if (i % 3 === 0) {
        node = document.createElement('img');
        node.src = slovikUrls[i % slovikUrls.length];
        node.className = 'chit-chest-modal__spark chit-chest-modal__spark--slovik';
        node.alt = '';
      } else {
        node = document.createElement('span');
        node.className = 'chit-chest-modal__spark';
      }
      var angle = (Math.PI * 2 * i) / 10;
      var dist = 36 + Math.random() * 32;
      node.style.left = '50%';
      node.style.top = '42%';
      node.style.setProperty('--sx', Math.round(Math.cos(angle) * dist) + 'px');
      node.style.setProperty('--sy', Math.round(Math.sin(angle) * dist - 24) + 'px');
      node.style.animationDelay = (i * 0.04) + 's';
      sparksEl.appendChild(node);
    }
  }

  function renderRewards(items) {
    if (!rewardsEl) return;
    rewardsEl.innerHTML = '';
    items.forEach(function (item, idx) {
      var card = document.createElement('div');
      card.className = 'chit-chest-modal__reward';
      card.style.animationDelay = (idx * 0.07) + 's';
      if (item.image_url) {
        var img = document.createElement('img');
        img.src = item.image_url;
        img.alt = '';
        card.appendChild(img);
      }
      var label = document.createElement('strong');
      label.textContent = item.label || '';
      card.appendChild(label);
      if (item.kind === 'letter') {
        var note = document.createElement('span');
        note.className = 'chit-chest-modal__reward-note';
        note.textContent = 'Прочитай сейчас — в сокровищницу не сохраняется';
        card.appendChild(note);
      }
      if (item.downloadable && item.download_url) {
        var link = document.createElement('a');
        link.className = 'chit-chest-modal__reward-download';
        link.href = item.download_url;
        link.download = item.download_name || '';
        link.textContent = 'Скачать';
        card.appendChild(link);
      }
      rewardsEl.appendChild(card);
    });
  }

  async function playOpenAnimation(panel) {
    var closed = panel.getAttribute('data-chest-closed') || '/static/chest/chest-closed.png';
    var opening = panel.getAttribute('data-chest-opening') || '/static/chest/chest-opening.png';
    var open = panel.getAttribute('data-chest-open') || '/static/chest/chest-open.png';

    resetModal();
    modal.hidden = false;
    document.body.style.overflow = 'hidden';

    if (chestImg) {
      chestImg.src = closed;
      chestImg.classList.add('is-shake');
    }
    await wait(280);

    if (chestImg) {
      chestImg.classList.remove('is-shake');
      chestImg.src = opening;
    }
    if (lightEl) lightEl.classList.add('is-on');
    spawnSparks();
    await wait(420);

    if (chestImg) {
      chestImg.src = open;
      chestImg.classList.add('is-open-pop');
    }
    await wait(480);

    if (animateStage) animateStage.hidden = true;
    if (revealStage) revealStage.hidden = false;
  }

  async function openAndClaim(panel) {
    activePanel = panel;
    activeItems = panelItems(panel);
    if (subEl) {
      subEl.textContent = 'Посмотри награды. Они уже сохраняются в сокровищницу.';
    }
    renderRewards(activeItems);
    await playOpenAnimation(panel);
    // Сразу сохраняем — иначе при закрытии модалки сундук «открыт», а наград нет.
    await claimReward();
  }

  function closeModal() {
    modal.hidden = true;
    document.body.style.overflow = '';
    resetModal();
    activePanel = null;
    activeItems = [];
  }

  function panelItems(panel) {
    var node = panel.querySelector('.chit-chest-data');
    if (!node) return [];
    try {
      var data = JSON.parse(node.textContent || '{}');
      return data.items || [];
    } catch (e) {
      return [];
    }
  }

  function markPanelClaimed(panel) {
    panel.setAttribute('data-chest-claimed', '1');
    panel.setAttribute('data-chest-ready', '0');
    panel.classList.remove('is-ready');
    panel.classList.add('is-claimed');
    var img = panel.querySelector('[data-chest-img]');
    var openUrl = panel.getAttribute('data-chest-open');
    if (img && openUrl) img.src = openUrl;
    var btn = panel.querySelector('button[data-chest-open]');
    if (btn) {
      var link = document.createElement('a');
      link.className = btn.className;
      link.href = panel.getAttribute('data-treasury-href') || '#treasury-1';
      link.textContent = 'В сокровищницу';
      btn.replaceWith(link);
    }
    var hint = panel.querySelector('.chit-chest__hint');
    if (hint) hint.textContent = 'Награда уже в сокровищнице';
  }

  function treasuryHref(panel) {
    return panel.getAttribute('data-treasury-href') || '#treasury-1';
  }

  function treasuryIdFromHref(href) {
    if (!href || href.charAt(0) !== '#') return 'treasury-1';
    return href.slice(1) || 'treasury-1';
  }

  function isTreasuryItem(item) {
    if (!item) return false;
    var kind = String(item.kind || '');
    if (kind === 'letter') return false;
    return true;
  }

  function buildTreasuryCard(item) {
    var article = document.createElement('article');
    article.className = 'chit-treasury-item';
    article.setAttribute('role', 'button');
    article.setAttribute('tabindex', '0');
    article.setAttribute('data-treasury-preview', '');
    article.setAttribute('data-just-added', '1');
    article.setAttribute('data-label', item.label || '');
    article.setAttribute(
      'data-caption',
      item.lesson_caption || (item.tale_title ? ('Урок «' + item.tale_title + '»') : '')
    );
    article.setAttribute('data-image', item.image_url || '');
    article.setAttribute(
      'data-download',
      item.downloadable && item.download_url ? item.download_url : ''
    );
    article.setAttribute('data-download-name', item.download_name || '');
    article.setAttribute('data-kind', item.kind || '');
    article.setAttribute('data-tale-slug', item.tale_slug || '');
    if (item.image_url) {
      var img = document.createElement('img');
      img.src = item.image_url;
      img.alt = '';
      img.loading = 'lazy';
      article.appendChild(img);
    }
    var strong = document.createElement('strong');
    strong.textContent = item.label || '';
    article.appendChild(strong);
    var span = document.createElement('span');
    span.textContent = item.lesson_caption || (item.tale_title ? ('Урок «' + item.tale_title + '»') : '');
    article.appendChild(span);
    return article;
  }

  function ensureTreasuryShell(panel) {
    var href = treasuryHref(panel);
    var id = treasuryIdFromHref(href);
    var section = document.getElementById(id);
    if (section) {
      var empty = section.querySelector('.chit-treasury-empty');
      if (empty) empty.remove();
      var wrap = section.querySelector('[data-treasury]');
      if (wrap) return wrap;
      wrap = document.createElement('div');
      wrap.className = 'chit-treasury';
      wrap.setAttribute('data-treasury', '');
      wrap.innerHTML =
        '<div class="chit-treasury-grid"></div>' +
        '<nav class="chit-treasury-pager" data-treasury-pager hidden aria-label="Страницы сокровищницы">' +
        '<button type="button" class="chit-treasury-pager__btn" data-treasury-prev aria-label="Предыдущая страница">‹</button>' +
        '<span class="chit-treasury-pager__label" data-treasury-label></span>' +
        '<button type="button" class="chit-treasury-pager__btn" data-treasury-next aria-label="Следующая страница">›</button>' +
        '</nav>';
      section.appendChild(wrap);
      return wrap;
    }

    section = document.createElement('section');
    section.className = 'chit-panel chit-panel--treasury chit-panel--treasury-under-chest';
    section.id = id;
    section.innerHTML =
      '<h2 class="chit-section-title">Моя сокровищница</h2>' +
      '<p class="chit-section-sub">Творческие задания из сундука — можно скачать снова.</p>' +
      '<div class="chit-treasury" data-treasury>' +
      '<div class="chit-treasury-grid"></div>' +
      '<nav class="chit-treasury-pager" data-treasury-pager hidden aria-label="Страницы сокровищницы">' +
      '<button type="button" class="chit-treasury-pager__btn" data-treasury-prev aria-label="Предыдущая страница">‹</button>' +
      '<span class="chit-treasury-pager__label" data-treasury-label></span>' +
      '<button type="button" class="chit-treasury-pager__btn" data-treasury-next aria-label="Следующая страница">›</button>' +
      '</nav>' +
      '</div>';
    panel.insertAdjacentElement('afterend', section);
    return section.querySelector('[data-treasury]');
  }

  function addItemsToTreasury(panel, items) {
    var list = (items || []).filter(isTreasuryItem);
    if (!list.length) return null;
    var wrap = ensureTreasuryShell(panel);
    if (!wrap) return null;
    var grid = wrap.querySelector('.chit-treasury-grid');
    if (!grid) return null;
    list.forEach(function (item) {
      grid.appendChild(buildTreasuryCard(item));
    });
    if (window.ChitTreasury && window.ChitTreasury.refresh) {
      window.ChitTreasury.refresh(wrap);
    }
    return document.getElementById(treasuryIdFromHref(treasuryHref(panel)));
  }

  function scrollToTreasury(section) {
    if (!section) return;
    try {
      section.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (e) {
      section.scrollIntoView(true);
    }
  }

  async function claimReward() {
    if (!activePanel || !claimBtn || claimDone) return;
    claimBtn.disabled = true;
    var token = activePanel.getAttribute('data-progress-token');
    var childId = activePanel.getAttribute('data-child-id');
    var taleSlug = activePanel.getAttribute('data-tale-slug');
    if (!token || !childId || !taleSlug) {
      claimBtn.disabled = false;
      return;
    }
    try {
      var res = await fetch('/api/progress/' + encodeURIComponent(token) + '/chest/claim', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ child_id: childId, tale_slug: taleSlug }),
      });
      var data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Ошибка');
      claimDone = true;
      markPanelClaimed(activePanel);
      var treasuryItems = data.items && data.items.length ? data.items : activeItems;
      claimedTreasurySection = addItemsToTreasury(activePanel, treasuryItems);
      if (titleEl) titleEl.textContent = 'Награды в сокровищнице!';
      if (subEl) {
        subEl.textContent = 'Сначала ты увидел награды здесь — теперь они лежат в сокровищнице под сундуком.';
      }
      claimBtn.textContent = 'Смотреть сокровищницу';
      claimBtn.disabled = false;
      if (data.badge_name && window.ChitSlovik && window.ChitSlovik.showReward) {
        var badgeName = data.badge_name;
        var badgeImage =
          (window.ChitSlovik.BADGE_IMAGES && window.ChitSlovik.BADGE_IMAGES[badgeName]) || '';
        window.ChitSlovik.showReward({
          badge: badgeName,
          badgeImage: badgeImage,
          message: 'Бейдж «' + badgeName + '»!',
          points: 0,
          slovikKey: 'reward',
        });
      }
    } catch (err) {
      claimBtn.disabled = false;
      if (subEl) subEl.textContent = (err && err.message) || 'Не удалось сохранить награду';
    }
  }

  window.ChitChest = {
    openFromPanel: function (panel) {
      if (!panel || panel.getAttribute('data-chest-claimed') === '1') return;
      if (panel.getAttribute('data-chest-ready') !== '1') return;
      openAndClaim(panel);
    },
    showClaimedInTreasury: function (panel) {
      if (!panel) return;
      var section = document.getElementById(treasuryIdFromHref(treasuryHref(panel)));
      if (!section) {
        section = document.getElementById('treasury-all');
      }
      if (!section) return;
      var slug = panel.getAttribute('data-tale-slug') || '';
      section.querySelectorAll('.chit-treasury-item').forEach(function (item) {
        var match = !slug || item.getAttribute('data-tale-slug') === slug;
        item.classList.toggle('is-highlight', match);
      });
      if (window.ChitTreasury && window.ChitTreasury.showTale) {
        window.ChitTreasury.showTale(section, slug);
      }
      scrollToTreasury(section);
      focusChestPanel(panel);
    },
  };

  modal.querySelectorAll('[data-chest-modal-close]').forEach(function (el) {
    el.addEventListener('click', function () {
      var section = claimDone ? claimedTreasurySection : null;
      closeModal();
      if (section) scrollToTreasury(section);
    });
  });

  if (claimBtn) {
    claimBtn.addEventListener('click', function () {
      if (claimDone) {
        var section = claimedTreasurySection;
        closeModal();
        if (section) scrollToTreasury(section);
        return;
      }
      claimReward();
    });
  }
})();
