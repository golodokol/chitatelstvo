/**
 * Рендер и сбор ответов для квизов урока (single, multi, matching, ordering, picture_match).
 */
(function (global) {
  'use strict';

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function optionHasImages(items) {
    return (items || []).some(function (item) { return item && item.image; });
  }

  function renderOptionImage(item) {
    if (!item || !item.image) return '';
    const alt = item.alt || item.text || '';
    return (
      '<span class="chit-opt-img-wrap">' +
      '<img class="chit-opt-img" src="' + escapeHtml(item.image) + '" alt="' + escapeHtml(alt) + '" loading="lazy">' +
      '</span>'
    );
  }

  function appendPromptImage(div, q) {
    if (!q.prompt_image) return;
    const wrap = document.createElement('div');
    wrap.className = 'chit-q-prompt-image';
    const img = document.createElement('img');
    img.src = q.prompt_image;
    img.alt = q.prompt_image_alt || '';
    img.loading = 'lazy';
    wrap.appendChild(img);
    div.appendChild(wrap);
  }

  function appendQuestionHeader(div, q, idx) {
    const title = document.createElement('strong');
    title.className = 'chit-q-title';
    title.textContent = (idx + 1) + '. ' + (q.text || '');
    div.appendChild(title);
    if (q.hint) {
      const hint = document.createElement('p');
      hint.className = 'chit-q-hint';
      hint.textContent = q.hint;
      div.appendChild(hint);
    }
  }

  function notifyFormChange(formId) {
    const form = document.getElementById(formId);
    if (form) form.dispatchEvent(new Event('change', { bubbles: true }));
  }

  function renderChoiceChips(formId, q, rowKey, options, selectedId) {
    const wrap = document.createElement('div');
    wrap.className = 'chit-match-choices';
    wrap.setAttribute('role', 'group');
    (options || []).forEach(function (opt) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chit-match-choice';
      btn.dataset.rightId = opt.id;
      btn.dataset.rowKey = rowKey;
      btn.setAttribute('aria-pressed', selectedId === opt.id ? 'true' : 'false');
      if (selectedId === opt.id) btn.classList.add('is-selected');
      btn.textContent = opt.text;
      wrap.appendChild(btn);
    });
    return wrap;
  }

  function clearConflictingChoice(root, rightId, exceptRowKey) {
    root.querySelectorAll('.chit-match-choice.is-selected').forEach(function (btn) {
      if (btn.dataset.rightId !== rightId) return;
      if (btn.dataset.rowKey === exceptRowKey) return;
      btn.classList.remove('is-selected');
      btn.setAttribute('aria-pressed', 'false');
      const group = btn.closest('.chit-match-choices');
      if (group) group.dataset.selected = '';
    });
  }

  function attachExclusiveChoices(root, formId) {
    root.addEventListener('click', function (event) {
      const btn = event.target.closest('.chit-match-choice');
      if (!btn || !root.contains(btn)) return;
      const group = btn.closest('.chit-match-choices');
      if (!group) return;
      const rightId = btn.dataset.rightId;
      const rowKey = btn.dataset.rowKey;
      const already = btn.classList.contains('is-selected');
      group.querySelectorAll('.chit-match-choice').forEach(function (other) {
        other.classList.remove('is-selected');
        other.setAttribute('aria-pressed', 'false');
      });
      if (!already) {
        clearConflictingChoice(root, rightId, rowKey);
        btn.classList.add('is-selected');
        btn.setAttribute('aria-pressed', 'true');
        group.dataset.selected = rightId;
      } else {
        group.dataset.selected = '';
      }
      notifyFormChange(formId);
    });
  }

  function renderSingleOrMulti(formId, q, idx, multi) {
    const div = document.createElement('div');
    const withImages = optionHasImages(q.options);
    div.className = withImages ? 'chit-q chit-q-with-images' : 'chit-q';
    div.dataset.qid = q.id;
    div.dataset.qtype = q.type || 'single';
    appendQuestionHeader(div, q, idx);
    const container = withImages ? document.createElement('div') : div;
    if (withImages) {
      container.className = 'chit-opt-grid';
      const optCount = (q.options || []).length;
      if (optCount === 6) {
        container.classList.add('chit-opt-grid--6');
        container.dataset.optCount = '6';
      } else if (optCount === 7) {
        container.classList.add('chit-opt-grid--7');
        container.dataset.optCount = '7';
      }
      div.appendChild(container);
    }
    (q.options || []).forEach(function (opt) {
      const id = formId + '-' + q.id + '-' + opt.id;
      const inputType = multi ? 'checkbox' : 'radio';
      const name = multi ? formId + '-' + q.id : q.id;
      const label = document.createElement('label');
      label.className = withImages ? 'chit-opt-card' : '';
      if (withImages) {
        label.innerHTML =
          '<input type="' + inputType + '" name="' + name + '" value="' + escapeHtml(opt.id) + '" id="' + id + '">' +
          renderOptionImage(opt) +
          '<span class="chit-opt-caption">' + escapeHtml(opt.text) + '</span>';
      } else {
        label.innerHTML =
          '<input type="' + inputType + '" name="' + name + '" value="' + escapeHtml(opt.id) + '" id="' + id + '"> ' +
          escapeHtml(opt.text);
      }
      container.appendChild(label);
    });
    return div;
  }

  function renderTrueFalse(formId, q, idx) {
    const div = document.createElement('div');
    div.className = 'chit-q';
    div.dataset.qid = q.id;
    div.dataset.qtype = 'true_false';
    appendQuestionHeader(div, q, idx);
    (q.statements || []).forEach(function (stmt) {
      const id = formId + '-' + q.id + '-' + stmt.id;
      const label = document.createElement('label');
      label.className = 'chit-q-check';
      label.innerHTML =
        '<input type="checkbox" name="' + formId + '-' + q.id + '" value="' + escapeHtml(stmt.id) + '" id="' + id + '"> ' +
        escapeHtml(stmt.text);
      div.appendChild(label);
    });
    return div;
  }

  function renderMatchItemContent(item, withImages) {
    if (withImages && item.image) {
      return renderOptionImage(item) + '<span class="chit-opt-caption">' + escapeHtml(item.text) + '</span>';
    }
    return '<span class="chit-match-item-text">' + escapeHtml(item.text) + '</span>';
  }

  function redrawMatchLines(board) {
    const svg = board.querySelector('.chit-match-lines');
    if (!svg) return;
    const rect = board.getBoundingClientRect();
    const width = Math.max(1, board.clientWidth);
    const height = Math.max(1, board.clientHeight);
    svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
    svg.setAttribute('width', String(width));
    svg.setAttribute('height', String(height));
    while (svg.firstChild) svg.removeChild(svg.firstChild);

    board.querySelectorAll('.chit-match-item--left[data-paired]').forEach(function (leftBtn) {
      const rightId = leftBtn.dataset.paired;
      if (!rightId) return;
      const rightBtn = board.querySelector('.chit-match-item--right[data-right-id="' + rightId + '"]');
      if (!rightBtn) return;
      const leftRect = leftBtn.getBoundingClientRect();
      const rightRect = rightBtn.getBoundingClientRect();
      const ah = 12;
      const pad = 6;
      const x1 = leftRect.right - rect.left + pad;
      const y1 = leftRect.top + leftRect.height / 2 - rect.top;
      // Tip stays in the gap so the button does not clip the arrowhead.
      const xTip = rightRect.left - rect.left - pad;
      const y2 = rightRect.top + rightRect.height / 2 - rect.top;
      const xLineEnd = xTip - ah + 1;
      const mid = (x1 + xLineEnd) / 2;
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute(
        'd',
        'M ' + x1 + ' ' + y1 + ' C ' + mid + ' ' + y1 + ', ' + mid + ' ' + y2 + ', ' + xLineEnd + ' ' + y2
      );
      path.setAttribute('class', 'chit-match-line');
      if (leftBtn.dataset.pairTone) path.setAttribute('data-pair-tone', leftBtn.dataset.pairTone);
      svg.appendChild(path);
      const tip = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
      tip.setAttribute(
        'points',
        xTip + ',' + y2 + ' ' +
        (xTip - ah) + ',' + (y2 - ah * 0.62) + ' ' +
        (xTip - ah * 0.55) + ',' + y2 + ' ' +
        (xTip - ah) + ',' + (y2 + ah * 0.62)
      );
      tip.setAttribute('class', 'chit-match-arrow');
      if (leftBtn.dataset.pairTone) tip.setAttribute('data-pair-tone', leftBtn.dataset.pairTone);
      svg.appendChild(tip);
    });
  }

  function attachMatchBoard(board, formId) {
    let activeLeft = null;
    const tones = ['1', '2', '3', '4', '5', '6'];

    function clearActive() {
      if (!activeLeft) return;
      activeLeft.classList.remove('is-active');
      activeLeft = null;
      board.classList.remove('has-active-left');
    }

    function nextTone() {
      const used = {};
      board.querySelectorAll('.chit-match-item--left[data-pair-tone]').forEach(function (btn) {
        used[btn.dataset.pairTone] = true;
      });
      for (let i = 0; i < tones.length; i += 1) {
        if (!used[tones[i]]) return tones[i];
      }
      return tones[0];
    }

    function clearPairForLeft(leftBtn) {
      const rightId = leftBtn.dataset.paired;
      leftBtn.removeAttribute('data-paired');
      leftBtn.removeAttribute('data-pair-tone');
      leftBtn.classList.remove('is-paired');
      if (rightId) {
        const rightBtn = board.querySelector('.chit-match-item--right[data-right-id="' + rightId + '"]');
        if (rightBtn) {
          rightBtn.removeAttribute('data-paired-left');
          rightBtn.removeAttribute('data-pair-tone');
          rightBtn.classList.remove('is-paired');
        }
      }
    }

    function clearPairForRight(rightBtn) {
      const leftId = rightBtn.dataset.pairedLeft;
      if (!leftId) return;
      const leftBtn = board.querySelector('.chit-match-item--left[data-left-id="' + leftId + '"]');
      if (leftBtn) clearPairForLeft(leftBtn);
    }

    function pair(leftBtn, rightBtn) {
      clearPairForLeft(leftBtn);
      clearPairForRight(rightBtn);
      const tone = nextTone();
      leftBtn.dataset.paired = rightBtn.dataset.rightId;
      leftBtn.dataset.pairTone = tone;
      leftBtn.classList.add('is-paired');
      rightBtn.dataset.pairedLeft = leftBtn.dataset.leftId;
      rightBtn.dataset.pairTone = tone;
      rightBtn.classList.add('is-paired');
      clearActive();
      redrawMatchLines(board);
      notifyFormChange(formId);
    }

    board.addEventListener('click', function (event) {
      const leftBtn = event.target.closest('.chit-match-item--left');
      if (leftBtn && board.contains(leftBtn)) {
        if (leftBtn.classList.contains('is-paired') && activeLeft !== leftBtn) {
          clearPairForLeft(leftBtn);
          redrawMatchLines(board);
          notifyFormChange(formId);
          clearActive();
          return;
        }
        if (activeLeft === leftBtn) {
          clearActive();
          return;
        }
        clearActive();
        activeLeft = leftBtn;
        leftBtn.classList.add('is-active');
        board.classList.add('has-active-left');
        return;
      }

      const rightBtn = event.target.closest('.chit-match-item--right');
      if (rightBtn && board.contains(rightBtn)) {
        if (!activeLeft) {
          if (rightBtn.classList.contains('is-paired')) {
            clearPairForRight(rightBtn);
            redrawMatchLines(board);
            notifyFormChange(formId);
          }
          return;
        }
        pair(activeLeft, rightBtn);
      }
    });

    window.addEventListener('resize', function () {
      redrawMatchLines(board);
    });
    if (typeof ResizeObserver !== 'undefined') {
      const ro = new ResizeObserver(function () { redrawMatchLines(board); });
      ro.observe(board);
    }
  }

  function renderMatching(formId, q, idx) {
    const div = document.createElement('div');
    div.className = 'chit-q chit-q-matching';
    div.dataset.qid = q.id;
    div.dataset.qtype = 'matching';
    appendQuestionHeader(div, q, idx);

    const tip = document.createElement('p');
    tip.className = 'chit-match-tip';
    tip.textContent = q.match_tip || q.tip || 'Нажми слева, потом справа — стрелка покажет пару.';
    div.appendChild(tip);

    const board = document.createElement('div');
    board.className = 'chit-match-board';
    const matchWithImages = optionHasImages(q.left);
    if (matchWithImages) {
      div.classList.add('chit-q-with-images');
      board.classList.add('chit-match-board--images');
    }

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.classList.add('chit-match-lines');
    svg.setAttribute('aria-hidden', 'true');
    board.appendChild(svg);

    const cols = document.createElement('div');
    cols.className = 'chit-match-cols';

    const leftCol = document.createElement('div');
    leftCol.className = 'chit-match-col chit-match-col--left';
    leftCol.setAttribute('aria-label', 'Герои');
    (q.left || []).forEach(function (left) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chit-match-item chit-match-item--left';
      btn.dataset.leftId = left.id;
      btn.innerHTML = renderMatchItemContent(left, matchWithImages);
      leftCol.appendChild(btn);
    });

    const rightCol = document.createElement('div');
    rightCol.className = 'chit-match-col chit-match-col--right';
    rightCol.setAttribute('aria-label', 'Варианты');
    (q.right || []).forEach(function (right) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chit-match-item chit-match-item--right';
      btn.dataset.rightId = right.id;
      btn.innerHTML = renderMatchItemContent(right, false);
      rightCol.appendChild(btn);
    });

    cols.appendChild(leftCol);
    cols.appendChild(rightCol);
    board.appendChild(cols);
    div.appendChild(board);
    attachMatchBoard(board, formId);
    requestAnimationFrame(function () { redrawMatchLines(board); });
    return div;
  }

  function shuffleItems(items) {
    const copy = (items || []).slice();
    for (let i = copy.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = copy[i];
      copy[i] = copy[j];
      copy[j] = tmp;
    }
    return copy;
  }

  function renderOrderCardContent(item, withImages) {
    if (withImages && item.image) {
      const alt = item.alt || item.text || '';
      return (
        '<span class="chit-order-media">' +
        '<img class="chit-order-img" src="' + escapeHtml(item.image) + '" alt="' + escapeHtml(alt) + '" loading="lazy" draggable="false">' +
        '</span>'
      );
    }
    return '<span class="chit-order-text">' + escapeHtml(item.text) + '</span>';
  }

  function attachOrderBoard(board) {
    const pool = board.querySelector('.chit-order-pool-cards');
    const drops = board.querySelectorAll('.chit-order-slot-drop');
    let selectedCard = null;

    function clearSelection() {
      if (!selectedCard) return;
      selectedCard.classList.remove('chit-order-card--selected');
      selectedCard = null;
    }

    function selectCard(card) {
      if (selectedCard === card) {
        clearSelection();
        return;
      }
      clearSelection();
      selectedCard = card;
      card.classList.add('chit-order-card--selected');
    }

    function cardDropZone(card) {
      return card.closest('.chit-order-slot-drop, .chit-order-pool-cards');
    }

    function findCard(itemId) {
      return board.querySelector('.chit-order-card[data-item-id="' + itemId + '"]');
    }

    function notifyChange() {
      clearSelection();
      board.dispatchEvent(new CustomEvent('chit-order-change', { bubbles: true }));
    }

    function returnToPool(card) {
      pool.appendChild(card);
    }

    function placeCard(card, targetDrop) {
      if (!card || !targetDrop) return;
      const existing = targetDrop.querySelector('.chit-order-card');
      if (existing && existing !== card && targetDrop.classList.contains('chit-order-slot-drop')) {
        returnToPool(existing);
      }
      targetDrop.appendChild(card);
      notifyChange();
    }

    board.querySelectorAll('.chit-order-card').forEach(function (card) {
      card.addEventListener('dragstart', function (event) {
        card.classList.add('chit-order-card--dragging');
        event.dataTransfer.effectAllowed = 'move';
        event.dataTransfer.setData('text/plain', card.dataset.itemId);
      });
      card.addEventListener('dragend', function () {
        card.classList.remove('chit-order-card--dragging');
        drops.forEach(function (drop) { drop.classList.remove('chit-order-slot-drop--over'); });
        pool.classList.remove('chit-order-pool-cards--over');
      });
      card.addEventListener('click', function (event) {
        event.stopPropagation();
        selectCard(card);
      });
    });

    drops.forEach(function (drop) {
      drop.addEventListener('dragover', function (event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'move';
        drop.classList.add('chit-order-slot-drop--over');
      });
      drop.addEventListener('dragleave', function () {
        drop.classList.remove('chit-order-slot-drop--over');
      });
      drop.addEventListener('drop', function (event) {
        event.preventDefault();
        drop.classList.remove('chit-order-slot-drop--over');
        const card = findCard(event.dataTransfer.getData('text/plain'));
        if (card) placeCard(card, drop);
      });
      drop.addEventListener('click', function () {
        if (selectedCard) placeCard(selectedCard, drop);
      });
    });

    pool.addEventListener('dragover', function (event) {
      event.preventDefault();
      event.dataTransfer.dropEffect = 'move';
      pool.classList.add('chit-order-pool-cards--over');
    });
    pool.addEventListener('dragleave', function (event) {
      if (!pool.contains(event.relatedTarget)) {
        pool.classList.remove('chit-order-pool-cards--over');
      }
    });
    pool.addEventListener('drop', function (event) {
      event.preventDefault();
      pool.classList.remove('chit-order-pool-cards--over');
      const card = findCard(event.dataTransfer.getData('text/plain'));
      if (card) {
        returnToPool(card);
        notifyChange();
      }
    });
    pool.addEventListener('click', function (event) {
      if (!selectedCard || event.target.closest('.chit-order-card')) return;
      if (cardDropZone(selectedCard) !== pool) {
        returnToPool(selectedCard);
        notifyChange();
      }
    });
  }

  function renderOrdering(formId, q, idx) {
    const div = document.createElement('div');
    const withImages = optionHasImages(q.items);
    const items = q.items || [];
    div.className = withImages ? 'chit-q chit-q-ordering chit-q-ordering-images' : 'chit-q chit-q-ordering';
    div.dataset.qid = q.id;
    div.dataset.qtype = 'ordering';
    const slotCount = items.length;
    appendPromptImage(div, q);
    appendQuestionHeader(div, q, idx);
    if (!q.hint) {
      const instruction = document.createElement('p');
      instruction.className = 'chit-order-instruction';
      instruction.textContent = withImages
        ? ('Перетащи картинки в ячейки 1–' + slotCount + ' по порядку сказки. На телефоне: нажми на картинку, затем на ячейку.')
        : 'Перетащи события в ячейки по порядку сказки. На телефоне: нажми на событие, затем на ячейку.';
      div.appendChild(instruction);
    }

    const board = document.createElement('div');
    board.className = 'chit-order-board';
    board.dataset.orderBoard = q.id;

    const slotsWrap = document.createElement('div');
    slotsWrap.className = 'chit-order-slots';
    // Два ряда: для 6 → 3+3, для 5 → 3+2, для 4 → 2+2
    const cols = slotCount <= 3 ? slotCount : Math.ceil(slotCount / 2);
    slotsWrap.dataset.cols = String(cols);
    slotsWrap.setAttribute('role', 'list');
    items.forEach(function (_item, slotIdx) {
      const slot = document.createElement('div');
      slot.className = 'chit-order-slot';
      slot.dataset.slot = String(slotIdx + 1);
      slot.setAttribute('role', 'listitem');
      const num = document.createElement('span');
      num.className = 'chit-order-slot-num';
      num.textContent = String(slotIdx + 1);
      num.setAttribute('aria-hidden', 'true');
      const drop = document.createElement('div');
      drop.className = 'chit-order-slot-drop';
      drop.setAttribute('role', 'button');
      drop.setAttribute('aria-label', 'Ячейка ' + (slotIdx + 1));
      drop.tabIndex = 0;
      slot.appendChild(num);
      slot.appendChild(drop);
      slotsWrap.appendChild(slot);
    });
    board.appendChild(slotsWrap);

    const poolWrap = document.createElement('div');
    poolWrap.className = 'chit-order-pool';
    const poolLabel = document.createElement('p');
    poolLabel.className = 'chit-order-pool-label';
    poolLabel.textContent = withImages ? 'Картинки' : 'События';
    poolWrap.appendChild(poolLabel);
    const pool = document.createElement('div');
    pool.className = 'chit-order-pool-cards';
    pool.setAttribute('aria-label', 'Запас картинок');
    shuffleItems(items).forEach(function (item) {
      const card = document.createElement('div');
      card.className = withImages ? 'chit-order-card chit-order-card--image' : 'chit-order-card';
      card.dataset.itemId = item.id;
      card.draggable = true;
      card.tabIndex = 0;
      card.innerHTML = renderOrderCardContent(item, withImages);
      pool.appendChild(card);
    });
    poolWrap.appendChild(pool);
    board.appendChild(poolWrap);
    div.appendChild(board);
    attachOrderBoard(board);
    return div;
  }

  function renderPictureMatch(formId, q, idx) {
    const div = document.createElement('div');
    div.className = 'chit-q chit-q-matching chit-q-pictures chit-q-with-images';
    div.dataset.qid = q.id;
    div.dataset.qtype = 'picture_match';
    appendQuestionHeader(div, q, idx);

    const tip = document.createElement('p');
    tip.className = 'chit-match-tip';
    tip.textContent = q.match_tip || q.tip || 'Нажми фото слева, потом имя справа. Стрелка покажет пару.';
    div.appendChild(tip);

    const board = document.createElement('div');
    board.className = 'chit-match-board chit-match-board--images chit-match-board--pictures';

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.classList.add('chit-match-lines');
    svg.setAttribute('aria-hidden', 'true');
    board.appendChild(svg);

    const cols = document.createElement('div');
    cols.className = 'chit-match-cols';

    const leftCol = document.createElement('div');
    leftCol.className = 'chit-match-col chit-match-col--left';
    leftCol.setAttribute('aria-label', 'Фото');
    (q.pictures || []).forEach(function (pic, picIdx) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chit-match-item chit-match-item--left chit-match-item--photo';
      btn.dataset.leftId = pic.id;
      const alt = pic.alt || ('Фото ' + (picIdx + 1));
      btn.innerHTML =
        '<span class="chit-match-photo-num">' + (picIdx + 1) + '</span>' +
        '<span class="chit-opt-img-wrap">' +
        '<img class="chit-opt-img" src="' + escapeHtml(pic.image) + '" alt="' + escapeHtml(alt) + '" loading="lazy">' +
        '</span>';
      leftCol.appendChild(btn);
    });

    const rightCol = document.createElement('div');
    rightCol.className = 'chit-match-col chit-match-col--right';
    rightCol.setAttribute('aria-label', 'Имена');
    (q.labels || []).forEach(function (label) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chit-match-item chit-match-item--right';
      btn.dataset.rightId = label.id;
      btn.innerHTML = '<span class="chit-match-item-text">' + escapeHtml(label.text) + '</span>';
      rightCol.appendChild(btn);
    });

    cols.appendChild(leftCol);
    cols.appendChild(rightCol);
    board.appendChild(cols);
    div.appendChild(board);
    attachMatchBoard(board, formId);
    requestAnimationFrame(function () { redrawMatchLines(board); });
    return div;
  }

  function renderQuestion(formId, q, idx) {
    const type = q.type || 'single';
    if (type === 'multi') return renderSingleOrMulti(formId, q, idx, true);
    if (type === 'true_false') return renderTrueFalse(formId, q, idx);
    if (type === 'matching') return renderMatching(formId, q, idx);
    if (type === 'ordering') return renderOrdering(formId, q, idx);
    if (type === 'picture_match') return renderPictureMatch(formId, q, idx);
    return renderSingleOrMulti(formId, q, idx, false);
  }

  function collectSingleAnswer(formId, q) {
    const picked = document.querySelector('#' + formId + ' input[name="' + q.id + '"]:checked');
    return picked ? picked.value : null;
  }

  function collectMultiAnswer(formId, q) {
    const nodes = document.querySelectorAll('#' + formId + ' input[name="' + formId + '-' + q.id + '"]:checked');
    if (!nodes.length) return null;
    return Array.prototype.map.call(nodes, function (node) { return node.value; });
  }

  function collectMatchingAnswer(formId, q) {
    const map = {};
    let complete = true;
    const root = document.querySelector('#' + formId + ' .chit-q-matching[data-qid="' + q.id + '"]');
    (q.left || []).forEach(function (left) {
      const leftBtn = root
        ? root.querySelector('.chit-match-item--left[data-left-id="' + left.id + '"]')
        : null;
      const value = leftBtn && leftBtn.dataset.paired ? leftBtn.dataset.paired : '';
      if (!value) {
        complete = false;
        return;
      }
      map[left.id] = value;
    });
    return complete ? map : null;
  }

  function collectOrderingAnswer(formId, q) {
    const board = document.querySelector('#' + formId + ' [data-order-board="' + q.id + '"]');
    if (!board) return null;
    const order = [];
    const slots = board.querySelectorAll('.chit-order-slot-drop');
    for (let i = 0; i < slots.length; i += 1) {
      const card = slots[i].querySelector('.chit-order-card');
      if (!card) return null;
      order.push(card.dataset.itemId);
    }
    return order.length ? order : null;
  }

  function collectPictureMatchAnswer(formId, q) {
    const map = {};
    let complete = true;
    const root = document.querySelector('#' + formId + ' .chit-q-pictures[data-qid="' + q.id + '"]');
    (q.pictures || []).forEach(function (pic) {
      const leftBtn = root
        ? root.querySelector('.chit-match-item--left[data-left-id="' + pic.id + '"]')
        : null;
      const value = leftBtn && leftBtn.dataset.paired ? leftBtn.dataset.paired : '';
      if (!value) {
        complete = false;
        return;
      }
      map[pic.id] = value;
    });
    return complete ? map : null;
  }

  function collectQuestionAnswer(formId, q) {
    const type = q.type || 'single';
    if (type === 'multi' || type === 'true_false') return collectMultiAnswer(formId, q);
    if (type === 'matching') return collectMatchingAnswer(formId, q);
    if (type === 'ordering') return collectOrderingAnswer(formId, q);
    if (type === 'picture_match') return collectPictureMatchAnswer(formId, q);
    return collectSingleAnswer(formId, q);
  }

  function render(formId, quiz) {
    const form = document.getElementById(formId);
    if (!form || !quiz) return;
    form.innerHTML = '';
    (quiz.questions || []).forEach(function (q, idx) {
      form.appendChild(renderQuestion(formId, q, idx));
    });
  }

  function collect(formId, quiz) {
    const answers = {};
    for (const q of quiz.questions || []) {
      const value = collectQuestionAnswer(formId, q);
      if (value == null || (Array.isArray(value) && !value.length)) return null;
      answers[q.id] = value;
    }
    return answers;
  }

  function missingQuestions(formId, quiz) {
    const missing = [];
    (quiz.questions || []).forEach(function (q, idx) {
      const value = collectQuestionAnswer(formId, q);
      if (value == null || (Array.isArray(value) && !value.length)) {
        missing.push({ index: idx + 1, question: q });
      }
    });
    return missing;
  }

  global.ChitLessonQuiz = {
    render: render,
    collect: collect,
    missingQuestions: missingQuestions,
  };
})(window);
