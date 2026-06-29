(function (global) {
  var VIEW = 1000;
  var CX = VIEW / 2;
  var CY = VIEW / 2;
  var R_INNER = 72;
  var R_OUTER = 492;
  var DEFAULT_IMAGE = '/static/images/emotion-wheel.png';

  function toRad(deg) {
    return ((deg - 90) * Math.PI) / 180;
  }

  function sectorPath(startDeg, endDeg) {
    var x1o = CX + R_OUTER * Math.cos(toRad(startDeg));
    var y1o = CY + R_OUTER * Math.sin(toRad(startDeg));
    var x2o = CX + R_OUTER * Math.cos(toRad(endDeg));
    var y2o = CY + R_OUTER * Math.sin(toRad(endDeg));
    var x1i = CX + R_INNER * Math.cos(toRad(startDeg));
    var y1i = CY + R_INNER * Math.sin(toRad(startDeg));
    var x2i = CX + R_INNER * Math.cos(toRad(endDeg));
    var y2i = CY + R_INNER * Math.sin(toRad(endDeg));
    var large = endDeg - startDeg > 180 ? 1 : 0;
    return 'M ' + x1i + ' ' + y1i +
      ' L ' + x1o + ' ' + y1o +
      ' A ' + R_OUTER + ' ' + R_OUTER + ' 0 ' + large + ' 1 ' + x2o + ' ' + y2o +
      ' L ' + x2i + ' ' + y2i +
      ' A ' + R_INNER + ' ' + R_INNER + ' 0 ' + large + ' 0 ' + x1i + ' ' + y1i +
      ' Z';
  }

  function init(container, options) {
    var emotions = options.emotions || [];
    var pickN = parseInt(options.pick, 10) || 1;
    var imageUrl = options.imageUrl || DEFAULT_IMAGE;
    var sectorOffset = Number(options.sectorOffset) || 0;
    var selected = new Set();
    var onChange = options.onChange || function () {};
    var sectorCount = emotions.length || 10;
    var step = 360 / sectorCount;

    container.innerHTML = '';
    container.classList.add('chit-emotion-wheel');

    var stage = document.createElement('div');
    stage.className = 'chit-emotion-wheel__stage';

    var art = document.createElement('img');
    art.className = 'chit-emotion-wheel__art';
    art.src = imageUrl;
    art.alt = 'Колесо эмоций — нажми на лепесток, чтобы выбрать чувство';
    art.setAttribute('draggable', 'false');
    stage.appendChild(art);

    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 ' + VIEW + ' ' + VIEW);
    svg.setAttribute('class', 'chit-emotion-wheel__overlay');
    svg.setAttribute('role', 'group');
    svg.setAttribute('aria-label', 'Выбор эмоции на колесе');

    var gSectors = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gSectors.setAttribute('class', 'chit-emotion-wheel__sectors');

    emotions.forEach(function (emo, i) {
      var start = sectorOffset + i * step;
      var end = start + step;
      var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', sectorPath(start, end));
      path.setAttribute('class', 'chit-emotion-wheel__sector');
      path.setAttribute('data-id', emo.id);
      path.setAttribute('data-color', emo.color || '#ffffff');
      path.setAttribute('tabindex', '0');
      path.setAttribute('role', 'button');
      path.setAttribute('aria-label', emo.label);
      path.setAttribute('aria-pressed', 'false');

      path.addEventListener('click', function () { toggle(emo.id); });
      path.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggle(emo.id);
        }
      });

      gSectors.appendChild(path);
    });

    svg.appendChild(gSectors);
    stage.appendChild(svg);
    container.appendChild(stage);

    var chips = document.createElement('div');
    chips.className = 'chit-emotion-chips';
    chips.setAttribute('role', 'group');
    chips.setAttribute('aria-label', 'Эмоции — список для выбора');

    emotions.forEach(function (emo) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'chit-emotion-chip';
      btn.dataset.id = emo.id;
      btn.textContent = emo.label;
      btn.style.setProperty('--chip-color', emo.color);
      btn.addEventListener('click', function () { toggle(emo.id); });
      chips.appendChild(btn);
    });
    container.appendChild(chips);

    var pickedEl = document.createElement('p');
    pickedEl.className = 'chit-emotion-picked';
    pickedEl.setAttribute('aria-live', 'polite');
    container.appendChild(pickedEl);

    function emotionLabel(id) {
      var found = emotions.find(function (e) { return e.id === id; });
      return found ? found.label : id;
    }

    function renderPicked() {
      if (!selected.size) {
        pickedEl.textContent = pickN === 1
          ? 'Нажми на лепесток колеса'
          : 'Нажми на ' + pickN + ' лепестка на колесе';
        return;
      }
      var names = Array.from(selected).map(emotionLabel);
      pickedEl.textContent = 'Выбрано: ' + names.join(', ');
    }

    function selectionComplete() {
      return selected.size === pickN;
    }

    function syncSectorVisual(node, id, on) {
      var color = node.getAttribute('data-color') || '#fff';
      if (on) {
        node.style.fill = color;
        node.style.fillOpacity = '0.42';
      } else if (!node.classList.contains('is-correct') && !node.classList.contains('is-wrong')) {
        node.style.fill = '';
        node.style.fillOpacity = '';
      }
    }

    function syncUI() {
      container.querySelectorAll('.chit-emotion-wheel__sector').forEach(function (node) {
        var id = node.getAttribute('data-id');
        var on = selected.has(id);
        node.classList.toggle('is-selected', on);
        node.setAttribute('aria-pressed', on ? 'true' : 'false');
        syncSectorVisual(node, id, on);
      });
      container.querySelectorAll('.chit-emotion-chip').forEach(function (node) {
        node.classList.toggle('is-selected', selected.has(node.dataset.id));
        node.setAttribute('aria-pressed', selected.has(node.dataset.id) ? 'true' : 'false');
      });
      renderPicked();
      onChange(Array.from(selected), selectionComplete());
    }

    function toggle(id) {
      if (selected.has(id)) {
        selected.delete(id);
      } else if (selected.size < pickN) {
        selected.add(id);
      } else if (pickN === 1) {
        selected.clear();
        selected.add(id);
      } else {
        container.classList.add('is-shake');
        setTimeout(function () { container.classList.remove('is-shake'); }, 400);
        return;
      }
      syncUI();
    }

    function getSelected() {
      return Array.from(selected);
    }

    function setSelected(ids) {
      selected = new Set(ids);
      syncUI();
    }

    function markResult(correctIds, ok) {
      var correct = new Set(correctIds || []);
      container.querySelectorAll('.chit-emotion-wheel__sector').forEach(function (node) {
        var id = node.getAttribute('data-id');
        node.classList.remove('is-correct', 'is-wrong');
        if (ok && correct.has(id)) node.classList.add('is-correct');
        if (!ok && selected.has(id) && !correct.has(id)) node.classList.add('is-wrong');
        if (!ok && correct.has(id)) node.classList.add('is-correct');
        syncSectorVisual(node, id, selected.has(id));
      });
      container.querySelectorAll('.chit-emotion-chip').forEach(function (node) {
        var id = node.dataset.id;
        node.classList.remove('is-correct', 'is-wrong');
        if (ok && correct.has(id)) node.classList.add('is-correct');
        if (!ok && selected.has(id) && !correct.has(id)) node.classList.add('is-wrong');
        if (!ok && correct.has(id)) node.classList.add('is-correct');
      });
    }

    function clearResult() {
      container.querySelectorAll('.chit-emotion-wheel__sector, .chit-emotion-chip').forEach(function (node) {
        node.classList.remove('is-correct', 'is-wrong');
        if (node.classList.contains('chit-emotion-wheel__sector')) {
          node.style.fill = '';
          node.style.fillOpacity = '';
        }
      });
      syncUI();
    }

    syncUI();

    return {
      getSelected: getSelected,
      setSelected: setSelected,
      markResult: markResult,
      clearResult: clearResult,
      isComplete: selectionComplete,
    };
  }

  global.ChitEmotionWheel = { init: init };
})(window);
