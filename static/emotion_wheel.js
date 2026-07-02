(function (global) {
  var DEFAULT_IMAGE = '/static/images/emotion-wheel.png';
  var VIEW = 1024;

  function init(container, options) {
    var emotions = options.emotions || [];
    var pickN = parseInt(options.pick, 10) || 1;
    var imageUrl = options.imageUrl || DEFAULT_IMAGE;
    var petalPaths = options.petalPaths || {};
    var selected = new Set();
    var onChange = options.onChange || function () {};

    container.innerHTML = '';
    container.classList.add('chit-emotion-wheel');

    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 ' + VIEW + ' ' + VIEW);
    svg.setAttribute('class', 'chit-emotion-wheel__svg');
    svg.setAttribute('role', 'group');
    svg.setAttribute('aria-label', 'Колесо эмоций');

    var art = document.createElementNS('http://www.w3.org/2000/svg', 'image');
    art.setAttributeNS('http://www.w3.org/1999/xlink', 'href', imageUrl);
    art.setAttribute('href', imageUrl);
    art.setAttribute('x', '0');
    art.setAttribute('y', '0');
    art.setAttribute('width', String(VIEW));
    art.setAttribute('height', String(VIEW));
    art.setAttribute('preserveAspectRatio', 'xMidYMid meet');
    art.setAttribute('class', 'chit-emotion-wheel__art');
    svg.appendChild(art);

    var gSectors = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    gSectors.setAttribute('class', 'chit-emotion-wheel__sectors');

    emotions.forEach(function (emo) {
      var d = petalPaths[emo.id];
      if (!d) return;

      var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', d);
      path.setAttribute('class', 'chit-emotion-wheel__sector');
      path.setAttribute('data-id', emo.id);
      path.setAttribute('data-color', emo.color || '#ffffff');
      path.setAttribute('tabindex', '0');
      path.setAttribute('role', 'button');
      path.setAttribute('aria-label', emo.label);
      path.setAttribute('aria-pressed', 'false');

      path.addEventListener('click', function () {
        toggle(emo.id);
        path.blur();
      });
      path.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggle(emo.id);
        }
      });

      gSectors.appendChild(path);
    });

    svg.appendChild(gSectors);
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

    function syncUI(notifyChange) {
      if (notifyChange === undefined) notifyChange = true;
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
      if (notifyChange) onChange(Array.from(selected), selectionComplete());
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
      syncUI(false);
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
