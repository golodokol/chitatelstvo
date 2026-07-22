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

  function renderSingleOrMulti(formId, q, idx, multi) {
    const div = document.createElement('div');
    const withImages = optionHasImages(q.options);
    div.className = withImages ? 'chit-q chit-q-with-images' : 'chit-q';
    div.dataset.qid = q.id;
    div.dataset.qtype = q.type || 'single';
    let html = '<strong>' + (idx + 1) + '. ' + escapeHtml(q.text) + '</strong>';
    if (q.hint) html += '<p class="chit-q-hint">' + escapeHtml(q.hint) + '</p>';
    div.innerHTML = html;
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
    let html = '<strong>' + (idx + 1) + '. ' + escapeHtml(q.text) + '</strong>';
    if (q.hint) html += '<p class="chit-q-hint">' + escapeHtml(q.hint) + '</p>';
    div.innerHTML = html;
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

  function renderMatching(formId, q, idx) {
    const div = document.createElement('div');
    div.className = 'chit-q chit-q-matching';
    div.dataset.qid = q.id;
    div.dataset.qtype = 'matching';
    let html = '<strong>' + (idx + 1) + '. ' + escapeHtml(q.text) + '</strong>';
    if (q.hint) html += '<p class="chit-q-hint">' + escapeHtml(q.hint) + '</p>';
    div.innerHTML = html;
    const table = document.createElement('div');
    table.className = 'chit-match-grid';
    const matchWithImages = optionHasImages(q.left);
    if (matchWithImages) div.classList.add('chit-q-with-images');
    (q.left || []).forEach(function (left) {
      const row = document.createElement('div');
      row.className = 'chit-match-row';
      const label = document.createElement('span');
      label.className = matchWithImages ? 'chit-match-left chit-opt-card chit-match-card' : 'chit-match-left';
      if (matchWithImages && left.image) {
        label.innerHTML = renderOptionImage(left) + '<span class="chit-opt-caption">' + escapeHtml(left.text) + '</span>';
      } else {
        label.textContent = left.text;
      }
      const select = document.createElement('select');
      select.className = 'chit-q-select chit-match-select';
      select.name = formId + '-' + q.id + '-' + left.id;
      select.dataset.leftId = left.id;
      const matchPrompt = (function () {
        if (q.select_prompt) return q.select_prompt;
        const t = String(q.text || '') + ' ' + String(q.hint || '');
        const low = t.toLowerCase();
        if (low.indexOf('желани') !== -1 || low.indexOf('просил') !== -1) return '— выбери желание —';
        if (low.indexOf('действие') !== -1 || low.indexOf('делает') !== -1 || low.indexOf('героя') !== -1) {
          return '— выбери действие —';
        }
        if (low.indexOf('черт') !== -1) return '— выбери главную черту —';
        if (low.indexOf('поступ') !== -1 || low.indexOf('привёл') !== -1 || low.indexOf('привел') !== -1) {
          return '— выбери последствие —';
        }
        if (low.indexOf('конец') !== -1 || low.indexOf('начала') !== -1 || low.indexOf('начало') !== -1) {
          return '— выбери конец —';
        }
        return '— выбери уместное —';
      })();
      select.innerHTML = '<option value="">' + escapeHtml(matchPrompt) + '</option>';
      (q.right || []).forEach(function (right) {
        const opt = document.createElement('option');
        opt.value = right.id;
        opt.textContent = right.text;
        select.appendChild(opt);
      });
      row.appendChild(label);
      row.appendChild(select);
      table.appendChild(row);
    });
    div.appendChild(table);
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
    let html = '<strong>' + (idx + 1) + '. ' + escapeHtml(q.text) + '</strong>';
    if (q.hint) {
      html += '<p class="chit-q-hint">' + escapeHtml(q.hint) + '</p>';
    } else {
      const instruction = withImages
        ? ('Перетащи картинки в ячейки 1–' + slotCount + ' по порядку сказки. На телефоне: нажми на картинку, затем на ячейку.')
        : 'Перетащи события в ячейки по порядку сказки. На телефоне: нажми на событие, затем на ячейку.';
      html += '<p class="chit-order-instruction">' + instruction + '</p>';
    }
    div.innerHTML = html;

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

  function pictureMatchPlaceholder(q) {
    if (q.select_prompt) return q.select_prompt;
    const text = String(q.text || '').toLowerCase();
    if (text.indexOf('что') !== -1) return '— что это? —';
    return '— кто это? —';
  }

  function renderPictureMatch(formId, q, idx) {
    const div = document.createElement('div');
    div.className = 'chit-q chit-q-pictures';
    div.dataset.qid = q.id;
    div.dataset.qtype = 'picture_match';
    let html = '<strong>' + (idx + 1) + '. ' + escapeHtml(q.text) + '</strong>';
    if (q.hint) html += '<p class="chit-q-hint">' + escapeHtml(q.hint) + '</p>';
    div.innerHTML = html;
    const grid = document.createElement('div');
    grid.className = 'chit-picture-grid';
    const placeholder = pictureMatchPlaceholder(q);
    (q.pictures || []).forEach(function (pic, picIdx) {
      const card = document.createElement('div');
      card.className = 'chit-picture-card';
      const badge = document.createElement('span');
      badge.className = 'chit-picture-num';
      badge.textContent = String(picIdx + 1);
      card.appendChild(badge);
      const img = document.createElement('img');
      img.src = pic.image;
      img.alt = pic.alt || '';
      img.loading = 'lazy';
      card.appendChild(img);
      const select = document.createElement('select');
      select.className = 'chit-q-select chit-picture-select';
      select.name = formId + '-' + q.id + '-' + pic.id;
      select.dataset.pictureId = pic.id;
      select.innerHTML = '<option value="">' + escapeHtml(placeholder) + '</option>';
      (q.labels || []).forEach(function (label) {
        const opt = document.createElement('option');
        opt.value = label.id;
        opt.textContent = label.text;
        select.appendChild(opt);
      });
      card.appendChild(select);
      select.addEventListener('change', function () {
        const form = document.getElementById(formId);
        if (form) form.dispatchEvent(new Event('change', { bubbles: true }));
      });
      grid.appendChild(card);
    });
    div.appendChild(grid);
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
    (q.left || []).forEach(function (left) {
      const select = document.querySelector(
        '#' + formId + ' select[name="' + formId + '-' + q.id + '-' + left.id + '"]'
      );
      if (!select || !select.value) {
        complete = false;
        return;
      }
      map[left.id] = select.value;
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
    (q.pictures || []).forEach(function (pic) {
      const select = document.querySelector(
        '#' + formId + ' select[name="' + formId + '-' + q.id + '-' + pic.id + '"]'
      );
      if (!select || !select.value) {
        complete = false;
        return;
      }
      map[pic.id] = select.value;
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
