(function () {
  const root = document.getElementById("chit-exp-root");
  if (!root) return;

  const ASSET = root.dataset.asset || "/static/expedition/";
  const DATA_URL = root.dataset.data || ASSET + "data.json";
  const API = (root.dataset.api || "").replace(/\/$/, "");
  const PROG_KEY = "chit-expedition-progress-v1";
  const AUTH_KEY = "chit-expedition-session";
  const AVATARS = { compass: "🧭", book: "📖", star: "✦", boat: "🛶", fox: "🦊" };

  let DATA = null;
  let progress = loadProgress();
  let session = loadSession();
  let profile = null;
  let accessMap = {};
  let tariffs = [];
  let mapState = { scale: 1, x: 0, y: 0, atlas: false, filters: { q: "", age: "", theme: "", audio: "", status: "" } };
  let passState = { i: 0, side: 0 };
  let passSpreadsCache = [];

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
    if (session && session.token) syncProgress();
  }
  function loadSession() {
    try {
      return JSON.parse(localStorage.getItem(AUTH_KEY) || "null");
    } catch (e) {
      return null;
    }
  }
  function saveSession(next) {
    session = next;
    if (next) localStorage.setItem(AUTH_KEY, JSON.stringify(next));
    else localStorage.removeItem(AUTH_KEY);
  }
  function apiUrl(path) {
    return (API || "") + path;
  }
  function syncProgress() {
    if (!session || !session.token) return;
    fetch(apiUrl("/expedition/api/cabinet/progress"), {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + session.token },
      body: JSON.stringify(progress)
    }).then(function (r) { return r.json(); }).then(function (body) {
      if (body && body.profile) {
        profile = body.profile;
        accessMap = body.profile.access || accessMap;
      }
    }).catch(function () {});
  }
  function refreshCabinet() {
    const headers = {};
    if (session && session.token) headers.Authorization = "Bearer " + session.token;
    return fetch(apiUrl("/expedition/api/cabinet"), { headers: headers }).then(function (r) { return r.json(); }).then(function (body) {
      tariffs = body.tariffs || [];
      accessMap = body.access || {};
      if (body.signed_in && body.profile) {
        profile = body.profile;
        if (body.token) saveSession({ token: body.token, child_name: body.profile.child_name });
        progress = Object.assign(progress, body.progress || {});
        saveProgressLocal();
      }
      return body;
    }).catch(function () { return null; });
  }
  function saveProgressLocal() {
    progress.updatedAt = new Date().toISOString();
    localStorage.setItem(PROG_KEY, JSON.stringify(progress));
  }
  function ensureProg() {
    progress.stories = progress.stories || {};
    progress.badges = progress.badges || [];
    progress.saved = progress.saved || [];
    progress.regions = progress.regions || {};
    progress.stamps = progress.stamps || {};
    progress.route = progress.route || "";
    progress.quiz = progress.quiz || {};
    progress.listened = progress.listened || [];
    progress.finds = progress.finds || {};
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
  function storyAccess(s) {
    if (!s) return "locked";
    if (s.status === "hidden") return "locked";
    if (accessMap[s.slug] && accessMap[s.slug] !== "locked") return accessMap[s.slug];
    if (s.access === "demo") return "demo";
    return "open";
  }
  function isOpenStory(s) {
    const a = storyAccess(s);
    return a === "demo" || a === "free" || a === "open";
  }
  function activeTariffs() {
    const list = (tariffs && tariffs.length) ? tariffs : ((DATA && DATA.tariffs) || []);
    return list.filter(function (t) { return t.active !== false; });
  }
  function tariffCardsHtml(audience) {
    return activeTariffs().filter(function (t) {
      return audience === "library" ? t.audience === "library" : t.audience !== "library";
    }).map(function (t) {
      const price = t.price_rub == null ? "цену задаёт администратор" : t.price_rub + " ₽";
      return '<article class="chit-card"><h3>' + escapeHtml(t.title) + "</h3><p>" + escapeHtml(t.blurb || "") + "</p><p><strong>" + escapeHtml(String(price)) + "</strong></p></article>";
    }).join("");
  }
  function stampMotif(symbol) {
    return {
      frog: '<circle cx="32" cy="28" r="10"/><ellipse cx="32" cy="44" rx="14" ry="8"/><circle cx="24" cy="22" r="4"/><circle cx="40" cy="22" r="4"/>',
      frost: '<path d="M32 10v44M16 32h32M20 18l12 14 12-14M20 46l12-14 12 14"/>',
      star: '<path d="M32 12l5 14h15l-12 9 5 14-13-9-13 9 5-14-12-9h15z"/>',
      horn: '<path d="M18 44c8-22 26-22 34-4-10-2-18 4-22 14-6-4-10-8-12-10z"/>',
      horse: '<path d="M14 42l8-18 10-6 6 4 12-8 4 6-10 6 2 16H22z"/>',
      sun: '<circle cx="32" cy="32" r="10"/><path d="M32 8v8M32 48v8M8 32h8M48 32h8M16 16l6 6M42 42l6 6M16 48l6-6M42 22l6-6"/>',
      road: '<path d="M24 54L30 10h4L40 54z"/><path d="M32 18v6M32 30v6M32 42v6"/>',
      lake: '<ellipse cx="32" cy="36" rx="18" ry="10"/><path d="M18 22c6-8 22-8 28 0"/>',
      wave: '<path d="M10 28c6 8 10 8 16 0s10-8 16 0 10 8 16 0"/><path d="M10 40c6 8 10 8 16 0s10-8 16 0 10 8 16 0"/>',
      pine: '<path d="M32 10l14 18H18zM32 22l16 20H16zM29 42h6v12h-6z"/>',
      stone: '<path d="M12 42l8-16 14-8 16 10 4 14H12z"/>'
    }[symbol] || '<circle cx="32" cy="32" r="14"/><path d="M32 18v28M20 32h24"/>';
  }
  function stampSvg(symbol, color, level, ghost) {
    const c = color || "#8B3A42";
    const gold = level === "gold";
    const op = ghost ? "0.35" : "1";
    return '<svg class="chit-stamp-svg" viewBox="0 0 64 64" aria-hidden="true" style="opacity:' + op + '"><circle cx="32" cy="32" r="30" fill="' + (gold ? c : "transparent") + '" fill-opacity="' + (gold ? "0.18" : "0") + '" stroke="' + c + '" stroke-width="3"/><g fill="none" stroke="' + c + '" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">' + stampMotif(symbol) + "</g></svg>";
  }
  function stampSealSvg(opts) {
    const c = opts.color || "#8B3A42";
    const gold = opts.level === "gold";
    const ghost = !!opts.ghost;
    const uid = "chit-ring-" + String(opts.uid || "x").replace(/[^a-z0-9_-]/gi, "");
    const region = escapeHtml(opts.regionName || "");
    const poetic = escapeHtml(opts.poetic || "");
    const date = escapeHtml(opts.date || "");
    const fill = gold ? "rgba(196,165,106,0.18)" : "rgba(255,248,236,0.4)";
    const label = region + (poetic ? ". " + poetic : "") + (date ? ". " + date : "");
    return '<div class="chit-seal' + (ghost ? " is-ghost" : "") + (opts.sample ? " is-sample" : "") + '">' +
      '<svg class="chit-seal-svg" viewBox="0 0 200 200" role="img" aria-label="' + label + '">' +
      '<defs><path id="' + uid + '" d="M100,100 m-78,0 a78,78 0 1,1 156,0 a78,78 0 1,1 -156,0"/></defs>' +
      '<circle cx="100" cy="100" r="96" fill="' + fill + '" stroke="' + c + '" stroke-width="' + (gold ? 5 : 3.2) + '" stroke-dasharray="' + (ghost ? "5 6" : "0") + '"/>' +
      '<circle cx="100" cy="100" r="82" fill="none" stroke="' + c + '" stroke-width="1.1" opacity="0.65"/>' +
      '<text fill="' + c + '" font-size="8.2" font-family="Georgia, serif" letter-spacing="1.8">' +
      '<textPath href="#' + uid + '" startOffset="0%">ЧИТАТЕЛЬСКАЯ ЭКСПЕДИЦИЯ · ЧИТАТЕЛЬСТВО · ЧИТАТЕЛЬСКАЯ ЭКСПЕДИЦИЯ · </textPath></text>' +
      '<text x="100" y="56" text-anchor="middle" fill="' + c + '" font-size="8" font-family="Georgia, serif" font-weight="700">' + region + "</text>" +
      '<g transform="translate(68 68)" fill="none" stroke="' + c + '" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">' + stampMotif(opts.symbol) + "</g>" +
      '<text x="100" y="146" text-anchor="middle" fill="' + c + '" font-size="8.4" font-family="Georgia, serif">' + poetic + "</text>" +
      (date ? '<text x="100" y="164" text-anchor="middle" fill="' + c + '" font-size="7" opacity="0.85">' + date + "</text>" : "") +
      '<text x="100" y="178" text-anchor="middle" fill="' + c + '" font-size="11">✦</text>' +
      "</svg></div>";
  }
  function stampCardHtml(r, st) {
    const meta = r.stamp || {};
    const on = !!st;
    const color = (st && st.color) || meta.color || "#8B3A42";
    const level = (st && st.level) || "";
    const title = (st && st.poetic_title) || meta.poetic_title || r.pin;
    const date = st && st.earned_at ? formatRuDate(st.earned_at) : "ждёт миссии";
    return '<div class="chit-stamp' + (on ? " is-on" : "") + '" style="--stamp:' + color + '">' +
      stampSvg(meta.symbol, color, level, !on) +
      "<strong>" + escapeHtml(title) + "</strong>" +
      "<small>" + escapeHtml(r.name) + (level ? " · " + level : "") + " · " + escapeHtml(date) + "</small></div>";
  }
  function formatRuDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    if (isNaN(d.getTime())) return String(iso).slice(0, 10);
    return d.toLocaleDateString("ru-RU");
  }
  function childLevel() {
    const n = DATA.stories.filter(function (s) { return storyDone(s.slug); }).length;
    if (n >= 8) return "Литературный детектив";
    if (n >= 5) return "Мастер слова";
    if (n >= 3) return "Исследователь";
    if (n >= 1) return "Юный читатель";
    return "Старт";
  }
  function seasonRegions() {
    return (DATA.regions || []).slice(0, 12);
  }
  function awardStamp(regionSlug, levelHint) {
    const region = regionBy(regionSlug);
    if (!region) return null;
    ensureProg();
    const stories = DATA.stories.filter(function (s) { return s.region === regionSlug; });
    const done = stories.filter(function (s) { return storyDone(s.slug); }).length;
    let level = levelHint || "";
    if (done >= 3) level = "gold";
    else if (done >= 1) level = "basic";
    else if (!level) return null;
    const prev = progress.stamps[regionSlug] || {};
    const rank = { marker: 1, basic: 2, gold: 3 };
    if ((rank[level] || 0) <= (rank[prev.level] || 0)) return progress.stamps[regionSlug];
    const meta = region.stamp || {};
    progress.stamps[regionSlug] = {
      level: level,
      poetic_title: meta.poetic_title || region.pin,
      motif: meta.motif || "",
      symbol: meta.symbol || "",
      color: meta.color || "#8B3A42",
      region_name: region.name,
      earned_at: new Date().toISOString()
    };
    progress.regions[regionSlug] = true;
    saveProgress();
    return progress.stamps[regionSlug];
  }
  function showNewStampModal(stamp, region) {
    const existing = document.querySelector(".chit-stamp-press");
    if (existing) existing.remove();
    const meta = (region && region.stamp) || {};
    const el = document.createElement("div");
    el.className = "chit-stamp-press";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-labelledby", "chit-new-stamp-title");
    const saveBlock = profile
      ? ""
      : "<p class=\"chit-note\">Чтобы штамп остался в паспорте, попроси взрослого помочь открыть его.</p>" +
        '<p><button class="chit-btn chit-btn--primary" type="button" data-act="open-passport">Открыть паспорт с взрослым</button></p>';
    el.innerHTML = '<div class="chit-stamp-press__seal">' +
      stampSealSvg({
        uid: "modal-" + ((region && region.slug) || "x"),
        regionName: stamp.region_name || (region && region.name) || "",
        poetic: stamp.poetic_title || meta.poetic_title,
        symbol: stamp.symbol || meta.symbol,
        color: stamp.color || meta.color,
        level: stamp.level,
        date: formatRuDate(stamp.earned_at)
      }) +
      '<strong id="chit-new-stamp-title">Новый штамп!</strong>' +
      "<span>«" + escapeHtml(stamp.poetic_title || "Печать экспедиции") + "»</span>" +
      "<span>" + escapeHtml(stamp.region_name || "") + "</span>" +
      "<p>Ты заметил важные детали в сказке и выполнил миссию читателя.</p>" +
      saveBlock +
      '<div class="chit-stamp-press__actions">' +
      '<a class="chit-btn chit-btn--primary" data-go="/passport" href="' + href("/passport") + '">Посмотреть в паспорте</a>' +
      '<button class="chit-btn chit-btn--ghost" type="button" data-act="close-stamp">Продолжить путешествие</button>' +
      "</div></div>";
    document.body.appendChild(el);
    el.addEventListener("click", function (e) {
      const goEl = e.target.closest("[data-go]");
      if (goEl) {
        e.preventDefault();
        const slug = region && region.slug;
        if (slug) {
          const idx = seasonRegions().findIndex(function (r) { return r.slug === slug; });
          passState.i = idx >= 0 ? idx + 2 : 0;
          passState.side = 1;
        }
        closeStampModal();
        go(goEl.getAttribute("data-go"));
        return;
      }
      const act = e.target.closest("[data-act]");
      if (!act) return;
      const name = act.getAttribute("data-act");
      if (name === "close-stamp") closeStampModal();
      if (name === "open-passport") {
        closeStampModal();
        openPassportModal();
      }
    });
  }
  function closeStampModal() {
    const el = document.querySelector(".chit-stamp-press");
    if (el) el.remove();
  }
  function placeStoryStamp(s) {
    if (!s) return;
    ensureProg();
    if (!storyDone(s.slug)) return;
    const stamp = awardStamp(s.region);
    const region = regionBy(s.region);
    if (!stamp) return;
    showNewStampModal(stamp, region);
    const ritual = document.getElementById("chit-ritual");
    if (ritual) {
      ritual.innerHTML = "<p>Экспедиция в регионе «" + escapeHtml((region && region.name) || "экспедиции") + "» завершена. Печать стоит в паспорте.</p>";
    }
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
    const signed = !!(profile && profile.child_name);
    const links = [
      ["/map", "Карта"],
      ["/routes", "Маршруты"],
      ["/passport", "Паспорт"],
      ["/collection", "Мои истории"]
    ];
    const account = signed
      ? '<a class="chit-account" data-go="/passport" href="' + href("/passport") + '">' + escapeHtml(profile.child_name) + "</a>"
      : '<a class="chit-account" href="#" data-act="open-passport">Сохранить паспорт</a>';
    return (
      '<header class="chit-exp-header"><div class="chit-exp-header__inner">' +
      '<a class="chit-exp-logo" href="https://chitatelstvo.ru">' +
      '<img src="https://api.chitatelstvo.ru/assets/logo-chitatelstvo.png" alt="Читательство" width="150" height="40">' +
      "<span>Читательская экспедиция</span></a>" +
      '<nav class="chit-exp-nav chit-child-nav" aria-label="Разделы экспедиции">' +
      links.map(function (l) {
        return '<a href="' + href(l[0]) + '" class="' + (active === l[0] ? "is-on" : "") + '" data-go="' + l[0] + '">' + l[1] + "</a>";
      }).join("") +
      account +
      "</nav></div></header>"
    );
  }

  function footer() {
    return (
      '<footer class="chit-exp-footer">' +
      "<p>Читательская экспедиция от литературной школы «Читательство».</p>" +
      '<p><a href="https://chitatelstvo.ru">chitatelstvo.ru</a> · ' +
      '<a href="mailto:info@chitatelstvo.ru">info@chitatelstvo.ru</a> · ' +
      '<a data-go="/parents" href="' + href("/parents") + '">Родителям</a> · ' +
      '<a data-go="/libraries" href="' + href("/libraries") + '">Для библиотек</a> · ' +
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
      "<p class=\"chit-note\">Истории открыты для знакомства. Чтобы сохранить штамп и паспорт, попросите взрослого оставить контакт.</p>" +
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
      "<h2 class=\"chit-h2\">Паспорт читательской экспедиции</h2>" +
      "<p>Разворот паспорта, штампы регионов, книжная полка и следующая остановка. Можно листать до регистрации — сохранение печати просит помощи взрослого.</p>" +
      '<p style="margin-top:16px"><a class="chit-btn chit-btn--ghost" data-go="/passport" href="' + href("/passport") + '">Листать паспорт</a></p>' +
      "</div></div></section>" +

      '<section class="chit-cta-band"><div class="chit-wrap">' +
      "<h2 class=\"chit-h2\">Продолжите литературное путешествие в «Читательстве»</h2>" +
      "<p>Хотите продолжить исследование? В литературной школе «Читательство» вас ждут полные занятия, новые истории, творческие задания и следующий уровень читательского пути.</p>" +
      '<a class="chit-btn chit-btn--primary" href="https://chitatelstvo.ru/#program">К программам школы</a>' +
      "</div></section></main>" + footer();
  }

  function pinMarkup(r, selected, mode) {
    const atlas = mode === "atlas";
    const x = atlas && r.gx != null ? r.gx : r.cx;
    const y = atlas && r.gy != null ? r.gy : r.cy;
    const rad = atlas ? 7 : 6;
    const on = selected && selected.slug === r.slug ? " is-on" : "";
    const n = (r.stories || []).length;
    const label = r.pin || r.name;
    const lx = atlas ? (r.glx != null ? r.glx : x) : x;
    const ly = atlas ? (r.gly != null ? r.gly : y + rad + 16) : y;
    return (
      '<g class="chit-pin ' + pinClass(r) + on + '" data-region="' + r.slug + '" tabindex="0" role="button" aria-label="' + escapeHtml(r.name) + '">' +
      (atlas ? '<circle class="chit-pin__glow" cx="' + x + '" cy="' + y + '" r="' + (rad + 8) + '"></circle>' : "") +
      '<circle class="chit-pin__ring" cx="' + x + '" cy="' + y + '" r="' + (rad + 2) + '"></circle>' +
      '<circle class="region" cx="' + x + '" cy="' + y + '" r="' + rad + '"></circle>' +
      (atlas ? '<text class="chit-pin__label" x="' + lx + '" y="' + ly + '" text-anchor="middle">' + escapeHtml(label) + "</text>" : "") +
      "<title>" + escapeHtml(r.name) + (n ? " · историй: " + n : "") + "</title>" +
      "</g>"
    );
  }

  function renderMap(selectedSlug) {
    document.title = "Карта экспедиции — Читательство";
    const selected = selectedSlug ? regionBy(selectedSlug) : DATA.regions.find(function (r) { return r.status !== "empty"; });
    const fairyPins = DATA.regions.filter(function (r) {
      return regionMatches(r) && r.stories && r.stories.length;
    }).map(function (r) { return pinMarkup(r, selected, "fairy"); }).join("");
    const atlasPins = DATA.regions.filter(regionMatches).map(function (r) { return pinMarkup(r, selected, "atlas"); }).join("");
    const fairySrc = img("hero-map.png") + "?v=20260918p";
    const atlasSrc = img("hero-map-atlas.png") + "?v=20260918p";

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
      '<button type="button" class="chit-btn chit-btn--small chit-btn--ghost" id="chit-map-atlas-btn" aria-pressed="' + (mapState.atlas ? "true" : "false") + '">Атлас</button>' +
      "</div>" +
      '<div class="chit-zoom"><button type="button" data-zoom="-">−</button><button type="button" data-zoom="+">+</button></div>' +
      '<div class="chit-map-svg-wrap' + (mapState.atlas ? " is-atlas" : "") + '" id="chit-map-drag">' +
      '<div class="chit-map-artboard" style="background-image:url(\'' + fairySrc + '\')">' +
      '<div class="chit-map-atlas-layer" style="background-image:url(\'' + atlasSrc + '\')"></div>' +
      '<svg class="chit-map-svg chit-map-svg--fairy" viewBox="0 0 1000 562" role="img" aria-label="Сказочная карта маршрутов экспедиции">' +
      fairyPins +
      "</svg>" +
      '<svg class="chit-map-svg chit-map-svg--atlas" viewBox="0 0 1024 576" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Атлас регионов России">' +
      atlasPins +
      "</svg></div></div>" +
      '<p class="chit-map-hint">Наведите на карту — откроется атлас с границами регионов.</p>' +
      '<div class="chit-legend-map">' +
      "<div><i class=\"is-wait\"></i>скоро</div>" +
      "<div><i class=\"is-open\"></i>доступен</div>" +
      "<div><i class=\"is-route\"></i>есть маршрут</div>" +
      "<div><i class=\"is-done\"></i>пройден</div>" +
      "</div></div>" +
      '<aside class="chit-map-side" id="chit-map-side">' + regionPanel(selected) + "</aside>" +
      "</main>" + footer();

    bindMap();
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
    const wrap = document.getElementById("chit-map-drag");
    const atlasBtn = document.getElementById("chit-map-atlas-btn");
    function setAtlas(on) {
      if (!wrap) return;
      wrap.classList.toggle("is-atlas", on);
      if (atlasBtn) atlasBtn.setAttribute("aria-pressed", on ? "true" : "false");
    }
    if (wrap) {
      wrap.addEventListener("mouseenter", function () { setAtlas(true); });
      wrap.addEventListener("mouseleave", function () { if (!mapState.atlas) setAtlas(false); });
    }
    if (atlasBtn) {
      atlasBtn.addEventListener("click", function () {
        mapState.atlas = !mapState.atlas;
        setAtlas(mapState.atlas);
      });
    }
    if (mapState.atlas) setAtlas(true);
    if (wrap && wrap.matches(":hover")) setAtlas(true);
    root.querySelectorAll("[data-zoom]").forEach(function (b) {
      b.addEventListener("click", function () {
        const board = root.querySelector(".chit-map-artboard");
        mapState.scale = Math.min(2.4, Math.max(0.8, mapState.scale + (b.getAttribute("data-zoom") === "+" ? 0.2 : -0.2)));
        if (board) {
          board.style.transform = "scale(" + mapState.scale + ")";
          board.style.transformOrigin = "center";
        }
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
      (first ? "<h2 class=\"chit-h2\">История региона</h2><p>Иллюстрация, герой, аудио, фрагмент и миссия читателя. После миссии можно поставить штамп в паспорт.</p>" : "") +
      "<h2 class=\"chit-h2\">Герои и истории региона</h2>" +
      '<div class="chit-grid-3">' + stories.map(function (s) {
        const open = isOpenStory(s) || storyDone(s.slug);
        const status = storyDone(s.slug) ? chip("пройдено", "sage") : (open ? chip("открыто") : chip("тизер", "gold"));
        return '<a class="chit-card chit-card--link" data-go="/stories/' + s.slug + '" href="' + href("/stories/" + s.slug) + '">' +
          '<img src="' + img(s.image) + '" alt="" style="border-radius:12px;aspect-ratio:16/10;object-fit:cover;width:100%;margin-bottom:8px">' +
          chip(s.ageLabel || s.age) + credChip(s) + status +
          "<h3>" + escapeHtml(s.title) + "</h3><p>" + (open ? s.minutes + " минут" : escapeHtml(s.learn || "История откроется по тарифу.")) + "</p></a>";
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
    if (!isOpenStory(s)) return renderStoryTeaser(s);
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
      '<div class="chit-stamp-ritual" id="chit-ritual"' + (storyDone(s.slug) ? "" : " hidden") + ">" +
      (progress.stamps[s.region]
        ? "<p>Экспедиция в этом регионе завершена. Печать уже в паспорте.</p>"
        : "<p>История прочитана. Поставь печать — и регион останется на странице паспорта.</p>" +
          '<button class="chit-btn chit-btn--primary" type="button" data-act="place-stamp" data-story="' + s.slug + '">Я готов поставить штамп</button>') +
      (!profile ? "<p class=\"chit-note\">Чтобы сохранить штамп, попроси взрослого помочь открыть паспорт.</p>" : "") +
      "</div>" +
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
      grantBadge("teller");
      toast("Отклик сохранён в паспорте");
    });
  }

  function completeStory(s) {
    ensureProg();
    progress.stories[s.slug] = progress.stories[s.slug] || {};
    progress.stories[s.slug].done = true;
    progress.regions[s.region] = true;
    saveProgress();
    grantBadge(s.badge || "reader");
    grantBadge("reader");
    const doneCount = Object.keys(progress.stories).filter(function (k) { return progress.stories[k].done; }).length;
    if (doneCount >= 3) grantBadge("explorer");
    if (Object.keys(progress.regions).length >= 2) grantBadge("traveler");
    const ritual = document.getElementById("chit-ritual");
    if (ritual) ritual.hidden = false;
    if (!progress.stamps[s.region] && ritual) {
      ritual.querySelector("[data-act='place-stamp']") && ritual.querySelector("[data-act='place-stamp']").focus();
    }
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
    document.title = "Паспорт читательской экспедиции — Читательство";
    ensureProg();
    passSpreadsCache = buildPassportSpreads();
    if (passState.i >= passSpreadsCache.length) passState.i = 0;
    const rec = recommend();
    const toNext = rec && !progress.stamps[rec.region] ? 1 : 0;
    const dots = passSpreadsCache.map(function (_, i) {
      return "<span class=\"" + (i === passState.i ? "is-on" : "") + "\"></span>";
    }).join("");
    root.innerHTML = header("/passport") +
      '<main class="chit-exp-main chit-pass-desk">' +
      '<div class="chit-pass-hero">' +
      '<p class="chit-kicker">Читательская экспедиция</p>' +
      '<h1 class="chit-h1">Паспорт читательской экспедиции</h1>' +
      "<p class=\"chit-lead\">Здесь сохраняются сказки, которые ты открыл, регионы, которые исследовал, и штампы, которые заслужил.</p>" +
      "</div>" +
      '<div class="chit-pass-cover">' +
      '<div class="chit-pass-cover__foil">Читательская экспедиция</div>' +
      '<div class="chit-pass-book" id="chit-pass-book" data-side="' + (passState.side ? "right" : "left") + '">' +
      '<div id="chit-pass-stage"></div></div></div>' +
      '<div class="chit-pass-toolbar">' +
      '<button class="chit-btn chit-btn--ghost chit-btn--small" type="button" data-act="pass-prev" aria-label="Назад">←</button>' +
      '<div class="chit-pass-pager"><span id="chit-pass-num"></span></div>' +
      '<button class="chit-btn chit-btn--ghost chit-btn--small" type="button" data-act="pass-next" aria-label="Вперёд">→</button>' +
      '<button class="chit-btn chit-btn--primary chit-btn--small" type="button" data-act="pass-next">Листать паспорт</button>' +
      '<a class="chit-btn chit-btn--ghost chit-btn--small" data-go="/map" href="' + href("/map") + '">Открыть карту</a>' +
      "</div>" +
      '<div class="chit-pass-dots" aria-hidden="true">' + dots + "</div>" +
      '<p class="chit-pass-hint">' + (toNext ? "До следующего штампа — 1 история." : "Следующая остановка уже открыта в паспорте.") + "</p>" +
      '<aside class="chit-pass-parent"><div><p><strong>Кабинет родителя.</strong> Тариф, доступ, данные профиля и прогресс ребёнка — отдельно от детских страниц.</p></div>' +
      '<a class="chit-btn chit-btn--ghost chit-btn--small" data-go="/parents" href="' + href("/parents") + '">Родителям</a></aside>' +
      "</main>" + footer();
    paintPassportSpread();
    bindPassportSwipe();
  }
  function buildPassportSpreads() {
    ensureProg();
    const name = (profile && profile.child_name) || "Юный экспедитор";
    const avatar = AVATARS[(profile && profile.avatar) || "compass"] || "🧭";
    const started = (profile && profile.started_at) ? formatRuDate(profile.started_at) : "сегодня, на этой странице";
    const rec = recommend();
    const doneStories = DATA.stories.filter(function (s) { return storyDone(s.slug); });
    const stampCount = Object.keys(progress.stamps || {}).length;
    const regionCount = Object.keys(progress.regions || {}).length;
    const sampleRegion = seasonRegions()[0];
    const sampleMeta = (sampleRegion && sampleRegion.stamp) || {};
    const titleLeft =
      '<p class="chit-pass-kicker">Читательская экспедиция</p>' +
      "<h2>Паспорт юного читателя</h2>" +
      '<div class="chit-passport-cover" style="margin-top:18px"><div class="chit-avatar" aria-hidden="true">' + avatar + "</div><div>" +
      "<p>Имя: <strong>" + escapeHtml(name) + "</strong></p>" +
      "<p>Экспедитор с: <strong>" + escapeHtml(started) + "</strong></p>" +
      "<p>Уровень: <strong>" + escapeHtml((profile && profile.level) || childLevel()) + "</strong></p>" +
      "<p style=\"margin-top:12px;font-style:italic\">«Я читаю, замечаю, думаю и открываю».</p>" +
      (!profile ? '<p style="margin-top:14px"><button class="chit-btn chit-btn--primary" type="button" data-act="open-passport">Открыть паспорт с взрослым</button></p>' : "") +
      "</div></div>";
    const titleRight =
      '<p class="chit-pass-kicker">Мои открытия</p>' +
      "<h2>Общий прогресс</h2>" +
      '<div class="chit-pass-stat"><span>Регионов открыто</span><strong>' + regionCount + "</strong></div>" +
      '<div class="chit-pass-stat"><span>Историй пройдено</span><strong>' + doneStories.length + "</strong></div>" +
      '<div class="chit-pass-stat"><span>Штампов собрано</span><strong>' + stampCount + "</strong></div>" +
      '<div class="chit-pass-stat"><span>Бейджей</span><strong>' + (progress.badges || []).length + "</strong></div>" +
      (rec ? "<p style=\"margin-top:16px\">Следующая остановка: <strong>" + escapeHtml((regionBy(rec.region) || {}).name || rec.title) + "</strong></p>" +
        '<p style="margin-top:8px"><a class="chit-btn chit-btn--primary" data-go="/stories/' + rec.slug + '" href="' + href("/stories/" + rec.slug) + '">Продолжить путь →</a></p>' : "") +
      (stampCount === 0 && sampleRegion ? stampSealSvg({
        uid: "sample",
        regionName: sampleRegion.name,
        poetic: sampleMeta.poetic_title,
        symbol: sampleMeta.symbol,
        color: sampleMeta.color,
        date: "образец печати",
        sample: true
      }) + "<p class=\"chit-note\">Так выглядит печать экспедиции. Ваша появится после первой миссии.</p>" : "");
    const mapLeft =
      '<p class="chit-pass-kicker">Сезон первый</p><h2>Карта моих открытий</h2>' +
      "<p>Пройденные регионы подсвечены. На закрытых — лёгкий контур. Клик открывает историю края.</p>" +
      "<p class=\"chit-note\">Ты открыл " + regionCount + " из " + seasonRegions().length + " регионов первого сезона.</p>";
    const mapRight = '<div class="chit-mini-map chit-mini-map--pass">' + seasonRegions().map(function (r) {
      const on = !!progress.regions[r.slug];
      return '<a data-go="/regions/' + r.slug + '" href="' + href("/regions/" + r.slug) + '" class="' + (on ? "is-open" : "") + '">' + escapeHtml(r.pin || r.name) + "</a>";
    }).join("") + "</div>";
    const finds = progress.finds || {};
    const spreads = [
      { id: "title", left: titleLeft, right: titleRight },
      { id: "map", left: mapLeft, right: mapRight }
    ];
    seasonRegions().forEach(function (r) {
      spreads.push(regionPassportSpread(r, doneStories.length));
    });
    const badgesLeft = '<p class="chit-pass-kicker">Коллекция</p><h2>Мои бейджи</h2><p>Полученные знаки — с датой и подписью. Будущие ждут в следующей истории.</p>';
    const badgesRight = DATA.badges.map(function (b) {
      const on = progress.badges.indexOf(b.id) !== -1;
      return '<div class="chit-badge' + (on ? " is-on" : "") + '"><div class="mark">' + (on ? "★" : "·") + "</div><div><strong>" + escapeHtml(b.name) + "</strong><br><span style=\"color:var(--chit-muted);font-size:13px\">" +
        (on ? escapeHtml(b.how) : "Этот бейдж ждёт тебя в следующей истории.") + "</span></div></div>";
    }).join("");
    const shelfLeft = '<p class="chit-pass-kicker">Библиотека</p><h2>Моя книжная полка</h2><p>Сказки, которые ты уже открыл. Можно вернуться к истории.</p>';
    const shelfRight = doneStories.length
      ? '<div class="chit-shelf">' + doneStories.map(function (s) {
        const r = regionBy(s.region) || {};
        const recs = progress.stories[s.slug] || {};
        const marks = [storyDone(s.slug) ? "прочитал" : "", (progress.listened || []).indexOf(s.slug) !== -1 ? "слушал" : "", recs.creative ? "выполнил миссию" : ""].filter(Boolean).join(" · ");
        return '<a class="chit-shelf-card" data-go="/stories/' + s.slug + '" href="' + href("/stories/" + s.slug) + '">' +
          '<img src="' + img(s.image) + '" alt="">' +
          "<div><h3>" + escapeHtml(s.title) + "</h3><p>" + escapeHtml(r.name || "") + "</p><p>" + escapeHtml(marks || "открыто") + "</p></div></a>";
      }).join("") + "</div>"
      : "<p>Первая книга появится после миссии читателя.</p>";
    const findsLeft = '<p class="chit-pass-kicker">Дневник</p><h2>Мои открытия</h2><p>Короткие ответы — карточками или своими словами. Это личная страница, без сравнений с другими детьми.</p>';
    const findsRight = '<form class="chit-form" data-form="finds">' +
      '<label>Самый запомнившийся герой<input name="hero" value="' + escapeHtml(finds.hero || "") + '"></label>' +
      '<label>Самый загадочный предмет<input name="object" value="' + escapeHtml(finds.object || "") + '"></label>' +
      '<label>История, которую я хочу рассказать кому-то<input name="tell" value="' + escapeHtml(finds.tell || "") + '"></label>' +
      '<label>Сказка, в которой я бы хотел побывать<input name="visit" value="' + escapeHtml(finds.visit || "") + '"></label>' +
      '<label>Мой любимый штамп<input name="favorite_stamp" value="' + escapeHtml(finds.favorite_stamp || "") + '"></label>' +
      '<button class="chit-btn chit-btn--primary" type="submit">Сохранить открытия</button></form>';
    const nextLeft = '<p class="chit-pass-kicker">В пути</p><h2>Следующая остановка</h2>' +
      (rec ? "<p>Тебя ждёт «" + escapeHtml(rec.title) + "».</p><p class=\"chit-note\">" + escapeHtml(String(rec.minutes || 10)) + " минут · 1 история · новая миссия</p>" : "<p>Новый маршрут появится в следующем сезоне.</p>");
    const nextMeta = rec ? ((regionBy(rec.region) || {}).stamp || {}) : {};
    const nextRight = rec
      ? stampSealSvg({
        uid: "next-" + rec.region,
        regionName: (regionBy(rec.region) || {}).name,
        poetic: nextMeta.poetic_title,
        symbol: nextMeta.symbol,
        color: nextMeta.color,
        ghost: !progress.stamps[rec.region],
        date: progress.stamps[rec.region] ? formatRuDate(progress.stamps[rec.region].earned_at) : "контур следующей печати"
      }) + '<p style="margin-top:12px"><a class="chit-btn chit-btn--primary" data-go="/stories/' + rec.slug + '" href="' + href("/stories/" + rec.slug) + '">Начать следующую экспедицию</a></p>'
      : "";
    spreads.push({ id: "badges", left: badgesLeft, right: badgesRight });
    spreads.push({ id: "shelf", left: shelfLeft, right: shelfRight });
    spreads.push({ id: "finds", left: findsLeft, right: findsRight });
    spreads.push({ id: "next", left: nextLeft, right: nextRight });
    return spreads;
  }
  function regionPassportSpread(r, doneTotal) {
    const st = progress.stamps[r.slug];
    const meta = r.stamp || {};
    const stories = DATA.stories.filter(function (s) { return s.region === r.slug; });
    const doneHere = stories.filter(function (s) { return storyDone(s.slug); });
    const first = stories[0];
    const left =
      '<p class="chit-pass-kicker">Регион</p>' +
      "<h2>" + escapeHtml(r.name) + "</h2>" +
      "<p>«" + escapeHtml(meta.poetic_title || r.pin) + "»</p>" +
      "<p>Ты открыл:</p><ul>" +
      (doneHere.length ? doneHere.map(function (s) { return "<li>✓ Историю «" + escapeHtml(s.title) + "»</li>"; }).join("") : "<li>История региона ждёт первой миссии.</li>") +
      (doneHere.length ? "<li>✓ Нашёл подсказки автора</li><li>✓ Выполнил миссию читателя</li>" : "") +
      "</ul>" +
      (first ? '<p style="margin-top:12px"><a class="chit-btn chit-btn--ghost chit-btn--small" data-go="/stories/' + first.slug + '" href="' + href("/stories/" + first.slug) + '">Открыть историю ещё раз</a></p>' : "") +
      (doneTotal >= 2 && (!st || st.level !== "gold")
        ? "<p class=\"chit-note\">В этом регионе можно собрать золотую печать «Хранитель " + escapeHtml(r.pin || r.name) + "».</p>" +
          '<p><a class="chit-btn chit-btn--ghost chit-btn--small" data-go="/parents" href="' + href("/parents") + '">Открыть полный маршрут</a></p>'
        : "");
    const right = stampSealSvg({
      uid: r.slug,
      regionName: r.name,
      poetic: (st && st.poetic_title) || meta.poetic_title,
      symbol: meta.symbol,
      color: meta.color,
      level: st && st.level,
      date: st ? formatRuDate(st.earned_at) : "",
      ghost: !st
    }) + (st ? "<p>Дата: " + escapeHtml(formatRuDate(st.earned_at)) + "</p>" : "<p class=\"chit-note\">Контур печати. Она станет цветной после миссии.</p>");
    return { id: "region-" + r.slug, left: left, right: right };
  }
  function paintPassportSpread() {
    const stage = document.getElementById("chit-pass-stage");
    const book = document.getElementById("chit-pass-book");
    const num = document.getElementById("chit-pass-num");
    if (!stage || !passSpreadsCache.length) return;
    const spread = passSpreadsCache[passState.i];
    stage.innerHTML = '<div class="chit-pass-spread">' +
      '<div class="chit-pass-leaf chit-pass-leaf--left">' + (spread.left || "") + "</div>" +
      '<div class="chit-pass-leaf chit-pass-leaf--right">' + (spread.right || "") + "</div></div>";
    if (book) book.setAttribute("data-side", passState.side ? "right" : "left");
    if (num) num.textContent = (passState.i + 1) + " / " + passSpreadsCache.length;
    const dots = document.querySelectorAll(".chit-pass-dots span");
    dots.forEach(function (d, i) { d.classList.toggle("is-on", i === passState.i); });
  }
  function passTurn(dir) {
    const n = passSpreadsCache.length;
    if (!n) return;
    const mobile = window.innerWidth <= 880;
    if (mobile) {
      if (dir > 0) {
        if (passState.side === 0) passState.side = 1;
        else { passState.i = Math.min(n - 1, passState.i + 1); passState.side = 0; }
      } else {
        if (passState.side === 1) passState.side = 0;
        else { passState.i = Math.max(0, passState.i - 1); passState.side = 1; }
      }
    } else {
      passState.i = Math.max(0, Math.min(n - 1, passState.i + dir));
      passState.side = 0;
    }
    paintPassportSpread();
  }
  function bindPassportSwipe() {
    const book = document.getElementById("chit-pass-book");
    if (!book) return;
    let x0 = null;
    book.addEventListener("touchstart", function (e) {
      x0 = e.changedTouches[0].clientX;
    }, { passive: true });
    book.addEventListener("touchend", function (e) {
      if (x0 == null) return;
      const dx = e.changedTouches[0].clientX - x0;
      x0 = null;
      if (Math.abs(dx) < 40) return;
      passTurn(dx < 0 ? 1 : -1);
    });
  }

  function renderCabinet() {
    document.title = "Моя экспедиция — Читательство";
    ensureProg();
    const name = (profile && profile.child_name) || "друг экспедиции";
    const rec = recommend();
    const done = DATA.stories.filter(function (s) { return storyDone(s.slug); }).length;
    const total = DATA.stories.length;
    const pct = Math.round((done / Math.max(total, 1)) * 100);
    root.innerHTML = header("/cabinet") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:32px 20px 64px">' +
      '<div class="chit-cabin-hero"><div>' +
      '<p class="chit-kicker">Моя экспедиция</p>' +
      '<h1 class="chit-h1">Здравствуйте, ' + escapeHtml(name) + "</h1>" +
      "<p class=\"chit-lead\">Читайте и слушайте истории, проходите миссии, ставьте штампы в паспорт и открывайте новые маршруты.</p>" +
      '<div class="chit-progress-bar" aria-label="Прогресс историй"><span style="width:' + pct + '%"></span></div>' +
      "<p>Пройдено историй: <strong>" + done + "</strong> из " + total + "</p>" +
      (rec ? '<div class="chit-card" style="margin-top:16px"><h3>Сейчас в пути</h3><p>' + escapeHtml(rec.title) + "</p>" +
        '<p style="margin-top:8px"><a class="chit-btn chit-btn--primary" data-go="/stories/' + rec.slug + '" href="' + href("/stories/" + rec.slug) + '">Открыть историю</a></p></div>' : "") +
      "</div><div class=\"chit-card\"><h3>Мини-карта открытий</h3><div class=\"chit-mini-map\" style=\"margin-top:10px\">" +
      DATA.regions.map(function (r) {
        return '<a data-go="/map" href="' + href("/map") + '" class="' + (progress.regions[r.slug] ? "is-open" : "") + '">' + escapeHtml(r.pin) + "</a>";
      }).join("") + "</div>" +
      '<p style="margin-top:14px"><a class="chit-btn chit-btn--ghost" data-go="/map" href="' + href("/map") + '">К карте</a></p></div></div></div></main>' + footer();
  }

  function renderCollection() {
    document.title = "Мои истории — Читательская экспедиция";
    const done = DATA.stories.filter(function (s) { return storyDone(s.slug); });
    root.innerHTML = header("/collection") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:32px 20px 64px">' +
      '<p class="chit-kicker">Книжная полка</p><h1 class="chit-h1">Мои истории</h1>' +
      "<p class=\"chit-lead\">Пройденные сказки и открытые маршруты. Все истории сезона можно читать сразу.</p>" +
      (done.length ? "<h2>Уже на полке</h2><div class=\"chit-shelf\" style=\"margin-bottom:28px\">" + done.map(function (s) {
        const r = regionBy(s.region) || {};
        return '<a class="chit-shelf-card" data-go="/stories/' + s.slug + '" href="' + href("/stories/" + s.slug) + '">' +
          '<img src="' + img(s.image) + '" alt=""><div><h3>' + escapeHtml(s.title) + "</h3><p>" + escapeHtml(r.name || "") + "</p></div></a>";
      }).join("") + "</div>" : "") +
      "<h2>Все истории сезона</h2>" +
      '<div class="chit-grid-3">' + DATA.stories.map(function (s) {
        return '<a class="chit-card chit-card--link" data-go="/stories/' + s.slug + '" href="' + href("/stories/" + s.slug) + '">' +
          (storyDone(s.slug) ? chip("пройдено", "sage") : chip("открыто")) +
          "<h3>" + escapeHtml(s.title) + "</h3><p>" + escapeHtml((regionBy(s.region) || {}).name || "") + "</p></a>";
      }).join("") + "</div></div></main>" + footer();
  }

  function renderParents() {
    document.title = "Родителям — Читательская экспедиция";
    const name = (profile && profile.child_name) || "ребёнка";
    const login = profile ? "" :
      '<form class="chit-form" data-form="login" style="margin-top:16px">' +
      "<h3>Вход родителя</h3>" +
      '<div class="row"><label>Email<input type="email" name="email" required></label><label>Пароль <span class="chit-note">(или оставьте пустым — вход по коду)</span><input type="password" name="password" autocomplete="current-password"></label></div>' +
      '<button class="chit-btn chit-btn--ghost" type="submit">Войти</button></form>';
    root.innerHTML = header("/parents") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:32px 20px 64px">' +
      '<p class="chit-kicker">Кабинет родителя</p>' +
      '<h1 class="chit-h1">Прогресс, рекомендации и доступ</h1>' +
      "<p class=\"chit-lead\">Оплата, тарифы и платежи — у родителя. Ребёнок ведёт карту, истории и паспорт.</p>" +
      '<div class="chit-card" style="margin:16px 0"><h3>Сейчас у ' + escapeHtml(name) + "</h3>" +
      "<p>Историй: " + DATA.stories.filter(function (s) { return storyDone(s.slug); }).length + " · штампов: " + Object.keys(progress.stamps || {}).length + " · бейджей: " + (progress.badges || []).length + "</p>" +
      (recommend() ? "<p>Следующая остановка: «" + escapeHtml(recommend().title) + "»</p>" : "") +
      (!profile ? '<p style="margin-top:12px"><button class="chit-btn chit-btn--primary" type="button" data-act="open-passport">Открыть паспорт с взрослым</button></p>' : "") +
      login +
      "</div><h2>Тарифы экспедиции</h2><div class=\"chit-grid-3\">" + tariffCardsHtml("parent") + "</div>" +
      "<p class=\"chit-note\">Оплата, прогресс ребёнка и тарифы экспедиции — в этом кабинете.</p></div></main>" + footer();
    const btn = root.querySelector("[data-act='open-passport']");
    if (btn) btn.addEventListener("click", openPassportModal);
  }

  function renderStoryTeaser(s) {
    document.title = s.title + " — тизер";
    const region = regionBy(s.region) || {};
    root.innerHTML = header("/collection") + '<main class="chit-exp-main"><div class="chit-wrap" style="padding:32px 20px 64px;max-width:720px">' +
      '<div class="chit-teaser is-locked"><span class="chit-lock">История откроется по тарифу экспедиции</span>' +
      '<p class="chit-kicker">' + escapeHtml(region.name || "") + "</p>" +
      '<h1 class="chit-h1">' + escapeHtml(s.title) + "</h1>" +
      '<img src="' + img(s.image) + '" alt="" style="border-radius:16px;margin:12px 0;max-height:240px;width:100%;object-fit:cover">' +
      "<p>Чему научится ребёнок: " + escapeHtml(s.learn || "внимательно прочитать историю края.") + "</p>" +
      (s.stampUnlock ? "<p>Откроет штамп: «" + escapeHtml(s.stampUnlock) + "»</p>" : "") +
      (s.badgeUnlock ? "<p>Откроет бейдж: «" + escapeHtml(s.badgeUnlock) + "»</p>" : "") +
      '<p style="margin-top:16px"><a class="chit-btn chit-btn--primary" data-go="/parents" href="' + href("/parents") + '">Тарифы для родителя</a> ' +
      '<a class="chit-btn chit-btn--ghost" data-go="/map" href="' + href("/map") + '">К карте</a></p></div></div></main>' + footer();
  }

  function passportFormHtml() {
    const avatars = (DATA.avatars || [{ id: "compass", label: "Компас" }]).map(function (a) {
      return '<label class="chit-check"><input type="radio" name="avatar" value="' + a.id + '"' + (a.id === "compass" ? " checked" : "") + "> " + escapeHtml(a.label) + "</label>";
    }).join("");
    return '<form class="chit-form" data-form="passport">' +
      "<h2 id=\"chit-pass-title\">Открыть паспорт с взрослым</h2>" +
      "<p>Имя ребёнка, возраст и контакт родителя. Штампы и страницы паспорта сохранятся.</p>" +
      '<div class="row"><label>Имя или никнейм ребёнка<input name="child_name" required></label><label>Возраст ребёнка<input name="child_age" type="number" min="4" max="16" required></label></div>' +
      '<label>Имя родителя<input name="parent_name" required></label>' +
      '<label>Email<input type="email" name="email" required></label>' +
      '<label>Пароль <span class="chit-note">(или оставьте пустым и входите по коду на почту)</span><input type="password" name="password" autocomplete="new-password"></label>' +
      "<p>Аватар</p>" + avatars +
      '<label class="chit-check"><input type="checkbox" name="pd" required> Согласие на обработку персональных данных</label>' +
      '<label class="chit-check"><input type="checkbox" name="expedition" required> Согласие на создание паспорта экспедиции</label>' +
      '<button class="chit-btn chit-btn--primary" type="submit">Сохранить паспорт</button>' +
      '<button class="chit-btn chit-btn--ghost" type="button" data-act="close-modal">Позже</button></form>';
  }

  function openPassportModal() {
    closePassportModal();
    const back = document.createElement("div");
    back.className = "chit-modal";
    back.id = "chit-pass-modal";
    back.innerHTML = '<div class="chit-modal__card" role="dialog" aria-labelledby="chit-pass-title">' + passportFormHtml() + "</div>";
    document.body.appendChild(back);
    back.addEventListener("click", function (e) {
      if (e.target === back) closePassportModal();
    });
    const closeBtn = back.querySelector("[data-act='close-modal']");
    if (closeBtn) closeBtn.addEventListener("click", closePassportModal);
    const form = back.querySelector("form[data-form='passport']");
    if (form) form.addEventListener("submit", submitPassport);
  }
  function closePassportModal() {
    const el = document.getElementById("chit-pass-modal");
    if (el) el.remove();
  }
  function submitPassport(e) {
    e.preventDefault();
    const form = e.target;
    const payload = {};
    new FormData(form).forEach(function (v, k) { payload[k] = v; });
    payload.consent = !!(payload.pd && payload.expedition);
    payload.child_age = payload.child_age ? Number(payload.child_age) : null;
    payload.progress = progress;
    const btn = form.querySelector("[type='submit']");
    if (btn) btn.disabled = true;
    fetch(apiUrl("/expedition/api/cabinet/register"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }).then(function (r) { return r.json().then(function (body) { return { ok: r.ok, body: body }; });     }).then(function (res) {
      if (!res.ok) {
        if (btn) btn.disabled = false;
        toast("Проверьте поля и согласия, затем попробуйте снова.");
        return;
      }
      saveSession({ token: res.body.token, child_name: res.body.profile.child_name });
      profile = res.body.profile;
      accessMap = (res.body.profile && res.body.profile.access) || accessMap;
      grantBadge("first-step");
      closePassportModal();
      toast("Паспорт экспедитора открыт");
      go("/passport");
    }).catch(function () {
      applyLocalPassport(payload);
      closePassportModal();
      toast("Паспорт экспедитора открыт");
      go("/passport");
    });
  }
  function applyLocalPassport(payload) {
    profile = {
      child_name: payload.child_name,
      child_age: payload.child_age,
      parent_name: payload.parent_name,
      email: payload.email,
      avatar: payload.avatar || "compass",
      started_at: new Date().toISOString(),
      level: "Старт"
    };
    saveSession({ token: "local-" + Date.now(), child_name: profile.child_name, local: true });
    grantBadge("first-step");
  }
  function submitLogin(e) {
    const form = e.target;
    const payload = {};
    new FormData(form).forEach(function (v, k) { payload[k] = v; });
    const btn = form.querySelector("[type='submit']");
    if (btn) btn.disabled = true;
    fetch(apiUrl("/expedition/api/cabinet/login"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: payload.email, password: payload.password || "" })
    }).then(function (r) { return r.json().then(function (body) { return { ok: r.ok, body: body }; }); }).then(function (res) {
      if (!res.ok) throw new Error((res.body && res.body.detail) || "error");
      saveSession({ token: res.body.token, child_name: res.body.profile.child_name });
      profile = res.body.profile;
      accessMap = (res.body.profile && res.body.profile.access) || accessMap;
      if (res.body.progress) progress = Object.assign(progress, res.body.progress);
      saveProgressLocal();
      toast("Добро пожаловать в экспедицию");
      go("/cabinet");
    }).catch(function () {
      if (btn) btn.disabled = false;
      toast("Не удалось войти. Проверьте почту или откройте новый паспорт.");
    });
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
      (tariffCardsHtml("library") ? "<h2 class=\"chit-h2\">Библиотечный доступ</h2><div class=\"chit-grid-3\">" + tariffCardsHtml("library") + "</div>" : "") +
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
    if (act && act.getAttribute("data-act") === "open-passport") {
      e.preventDefault();
      openPassportModal();
    }
    if (act && act.getAttribute("data-act") === "pass-next") { e.preventDefault(); passTurn(1); }
    if (act && act.getAttribute("data-act") === "pass-prev") { e.preventDefault(); passTurn(-1); }
    if (act && act.getAttribute("data-act") === "close-stamp") { e.preventDefault(); closeStampModal(); }
    if (act && act.getAttribute("data-act") === "place-stamp") {
      e.preventDefault();
      placeStoryStamp(storyBy(act.getAttribute("data-story")));
    }
  }

  function bindSubmit(e) {
    const form = e.target.closest("form[data-form]");
    if (!form) return;
    e.preventDefault();
    const kind = form.getAttribute("data-form");
    if (kind === "passport") return submitPassport(e);
    if (kind === "login") return submitLogin(e);
    if (kind === "finds") {
      ensureProg();
      progress.finds = progress.finds || {};
      new FormData(form).forEach(function (v, k) { progress.finds[k] = v; });
      saveProgress();
      toast("Открытия сохранены в паспорте");
      return;
    }
    sendForm(kind, form);
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
    if (p === "/cabinet" || p === "/me") return { name: "cabinet" };
    if (p === "/collection") return { name: "collection" };
    if (p === "/parents") return { name: "parents" };
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
    else if (r.name === "cabinet") renderCabinet();
    else if (r.name === "collection") renderCollection();
    else if (r.name === "parents") renderParents();
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
    return refreshCabinet();
  }).then(function () {
    render();
  }).catch(function () {
    if (DATA) render();
    else root.innerHTML = "<p style='padding:40px'>Не удалось загрузить данные экспедиции.</p>";
  });
})();
