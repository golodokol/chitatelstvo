(function (global) {
  var SECTOR_COUNT = 9;
  var CX = 200;
  var CY = 200;
  var R = 178;
  var LABEL_R = 128;

  function toRad(deg) {
    return ((deg - 90) * Math.PI) / 180;
  }

  function sectorPath(startDeg, endDeg) {
    var x1 = CX + R * Math.cos(toRad(startDeg));
    var y1 = CY + R * Math.sin(toRad(startDeg));
    var x2 = CX + R * Math.cos(toRad(endDeg));
    var y2 = CY + R * Math.sin(toRad(endDeg));
    var large = endDeg - startDeg > 180 ? 1 : 0;
    return 'M ' + CX + ' ' + CY + ' L ' + x1 + ' ' + y1 +
      ' A ' + R + ' ' + R + ' 0 ' + large + ' 1 ' + x2 + ' ' + y2 + ' Z';
  }

  function labelPos(midDeg) {
    return {
      x: CX + LABEL_R * Math.cos(toRad(midDeg)),
      y: CY + LABEL_R * Math.sin(toRad(midDeg)),
      rotate: midDeg,
    };
  }

  function splitLabel(text) {
    if (text.length <= 9) return [text];
    var parts = text.split(' ');
    if (parts.length > 1) return parts;
    var mid = Math.ceil(text.length / 2);
    return [text.slice(0, mid), text.slice(mid)];
  }

  function init(container, options) {
    var emotions = options.emotions || [];
    var pickN = parseInt(options.pick, 10) || 1;
    var selected = new Set();
    var onChange = options.onChange || function () {};

    container.innerHTML = '';
    container.classList.add('chit-emotion-wheel');

    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 400 400');
    svg.setAttribute('role', 'group');
    svg.setAttribute('aria-label', 'Колесо эмоций');

    var step = 360 / SECTOR_COUNT;
    var gSectors = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gSectors.setAttribute('class', 'chit-emotion-wheel__sectors');

    emotions.forEach(function (emo, i) {
      var start = i * step;
      var end = start + step;
      var mid = start + step / 2;
      var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', sectorPath(start, end));
      path.setAttribute('fill', emo.color);
      path.setAttribute('class', 'chit-emotion-wheel__sector');
      path.setAttribute('data-id', emo.id);
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

      var lp = labelPos(mid);
      var text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', lp.x);
      text.setAttribute('y', lp.y);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dominant-baseline', 'middle');
      text.setAttribute('transform', 'rotate(' + lp.rotate + ' ' + lp.x + ' ' + lp.y + ')');
      text.setAttribute('class', 'chit-emotion-wheel__label');
      text.setAttribute('pointer-events', 'none');

      var lines = splitLabel(emo.label);
      if (lines.length === 1) {
        text.textContent = lines[0];
      } else {
        lines.forEach(function (line, li) {
          var tspan = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
          tspan.setAttribute('x', lp.x);
          tspan.setAttribute('dy', li === 0 ? '-0.35em' : '1.1em');
          tspan.textContent = line;
          text.appendChild(tspan);
        });
      }
      gSectors.appendChild(text);
    });

    svg.appendChild(gSectors);

    var hub = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    hub.setAttribute('cx', String(CX));
    hub.setAttribute('cy', String(CY));
    hub.setAttribute('r', '14');
    hub.setAttribute('class', 'chit-emotion-wheel__hub');
    svg.appendChild(hub);

    var dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    dot.setAttribute('cx', String(CX));
    dot.setAttribute('cy', String(CY));
    dot.setAttribute('r', '4');
    dot.setAttribute('class', 'chit-emotion-wheel__hub-dot');
    svg.appendChild(dot);

    container.appendChild(svg);

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
          ? 'Выбери одну эмоцию'
          : 'Выбери ' + pickN + ' эмоции';
        return;
      }
      var names = Array.from(selected).map(emotionLabel);
      pickedEl.textContent = 'Выбрано: ' + names.join(', ');
    }

    function selectionComplete() {
      return selected.size === pickN;
    }

    function syncUI() {
      container.querySelectorAll('.chit-emotion-wheel__sector').forEach(function (node) {
        var id = node.getAttribute('data-id');
        var on = selected.has(id);
        node.classList.toggle('is-selected', on);
        node.setAttribute('aria-pressed', on ? 'true' : 'false');
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
      });
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
