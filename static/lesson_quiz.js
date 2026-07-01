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

  function renderSingleOrMulti(formId, q, idx, multi) {
    const div = document.createElement('div');
    div.className = 'chit-q';
    div.dataset.qid = q.id;
    div.dataset.qtype = q.type || 'single';
    let html = '<strong>' + (idx + 1) + '. ' + escapeHtml(q.text) + '</strong>';
    if (q.hint) html += '<p class="chit-q-hint">' + escapeHtml(q.hint) + '</p>';
    div.innerHTML = html;
    (q.options || []).forEach(function (opt) {
      const id = formId + '-' + q.id + '-' + opt.id;
      const inputType = multi ? 'checkbox' : 'radio';
      const name = multi ? formId + '-' + q.id : q.id;
      const label = document.createElement('label');
      label.innerHTML =
        '<input type="' + inputType + '" name="' + name + '" value="' + escapeHtml(opt.id) + '" id="' + id + '"> ' +
        escapeHtml(opt.text);
      div.appendChild(label);
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
    (q.left || []).forEach(function (left) {
      const row = document.createElement('div');
      row.className = 'chit-match-row';
      const label = document.createElement('span');
      label.className = 'chit-match-left';
      label.textContent = left.text;
      const select = document.createElement('select');
      select.name = formId + '-' + q.id + '-' + left.id;
      select.dataset.leftId = left.id;
      select.innerHTML = '<option value="">— выбери место —</option>';
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

  function renderOrdering(formId, q, idx) {
    const div = document.createElement('div');
    div.className = 'chit-q chit-q-ordering';
    div.dataset.qid = q.id;
    div.dataset.qtype = 'ordering';
    let html = '<strong>' + (idx + 1) + '. ' + escapeHtml(q.text) + '</strong>';
    if (q.hint) html += '<p class="chit-q-hint">' + escapeHtml(q.hint) + '</p>';
    div.innerHTML = html;
    const list = document.createElement('ol');
    list.className = 'chit-order-list';
    list.dataset.orderList = q.id;
    (q.items || []).forEach(function (item) {
      const li = document.createElement('li');
      li.className = 'chit-order-item';
      li.dataset.itemId = item.id;
      li.innerHTML =
        '<span class="chit-order-text">' + escapeHtml(item.text) + '</span>' +
        '<span class="chit-order-actions">' +
        '<button type="button" class="chit-order-btn" data-dir="up" aria-label="Выше">↑</button>' +
        '<button type="button" class="chit-order-btn" data-dir="down" aria-label="Ниже">↓</button>' +
        '</span>';
      list.appendChild(li);
    });
    div.appendChild(list);
    list.addEventListener('click', function (event) {
      const btn = event.target.closest('.chit-order-btn');
      if (!btn) return;
      const item = btn.closest('.chit-order-item');
      if (!item) return;
      const dir = btn.dataset.dir;
      if (dir === 'up' && item.previousElementSibling) {
        list.insertBefore(item, item.previousElementSibling);
      } else if (dir === 'down' && item.nextElementSibling) {
        list.insertBefore(item.nextElementSibling, item);
      }
    });
    return div;
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
    (q.pictures || []).forEach(function (pic) {
      const card = document.createElement('div');
      card.className = 'chit-picture-card';
      const img = document.createElement('img');
      img.src = pic.image;
      img.alt = pic.alt || '';
      img.loading = 'lazy';
      card.appendChild(img);
      const select = document.createElement('select');
      select.name = formId + '-' + q.id + '-' + pic.id;
      select.dataset.pictureId = pic.id;
      select.innerHTML = '<option value="">— кто это? —</option>';
      (q.labels || []).forEach(function (label) {
        const opt = document.createElement('option');
        opt.value = label.id;
        opt.textContent = label.text;
        select.appendChild(opt);
      });
      card.appendChild(select);
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
    const list = document.querySelector('#' + formId + ' ol[data-order-list="' + q.id + '"]');
    if (!list) return null;
    return Array.prototype.map.call(
      list.querySelectorAll('.chit-order-item'),
      function (item) { return item.dataset.itemId; }
    );
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

  global.ChitLessonQuiz = {
    render: render,
    collect: collect,
  };
})(window);
