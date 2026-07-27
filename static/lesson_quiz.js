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

  function renderMatching(formId, q, idx) {
    const div = document.createElement('div');
    div.className = 'chit-q chit-q-matching';
    div.dataset.qid = q.id;
    div.dataset.qtype = 'matching';
    appendQuestionHeader(div, q, idx);
    const table = document.createElement('div');
    table.className = 'chit-match-grid';
    const matchWithImages = optionHasImages(q.left);
    if (matchWithImages) div.classList.add('chit-q-with-images');
    (q.left || []).forEach(function (left) {
      const row = document.createElement('div');
      row.className = 'chit-match-row';
      row.dataset.leftId = left.id;
      const label = document.createElement('span');
      label.className = matchWithImages ? 'chit-match-left chit-opt-card chit-match-card' : 'chit-match-left';
      if (matchWithImages && left.image) {
        label.innerHTML = renderOptionImage(left) + '<span class="chit-opt-caption">' + escapeHtml(left.text) + '</span>';
      } else {
        label.textContent = left.text;
      }
      const choices = renderChoiceChips(formId, q, left.id, q.right, '');
      choices.dataset.leftId = left.id;
      choices.dataset.selected = '';
      row.appendChild(label);
      row.appendChild(choices);
      table.appendChild(row);
    });
    div.appendChild(table);
    attachExclusiveChoices(div, formId);
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
    div.className = 'chit-q chit-q-pictures';
    div.dataset.qid = q.id;
    div.dataset.qtype = 'picture_match';
    appendQuestionHeader(div, q, idx);
    const grid = document.createElement('div');
    grid.className = 'chit-picture-grid';
    (q.pictures || []).forEach(function (pic, picIdx) {
      const card = document.createElement('div');
      card.className = 'chit-picture-card';
      card.dataset.pictureId = pic.id;
      const badge = document.createElement('span');
      badge.className = 'chit-picture-num';
      badge.textContent = String(picIdx + 1);
      card.appendChild(badge);
      const img = document.createElement('img');
      img.src = pic.image;
      img.alt = pic.alt || '';
      img.loading = 'lazy';
      card.appendChild(img);
      const choices = renderChoiceChips(formId, q, pic.id, q.labels, '');
      choices.dataset.pictureId = pic.id;
      choices.dataset.selected = '';
      choices.classList.add('chit-match-choices--compact');
      card.appendChild(choices);
      grid.appendChild(card);
    });
    div.appendChild(grid);
    attachExclusiveChoices(div, formId);
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
      const group = root
        ? root.querySelector('.chit-match-choices[data-left-id="' + left.id + '"]')
        : null;
      const value = group && group.dataset.selected ? group.dataset.selected : '';
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
      const group = root
        ? root.querySelector('.chit-match-choices[data-picture-id="' + pic.id + '"]')
        : null;
      const value = group && group.dataset.selected ? group.dataset.selected : '';
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
