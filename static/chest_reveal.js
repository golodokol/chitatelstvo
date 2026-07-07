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
  var claimBtn = document.getElementById('chest-modal-claim');

  var activePanel = null;
  var activeItems = [];

  function wait(ms) {
    return new Promise(function (resolve) {
      setTimeout(resolve, ms);
    });
  }

  function resetModal() {
    if (chestImg) {
      chestImg.className = 'chit-chest-modal__chest';
      chestImg.src = '/static/chest/chest-closed.png';
    }
    if (lightEl) lightEl.classList.remove('is-on');
    if (sparksEl) sparksEl.innerHTML = '';
    if (rewardsEl) rewardsEl.innerHTML = '';
    if (animateStage) animateStage.hidden = false;
    if (revealStage) revealStage.hidden = true;
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
        link.download = '';
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

  async function claimReward() {
    if (!activePanel || !claimBtn) return;
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
      markPanelClaimed(activePanel);
      closeModal();
      window.location.reload();
    } catch (err) {
      claimBtn.disabled = false;
      if (subEl) subEl.textContent = (err && err.message) || 'Не удалось сохранить награду';
    }
  }

  window.ChitChest = {
    openFromPanel: function (panel) {
      if (!panel || panel.getAttribute('data-chest-claimed') === '1') return;
      if (panel.getAttribute('data-chest-ready') !== '1') return;
      activePanel = panel;
      activeItems = panelItems(panel);
      if (subEl) {
        subEl.textContent = 'Скачай творческие задания — они сохранятся в сокровищнице под сундуком.';
      }
      renderRewards(activeItems);
      playOpenAnimation(panel);
    },
  };

  modal.querySelectorAll('[data-chest-modal-close]').forEach(function (el) {
    el.addEventListener('click', closeModal);
  });

  if (claimBtn) {
    claimBtn.addEventListener('click', claimReward);
  }
})();
