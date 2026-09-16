(function () {
  const root = document.getElementById("chit-exp-root");
  if (!root) return;

  const ASSET = root.dataset.asset || "/static/expedition/";
  const DATA_URL = root.dataset.data || ASSET + "data.json";
  const API = (root.dataset.api || "").replace(/\/$/, "");
  const PROG_KEY = "chit-expedition-progress-v1";

  let DATA = null;
  let progress = loadProgress();
  let mapState = { scale: 1, x: 0, y: 0, filters: { q: "", age: "", theme: "", audio: "", status: "" } };

  const TITLE_DEFAULT = "Читательская экспедиция — Читательство";

  function loadProgress() {
    try {
      return JSON.parse(localStorage.getItem(PROG_KEY) || "{}");
    } catch (e) {
      return {};
    }
  }
  function saveProgress() {
    progress.updatedAt = new Date().toISOString();
    localStorage.setItem(PROG_KEY, JSON.stringify(progress));
  }
  function ensureProg() {
    progress.stories = progress.stories || {};
    progress.badges = progress.badges || [];
    progress.saved = progress.saved || [];
    progress.regions = progress.regions || {};
    progress.route = progress.route || "";
    progress.quiz = progress.quiz || {};
    progress.listened = progress.listened || [];
  }

  function img(name) {
    if (!name) return ASSET + "images/hero-map.png";
    if (/^https?:/.test(name)) return name;
    return ASSET + "images/" + name;
  }

  function useHash() {
    return root.dataset.router === "hash";
  }

  function currentPath() {
    if (useHash()) {
      const h = (location.hash || "#/").replace(/^#/, "");
      return h || "/";
    }
    const path = location.pathname.replace(/\/+$/, "") || "/";
    const idx = path.indexOf("/expedition");
    if (idx !== -1) {
      const rest = path.slice(idx + "/expedition".length) || "/";
      return rest === "" ? "/" : rest;
    }
    const h = (location.hash || "#/").replace(/^#/, "");
    return h || "/";
  }

  function href(to) {
    const clean = to.charAt(0) === "/" ? to : "/" + to;
    if (!useHash() && location.pathname.indexOf("/expedition") === 0) {
      return "/expedition" + (clean === "/" ? "" : clean);
    }
    return "#" + (clean === "/" ? "/" : clean);
  }

  function go(to, replace) {
    const url = href(to);
    if (url.charAt(0) === "#") {
      if (replace) location.replace(url);
      else location.hash = url.slice(1);
      return;
    }
    if (replace) history.replaceState({}, "", url);
    else history.pushState({}, "", url);
    render();
    window.scrollTo(0, 0);
  }

  function storyBy(slug) { return DATA.stories.find((s) => s.slug === slug); }
  function regionBy(slug) { return DATA.regions.find((r) => r.slug === slug); }
  function heroBy(slug) { return DATA.heroes.find((h) => h.slug === slug); }
  function routeBy(slug) { return DATA.routes.find((r) => r.slug === slug); }

  function storyDone(slug) {
    ensureProg();
    return !!(progress.stories[slug] && progress.stories[slug].done);
  }
  function grantBadge(id) {
    ensureProg();
    if (progress.badges.indexOf(id) === -1) {
      progress.badges.push(id);
      saveProgress();
      toast("Отметка в паспорте: «" + badgeName(id) + "»");
    }
  }
  function badgeName(id) {
    const b = DATA.badges.find((x) => x.id === id);
    return b ? b.name : id;
  }

  function toast(text) {
    const el = document.createElement("div");
    el.className = "chit-toast";
    el.textContent = text;
    document.body.appendChild(el);
    setTimeout(function () { el.remove(); }, 2400);
  }

  function header(active) {
    const links = [
      ["/", "Главная"],
      ["/map", "Карта"],
      ["/routes", "Маршруты"],
      ["/passport", "Паспорт"],
      ["/libraries", "Библиотекам"],
      ["/about", "О проекте"]
    ];
    return (
      '<header class="chit-exp-header"><div class="chit-exp-header__inner">' +
      '<a class="chit-exp-logo" href="https://chitatelstvo.ru">' +
      '<img src="https://api.chitatelstvo.ru/assets/logo-chitatelstvo.png" alt="Читательство" width="150" height="40">' +
      "<span>Читательская экспедиция</span></a>" +
      '<nav class="chit-exp-nav" aria-label="Разделы экспедиции">' +
      links.map(function (l) {
        return '<a href="' + href(l[0]) + '" class="' + (active === l[0] ? "is-on" : "") + '" data-go="' + l[0] + '">' + l[1] + "</a>";
      }).join("") +
      "</nav></div></header>"
    );
  }

  function footer() {
    return (
      '<footer class="chit-exp-footer">' +
      "<p>Читательская экспедиция от литературной школы «Читательство».</p>" +
      '<p><a href="https://chitatelstvo.ru">chitatelstvo.ru</a> · ' +
      '<a href="mailto:info@chitatelstvo.ru">info@chitatelstvo.ru</a> · ' +
      '<a data-go="/add-legend" href="' + href("/add-legend") + '">Предложить легенду</a> · ' +
      '<a data-go="/about" href="' + href("/about") + '">Сообщить об ошибке</a></p>' +
      "<p>Полные занятия, игровые задания и читательский путь — в школе «Читательство».</p>" +
      "</footer>"
    );
  }

  function chip(text, mod) {
    return '<span class="chit-chip' + (mod ? " chit-chip--" + mod : "") + '">' + escapeHtml(text) + "</span>";
  }

  function escapeHtml(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function credChip(story) {
    const map = { verified: "sage", tradition: "gold", interpretation: "rose" };
    return chip(story.credibilityLabel, map[story.credibility] || "");
  }

  function renderHome() {
    document.title = TITLE_DEFAULT;
    const routes = DATA.routeCards.map(function (c) {
      const locked = c.soon;
      const to = c.slug === "my-krai" ? "/libraries" : "/routes/" + c.slug;
      return (
        '<a class="chit-card chit-card--link" data-go="' + (locked ? "/routes" : to) + '" href="' + href(locked ? "/routes" : to) + '">' +
        chip(c.age, "rose") +
        "<h3>" + escapeHtml(c.title) + (locked ? " · скоро" : "") + "</h3>" +
        "<p>" + (routeBy(c.slug) ? escapeHtml(routeBy(c.slug).blurb) : "Готовый вход в экспедицию.") + "</p></a>"
      );
    }).join("");

    root.innerHTML =
      header("/") +
      '<main class="chit-exp-main">' +
      '<section class="chit-hero"><div class="chit-wrap chit-hero__grid">' +
      "<div><p class=\"chit-kicker\">Литературная школа для детей «Читательство» представляет</p>" +
      "<h1 class=\"chit-h1\">Читательская экспедиция</h1>" +
      "<p class=\"chit-lead\">Открывайте сказки, героев и легенды народов России. Читайте, слушайте, ищите подсказки, выполняйте задания и находите свой путь к любимым книгам.</p>" +
      '<div class="chit-btns">' +
      '<button class="chit-btn chit-btn--primary" type="button" data-act="start">Начать экспедицию</button>' +
      '<a class="chit-btn chit-btn--ghost" data-go="/routes" href="' + href("/routes") + '">Выбрать маршрут</a>' +
      '<a class="chit-btn chit-btn--ghost" data-go="/map" href="' + href("/map") + '">Открыть карту</a>' +
      '<a class="chit-btn chit-btn--ghost" data-go="/libraries" href="' + href("/libraries") + '">Я библиотека / педагог</a>' +
      "</div>" +
      "<p class=\"chit-note\">Пройдите первую мини-экспедицию бесплатно и получите отметку в читательском паспорте.</p>" +
      "</div>" +
      '<div class="chit-hero__visual"><img src="' + img("hero-map.png") + '" alt="Иллюстрированная карта читательского путешествия по России"></div>' +
      "</div></section>" +

      '<section class="chit-section" id="how"><div class="chit-wrap">' +
      "<h2 class=\"chit-h2\">Как это работает</h2>" +
      '<div class="chit-grid-4 chit-how">' +
      "<article class=\"chit-card\"><h3>Выберите возраст и интерес</h3><p>Волшебство, приключения, животные-помощники, тайны, смешные истории, сказки своего края.</p></article>" +
      "<article class=\"chit-card\"><h3>Откройте регион и историю</h3><p>Познакомьтесь с героем, послушайте аудиофрагмент или прочитайте небольшой отрывок.</p></article>" +
      "<article class=\"chit-card\"><h3>Выполните миссию читателя</h3><p>Найдите деталь, разгадайте загадку, объясните поступок героя, создайте продолжение.</p></article>" +
      "<article class=\"chit-card\"><h3>Соберите отметки и бейджи</h3><p>Открывайте новые маршруты и создавайте свой читательский путь.</p></article>" +
      "</div></div></section>" +

      '<section class="chit-section chit-section--alt"><div class="chit-wrap">' +
      "<h2 class=\"chit-h2\">Выберите маршрут</h2>" +
      '<div class="chit-grid-3">' + routes + "</div></div></section>" +

      '<section class="chit-section"><div class="chit-wrap chit-grid-2">' +
      '<div class="chit-card"><img src="' + img("library.png") + '" alt="Библиотечная встреча у карты" style="border-radius:12px;margin-bottom:12px;aspect-ratio:16/9;object-fit:cover;width:100%">' +
      "<h2 class=\"chit-h2\">Станьте точкой Читательской экспедиции</h2>" +
      "<p>Библиотеки помогают детям встретиться со сказкой не только на экране, но и среди настоящих книг. Проведите готовое занятие, представьте историю своего края и присоединитесь к карте читающих регионов.</p>" +
      '<p style="margin-top:16px"><a class="chit-btn chit-btn--primary" data-go="/libraries" href="' + href("/libraries") + '">Узнать об участии библиотеки</a></p>' +
      "</div>" +
      '<div class="chit-card"><img src="' + img("passport.png") + '" alt="Читательский паспорт" style="border-radius:12px;margin-bottom:12px;aspect-ratio:16/9;object-fit:cover;width:100%">' +
      "<h2 class=\"chit-h2\">Паспорт читателя</h2>" +
      "<p>Пройденные регионы, истории, бейджи и следующий шаг маршрута хранятся в вашем паспорте. Бейджи входят в игровую логику школы «Читательство».</p>" +
      '<p style="margin-top:16px"><a class="chit-btn chit-btn--ghost" data-go="/passport" href="' + href("/passport") + '">Открыть паспорт</a></p>' +
      "</div></div></section>" +

      '<section class="chit-cta-band"><div class="chit-wrap">' +
      "<h2 class=\"chit-h2\">Продолжите литературное путешествие в «Читательстве»</h2>" +
      "<p>Хотите продолжить исследование? В литературной школе «Читательство» вас ждут полные занятия, новые истории, творческие задания и следующий уровень читательского пути.</p>" +
      '<a class="chit-btn chit-btn--primary" href="https://chitatelstvo.ru/#program">К программам школы</a>' +
      "</div></section></main>" + footer();
  }

  function russiaPath() {
    return "M72 250 C90 210 118 188 148 200 C168 168 198 148 228 158 C248 118 278 108 308 138 C348 118 392 128 428 148 C488 132 560 138 630 152 C710 148 790 162 860 188 C910 198 958 228 972 268 C986 312 968 352 922 372 C860 402 790 412 728 422 C688 448 648 462 608 448 C558 468 500 452 458 428 C400 442 338 422 292 398 C244 412 196 388 158 352 C118 322 88 286 72 250 Z M900 210 C922 198 948 208 958 232 C948 258 922 262 900 248 C888 232 888 218 900 210 Z M78 318 C70 312 58 318 54 330 C62 342 78 340 84 328 C86 322 84 318 78 318 Z";
  }

  function pinClass(region) {
    if (region.stories && region.stories.some(storyDone)) return "done";
    if (region.status === "empty") return "empty";
    if (region.status === "route") return "route";
    return "available";
  }

  function regionMatches(region) {
    const f = mapState.filters;
    const stories = (region.stories || []).map(storyBy).filter(Boolean);
    if (f.q) {
      const q = f.q.toLowerCase();
      const hit = region.name.toLowerCase().indexOf(q) !== -1 ||
        stories.some(function (s) { return s.title.toLowerCase().indexOf(q) !== -1; });
      if (!hit) return false;
    }
    if (f.age && !stories.some(function (s) { return (s.ages || []).indexOf(f.age) !== -1 || s.age === f.age; })) {
      if (region.status !== "empty") return false;
    }
    if (f.theme && !stories.some(function (s) { return (s.themes || []).indexOf(f.theme) !== -1; })) return false;
    if (f.audio === "yes" && !stories.length) return false;
    if (f.status === "done" && !stories.some(function (s) { return storyDone(s.slug); })) return false;
    if (f.status === "new" && !region.new) return false;
    if (f.status === "lib" && !(region.libraries && region.libraries.length)) return false;
    if (f.status === "route" && region.status !== "route") return false;
    return true;
  }

  function renderMap(selectedSlug) {
    document.title = "Карта экспедиции — Читательство";
    const selected = selectedSlug ? regionBy(selectedSlug) : DATA.regions.find(function (r) { return r.status !== "empty"; });
    const pins = DATA.regions.filter(regionMatches).map(function (r) {
      const on = selected && selected.slug === r.slug ? " is-on" : "";
      const n = (r.stories || []).length;
      const star = progress.badges && progress.badges.length && (r.stories || []).some(storyDone);
      return (
        '<g class="chit-pin ' + pinClass(r) + on + '" data-region="' + r.slug + '" tabindex="0" role="button" aria-label="' + escapeHtml(r.name) + '">' +
        '<circle class="region" cx="' + r.cx + '" cy="' + r.cy + '" r="' + r.r + '"></circle>' +
        (r.new ? '<circle cx="' + (r.cx + r.r - 2) + '" cy="' + (r.cy - r.r + 2) + '" r="5" fill="#C6A15B"></circle>' : "") +
        (r.libraries && r.libraries.length ? '<circle cx="' + (r.cx - r.r + 2) + '" cy="' + (r.cy + r.r - 2) + '" r="4" fill="#3D4F7C"></circle>' : "") +
        (star ? '<text x="' + r.cx + '" y="' + (r.cy + 4) + '" text-anchor="middle" font-size="12">★</text>' : "") +
        '<title>' + escapeHtml(r.name) + " · историй: " + n + (r.new ? " · новая история" : "") + (storyDone((r.stories || [])[0]) ? " · пройдено" : "") + "</title>" +
        "</g>"
      );
    }).join("");

    const empty = DATA.emptyPins.map(function (p) {
      return '<g class="chit-pin empty" data-empty="' + p.id + '"><circle class="chit-dot-empty" cx="' + p.cx + '" cy="' + p.cy + '" r="7"></circle><title>' + escapeHtml(p.name) + " · регион пока не заполнен</title></g>";
    }).join("");

    root.innerHTML =
      header("/map") +
      '<main class="chit-exp-main chit-map-page">' +
      '<div class="chit-map-stage">' +
      '<div class="chit-map-toolbar">' +
      '<input type="search" id="chit-map-q" placeholder="Найти регион" value="' + escapeHtml(mapState.filters.q) + '" aria-label="Поиск региона">' +
      '<select id="chit-map-age" aria-label="Возраст"><option value="">Возраст</option>' +
      DATA.filters.ages.map(function (a) { return '<option value="' + a.id + '"' + (mapState.filters.age === a.id ? " selected" : "") + ">" + a.label + "</option>"; }).join("") +
      "</select>" +
      '<select id="chit-map-theme" aria-label="Тема"><option value="">Тема</option>' +
      DATA.filters.themes.map(function (a) { return '<option value="' + a.id + '"' + (mapState.filters.theme === a.id ? " selected" : "") + ">" + a.label + "</option>"; }).join("") +
      "</select>" +
      '<select id="chit-map-st" aria-label="Статус"><option value="">Все регионы</option>' +
      '<option value="route">Есть маршрут</option><option value="new">Новая история</option>' +
      '<option value="done">Пройдено</option><option value="lib">Библиотека-партнёр</option></select>' +
      '<a class="chit-btn chit-btn--small chit-btn--ghost" data-go="/regions" href="' + href("/regions") + '">Список регионов</a>' +
      '<div class="chit-zoom"><button type="button" data-zoom="-">−</button><button type="button" data-zoom="+">+</button></div>' +
      "</div>" +
      '<div class="chit-map-svg-wrap" id="chit-map-drag">' +
      '<svg class="chit-map-svg" viewBox="0 0 1000 520" role="img" aria-label="Карта регионов Читательской экспедиции">' +
      '<rect width="1000" height="520" fill="#EFE6D8"></rect>' +
      '<path class="chit-map-land" d="' + russiaPath() + '"></path>' +
      empty + pins +
      "</svg></div>" +
      '<div class="chit-legend-map">' +
      "<div><i style=\"background:#D9D4CC\"></i>пока не заполнен</div>" +
      "<div><i style=\"background:#E8DCC8\"></i>доступен</div>" +
      "<div><i style=\"background:#D9A39A\"></i>есть маршрут</div>" +
      "<div><i style=\"background:#8DA392\"></i>пройден</div>" +
      "</div></div>" +
      '<aside class="chit-map-side" id="chit-map-side">' + regionPanel(selected) + "</aside>" +
      "</main>" + footer();

    bindMap();
  }

  function regionPanel(r) {
    if (!r) {
      return "<p class=\"chit-kicker\">Карта-путешествие</p><h2>Выберите регион</h2><p>На карте — заполненные точки экспедиции. Серые точки появятся позже.</p>";
    }
    const stories = (r.stories || []).map(storyBy).filter(Boolean);
    const cover = stories[0] ? img(stories[0].image) : img("hero-map.png");
    if (r.status === "empty") {
      return (
        '<p class="chit-kicker">Регион пока не заполнен</p><h2>' + escapeHtml(r.name) + "</h2>" +
        "<p>" + escapeHtml(r.short) + "</p>" +
        '<p><a class="chit-btn chit-btn--small chit-btn--ghost" data-go="/add-legend" href="' + href("/add-legend") + '">Предложить легенду края</a></p>'
      );
    }
    return (
      '<div class="cover"><img src="' + cover + '" alt=""></div>' +
      '<p class="chit-kicker">Читательство представляет</p>' +
      "<h2>" + escapeHtml(r.name) + "</h2>" +
      "<p>" + escapeHtml(r.short) + "</p>" +
      '<div class="chit-card__meta" style="margin:10px 0">' +
      chip(stories.length + " истор.", "rose") +
      chip((r.heroes || []).length + " героев") +
      chip("аудио есть", "sage") +
      (r.libraries && r.libraries.length ? chip("библиотека-партнёр", "gold") : "") +
      "</div>" +
      stories.map(function (s) {
        return '<a class="chit-card chit-card--link" style="margin:8px 0" data-go="/stories/' + s.slug + '" href="' + href("/stories/" + s.slug) + '">' +
          chip(s.age === "family" ? "семейный" : s.age, "rose") + chip(s.minutes + " мин") +
          (storyDone(s.slug) ? chip("пройдено", "sage") : "") +
          "<h3>" + escapeHtml(s.title) + "</h3></a>";
      }).join("") +
      '<p style="margin-top:12px"><a class="chit-btn chit-btn--primary" data-go="/regions/' + r.slug + '" href="' + href("/regions/" + r.slug) + '">Начать маршрут</a></p>'
    );
  }

  function bindMap() {
    root.querySelectorAll("[data-region]").forEach(function (g) {
      g.addEventListener("click", function () { renderMap(g.getAttribute("data-region")); });
      g.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); g.click(); }
      });
    });
    const q = document.getElementById("chit-map-q");
    const age = document.getElementById("chit-map-age");
    const theme = document.getElementById("chit-map-theme");
    const st = document.getElementById("chit-map-st");
    function apply() {
      mapState.filters.q = q.value;
      mapState.filters.age = age.value;
      mapState.filters.theme = theme.value;
      mapState.filters.status = st.value;
      const keep = root.querySelector("[data-region].is-on");
      renderMap(keep ? keep.getAttribute("data-region") : "");
      const nq = document.getElementById("chit-map-q");
      if (nq) nq.focus();
    }
    if (q) q.addEventListener("change", apply);
    if (age) age.addEventListener("change", apply);
    if (theme) theme.addEventListener("change", apply);
    if (st) st.addEventListener("change", apply);
    root.querySelectorAll("[data-zoom]").forEach(function (b) {
      b.addEventListener("click", function () {
        const svg = root.querySelector(".chit-map-svg");
        mapState.scale = Math.min(2.4, Math.max(0.8, mapState.scale + (b.getAttribute("data-zoom") === "+" ? 0.2 : -0.2)));
        svg.style.transform = "scale(" + mapState.scale + ")";
        svg.style.transformOrigin = "center";
      });
    });
  }

  function renderRegions() {
    document.title = "Регионы экспедиции — Читательство";
    const cards = DATA.regions.map(function (r) {
      const n = (r.stories || []).length;
      return (
        '<a class="chit-card chit-card--link" data-go="/regions/' + r.slug + '" href="' + href("/regions/" + r.slug) + '">' +
        chip(r.status === "empty" ? "скоро" : n + " истор.", r.status === "empty" ? "gray" : "rose") +
        "<h3>" + escapeHtml(r.name) + "</h3><p>" + escapeHtml(r.short) + "</p></a>"
      );
    }).join("");
    root.innerHTML = header("/map") + '<main class="chit-exp-main chit-list-mode"><div class="chit-wrap">' +
      "<p class=\"chit-kicker\">Список регионов</p><h1 class=\"chit-h1\">Каталог карты</h1>" +
      "<p class=\"chit-lead\">Алфавитный вход без карты — удобно на телефоне.</p>" +
      '<div class="chit-grid-3">' + cards + "</div></div></main>" + footer();
  }

  function renderRegion(slug) {
    const r = regionBy(slug);
    if (!r) return renderNotFound();
    document.title = r.name + " — Читательская экспедиция";
    const stories = (r.stories || []).map(storyBy).filter(Boolean);
    const heroes = (r.heroes || []).map(heroBy).filter(Boolean);
    const first = stories[0];
    root.innerHTML = header("/map") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding-top:24px;padding-bottom:64px">' +
      '<div class="chit-cover-hero"><img src="' + img(first ? first.image : "hero-map.png") + '" alt=""></div>' +
      '<p class="chit-kicker">Библиотека-партнёр «Читательства» · регион на карте</p>' +
      '<h1 class="chit-h1">' + escapeHtml(r.name) + "</h1>" +
      "<p class=\"chit-lead\">" + escapeHtml(r.short) + "</p>" +
      '<div class="chit-card__meta">' + chip(stories.length + " историй") + chip(heroes.length + " героев") + chip("аудио и задания") + "</div>" +
      (first ? '<p style="margin:18px 0"><a class="chit-btn chit-btn--primary" data-go="/stories/' + first.slug + '" href="' + href("/stories/" + first.slug) + '">Начать маршрут</a></p>' : "") +
      (first ? "<h2 class=\"chit-h2\">История для первого знакомства</h2><p>Один бесплатный короткий материал: иллюстрация, герой, аудио, фрагмент, одно задание, отметка в паспорте.</p>" : "") +
      "<h2 class=\"chit-h2\">Герои и истории региона</h2>" +
      '<div class="chit-grid-3">' + stories.map(function (s) {
        return '<a class="chit-card chit-card--link" data-go="/stories/' + s.slug + '" href="' + href("/stories/" + s.slug) + '">' +
          '<img src="' + img(s.image) + '" alt="" style="border-radius:12px;aspect-ratio:16/10;object-fit:cover;width:100%;margin-bottom:8px">' +
          chip(s.ageLabel || s.age) + credChip(s) +
          (storyDone(s.slug) ? chip("пройдено", "sage") : chip("доступно")) +
          "<h3>" + escapeHtml(s.title) + "</h3><p>" + s.minutes + " минут</p></a>";
      }).join("") + "</div>" +
      "<h2 class=\"chit-h2\" style=\"margin-top:32px\">Сказки и легенды</h2>" +
      "<p>Проверенные редакцией «Читательства». Региональные версии подписаны отдельно. Материалы на проверке на сайт не попадают.</p>" +
      '<div class="chit-card" style="margin-top:16px"><h3>Что прочитать дальше</h3><p>Полные занятия, игровые задания и читательский путь — в школе «Читательство».</p>' +
      '<p style="margin-top:12px"><a class="chit-btn chit-btn--ghost" href="https://chitatelstvo.ru/#program">К программам</a> ' +
      '<a class="chit-btn chit-btn--ghost" data-go="/libraries" href="' + href("/libraries") + '">Провести экспедицию в библиотеке</a></p></div>' +
      "</div></main>" + footer();
  }

  function renderStory(slug) {
    const s = storyBy(slug);
    if (!s) return renderNotFound();
    const region = regionBy(s.region);
    const hero = heroBy(s.hero);
    document.title = s.title + " — Читательская экспедиция";
    ensureProg();
    const saved = progress.stories[slug] || {};
    root.innerHTML = header("/map") + '<main class="chit-exp-main"><div class="chit-wrap chit-story">' +
      '<div class="chit-story__media">' +
      '<img src="' + img(s.image) + '" alt="' + escapeHtml(s.title) + '">' +
      '<div class="chit-audio"><strong>Послушайте историю</strong>' +
      "<p style=\"margin:6px 0 10px;color:var(--chit-muted);font-size:14px\">«Послушай за 2 минуты». Диктор: " + escapeHtml(s.speaker) + ". " + escapeHtml(s.rights) + "</p>" +
      '<div class="chit-btns"><button class="chit-btn chit-btn--sage chit-btn--small" type="button" data-act="speak">Слушать</button>' +
      '<button class="chit-btn chit-btn--ghost chit-btn--small" type="button" data-act="pause">Пауза</button>' +
      '<button class="chit-btn chit-btn--ghost chit-btn--small" type="button" data-act="slow">Медленнее</button></div>' +
      "<p style=\"margin-top:8px;font-size:13px;color:var(--chit-muted)\">Для 6–8 лет — спокойный темп, без пугающих звуков. В полной версии будет запись диктора.</p></div>" +
      "</div><div>" +
      '<p class="chit-kicker">Читательство представляет</p>' +
      '<h1 class="chit-h1">' + escapeHtml(s.title) + "</h1>" +
      '<div class="chit-card__meta">' +
      chip("Регион: " + (region ? region.name : "")) +
      chip("Традиция: " + s.tradition) +
      chip("Возраст: " + (s.age === "family" ? "семейный" : s.age)) +
      chip("Время: " + s.minutes + " минут") +
      credChip(s) +
      "</div>" +
      "<p class=\"chit-note\">" + escapeHtml(s.locationNote) + "</p>" +
      "<h2>Кто герой?</h2><p>" + escapeHtml(s.who) + (hero ? ' <a data-go="/heroes/' + hero.slug + '" href="' + href("/heroes/" + hero.slug) + '">Карточка героя</a>' : "") + "</p>" +
      "<h2>Откройте фрагмент</h2><div class=\"chit-excerpt\">" + escapeHtml(s.excerpt) + "</div>" +
      "<h2>Что заметить?</h2><p>" + escapeHtml(s.notice) + "</p>" +
      '<div class="chit-task"><h2>Миссия читателя</h2><p>' + escapeHtml(s.task.prompt) + "</p>" +
      s.task.options.map(function (o) {
        return '<button class="chit-option" type="button" data-opt="' + o.id + '">' + escapeHtml(o.text) + "</button>";
      }).join("") +
      '<p class="chit-explain" hidden></p></div>' +
      '<div class="chit-creative"><h2>Создайте свой ответ</h2><p>' + escapeHtml(s.creative) + "</p>" +
      '<textarea placeholder="Письмо, идея рисунка, карта или продолжение" data-creative>' + escapeHtml(saved.creative || "") + "</textarea>" +
      '<p style="margin-top:8px"><button class="chit-btn chit-btn--primary" type="button" data-act="save-creative">Сохранить отклик</button></p>' +
      "<p class=\"chit-note\">Голосовое сообщение ребёнка — только через родительский профиль школы.</p></div>" +
      '<div class="chit-card" style="margin-top:16px"><strong>Получено:</strong> бейдж «' + escapeHtml(badgeName(s.badge)) + '» после миссии.</div>' +
      "<h2 style=\"margin-top:24px\">Продолжите путь</h2>" +
      '<div class="chit-grid-3">' + (s.similar || []).map(function (id) {
        const x = storyBy(id);
        if (!x) return "";
        return '<a class="chit-card chit-card--link" data-go="/stories/' + x.slug + '" href="' + href("/stories/" + x.slug) + '"><h3>' + escapeHtml(x.title) + "</h3><p>" + (regionBy(x.region) || {}).name + "</p></a>";
      }).join("") + "</div>" +
      "<h2>Книги и материалы</h2><ul>" + s.books.map(function (b) {
        return "<li>" + (b.url ? '<a href="' + b.url + '">' + escapeHtml(b.title) + "</a>" : escapeHtml(b.title)) + " · " + escapeHtml(b.age) + "</li>";
      }).join("") + "</ul>" +
      "<h2>Источники</h2><ul class=\"chit-sources\">" + s.sources.map(function (x) { return "<li>" + escapeHtml(x) + "</li>"; }).join("") + "</ul>" +
      '<p style="margin-top:20px"><a class="chit-btn chit-btn--ghost" href="https://chitatelstvo.ru/#program">Продолжите литературное путешествие в «Читательстве»</a></p>' +
      "</div></div></main>" + footer();

    const explain = root.querySelector(".chit-explain");
    root.querySelectorAll("[data-opt]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const opt = s.task.options.find(function (o) { return o.id === btn.getAttribute("data-opt"); });
        root.querySelectorAll("[data-opt]").forEach(function (b) { b.className = "chit-option"; });
        btn.className = "chit-option " + (opt.ok ? "is-ok" : "is-bad");
        explain.hidden = false;
        explain.textContent = opt.ok ? s.task.explain : "Посмотрите фрагмент ещё раз — ответ спрятан в детали.";
        if (opt.ok) completeStory(s);
      });
    });
    root.querySelector("[data-act='speak']").addEventListener("click", function () { speak(s.excerpt, 0.95); markListen(s.slug); });
    root.querySelector("[data-act='pause']").addEventListener("click", function () { window.speechSynthesis && window.speechSynthesis.cancel(); });
    root.querySelector("[data-act='slow']").addEventListener("click", function () { speak(s.excerpt, 0.8); markListen(s.slug); });
    root.querySelector("[data-act='save-creative']").addEventListener("click", function () {
      ensureProg();
      progress.stories[s.slug] = progress.stories[s.slug] || {};
      progress.stories[s.slug].creative = root.querySelector("[data-creative]").value;
      saveProgress();
      grantBadge("maker");
      toast("Отклик сохранён в паспорте");
    });
  }

  function completeStory(s) {
    ensureProg();
    progress.stories[s.slug] = progress.stories[s.slug] || {};
    progress.stories[s.slug].done = true;
    progress.regions[s.region] = true;
    saveProgress();
    grantBadge(s.badge || "seeker");
    const doneCount = Object.keys(progress.stories).filter(function (k) { return progress.stories[k].done; }).length;
    if (doneCount >= 3) grantBadge("keeper");
    if (Object.keys(progress.regions).length >= 2) grantBadge("traveler");
  }

  function markListen(slug) {
    ensureProg();
    if (progress.listened.indexOf(slug) === -1) progress.listened.push(slug);
    saveProgress();
    grantBadge("listener");
  }

  function speak(text, rate) {
    if (!window.speechSynthesis) { toast("В этом браузере нет озвучки"); return; }
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "ru-RU";
    u.rate = rate || 0.95;
    window.speechSynthesis.speak(u);
  }

  function renderHero(slug) {
    const h = heroBy(slug);
    if (!h) return renderNotFound();
    const s = storyBy(h.story);
    document.title = h.name + " — Читательская экспедиция";
    root.innerHTML = header("/map") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:32px 20px 64px;max-width:760px">' +
      '<p class="chit-kicker">Карточка героя · Читательство представляет</p>' +
      '<h1 class="chit-h1">' + escapeHtml(h.name) + "</h1>" +
      "<p class=\"chit-lead\">" + escapeHtml(h.blurb) + "</p>" +
      (s ? '<p><a class="chit-btn chit-btn--primary" data-go="/stories/' + s.slug + '" href="' + href("/stories/" + s.slug) + '">Открыть историю</a></p>' : "") +
      "</div></main>" + footer();
  }

  function renderRoutes() {
    document.title = "Маршруты экспедиции — Читательство";
    root.innerHTML = header("/routes") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:32px 20px 64px">' +
      '<p class="chit-kicker">Готовые маршруты</p><h1 class="chit-h1">Выберите свою экспедицию</h1>' +
      '<p class="chit-lead">Три открытых маршрута прототипа. Остальные темы появятся по мере наполнения карты.</p>' +
      '<p><button class="chit-btn chit-btn--primary" type="button" data-act="start">Подобрать по вопросам</button></p>' +
      '<div class="chit-grid-3" style="margin-top:20px">' + DATA.routes.map(function (r) {
        return '<a class="chit-card chit-card--link" data-go="/routes/' + r.slug + '" href="' + href("/routes/" + r.slug) + '">' +
          chip(r.ageLabel, "rose") + chip(r.time) +
          "<h3>" + escapeHtml(r.title) + "</h3><p>" + escapeHtml(r.blurb) + "</p></a>";
      }).join("") + "</div></div></main>" + footer();
  }

  function renderRoute(slug) {
    if (slug === "my-krai") return renderLibraries();
    const r = routeBy(slug);
    if (!r) {
      document.title = "Маршрут появится позже — Читательство";
      root.innerHTML = header("/routes") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:48px 20px">' +
        "<h1 class=\"chit-h1\">Маршрут готовится</h1><p>Эта тема войдёт в следующую очередь наполнения. Сейчас открыты три маршрута прототипа.</p>" +
        '<p><a class="chit-btn chit-btn--primary" data-go="/routes" href="' + href("/routes") + '">К открытым маршрутам</a></p></div></main>' + footer();
      return;
    }
    document.title = r.title + " — Читательская экспедиция";
    progress.route = r.slug;
    saveProgress();
    root.innerHTML = header("/routes") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:32px 20px 64px">' +
      '<p class="chit-kicker">Маршрут от школы «Читательство»</p>' +
      '<h1 class="chit-h1">' + escapeHtml(r.title) + "</h1>" +
      '<p class="chit-lead">' + escapeHtml(r.blurb) + " · " + escapeHtml(r.ageLabel) + " · " + escapeHtml(r.time) + "</p>" +
      '<div class="chit-grid-3">' + r.steps.map(function (id, i) {
        const s = storyBy(id);
        if (!s) return "";
        return '<a class="chit-card chit-card--link" data-go="/stories/' + s.slug + '" href="' + href("/stories/" + s.slug) + '">' +
          chip("шаг " + (i + 1)) + (storyDone(s.slug) ? chip("пройдено", "sage") : chip("открыто")) +
          "<h3>" + escapeHtml(s.title) + "</h3><p>" + (regionBy(s.region) || {}).name + "</p></a>";
      }).join("") + "</div></div></main>" + footer();
  }

  function renderPassport() {
    document.title = "Паспорт читателя — Читательство";
    ensureProg();
    const done = DATA.stories.filter(function (s) { return storyDone(s.slug); });
    const rec = recommend();
    root.innerHTML = header("/passport") + '<main class="chit-exp-main"><div class="chit-wrap chit-passport-grid" style="padding:32px 20px 64px">' +
      "<div><p class=\"chit-kicker\">Паспорт читателя</p><h1 class=\"chit-h1\">Ваш путь по экспедиции</h1>" +
      "<p class=\"chit-lead\">Пройденные регионы, истории, бейджи и следующий шаг. Бейджи — часть игровой логики «Читательства».</p>" +
      '<img src="' + img("passport.png") + '" alt="" style="border-radius:20px;margin:12px 0;max-height:260px;width:100%;object-fit:cover">' +
      "<p>Пройдено историй: <strong>" + done.length + "</strong> · регионов: <strong>" + Object.keys(progress.regions).length + "</strong></p>" +
      (rec ? '<div class="chit-card" style="margin-top:12px"><h3>Следующий шаг</h3><p>' + escapeHtml(rec.title) + "</p>" +
        '<p style="margin-top:8px"><a class="chit-btn chit-btn--primary" data-go="/stories/' + rec.slug + '" href="' + href("/stories/" + rec.slug) + '">Продолжить</a></p></div>' : "") +
      "<h2>Открытые истории</h2>" +
      (done.length ? "<ul>" + done.map(function (s) { return "<li>" + escapeHtml(s.title) + "</li>"; }).join("") : "<p>Ещё нет отметок — начните с первой мини-экспедиции.</p>") +
      "</div><div><h2>Бейджи</h2>" +
      DATA.badges.map(function (b) {
        const on = progress.badges.indexOf(b.id) !== -1;
        return '<div class="chit-badge' + (on ? " is-on" : "") + '"><div class="mark">' + (on ? "★" : "·") + "</div><div><strong>" + escapeHtml(b.name) + "</strong><br><span style=\"color:var(--chit-muted);font-size:13px\">" + escapeHtml(b.how) + "</span></div></div>";
      }).join("") +
      "</div></div></main>" + footer();
  }

  function recommend() {
    ensureProg();
    const age = (progress.quiz && progress.quiz.age) || "";
    const interest = (progress.quiz && progress.quiz.interest) || "";
    const pool = DATA.stories.filter(function (s) { return !storyDone(s.slug); });
    if (age === "6-8") return pool.find(function (s) { return s.age === "6-8"; }) || pool[0];
    if (age === "9-11") return pool.find(function (s) { return s.age === "9-11"; }) || pool[0];
    if (interest === "objects") return pool.find(function (s) { return (s.themes || []).indexOf("objects") !== -1; }) || pool[0];
    if (interest === "local") return pool.find(function (s) { return (s.themes || []).indexOf("local") !== -1; }) || pool[0];
    return pool[0];
  }

  function renderLibraries() {
    document.title = "Библиотекам — Читательская экспедиция";
    const sc = DATA.scenario;
    root.innerHTML = header("/libraries") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:32px 20px 64px">' +
      '<p class="chit-kicker">Раздел для библиотек и педагогов</p>' +
      '<h1 class="chit-h1">Станьте точкой Читательской экспедиции</h1>' +
      '<div class="chit-grid-2">' +
      '<img src="' + img("library.png") + '" alt="Встреча в библиотеке" style="border-radius:20px;width:100%;object-fit:cover;aspect-ratio:16/10">' +
      "<div><p class=\"chit-lead\">Готовый сценарий, презентация, задания, паспорта, афиша, текст анонса, QR на маршрут и диплом участника.</p>" +
      "<p>Библиотека проводит встречу, собирает группу, оформляет полку, присылает короткий отчёт и при возможности — локальный материал с источниками.</p></div></div>" +
      '<div class="chit-card" style="margin:24px 0"><h2>' + escapeHtml(sc.title) + "</h2>" +
      "<p>Возраст: " + escapeHtml(sc.age) + ". Длительность: " + sc.minutes + " минут.</p><ol>" +
      sc.steps.map(function (s) { return "<li><strong>" + s.m + " мин</strong> — " + escapeHtml(s.t) + "</li>"; }).join("") +
      "</ol>" +
      '<p><a class="chit-btn chit-btn--ghost" href="' + (API || "") + '/expedition/kit.html" target="_blank" rel="noopener">Открыть сценарий для печати</a></p></div>' +
      "<h2 class=\"chit-h2\">Заявка на участие</h2>" +
      '<form class="chit-form" data-form="library">' +
      '<div class="row"><label>Учреждение<input name="org" required></label><label>Город<input name="city" required></label></div>' +
      '<div class="row"><label>Регион<input name="region" required></label><label>Контактное лицо<input name="contact" required></label></div>' +
      '<div class="row"><label>Email<input type="email" name="email" required></label><label>Телефон<input name="phone"></label></div>' +
      '<label>Комментарий<textarea name="comment"></textarea></label>' +
      '<label class="chit-check"><input type="checkbox" name="pd" required> Согласие на обработку персональных данных</label>' +
      '<button class="chit-btn chit-btn--primary" type="submit">Отправить заявку</button></form>' +
      '<p class="chit-form-out"></p></div></main>' + footer();
  }

  function renderLegend() {
    document.title = "Помогите нанести историю на карту — Читательство";
    root.innerHTML = header("/about") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:32px 20px 64px">' +
      '<p class="chit-kicker">Форма для библиотек, педагогов, музеев и семей</p>' +
      '<h1 class="chit-h1">Помогите нанести историю на карту</h1>' +
      '<p class="chit-lead">Знаете сказку, предание или легенду своего края? Расскажите о ней. После проверки редакцией «Читательства» она может стать частью «Читательской экспедиции».</p>' +
      "<p>Дети отправляют материал только через аккаунт взрослого. Сакральные и закрытые сюжеты без согласования не публикуются. Точные координаты частных и уязвимых объектов не нужны.</p>" +
      '<form class="chit-form" data-form="legend">' +
      '<div class="row"><label>Название истории<input name="title" required></label><label>Тип<select name="kind" required><option value="сказка">сказка</option><option value="легенда">легенда</option><option value="предание">предание</option><option value="персонаж">персонаж</option><option value="локация">локация</option></select></label></div>' +
      '<div class="row"><label>Регион<input name="region" required></label><label>Населённый пункт<input name="place" required></label></div>' +
      '<label>Точка на карте или примерные координаты<input name="coords"></label>' +
      '<label>Краткий пересказ<textarea name="summary" required></textarea></label>' +
      '<label>Полный текст (если есть право на публикацию)<textarea name="fulltext"></textarea></label>' +
      '<div class="row"><label>Имя героя<input name="hero"></label><label>Народ / традиция<input name="tradition" required></label></div>' +
      '<div class="row"><label>Язык оригинала<input name="lang" required></label><label>Возрастная рекомендация<select name="age"><option>6–8</option><option>9–11</option><option>семейный</option></select></label></div>' +
      '<label>Источник (книга, архив, музей, библиотека, ссылка)<input name="source" required></label>' +
      '<div class="row"><label>Кто подготовил<input name="author" required></label><label>Дата и место записи<input name="recorded"></label></div>' +
      '<div class="row"><label>Email<input type="email" name="email" required></label><label>Имя контакта<input name="contact" required></label></div>' +
      '<label class="chit-check"><input type="checkbox" name="rules" required> Согласие с правилами публикации</label>' +
      '<label class="chit-check"><input type="checkbox" name="pd" required> Согласие на обработку персональных данных</label>' +
      '<button class="chit-btn chit-btn--primary" type="submit">Отправить на проверку</button></form>' +
      '<p class="chit-form-out"></p></div></main>' + footer();
  }

  function renderAbout() {
    document.title = "О проекте — Читательская экспедиция";
    root.innerHTML = header("/about") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:32px 20px 64px;max-width:800px">' +
      '<p class="chit-kicker">О проекте</p>' +
      '<h1 class="chit-h1">Читательская экспедиция внутри школы «Читательство»</h1>' +
      "<p>«Читательская экспедиция» — интерактивный литературный маршрут от школы «Читательство» для детей 6–11 лет, семей и библиотек.</p>" +
      "<p>Через карту, сказки, героев, аудиоистории и игровые задания дети знакомятся с культурой народов России и учатся читать внимательно: замечать детали, понимать поступки персонажей, сравнивать сюжеты, задавать вопросы и создавать собственный творческий отклик.</p>" +
      "<p>Каждый регион здесь — часть большого путешествия по книгам, смыслам и историям.</p>" +
      "<h2>Как устроена достоверность</h2>" +
      "<ul><li><strong>Подтверждено источниками</strong> — сборник, архив, библиотека, музей, признанный источник.</li>" +
      "<li><strong>Региональная традиция</strong> — местное предание, устойчивая локальная версия.</li>" +
      "<li><strong>Современная культурная интерпретация</strong> — фестивальный образ, музейный персонаж, поздняя легенда.</li>" +
      "<li><strong>Материал на проверке</strong> — не публикуется как факт.</li></ul>" +
      "<h2>Сообщить об ошибке</h2>" +
      '<form class="chit-form" data-form="error"><label>Что исправить<textarea name="message" required></textarea></label>' +
      '<label>Email для ответа<input type="email" name="email"></label>' +
      '<button class="chit-btn chit-btn--primary" type="submit">Отправить</button></form><p class="chit-form-out"></p>' +
      "</div></main>" + footer();
  }

  function renderNotFound() {
    document.title = "Страница не найдена — Читательство";
    root.innerHTML = header("/") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:64px 20px"><h1>Этой точки на карте пока нет</h1>' +
      '<p><a class="chit-btn chit-btn--primary" data-go="/" href="' + href("/") + '">На главную экспедиции</a></p></div></main>' + footer();
  }

  function openQuiz() {
    const box = document.createElement("div");
    box.className = "chit-modal";
    box.innerHTML = '<div class="chit-modal__card" role="dialog" aria-labelledby="q-title">' +
      '<p class="chit-kicker">Выберите свою экспедицию</p><h2 id="q-title">Четыре коротких вопроса</h2>' +
      '<div id="q-body"></div></div>';
    document.body.appendChild(box);
    const state = { step: 0, age: "", interest: "", time: "", start: "" };
    const steps = [
      { key: "age", q: "Сколько вам лет?", opts: [["6-8", "6–8 лет"], ["9-11", "9–11 лет"], ["family", "Читаем всей семьёй"], ["lib", "Я библиотекарь / педагог"]] },
      { key: "interest", q: "Что интересно?", opts: [["objects", "Волшебные предметы"], ["animals", "Животные-помощники"], ["heroes", "Смелые герои"], ["mystery", "Загадки и тайны"], ["travel", "Путешествия"], ["local", "Сказки моего края"], ["any", "Хочу выбрать сам"]] },
      { key: "time", q: "Сколько времени есть?", opts: [["10", "10 минут"], ["30", "20–30 минут"], ["lesson", "Одно занятие"], ["week", "Неделя"], ["month", "Месяц"]] },
      { key: "start", q: "С чего начать?", opts: [["my", "С моего региона"], ["any", "С любого региона России"], ["theme", "С тематического маршрута"]] }
    ];
    function paint() {
      const s = steps[state.step];
      document.getElementById("q-body").innerHTML = "<p>" + s.q + "</p>" +
        s.opts.map(function (o) { return '<button class="chit-quiz-opt" type="button" data-k="' + o[0] + '">' + o[1] + "</button>"; }).join("");
      document.getElementById("q-body").querySelectorAll("[data-k]").forEach(function (b) {
        b.addEventListener("click", function () {
          state[s.key] = b.getAttribute("data-k");
          if (state.step < steps.length - 1) { state.step += 1; paint(); }
          else finish();
        });
      });
    }
    function finish() {
      ensureProg();
      progress.quiz = { age: state.age, interest: state.interest, time: state.time, start: state.start };
      saveProgress();
      box.remove();
      if (state.age === "lib") return go("/libraries");
      if (state.age === "6-8") return go("/routes/first-expedition");
      if (state.age === "9-11") return go("/routes/literary-detective");
      if (state.age === "family") return go("/routes/family-reading");
      go("/map");
    }
    box.addEventListener("click", function (e) { if (e.target === box) box.remove(); });
    paint();
  }

  async function sendForm(kind, form) {
    const out = form.parentElement.querySelector(".chit-form-out");
    const payload = { kind: kind };
    new FormData(form).forEach(function (v, k) { payload[k] = v; });
    payload.status = "submitted";
    payload.createdAt = new Date().toISOString();
    try {
      const res = await fetch((API || "") + "/expedition/api/" + kind, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("bad");
      form.hidden = true;
      out.innerHTML = '<div class="chit-success-msg">Заявка отправлена на проверку редакции «Читательства». Мы напишем на указанный контакт.</div>';
    } catch (e) {
      const key = "chit-expedition-" + kind;
      const list = JSON.parse(localStorage.getItem(key) || "[]");
      list.push(payload);
      localStorage.setItem(key, JSON.stringify(list));
      form.hidden = true;
      out.innerHTML = '<div class="chit-success-msg">Заявка сохранена. Когда сервер будет доступен, редакция получит её из очереди прототипа.</div>';
    }
  }

  function bindClicks(e) {
    const goEl = e.target.closest("[data-go]");
    if (goEl) {
      const to = goEl.getAttribute("data-go");
      if (to && goEl.getAttribute("href") && goEl.getAttribute("href").charAt(0) !== "h") {
        e.preventDefault();
        go(to);
      } else if (to && !goEl.getAttribute("href")) {
        e.preventDefault();
        go(to);
      } else if (to && goEl.getAttribute("href") && goEl.getAttribute("href").indexOf("/expedition") === 0) {
        e.preventDefault();
        go(to);
      } else if (to && goEl.getAttribute("href") && goEl.getAttribute("href").charAt(0) === "#") {
        e.preventDefault();
        go(to);
      }
    }
    const act = e.target.closest("[data-act]");
    if (act && act.getAttribute("data-act") === "start") openQuiz();
  }

  function bindSubmit(e) {
    const form = e.target.closest("form[data-form]");
    if (!form) return;
    e.preventDefault();
    sendForm(form.getAttribute("data-form"), form);
  }

  function parseRoute() {
    let p = currentPath();
    const qIdx = location.search.indexOf("region=");
    if (p === "/map" && qIdx !== -1) {
      return { name: "map", slug: new URLSearchParams(location.search).get("region") };
    }
    if (p.charAt(0) !== "/") p = "/" + p;
    if (p === "/" || p === "") return { name: "home" };
    if (p === "/map") return { name: "map" };
    if (p === "/regions") return { name: "regions" };
    if (p === "/routes") return { name: "routes" };
    if (p === "/passport") return { name: "passport" };
    if (p === "/libraries") return { name: "libraries" };
    if (p === "/add-legend") return { name: "legend" };
    if (p === "/about") return { name: "about" };
    const parts = p.split("/").filter(Boolean);
    if (parts[0] === "regions" && parts[1]) return { name: "region", slug: parts[1] };
    if (parts[0] === "stories" && parts[1]) return { name: "story", slug: parts[1] };
    if (parts[0] === "heroes" && parts[1]) return { name: "hero", slug: parts[1] };
    if (parts[0] === "routes" && parts[1]) return { name: "route", slug: parts[1] };
    if (parts[0] === "map") return { name: "map" };
    return { name: "notfound" };
  }

  function render() {
    if (!DATA) return;
    ensureProg();
    const r = parseRoute();
    if (r.name === "home") renderHome();
    else if (r.name === "map") renderMap(r.slug);
    else if (r.name === "regions") renderRegions();
    else if (r.name === "region") renderRegion(r.slug);
    else if (r.name === "story") renderStory(r.slug);
    else if (r.name === "hero") renderHero(r.slug);
    else if (r.name === "routes") renderRoutes();
    else if (r.name === "route") renderRoute(r.slug);
    else if (r.name === "passport") renderPassport();
    else if (r.name === "libraries") renderLibraries();
    else if (r.name === "legend") renderLegend();
    else if (r.name === "about") renderAbout();
    else renderNotFound();
  }

  root.addEventListener("click", bindClicks);
  root.addEventListener("submit", bindSubmit);
  window.addEventListener("popstate", render);
  window.addEventListener("hashchange", render);

  fetch(DATA_URL).then(function (r) { return r.json(); }).then(function (d) {
    DATA = d;
    render();
  }).catch(function () {
    root.innerHTML = "<p style='padding:40px'>Не удалось загрузить данные экспедиции.</p>";
  });
})();
