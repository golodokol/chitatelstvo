(function () {
  var cfg = window.CHIT_QUEST || {};
  var stations = Array.isArray(cfg.stations) ? cfg.stations : [];
  var idx = 0;
  var sparks = 0;
  var sparkLabels = (cfg.quest && cfg.quest.spark_labels) || {
    sound: "Звук",
    letter: "Буква",
    syllable: "Слог"
  };
  var sparkKinds = {};
  Object.keys(sparkLabels).forEach(function (k) { sparkKinds[k] = false; });
  (function paintSparkHud() {
    var hud = document.getElementById("quest-sparks-hud");
    if (!hud) return;
    hud.innerHTML = "";
    Object.keys(sparkLabels).forEach(function (k) {
      var chip = document.createElement("span");
      chip.className = "quest-spark-chip";
      chip.setAttribute("data-spark", k);
      chip.textContent = sparkLabels[k];
      hud.appendChild(chip);
    });
  })();
  var stationCleared = false;
  var passedStations = [];
  var completeSent = false;
  var goalCount = (cfg.quest && cfg.quest.goal_count) || 3;
  var selected = [];
  var audio = new Audio();
  var sfx = new Audio();
  var contentRoot = null;
  var typeTimer = null;
  var gameTimer = null;
  var gameRaf = null;
  var coachStation = null;

  var elTitle = document.getElementById("quest-station-title");
  var elLine = document.getElementById("quest-slovik-line");
  var elBody = document.getElementById("quest-body");
  var elMsg = document.getElementById("quest-msg");
  var elLabel = document.getElementById("quest-progress-label");
  var elSparks = document.getElementById("quest-sparks");
  var elPath = document.getElementById("quest-path");
  var btnNext = document.getElementById("quest-btn-next");
  var btnAudio = document.getElementById("quest-btn-audio");
  var miniSkip = null;
  var retryMode = false;

  function authBody(extra) {
    var body = {
      child_id: cfg.childId,
      exp: cfg.exp,
      sig: cfg.sig || "",
    };
    if (cfg.testKey) body.test_key = cfg.testKey;
    if (extra) Object.keys(extra).forEach(function (k) { body[k] = extra[k]; });
    return body;
  }

  function showMsg(text, ok) {
    if (!elMsg) return;
    elMsg.style.display = "block";
    elMsg.className = "chit-msg " + (ok ? "ok" : "info");
    elMsg.textContent = text;
  }

  // Skip .ogg: many early files were saved as M4A under a .ogg name and break playback fallback.
  var AUDIO_EXTS = [".mp3", ".MP3", ".m4a", ".wav"];
  var AUDIO_VER = "20260823c";

  function audioCandidates(id) {
    if (!id) return [];
    if (String(id).indexOf("/") === 0 || String(id).indexOf("http") === 0) return [id];
    var base = (cfg.assetsBase || "").replace(/\/$/, "");
    var stem = base + "/static/early/audio/" + id;
    return AUDIO_EXTS.map(function (ext) { return stem + ext + "?v=" + AUDIO_VER; });
  }

  function audioUrl(id) {
    var urls = audioCandidates(id);
    return urls.length ? urls[0] : "";
  }

  function resolveLessonLink(item) {
    if (!item) return "";
    var links = cfg.lessonLinks || {};
    var url = String(item.url || "").trim();
    var slug = String(item.slug || "").trim();
    if (!slug && url.indexOf("/lesson/") >= 0) {
      slug = url.split("/lesson/")[1].split("?")[0].split("#")[0];
    }
    if (slug && links[slug]) return links[slug];
    if (url && url.indexOf("http") === 0) return url;
    if (url && url.indexOf("/lesson/") === 0 && slug && links[slug]) return links[slug];
    return url;
  }

  function playOnEl(el, urls, onFail) {
    var idx = 0;
    function tryNext() {
      if (idx >= urls.length) {
        if (onFail) onFail();
        return;
      }
      var url = urls[idx++];
      var settled = false;
      function cleanup() {
        el.onerror = null;
        el.oncanplay = null;
      }
      function fail() {
        if (settled) return;
        settled = true;
        cleanup();
        tryNext();
      }
      function ok() {
        if (settled) return;
        settled = true;
        cleanup();
      }
      el.onerror = fail;
      el.oncanplay = function () {
        el.oncanplay = null;
        var p = el.play();
        if (p && p.then) {
          p.then(ok).catch(function (err) {
            // Autoplay blocked: don't fall through to other formats; wait for «Послушать».
            if (err && err.name === "NotAllowedError") {
              ok();
              return;
            }
            if (el.paused && !settled) fail();
            else ok();
          });
        } else {
          ok();
        }
      };
      el.src = url;
      el.load();
    }
    tryNext();
  }

  function hushVoice() {
    try {
      if (window.speechSynthesis) window.speechSynthesis.cancel();
    } catch (e) {}
  }

  var instructionPlaying = false;
  var pendingVoiceCb = null;
  var playGen = 0;
  var audioToken = 0;

  function finishVoiceWait() {
    instructionPlaying = false;
    var cb = pendingVoiceCb;
    pendingVoiceCb = null;
    if (cb) cb();
  }

  function afterStationVoice(fn) {
    var gen = playGen;
    pendingVoiceCb = function () {
      if (gen !== playGen) return;
      fn();
    };
    if (!instructionPlaying) {
      pendingVoiceCb = null;
      if (gen === playGen) fn();
    }
  }

  function playId(id, onEnded) {
    var urls = audioCandidates(id);
    var finished = false;
    var token = ++audioToken;
    function finish() {
      if (finished) return;
      finished = true;
      try { audio.onended = null; } catch (e) {}
      if (token !== audioToken) return;
      if (typeof onEnded === "function") onEnded();
    }
    if (!urls.length) {
      finish();
      return;
    }
    try {
      hushVoice();
      sfx.pause();
      audio.pause();
      audio.onended = finish;
      playOnEl(audio, urls, function () {
        finish();
      });
      if (onEnded) {
        setTimeout(function () {
          if (token === audioToken) finish();
        }, 15000);
        audio.addEventListener("loadedmetadata", function meta() {
          audio.removeEventListener("loadedmetadata", meta);
          var d = audio.duration;
          if (isFinite(d) && d > 0) {
            setTimeout(function () {
              if (token === audioToken) finish();
            }, Math.ceil(d * 1000) + 350);
          }
        });
      }
    } catch (e) {
      finish();
    }
  }

  var VO_LINE = {
    ok: "Правильно!",
    yes: "Есть!",
    good: "Здорово!",
    found: "Нашёл!",
    spark: "Искорка с нами!",
    try: "Попробуй ещё.",
    more: "Давай ещё.",
    wrong: "Не то. Ищи дальше."
  };

  function voPrefix() {
    return String(cfg.slug || "").indexOf("stories") >= 0 ? "ph-vo-" : "vo-";
  }

  function voLine(kind) {
    if (kind === "wrong" && String(cfg.slug || "").indexOf("stories") >= 0) {
      return "Не то. Читай ещё раз.";
    }
    return VO_LINE[kind] || "";
  }

  var VO_SILENT = { yes: true, more: true };

  function coachReact(kind, ok) {
    var line = voLine(kind);
    if (kind && !VO_SILENT[kind]) playId(voPrefix() + kind);
    if (typeof ok === "boolean") {
      showMsg(line || voLine(ok ? "ok" : "try"), ok);
    }
  }

  function playSfx(id) {
    if (instructionPlaying) return;
    hushVoice();
    var urls = audioCandidates(id);
    if (!urls.length) return;
    try {
      // Never pause `audio` here — letter beeps were cutting off Slovik's line.
      sfx.pause();
      playOnEl(sfx, urls);
    } catch (e) {}
  }

  function assetUrl(path) {
    if (!path) return "";
    if (String(path).indexOf("http") === 0) return path;
    var base = (cfg.assetsBase || "").replace(/\/$/, "");
    var url = base + path;
    if (/\.(png|jpe?g|webp)$/i.test(path) && url.indexOf("?") < 0) {
      url += "?v=20260823c";
    }
    return url;
  }

  function updatePath() {
    if (!elPath) return;
    elPath.innerHTML = "";
    stations.forEach(function (st, i) {
      var dot = document.createElement("span");
      var counted = !!(st && st.id && passedStations.indexOf(st.id) >= 0);
      dot.className = "quest-path__dot";
      if (i === idx) {
        dot.classList.add("is-current");
      } else if (counted || (i < idx && isGuideStation(st))) {
        dot.classList.add("is-done");
      } else if (i < idx) {
        dot.classList.add("is-skipped");
      }
      elPath.appendChild(dot);
    });
  }

  function updateSparkHud() {
    document.querySelectorAll(".quest-spark-chip").forEach(function (chip) {
      var kind = chip.getAttribute("data-spark");
      chip.classList.toggle("is-on", !!sparkKinds[kind]);
    });
  }

  function updateProgress() {
    var total = Math.max(stations.length, 1);
    if (elLabel) {
      var st = stations[idx];
      var chapter = st && st.chapter ? st.chapter + " · " : "";
      elLabel.textContent = chapter + (st && st.title ? st.title : ("Станция " + (idx + 1)));
    }
    if (elSparks) {
      var label = (cfg.quest && cfg.quest.goal_label) || "искорки";
      elSparks.textContent = "Собрано: " + sparks + " / " + goalCount + " (" + label + ")";
    }
    updateSparkHud();
    updatePath();
  }

  function enableNext(show) {
    stationCleared = !!show;
    if (show) {
      var cleared = stations[idx];
      if (cleared) {
        if (cleared.success_msg) showMsg(cleared.success_msg, true);
        else if (cleared.tech_msg) showMsg(cleared.tech_msg, true);
      }
    }
    if (!btnNext) return;
    var station = stations[idx];
    var kind = station && station.kind;
    btnNext.hidden = !station || kind === "intro_video";
  }

  function onNextClick() {
    if (stationCleared) {
      goNext();
      return;
    }
    if (typeof miniSkip === "function") {
      miniSkip();
      return;
    }
    goNext();
  }

  function allSparksEarned() {
    return sparks >= goalCount;
  }

  function isGuideStation(station) {
    var kind = station && station.kind;
    return kind === "intro_video" || kind === "reward" || kind === "enter";
  }

  function incompleteIndices() {
    var list = [];
    stations.forEach(function (st, i) {
      if (!st || isGuideStation(st)) return;
      if (st.id && passedStations.indexOf(st.id) >= 0) return;
      list.push(i);
    });
    return list;
  }

  function goToStation(next) {
    idx = next;
    selected = [];
    stationCleared = false;
    miniSkip = null;
    if (elMsg) elMsg.style.display = "none";
    render();
  }

  function retryIncomplete() {
    var miss = incompleteIndices();
    if (!miss.length) return;
    retryMode = true;
    completeSent = false;
    goToStation(miss[0]);
  }

  function bindFinishButton() {
    if (!btnNext) return;
    if (incompleteIndices().length) {
      btnNext.hidden = true;
      return;
    }
    btnNext.hidden = false;
    btnNext.textContent = "Завершить";
    btnNext.onclick = function () {
      window.location.href = cfg.progressUrl || "/";
    };
  }

  function groupKind(station) {
    if (!station) return "";
    return station.spark_group || station.spark_kind || "";
  }

  function groupComplete(kind) {
    if (!kind) return false;
    var members = stations.filter(function (st) { return groupKind(st) === kind; });
    if (!members.length) return false;
    return members.every(function (st) {
      return st.id && passedStations.indexOf(st.id) >= 0;
    });
  }

  function showSparkFly(kind, done) {
    var board = document.querySelector(".quest-board") || document.body;
    var field = (elBody && elBody.querySelector(".quest-playfield")) || elBody || board;
    var chip = document.querySelector('.quest-spark-chip[data-spark="' + kind + '"]');
    var sparkPath = "/static/early/letters/spark.png";
    var fly = document.createElement("img");
    fly.className = "quest-spark-rise";
    fly.src = assetUrl(sparkPath);
    fly.alt = "Искорка";
    board.appendChild(fly);
    var boardRect = board.getBoundingClientRect();
    var from = field.getBoundingClientRect();
    fly.style.left = (from.left + from.width / 2 - boardRect.left) + "px";
    fly.style.top = (from.top + from.height * 0.48 - boardRect.top) + "px";

    var line = voLine("spark");
    if (line) showMsg(line, true);

    var animDone = false;
    var voiceDone = false;
    function maybeFinish() {
      if (animDone && voiceDone) {
        updateProgress();
        if (typeof done === "function") done();
      }
    }

    playId(voPrefix() + "spark", function () {
      voiceDone = true;
      maybeFinish();
    });

    requestAnimationFrame(function () {
      fly.classList.add("is-in");
      setTimeout(function () {
        var to = chip ? chip.getBoundingClientRect() : from;
        var boardNow = board.getBoundingClientRect();
        fly.style.left = (to.left + to.width / 2 - boardNow.left) + "px";
        fly.style.top = (to.top + to.height / 2 - boardNow.top) + "px";
        fly.classList.add("is-up");
        if (chip) {
          chip.classList.add("is-on", "is-pop");
          setTimeout(function () { chip.classList.remove("is-pop"); }, 620);
        }
      }, 420);
    });
    setTimeout(function () {
      if (fly.parentNode) fly.parentNode.removeChild(fly);
      animDone = true;
      maybeFinish();
    }, 2600);
  }

  function awardSpark(station) {
    if (!stationCleared) return "";
    var kind = groupKind(station);
    if (kind && sparkKinds.hasOwnProperty(kind)) {
      if (!sparkKinds[kind] && groupComplete(kind)) {
        sparkKinds[kind] = true;
        sparks += 1;
        return kind;
      }
      return "";
    }
    if (station && station.spark) {
      sparks += 1;
      return "spark";
    }
    return "";
  }

  function completeLesson() {
    if (completeSent) return;
    completeSent = true;
    fetch("/api/lesson/" + encodeURIComponent(cfg.slug) + "/quest-complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(authBody({
        sparks: sparks,
        passed_stations: passedStations
      })),
    })
      .then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function () {
        bindFinishButton();
      })
      .catch(function () {
        bindFinishButton();
      });
  }

  function goNext() {
    var cur = stations[idx];
    if (stationCleared && cur && cur.id && passedStations.indexOf(cur.id) < 0) {
      passedStations.push(cur.id);
    }
    var got = awardSpark(cur);
    var next = idx + 1;
    if (retryMode) {
      var miss = incompleteIndices();
      var later = miss.filter(function (i) { return i > idx; });
      if (later.length) {
        next = later[0];
      } else {
        retryMode = false;
        next = stations.findIndex(function (st) { return st && st.kind === "reward"; });
        if (next < 0) next = stations.length - 1;
      }
    }
    function proceed() {
      if (next < 0 || next >= stations.length) {
        completeLesson();
        return;
      }
      goToStation(next);
    }
    if (got && got !== "spark") {
      showSparkFly(got, proceed);
      return;
    }
    if (got) updateProgress();
    proceed();
  }

  function slovikUrl(pose) {
    return assetUrl("/static/early/slovik/" + (pose || "talk") + ".png");
  }

  function shuffle(list) {
    var a = (list || []).slice();
    var i, j, t;
    for (i = a.length - 1; i > 0; i--) {
      j = Math.floor(Math.random() * (i + 1));
      t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
    return a;
  }

  function clearQuestTimers() {
    playGen += 1;
    pendingVoiceCb = null;
    instructionPlaying = false;
    if (typeTimer) {
      clearInterval(typeTimer);
      typeTimer = null;
    }
    if (gameTimer) {
      clearTimeout(gameTimer);
      gameTimer = null;
    }
    if (gameRaf) {
      cancelAnimationFrame(gameRaf);
      gameRaf = null;
    }
    hushVoice();
    try {
      sfx.pause();
      sfx.removeAttribute("src");
      sfx.load();
    } catch (e) {}
  }

  function coachSay(text, speed) {
    var bubble = document.getElementById("quest-buddy-bubble");
    var line = text || "";
    if (!bubble) return;
    if (typeTimer) {
      clearInterval(typeTimer);
      typeTimer = null;
    }
    bubble.classList.add("is-speaking");
    bubble.textContent = "";
    var i = 0;
    var step = speed || 32;
    function caret() {
      var mark = document.createElement("span");
      mark.className = "quest-coach__caret";
      mark.setAttribute("aria-hidden", "true");
      return mark;
    }
    function tick() {
      i += 1;
      bubble.textContent = line.slice(0, i);
      if (i < line.length) {
        bubble.appendChild(caret());
      } else {
        clearInterval(typeTimer);
        typeTimer = null;
        bubble.classList.remove("is-speaking");
      }
    }
    if (!line) {
      bubble.classList.remove("is-speaking");
      return;
    }
    typeTimer = setInterval(tick, step);
    tick();
  }

  function speakTask(station) {
    coachStation = station || coachStation;
    var line = (station && station.slovik_line) || "";
    coachSay(line);
    if (station && station.tech_msg) showMsg(station.tech_msg, true);
    if (station && station.audio) {
      instructionPlaying = true;
      playId(station.audio, finishVoiceWait);
    } else {
      finishVoiceWait();
    }
  }

  function rewardSpeakView(station) {
    if (allSparksEarned()) return station;
    return {
      slovik_line: station.fail_slovik_line || "Искорки ещё не все. Давай пройдём ещё раз.",
      slovik_pose: station.fail_pose || "worry",
      scene_image: station.scene_image,
      audio: station.fail_audio || ""
    };
  }

  function appendCoach(station) {
    var coach = document.createElement("div");
    coach.className = "quest-coach";
    var img = document.createElement("img");
    img.id = "quest-buddy-img";
    img.className = "quest-coach__img";
    img.src = slovikUrl(station.slovik_pose || "talk");
    img.alt = "Словик";
    var cloud = document.createElement("div");
    cloud.className = "quest-coach__cloud";
    var bubble = document.createElement("button");
    bubble.type = "button";
    bubble.id = "quest-buddy-bubble";
    bubble.className = "quest-coach__bubble";
    bubble.setAttribute("aria-label", "Речь Словика");
    bubble.textContent = "";
    function replay() { speakTask(station); }
    bubble.addEventListener("click", replay);
    cloud.appendChild(bubble);
    coach.appendChild(img);
    coach.appendChild(cloud);
    elBody.appendChild(coach);
  }

  function questFooter() {
    return document.querySelector(".quest-footer");
  }

  function parkFooter() {
    var footer = questFooter();
    var stage = document.getElementById("quest-stage");
    if (footer && stage && footer.parentElement !== stage) {
      stage.appendChild(footer);
    }
    if (elMsg && stage && elMsg.parentElement !== stage) {
      stage.insertBefore(elMsg, footer || null);
    }
  }

  function mountFooterOnPlayfield(field) {
    var footer = questFooter();
    if (!footer || !field) return;
    var dock = field.querySelector(".quest-playfield__dock") || field;
    dock.appendChild(footer);
    if (elMsg && field.parentNode) {
      field.parentNode.insertBefore(elMsg, field.nextSibling);
    }
  }

  function openPlayfield(station) {
    clearQuestTimers();
    parkFooter();
    elBody.innerHTML = "";
    appendCoach(station);
    var field = document.createElement("div");
    field.className = "quest-playfield";
    var scene = station && station.scene_image;
    var hasVideo = !!videoSrc(station);
    var sceneUrl = (scene && !hasVideo) ? assetUrl(scene) : "";

    var canvas = document.createElement("div");
    canvas.className = "quest-playfield__canvas";
    if (sceneUrl) {
      field.classList.add("quest-playfield--has-scene");
      canvas.style.backgroundImage = "url('" + sceneUrl + "')";
    } else if (hasVideo) {
      field.classList.add("quest-playfield--video");
    }

    var surface = document.createElement("div");
    surface.className = "quest-playfield__surface";
    canvas.appendChild(surface);
    field.appendChild(canvas);

    var dock = document.createElement("div");
    dock.className = "quest-playfield__dock";
    if (sceneUrl) {
      var blur = document.createElement("div");
      blur.className = "quest-playfield__dock-blur";
      blur.setAttribute("aria-hidden", "true");
      blur.style.backgroundImage = "url('" + sceneUrl + "')";
      dock.appendChild(blur);
    }
    field.appendChild(dock);

    elBody.appendChild(field);
    mountFooterOnPlayfield(field);
    contentRoot = surface;
    speakTask(station);
    return surface;
  }

  function root() {
    return contentRoot || elBody;
  }

  function layoutAround(grid) {
    var field = elBody.querySelector(".quest-playfield");
    if (field) field.classList.add("quest-playfield--around");
    if (!grid) return grid;
    grid.classList.add("quest-around-grid");
    var compact = window.innerWidth < 560;
    var spots = compact
      ? [
          { x: 18, y: 20 },
          { x: 82, y: 20 },
          { x: 18, y: 80 },
          { x: 82, y: 80 }
        ]
      : [
          { x: 14, y: 22 },
          { x: 86, y: 22 },
          { x: 14, y: 80 },
          { x: 86, y: 80 }
        ];
    var kids = grid.children;
    for (var i = 0; i < kids.length; i++) {
      var spot = spots[i] || spots[i % spots.length];
      kids[i].style.left = spot.x + "%";
      kids[i].style.top = spot.y + "%";
    }
    return grid;
  }

  function appendPromptPic(obj) {
    var src = obj && (obj.prompt_image || obj.image);
    if (!src) return;
    var pic = document.createElement("img");
    pic.className = "quest-prompt-pic";
    pic.src = assetUrl(src);
    pic.alt = (obj && (obj.prompt_alt || obj.word || obj.phrase)) || "";
    pic.onerror = function () { pic.style.display = "none"; };
    root().appendChild(pic);
  }

  function renderOptions(options, onPick, multi, flags) {
    flags = flags || {};
    var grid = document.createElement("div");
    var hasImg = (options || []).some(function (opt) { return opt && opt.image; });
    grid.className = "quest-grid" + (hasImg ? " quest-grid--rich" : " quest-grid--choice");
    (options || []).forEach(function (opt) {
      var id = typeof opt === "string" ? opt : opt.id;
      var label = typeof opt === "string" ? opt : (opt.label || opt.id);
      var hideLabel = flags.picture_only || (opt && opt.hide_label);
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "quest-opt";
      if (opt && opt.image) btn.classList.add("quest-opt--pic");
      else btn.classList.add("quest-opt--choice");
      btn.dataset.id = id;
      btn.setAttribute("aria-label", label);
      if (opt && opt.image) {
        var img = document.createElement("img");
        img.src = assetUrl(opt.image);
        img.alt = hideLabel ? label : "";
        img.onerror = function () {
          img.style.display = "none";
          if (hideLabel && !btn.querySelector("span")) {
            var fallback = document.createElement("span");
            fallback.textContent = label;
            btn.appendChild(fallback);
          }
        };
        btn.appendChild(img);
      }
      if (!hideLabel) {
        var span = document.createElement("span");
        span.className = "quest-opt__label";
        span.textContent = label;
        btn.appendChild(span);
      }
      btn.addEventListener("click", function () {
        if (opt && opt.word_audio) playId(opt.word_audio);
        onPick(id, btn, multi);
      });
      grid.appendChild(btn);
    });
    return grid;
  }

  function setSlovikPose(pose) {
    var el = document.getElementById("quest-buddy-img") || document.getElementById("quest-slovik");
    if (!el || !pose) return;
    el.src = slovikUrl(pose);
  }

  function renderEcho(station) {
    var taps = 0;
    var need = station.taps || 3;
    var box = document.createElement("div");
    box.className = "quest-echo";
    var letter = document.createElement("button");
    letter.type = "button";
    letter.className = "quest-echo__letter";
    letter.textContent = station.letter || "А";
    var count = document.createElement("p");
    count.className = "quest-echo__count";
    count.textContent = "0 / " + need;
    letter.addEventListener("click", function () {
      if (taps >= need) return;
      taps += 1;
      box.classList.add("is-playing");
      letter.classList.add("is-hit");
      playId(station.sound);
      count.textContent = taps + " / " + need;
      setTimeout(function () {
        box.classList.remove("is-playing");
        letter.classList.remove("is-hit");
      }, 280);
      if (taps >= need) {
        coachReact("ok", true);
        enableNext(true);
      }
    });
    box.appendChild(letter);
    box.appendChild(count);
    root().appendChild(box);
  }

  function renderMeetLetter(station) {
    var field = elBody.querySelector(".quest-playfield");
    if (field) field.classList.add("quest-playfield--meet");
    var box = document.createElement("div");
    box.className = "quest-meet";
    var letter = document.createElement("button");
    letter.type = "button";
    letter.className = "quest-meet__letter";
    var word = String(station.letter || "А");
    if (word.length > 1) letter.classList.add("is-word");
    letter.setAttribute("aria-label", word);
    if (station.letter_image) {
      var art = document.createElement("img");
      art.alt = word;
      art.src = assetUrl(station.letter_image);
      art.addEventListener("error", function () {
        letter.classList.remove("has-art");
        if (!letter.querySelector(".quest-meet__word")) {
          letter.textContent = word;
        }
      });
      letter.classList.add("has-art");
      letter.appendChild(art);
    } else {
      letter.textContent = word;
    }
    var met = false;
    // tap-prompt below the word
    var tapHint = document.createElement("p");
    tapHint.className = "quest-meet__hint quest-meet__tap";
    tapHint.textContent = station.hint || "Нажми на слово";
    box.appendChild(letter);
    box.appendChild(tapHint);

    letter.addEventListener("click", function () {
      letter.classList.add("is-hit");
      tapHint.style.opacity = "0";
      if (met) {
        playId(station.sound);
        return;
      }
      met = true;
      var stayId = station.id;
      if (station.tech_msg) showMsg(station.tech_msg, true);
      playId(station.sound, function () {
        if (!stations[idx] || stations[idx].id !== stayId) return;
        var coachLine = station.coach_success || station.success_msg;
        if (coachLine) coachSay(coachLine);
        if (station.success_audio) playId(station.success_audio);
      });
    });
    root().appendChild(box);
    enableNext(true);
  }

  function renderBuildLetter(station) {
    var field = elBody.querySelector(".quest-playfield");
    if (field) field.classList.add("quest-playfield--build");
    var parts = shuffle((station.parts || [
      { id: "left", role: "leg-left", label: "левая ножка" },
      { id: "right", role: "leg-right", label: "правая ножка" },
      { id: "bar", role: "bar", label: "перекладина" }
    ]).map(function (p) {
      return {
        id: p.id,
        role: p.role,
        label: p.label || p.role
      };
    }));
    var placed = {};
    var selected = null;
    var wrap = document.createElement("div");
    wrap.className = "quest-build";

    var letter = document.createElement("div");
    letter.className = "quest-build__letter";
    letter.setAttribute("aria-label", "Собери букву " + (station.letter || "А"));

    function clearPick() {
      selected = null;
      wrap.classList.remove("has-pick");
      wrap.querySelectorAll(".quest-build__part").forEach(function (el) {
        el.classList.remove("is-picked");
      });
      wrap.querySelectorAll(".quest-build__slot").forEach(function (el) {
        el.classList.remove("is-target");
      });
    }

    function tryPlace(role, slotBtn) {
      if (slotBtn.classList.contains("is-filled")) return;
      if (!selected) {
        showMsg("Сначала нажми на часть внизу.", false);
        return;
      }
      if (selected.role !== role) {
        slotBtn.classList.add("is-wrong");
        coachReact("wrong", false);
        setTimeout(function () {
          slotBtn.classList.remove("is-wrong");
          if (elMsg) elMsg.style.display = "none";
        }, 650);
        return;
      }
      placed[role] = true;
      slotBtn.classList.add("is-filled");
      selected.btn.classList.add("is-used");
      clearPick();
      var left = parts.filter(function (p) { return !placed[p.role]; });
      if (!left.length) {
        wrap.classList.add("is-done");
        if (!station.success_msg) coachReact("good", true);
        enableNext(true);
      } else {
        coachReact("yes");
      }
    }

    [
      { role: "leg-left", label: "левая ножка" },
      { role: "leg-right", label: "правая ножка" },
      { role: "bar", label: "перекладина" }
    ].forEach(function (slot) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "quest-build__slot is-" + slot.role;
      btn.setAttribute("aria-label", slot.label);
      btn.addEventListener("click", function () { tryPlace(slot.role, btn); });
      letter.appendChild(btn);
    });
    wrap.appendChild(letter);

    var tray = document.createElement("div");
    tray.className = "quest-build__parts";
    parts.forEach(function (part) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "quest-build__part is-" + part.role;
      btn.setAttribute("aria-label", part.label || part.role);
      var preview = document.createElement("span");
      preview.className = "quest-build__preview";
      var stick = document.createElement("span");
      stick.className = "quest-build__stick";
      preview.appendChild(stick);
      btn.appendChild(preview);
      var cap = document.createElement("span");
      cap.className = "quest-build__cap";
      cap.textContent = part.role === "bar"
        ? "перекладина"
        : (part.role === "leg-left" ? "левая" : "правая");
      btn.appendChild(cap);
      btn.addEventListener("click", function () {
        if (btn.classList.contains("is-used") || wrap.classList.contains("is-done")) return;
        wrap.querySelectorAll(".quest-build__part").forEach(function (el) {
          el.classList.remove("is-picked");
        });
        if (selected && selected.btn === btn) {
          clearPick();
          return;
        }
        wrap.querySelectorAll(".quest-build__slot").forEach(function (el) {
          el.classList.toggle("is-target", el.classList.contains("is-" + part.role) && !el.classList.contains("is-filled"));
        });
        wrap.classList.add("has-pick");
        selected = { role: part.role, btn: btn };
        btn.classList.add("is-picked");
      });
      tray.appendChild(btn);
    });
    wrap.appendChild(tray);

    if (station.hint) showMsg(station.hint, true);
    root().appendChild(wrap);
  }

  function letterSoundId(station, letter) {
    var map = station.letter_sounds || {};
    if (map[letter]) return map[letter];
    var fallback = {
      "А": "snd-a",
      "О": "snd-o",
      "И": "snd-i",
      "У": "snd-u",
      "М": "snd-m"
    };
    return fallback[letter] || "";
  }

  function renderCatchLetter(station) {
    var gen = playGen;
    var target = station.letter || "А";
    var need = station.catches || 3;
    var letters = station.letters || ["А", "О", "И", "У"];
    var got = 0;
    var glowing = null;
    var done = false;
    var wrap = document.createElement("div");
    wrap.className = "quest-catch";
    var count = document.createElement("p");
    count.className = "quest-echo__count";
    count.textContent = "Поймано: 0 / " + need;
    var row = document.createElement("div");
    row.className = "quest-catch__row";
    var btns = {};

    function alive() {
      return !done && gen === playGen;
    }

    function dimAll() {
      letters.forEach(function (L) {
        if (btns[L]) btns[L].classList.remove("is-glow", "is-hit", "is-wrong");
      });
    }

    function glowLetter(letter) {
      if (!alive()) return;
      glowing = letter;
      if (btns[glowing]) btns[glowing].classList.add("is-glow");
      playSfx(letterSoundId(station, glowing));
    }

    function scheduleFlash() {
      if (!alive()) return;
      if (gameTimer) clearTimeout(gameTimer);
      gameTimer = setTimeout(function () {
        if (!alive()) return;
        dimAll();
        glowing = null;
        gameTimer = setTimeout(function () {
          if (!alive()) return;
          var others = letters.filter(function (L) { return L !== target; });
          var next = Math.random() < 0.52 ? target : others[Math.floor(Math.random() * others.length)];
          glowLetter(next);
          gameTimer = setTimeout(function () {
            if (!alive()) return;
            if (btns[glowing]) btns[glowing].classList.remove("is-glow");
            glowing = null;
            scheduleFlash();
          }, 1600);
        }, 500);
      }, 320);
    }

    letters.forEach(function (L) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "quest-echo__letter quest-catch__letter";
      b.textContent = L;
      b.addEventListener("click", function () {
        if (!alive() || !glowing) return;
        if (L === target && glowing === target) {
          got += 1;
          count.textContent = "Поймано: " + got + " / " + need;
          b.classList.add("is-hit");
          glowing = null;
          dimAll();
          if (got >= need) {
            done = true;
            if (gameTimer) clearTimeout(gameTimer);
            gameTimer = null;
            hushVoice();
            try {
              sfx.pause();
              sfx.removeAttribute("src");
              sfx.load();
            } catch (e) {}
            coachReact("good", true);
            enableNext(true);
            return;
          }
          coachReact("yes");
          scheduleFlash();
        } else {
          b.classList.add("is-wrong");
          coachReact("wrong", false);
          setTimeout(function () { b.classList.remove("is-wrong"); }, 450);
          dimAll();
          glowing = null;
          scheduleFlash();
        }
      });
      row.appendChild(b);
      btns[L] = b;
    });
    wrap.appendChild(row);
    wrap.appendChild(count);
    root().appendChild(wrap);
    afterStationVoice(function () {
      if (alive()) scheduleFlash();
    });
  }

  function gridPositions(count, cols) {
    cols = cols || (count <= 4 ? 2 : 3);
    var rows = Math.max(1, Math.ceil(count / cols));
    var out = [];
    for (var i = 0; i < count; i++) {
      var r = Math.floor(i / cols);
      var c = i % cols;
      var colsInRow = Math.min(cols, count - r * cols);
      out.push({
        x: ((c + 0.5) / colsInRow) * 100,
        y: ((r + 0.5) / rows) * 100
      });
    }
    return out;
  }

  function renderSceneHunt(station) {
    var need = (station.correct_ids || []).slice();
    var found = {};
    var hotspots = station.hotspots || [];
    var letterTiles = hotspots.length && !hotspots.some(function (hs) { return hs.image; });
    var moving = station.moving === true || (station.moving !== false && letterTiles);
    if (moving && window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      moving = false;
    }
    var useGrid = !moving && (station.layout === "grid" || (!letterTiles && hotspots.length >= 4));
    var spots = useGrid ? gridPositions(hotspots.length, station.grid_cols || 3) : null;
    var scene = document.createElement("div");
    scene.className = "quest-scene" + (moving ? " is-moving" : "") + (useGrid ? " is-grid" : "");
    var layer = document.createElement("div");
    layer.className = "quest-scene__hotspots";
    var wanderers = [];
    var count = null;
    if (need.length > 1) {
      count = document.createElement("p");
      count.className = "quest-echo__count quest-scene__count";
      count.textContent = "0 / " + need.length;
      scene.appendChild(count);
    }
    function refreshCount() {
      if (!count) return;
      var got = need.filter(function (c) { return found[c]; }).length;
      count.textContent = got + " / " + need.length;
    }
    hotspots.forEach(function (hs, i) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "quest-hotspot" + (hs.image ? " quest-hotspot--pic" : "") + (hs.size === "sm" ? " is-sm" : "") + (moving ? " quest-hotspot--wander" : "");
      var startX = (spots && spots[i] ? spots[i].x : hs.x) || 50;
      var startY = (spots && spots[i] ? spots[i].y : hs.y) || 50;
      btn.style.left = startX + "%";
      btn.style.top = startY + "%";
      btn.dataset.id = hs.id;
      if (hs.image) {
        var im = document.createElement("img");
        im.src = assetUrl(hs.image);
        im.alt = hs.label || hs.id;
        btn.appendChild(im);
      }
      if ((hs.caption || station.captions) && hs.label) {
        btn.classList.add("quest-hotspot--word");
        var cap = document.createElement("span");
        cap.className = "quest-hotspot__label";
        cap.textContent = hs.label;
        btn.appendChild(cap);
      } else if (!hs.image) {
        btn.textContent = hs.label || hs.id;
      }
      btn.addEventListener("click", function () {
        var id = hs.id;
        if (need.indexOf(id) >= 0) {
          if (found[id]) return;
          found[id] = true;
          btn.classList.add("is-correct");
          refreshCount();
          var left = need.filter(function (c) { return !found[c]; });
          if (!left.length) {
            if (gameRaf) {
              cancelAnimationFrame(gameRaf);
              gameRaf = null;
            }
            coachReact("found", true);
            enableNext(true);
          } else {
            coachReact("yes", true);
          }
        } else {
          btn.classList.add("is-wrong");
          coachReact("wrong", false);
          setTimeout(function () {
            btn.classList.remove("is-wrong");
            if (elMsg) elMsg.style.display = "none";
          }, 700);
        }
      });
      layer.appendChild(btn);
      if (moving) {
        var ang = Math.random() * Math.PI * 2;
        var base = Number(station.move_speed) > 0 ? Number(station.move_speed) : 5;
        var spd = base + Math.random() * (base * 0.35);
        wanderers.push({
          el: btn,
          x: startX,
          y: startY,
          vx: Math.cos(ang) * spd,
          vy: Math.sin(ang) * spd
        });
      }
    });
    scene.appendChild(layer);
    root().appendChild(scene);
    if (!wanderers.length) return;

    var last = 0;
    function tick(now) {
      if (!layer.isConnected) {
        gameRaf = null;
        return;
      }
      var dt = last ? Math.min(0.04, (now - last) / 1000) : 0.016;
      last = now;
      wanderers.forEach(function (m) {
        if (m.el.classList.contains("is-correct")) return;
        m.x += m.vx * dt;
        m.y += m.vy * dt;
        if (m.x < 8) { m.x = 8; m.vx = Math.abs(m.vx); }
        if (m.x > 92) { m.x = 92; m.vx = -Math.abs(m.vx); }
        if (m.y < 10) { m.y = 10; m.vy = Math.abs(m.vy); }
        if (m.y > 90) { m.y = 90; m.vy = -Math.abs(m.vy); }
        // Keep wandering letters out of the top slot row (letter cells).
        if (m.x >= 26 && m.x <= 74 && m.y <= 30) {
          m.y = 32;
          m.vy = Math.abs(m.vy) || 4;
        }
        var dx = m.x - 50;
        var dy = m.y - 54;
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 18 && dist > 0.2) {
          var nx = dx / dist;
          var ny = dy / dist;
          m.x = 50 + nx * 18;
          m.y = 54 + ny * 18;
          var push = m.vx * nx + m.vy * ny;
          if (push < 0) {
            m.vx -= 2 * push * nx;
            m.vy -= 2 * push * ny;
          }
        }
        if (Math.random() < 0.008) {
          m.vx += (Math.random() - 0.5) * 2.4;
          m.vy += (Math.random() - 0.5) * 2.4;
        }
        m.el.style.left = m.x + "%";
        m.el.style.top = m.y + "%";
      });
      gameRaf = requestAnimationFrame(tick);
    }
    gameRaf = requestAnimationFrame(tick);
  }

  function renderDragBasket(station) {
    var need = (station.correct || []).slice();
    var inBasket = [];
    var wrap = document.createElement("div");
    wrap.className = "quest-basket-wrap";
    var basket = document.createElement("div");
    basket.className = "quest-basket";
    basket.textContent = station.basket_label || "Корзина для а-а-а";
    wrap.appendChild(basket);
    root().appendChild(wrap);
    root().appendChild(renderOptions(station.options || [], function (id, btn) {
      if (inBasket.indexOf(id) >= 0) return;
      if (need.indexOf(id) < 0) {
        btn.classList.add("is-wrong");
        coachReact("wrong", false);
        setTimeout(function () {
          btn.classList.remove("is-wrong");
          if (elMsg) elMsg.style.display = "none";
        }, 800);
        return;
      }
      inBasket.push(id);
      btn.classList.add("is-correct");
      btn.disabled = true;
      if (basket.textContent && !basket.querySelector(".quest-opt")) {
        basket.textContent = "";
      }
      var clone = btn.cloneNode(true);
      clone.disabled = true;
      basket.appendChild(clone);
      basket.classList.add("is-target");
      if (need.every(function (c) { return inBasket.indexOf(c) >= 0; })) {
        coachReact("good", true);
        enableNext(true);
      }
    }));
  }

  function renderSortTwo(station) {
    var field = elBody.querySelector(".quest-playfield");
    if (field) field.classList.add("quest-playfield--sort");
    var leftIds = (station.left && station.left.correct) || [];
    var rightIds = (station.right && station.right.correct) || [];
    var total = leftIds.length + rightIds.length;
    var placed = 0;
    var picked = null;
    var wrap = document.createElement("div");
    wrap.className = "quest-sort";
    var bins = document.createElement("div");
    bins.className = "quest-sort__bins";

    function makeBin(side, spec) {
      var bin = document.createElement("div");
      bin.className = "quest-sort__bin";
      bin.dataset.side = side;
      var title = document.createElement("span");
      var label = (spec && spec.label) || side;
      title.className = "quest-sort__bin-title" + (String(label).length <= 2 ? " is-letter" : "");
      title.textContent = label;
      bin.appendChild(title);
      bin.addEventListener("click", function () {
        if (!picked) {
          coachReact("more");
          return;
        }
        var ok = side === "left" ? leftIds.indexOf(picked.id) >= 0 : rightIds.indexOf(picked.id) >= 0;
        if (!ok) {
          picked.btn.classList.add("is-wrong");
          bin.classList.add("is-wrong");
          coachReact("wrong", false);
          setTimeout(function () {
            picked.btn.classList.remove("is-wrong", "is-picked");
            bin.classList.remove("is-wrong");
            picked = null;
          }, 700);
          return;
        }
        picked.btn.classList.add("is-correct");
        picked.btn.disabled = true;
        picked.btn.classList.remove("is-picked");
        var clone = picked.btn.cloneNode(true);
        clone.disabled = true;
        bin.appendChild(clone);
        bin.classList.add("is-filled");
        placed += 1;
        picked = null;
        if (placed >= total) {
          coachReact("good", true);
          enableNext(true);
        } else {
          coachReact("yes");
        }
      });
      return bin;
    }

    bins.appendChild(makeBin("left", station.left));
    bins.appendChild(makeBin("right", station.right));
    wrap.appendChild(bins);
    wrap.appendChild(renderOptions(shuffle(station.options || []), function (id, btn) {
      if (btn.disabled) return;
      wrap.querySelectorAll(".quest-opt").forEach(function (el) {
        el.classList.remove("is-picked");
      });
      btn.classList.add("is-picked");
      picked = { id: id, btn: btn };
    }));
    root().appendChild(wrap);
  }

  function avoidTopSlotZone(x, y) {
    var px = Number(x);
    var py = Number(y);
    if (!(px >= 26 && px <= 74 && py <= 30)) {
      return { x: px, y: py };
    }
    if (px < 50) return { x: 12, y: Math.max(py, 36) };
    return { x: 88, y: Math.max(py, 36) };
  }

  function avoidCenterSlotZone(x, y) {
    var px = Number(x);
    var py = Number(y);
    if (!(px >= 24 && px <= 76 && py >= 36 && py <= 62)) {
      return { x: px, y: py };
    }
    if (px < 50 && py < 50) return { x: 14, y: 22 };
    if (px >= 50 && py < 50) return { x: 86, y: 22 };
    if (px < 50) return { x: 14, y: 78 };
    return { x: 86, y: 78 };
  }

  function renderLetterPuzzle(station) {
    var field = elBody.querySelector(".quest-playfield");
    if (field) field.classList.add("quest-playfield--around");
    var order = shuffle((station.pieces || ["А", "А", "А"]).map(function (p, n) {
      if (typeof p === "string") {
        return { id: p + "-" + n, label: p, correct: true };
      }
      return {
        id: p.id || ("p" + n),
        label: p.label || p.id,
        correct: p.correct !== false
      };
    }));
    var need = order.filter(function (p) { return p.correct; }).length;
    var slots = station.slots || need;
    var spots = station.piece_spots || [
      { x: 12, y: 34 },
      { x: 88, y: 32 },
      { x: 9, y: 56 },
      { x: 91, y: 54 },
      { x: 16, y: 84 },
      { x: 84, y: 84 }
    ];
    var filled = 0;
    var slotRow = document.createElement("div");
    slotRow.className = "quest-slots";
    var slotEls = [];
    for (var i = 0; i < slots; i++) {
      var s = document.createElement("div");
      s.className = "quest-slot";
      s.textContent = "·";
      slotRow.appendChild(s);
      slotEls.push(s);
    }
    root().appendChild(slotRow);
    var pieces = document.createElement("div");
    pieces.className = "quest-pieces";
    order.forEach(function (piece, n) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "quest-piece";
      b.textContent = piece.label;
      var spot = avoidTopSlotZone(
        (spots[n] || spots[0] || {}).x || 50,
        (spots[n] || spots[0] || {}).y || 50
      );
      b.style.left = spot.x + "%";
      b.style.top = spot.y + "%";
      b.addEventListener("click", function () {
        if (b.classList.contains("is-used") || filled >= slots) return;
        if (!piece.correct) {
          b.classList.add("is-wrong");
          coachReact("wrong", false);
          setTimeout(function () { b.classList.remove("is-wrong"); }, 500);
          return;
        }
        b.classList.add("is-used");
        slotEls[filled].textContent = piece.label;
        slotEls[filled].classList.add("is-filled");
        filled += 1;
        if (filled >= slots) {
          coachReact("found", true);
          enableNext(true);
        } else {
          coachReact("yes");
        }
      });
      pieces.appendChild(b);
    });
    root().appendChild(pieces);
  }

  function renderSlotBuild(station) {
    var field = elBody.querySelector(".quest-playfield");
    if (field) field.classList.add("quest-playfield--around");
    appendPromptPic(station);
    var targets = station.targets || ["М", "А"];
    var spots = station.piece_spots || [
      { x: 12, y: 28 },
      { x: 88, y: 26 },
      { x: 14, y: 82 },
      { x: 86, y: 82 }
    ];
    var placed = [];
    var slotRow = document.createElement("div");
    slotRow.className = "quest-slots is-center";
    var wideSlots = targets.some(function (t) { return String(t).length > 2; });
    if (wideSlots) slotRow.classList.add("is-wide");
    var slotEls = targets.map(function () {
      var s = document.createElement("div");
      s.className = "quest-slot" + (wideSlots ? " is-wide" : "");
      s.textContent = "?";
      slotRow.appendChild(s);
      return s;
    });
    root().appendChild(slotRow);
    var pieces = document.createElement("div");
    pieces.className = "quest-pieces";
    shuffle(station.options || []).forEach(function (opt, n) {
      var id = typeof opt === "string" ? opt : opt.id;
      var label = typeof opt === "string" ? opt : (opt.label || opt.id);
      var b = document.createElement("button");
      b.type = "button";
      b.className = "quest-piece";
      if (String(label).length > 2) b.classList.add("is-wide");
      b.textContent = label;
      var spot = avoidCenterSlotZone(
        (spots[n] || spots[0] || {}).x || 50,
        (spots[n] || spots[0] || {}).y || 50
      );
      b.style.left = spot.x + "%";
      b.style.top = spot.y + "%";
      b.addEventListener("click", function () {
        var next = placed.length;
        if (next >= targets.length || b.classList.contains("is-used")) return;
        if (String(id) !== String(targets[next])) {
          b.classList.add("is-wrong");
          coachReact("try", false);
          setTimeout(function () {
            b.classList.remove("is-wrong");
            if (elMsg) elMsg.style.display = "none";
          }, 800);
          return;
        }
        placed.push(id);
        b.classList.add("is-used");
        slotEls[next].textContent = String(id);
        slotEls[next].classList.add("is-filled");
        if (placed.length >= targets.length) {
          var res = document.createElement("span");
          res.className = "quest-slots__result";
          res.textContent = station.result_label || "МА";
          slotRow.appendChild(res);
          coachReact("good", true);
          if (station.result_sound) playId(station.result_sound);
          enableNext(true);
        } else {
          coachReact("yes");
        }
      });
      pieces.appendChild(b);
    });
    root().appendChild(pieces);
  }

  function checkSingle(correct, picked, btn) {
    var ok = String(picked) === String(correct) ||
      (Array.isArray(correct) && correct.indexOf(picked) >= 0);
    root().querySelectorAll(".quest-opt").forEach(function (el) {
      el.disabled = true;
    });
    if (ok) {
      btn.classList.add("is-correct");
      coachReact("ok", true);
      enableNext(true);
    } else {
      btn.classList.add("is-wrong");
      coachReact("try", false);
      setTimeout(function () {
        root().querySelectorAll(".quest-opt").forEach(function (el) {
          el.disabled = false;
          el.classList.remove("is-wrong", "is-selected");
        });
        if (elMsg) elMsg.style.display = "none";
      }, 900);
    }
  }

  function renderListenPick(station, round) {
    var r = round || (station.rounds && station.rounds[0]) || station;
    if (r.sound) {
      var play = document.createElement("button");
      play.type = "button";
      play.className = "chit-btn";
      play.textContent = "▶ Слушать звук";
      play.addEventListener("click", function () { playId(r.sound); });
      root().appendChild(play);
    }
    appendPromptPic(r);
    root().appendChild(renderOptions(r.options || [], function (id, btn, multi) {
      if (multi || station.multi || (r.correct && Array.isArray(r.correct))) {
        btn.classList.toggle("is-selected");
        var pos = selected.indexOf(id);
        if (pos >= 0) selected.splice(pos, 1);
        else selected.push(id);
        var need = r.pick || (Array.isArray(r.correct) ? r.correct.length : 1);
        if (selected.length >= need) {
          var ok = Array.isArray(r.correct)
            ? r.correct.every(function (c) { return selected.indexOf(c) >= 0; }) && selected.length === r.correct.length
            : selected.indexOf(r.correct) >= 0;
          if (ok) {
            coachReact("ok", true);
            enableNext(true);
          } else {
            coachReact("more", false);
            selected = [];
            root().querySelectorAll(".quest-opt").forEach(function (el) { el.classList.remove("is-selected"); });
          }
        }
      } else {
        checkSingle(r.correct, id, btn);
      }
    }, station.multi, { picture_only: !!(station.picture_only || r.picture_only) }));
  }

  function renderFind(station) {
    var rounds = station.rounds || [station];
    var roundIdx = 0;
    function showRound() {
      openPlayfield(station);
      selected = [];
      enableNext(false);
      var r = rounds[roundIdx];
      if (r.sound) playId(r.sound);
      if (r.prompt_audio) playId(r.prompt_audio);
      appendPromptPic(r);
      root().appendChild(renderOptions(r.options || [], function (id, btn) {
        var ok = String(id) === String(r.correct);
        if (ok) {
          btn.classList.add("is-correct");
          roundIdx += 1;
          if (roundIdx >= rounds.length) {
            coachReact("found", true);
            enableNext(true);
          } else {
            coachReact("yes", true);
            setTimeout(showRound, 500);
          }
        } else {
          checkSingle(r.correct, id, btn);
        }
      }));
    }
    showRound();
  }

  function renderTrace(station) {
    var canvas = document.createElement("canvas");
    canvas.className = "quest-trace";
    canvas.width = 280;
    canvas.height = 280;
    root().appendChild(canvas);
    var letter = document.createElement("p");
    letter.className = "quest-letter";
    letter.style.textAlign = "center";
    letter.textContent = station.letter || "А";
    root().appendChild(letter);
    var ctx = canvas.getContext("2d");
    var drawing = false;
    var strokes = 0;
    function pos(e) {
      var rect = canvas.getBoundingClientRect();
      var t = e.touches ? e.touches[0] : e;
      return { x: t.clientX - rect.left, y: t.clientY - rect.top };
    }
    function start(e) {
      drawing = true;
      strokes += 1;
      var p = pos(e);
      ctx.beginPath();
      ctx.moveTo(p.x, p.y);
      e.preventDefault();
    }
    function move(e) {
      if (!drawing) return;
      var p = pos(e);
      ctx.strokeStyle = "#5B7FA6";
      ctx.lineWidth = 6;
      ctx.lineCap = "round";
      ctx.lineTo(p.x, p.y);
      ctx.stroke();
      e.preventDefault();
    }
    function end() {
      drawing = false;
      if (strokes >= 1) {
        showMsg("Нашёл!", true);
        enableNext(true);
      }
    }
    canvas.addEventListener("mousedown", start);
    canvas.addEventListener("mousemove", move);
    canvas.addEventListener("mouseup", end);
    canvas.addEventListener("touchstart", start, { passive: false });
    canvas.addEventListener("touchmove", move, { passive: false });
    canvas.addEventListener("touchend", end);
  }

  function renderMatchPairs(station) {
    var pairs = (station.pairs || []).slice();
    var words = pairs.slice();
    var pics = shuffle(pairs.slice());
    var picked = null;
    var done = {};
    var colors = ["#d98a5d", "#7f648f", "#84a96f"];
    var colorIdx = 0;

    var field = elBody.querySelector(".quest-playfield");
    if (field) field.classList.add("quest-playfield--match");

    var wrap = document.createElement("div");
    wrap.className = "quest-match";
    var wordCol = document.createElement("div");
    wordCol.className = "quest-match__col is-words";
    var picCol = document.createElement("div");
    picCol.className = "quest-match__col is-pics";

    function clearPick() {
      picked = null;
      wrap.querySelectorAll(".is-picked").forEach(function (el) {
        el.classList.remove("is-picked");
      });
    }

    function tryPair(wordId, picId, wordBtn, picBtn) {
      if (String(wordId) !== String(picId)) {
        wordBtn.classList.add("is-wrong");
        picBtn.classList.add("is-wrong");
        coachReact("wrong", false);
        setTimeout(function () {
          wordBtn.classList.remove("is-wrong");
          picBtn.classList.remove("is-wrong");
          if (elMsg) elMsg.style.display = "none";
        }, 650);
        clearPick();
        return;
      }
      var tone = colors[colorIdx % colors.length];
      colorIdx += 1;
      done[wordId] = true;
      wordBtn.classList.add("is-done");
      picBtn.classList.add("is-done");
      wordBtn.style.borderColor = tone;
      picBtn.style.borderColor = tone;
      wordBtn.disabled = true;
      picBtn.disabled = true;
      clearPick();
      var left = pairs.filter(function (p) { return !done[p.id]; });
      if (!left.length) {
        coachReact("found", true);
        enableNext(true);
      }
    }

    function bind(btn, side, id) {
      btn.addEventListener("click", function () {
        if (done[id] || btn.disabled) return;
        if (!picked) {
          picked = { side: side, id: id, btn: btn };
          btn.classList.add("is-picked");
          return;
        }
        if (picked.btn === btn) {
          clearPick();
          return;
        }
        if (picked.side === side) {
          clearPick();
          picked = { side: side, id: id, btn: btn };
          btn.classList.add("is-picked");
          return;
        }
        if (picked.side === "word") tryPair(picked.id, id, picked.btn, btn);
        else tryPair(id, picked.id, btn, picked.btn);
      });
    }

    words.forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "quest-match__chip is-word";
      btn.textContent = item.label || item.id;
      bind(btn, "word", item.id);
      wordCol.appendChild(btn);
    });
    pics.forEach(function (item) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "quest-match__chip is-pic";
      if (item.image) {
        var img = document.createElement("img");
        img.src = assetUrl(item.image);
        img.alt = item.label || "";
        btn.appendChild(img);
      }
      bind(btn, "pic", item.id);
      picCol.appendChild(btn);
    });

    wrap.appendChild(wordCol);
    wrap.appendChild(picCol);
    root().appendChild(wrap);
    var hint = document.createElement("p");
    hint.className = "quest-match__hint";
    hint.textContent = station.hint || "Нажми на слово, потом на картинку.";
    root().appendChild(hint);
  }

  function renderJoin(station) {
    var wrap = document.createElement("div");
    wrap.className = "quest-join";
    var left = document.createElement("button");
    left.type = "button";
    left.className = "quest-join__chip";
    if (station.left && station.left.image) {
      var li = document.createElement("img");
      li.src = assetUrl(station.left.image);
      li.alt = "";
      left.appendChild(li);
    }
    left.appendChild(document.createTextNode((station.left && station.left.label) || "М"));
    var arrow = document.createElement("span");
    arrow.textContent = "→";
    var right = document.createElement("button");
    right.type = "button";
    right.className = "quest-join__chip";
    if (station.right && station.right.image) {
      var ri = document.createElement("img");
      ri.src = assetUrl(station.right.image);
      ri.alt = "";
      right.appendChild(ri);
    }
    right.appendChild(document.createTextNode((station.right && station.right.label) || "А"));
    wrap.appendChild(left);
    wrap.appendChild(arrow);
    wrap.appendChild(right);
    root().appendChild(wrap);
    var step = 0;
    function finish() {
      if (station.result && station.result.sound) playId(station.result.sound);
      left.classList.add("is-done");
      right.classList.add("is-done");
      if (station.result && station.result.image) {
        var img = document.createElement("img");
        img.className = "quest-spark-fly";
        img.src = assetUrl(station.result.image);
        img.alt = "";
        root().appendChild(img);
      }
      var res = document.createElement("p");
      res.className = "quest-letter";
      res.style.textAlign = "center";
      res.textContent = (station.result && station.result.label) || "МА";
      root().appendChild(res);
      coachReact("good", true);
      enableNext(true);
    }
    left.addEventListener("click", function () {
      if (station.left && station.left.sound) playId(station.left.sound);
      step = Math.max(step, 1);
      left.classList.add("is-done");
      if (step >= 2) finish();
      else coachReact("yes", true);
    });
    right.addEventListener("click", function () {
      if (station.right && station.right.sound) playId(station.right.sound);
      if (step < 1) {
        coachReact("try", false);
        return;
      }
      step = 2;
      right.classList.add("is-done");
      finish();
    });
  }

  function renderWordPicture(station) {
    var items = station.items || [station];
    var itemIdx = 0;
    function showItem() {
      var item = items[itemIdx];
      var view = {
        slovik_line: itemIdx === 0 ? (station.slovik_line || "") : (item.slovik_line || ""),
        slovik_pose: station.slovik_pose,
        scene_image: station.scene_image,
        audio: itemIdx === 0 ? (station.audio || "") : (item.audio || ""),
        tech_msg: itemIdx === 0 ? station.tech_msg : undefined
      };
      openPlayfield(view);
      enableNext(false);
      var word = document.createElement("p");
      word.className = "quest-letter quest-letter--chip";
      word.textContent = item.word || station.word || "";
      root().appendChild(word);
      if (item.audio) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "chit-btn";
        b.textContent = "▶ Слушать слово";
        b.addEventListener("click", function () { playId(item.audio); });
        root().appendChild(b);
      }
      root().appendChild(renderOptions(item.options || [], function (id, btn) {
        if (String(id) === String(item.correct)) {
          btn.classList.add("is-correct");
          itemIdx += 1;
          if (itemIdx >= items.length) {
            coachReact("ok", true);
            enableNext(true);
          } else {
            setTimeout(showItem, 450);
          }
        } else {
          checkSingle(item.correct, id, btn);
        }
      }, false, { picture_only: !!(station.picture_only || item.picture_only) }));
    }
    showItem();
  }

  function renderPhrase(station) {
    appendPromptPic(station);
    if (station.phrase && station.phrase !== "?") {
      var word = document.createElement("p");
      word.className = "quest-letter quest-letter--chip";
      word.style.fontSize = "1.55rem";
      word.textContent = station.phrase;
      root().appendChild(word);
    }
    if (station.phrase_audio) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "chit-btn";
      b.textContent = "▶ Слушать фразу";
      b.addEventListener("click", function () { playId(station.phrase_audio); });
      root().appendChild(b);
    }
    root().appendChild(renderOptions(station.options || [], function (id, btn) {
      checkSingle(station.correct, id, btn);
    }, false, { picture_only: !!station.picture_only }));
  }

  function renderShapeRebus(station) {
    var rounds = station.rounds || [station];
    var roundIdx = 0;

    function legendIndex() {
      var byPair = {};
      var byLetter = {};
      var errors = [];
      (station.legend || []).forEach(function (item, i) {
        if (!item || !item.shape || !item.tone || !item.letter) {
          errors.push("legend[" + i + "]: нужна shape, tone, letter");
          return;
        }
        var pair = item.shape + "|" + item.tone;
        if (byPair[pair]) {
          errors.push("в ключе одна фигурка на две буквы: " + pair + " → " + byPair[pair] + " и " + item.letter);
        }
        byPair[pair] = item.letter;
        if (byLetter[item.letter]) {
          errors.push("буква «" + item.letter + "» в ключе дважды");
        }
        byLetter[item.letter] = item;
      });
      (rounds || []).forEach(function (r, ri) {
        (r.cipher || []).forEach(function (tok, ti) {
          if (!tok) return;
          if (tok.letter && byLetter[tok.letter]) return;
          var pair = (tok.shape || "") + "|" + (tok.tone || "");
          if (!byPair[pair]) {
            errors.push("раунд " + (ri + 1) + " символ " + (ti + 1) + ": фигурка не из ключа (" + pair + ")");
          }
        });
      });
      if (errors.length && typeof console !== "undefined" && console.warn) {
        console.warn("[shape_rebus]", station.id || station.title || "", errors);
      }
      return { byLetter: byLetter, byPair: byPair, errors: errors };
    }

    var legendMap = legendIndex();

    // token: { shape, tone, letter }
    // in legend → show shape + letter label
    // in cipher (encoded word) → show shape only, NO letter
    // in options → show plain text word label only
    function resolveToken(token) {
      if (!token) return token;
      if (token.letter && legendMap.byLetter[token.letter]) {
        var fromLegend = legendMap.byLetter[token.letter];
        return {
          shape: fromLegend.shape,
          tone: fromLegend.tone,
          letter: token.letter
        };
      }
      return token;
    }

    function tokenEl(token, showLetter) {
      var tok = resolveToken(token);
      var el = document.createElement("span");
      el.className = "quest-rebus__token";
      if (tok && tok.shape) el.classList.add("is-" + tok.shape);
      if (tok && tok.tone) el.classList.add("is-" + tok.tone);
      el.textContent = showLetter ? ((tok && tok.letter) || "") : "";
      return el;
    }

    function renderLegend() {
      if (!station.legend || !station.legend.length) return;
      var box = document.createElement("div");
      box.className = "quest-rebus";
      var legend = document.createElement("div");
      legend.className = "quest-rebus__legend";
      station.legend.forEach(function (item) {
        var chip = document.createElement("div");
        chip.className = "quest-rebus__legend-chip";
        // legend chip: small shape WITHOUT letter, then " = Б"
        var shape = tokenEl(item, false);
        shape.classList.add("is-small");
        chip.appendChild(shape);
        var text = document.createElement("span");
        text.textContent = " = " + ((item && item.letter) || "");
        chip.appendChild(text);
        legend.appendChild(chip);
      });
      box.appendChild(legend);
      root().appendChild(box);
    }

    function renderCipher(tokens) {
      // Display the encoded word: shapes only, no letters inside
      var row = document.createElement("div");
      row.className = "quest-rebus__cipher";
      (tokens || []).forEach(function (tok) {
        row.appendChild(tokenEl(tok, false));
      });
      root().appendChild(row);
    }

    function showRound() {
      openPlayfield(station);
      var field = elBody.querySelector(".quest-playfield");
      if (field) field.classList.add("quest-playfield--rebus");
      enableNext(false);
      var r = rounds[roundIdx];
      // 1. Legend (shape key)
      renderLegend();
      // 2. The cipher — encoded word shown as shapes (no letters)
      if (r.cipher) {
        var label = document.createElement("p");
        label.className = "quest-hint quest-rebus__prompt";
        label.textContent = r.prompt_text || "Прочитай шифр и выбери слово.";
        root().appendChild(label);
        renderCipher(r.cipher);
      }
      // 3. Word options — plain text, no shapes
      var grid = document.createElement("div");
      grid.className = "quest-grid quest-grid--choice quest-rebus__grid";
      (r.options || []).forEach(function (opt) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "quest-opt quest-opt--choice";
        btn.dataset.id = opt.id;
        btn.setAttribute("aria-label", opt.label || opt.id);
        var span = document.createElement("span");
        span.className = "quest-opt__label";
        span.textContent = opt.label || opt.id;
        btn.appendChild(span);
        btn.addEventListener("click", function () {
          var ok = String(opt.id) === String(r.correct);
          if (ok) {
            btn.classList.add("is-correct");
            roundIdx += 1;
            if (roundIdx >= rounds.length) {
              coachReact("found", true);
              enableNext(true);
            } else {
              coachReact("yes", true);
              setTimeout(showRound, 500);
            }
          } else {
            checkSingle(r.correct, opt.id, btn);
          }
        });
        grid.appendChild(btn);
      });
      root().appendChild(grid);
    }

    showRound();
  }

  function renderPathWord(station) {
    var rounds = station.rounds || [station];
    var roundIdx = 0;

    function renderBoard(round) {
      var left = round.left || [];
      var right = round.right || [];
      var pairs = round.pairs || [];
      var rows = Math.max(left.length, right.length, 2);
      var box = document.createElement("div");
      box.className = "quest-pathword";
      var board = document.createElement("div");
      board.className = "quest-pathword__board";
      var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("viewBox", "0 0 100 100");
      svg.setAttribute("preserveAspectRatio", "none");
      svg.classList.add("quest-pathword__svg");
      pairs.forEach(function (pair) {
        var from = pair.from || 0;
        var to = pair.to || 0;
        var y1 = rows === 1 ? 50 : (18 + (64 * from / Math.max(1, rows - 1)));
        var y2 = rows === 1 ? 50 : (18 + (64 * to / Math.max(1, rows - 1)));
        var d = "M 18 " + y1 + " C 40 " + y1 + ", 60 " + y2 + ", 82 " + y2;
        var color = pair.color || "#3d8b6e";
        var under = document.createElementNS("http://www.w3.org/2000/svg", "path");
        under.setAttribute("d", d);
        under.setAttribute("fill", "none");
        under.setAttribute("stroke", "#fff8f0");
        under.setAttribute("stroke-width", "9");
        under.setAttribute("stroke-linecap", "round");
        under.setAttribute("stroke-opacity", "0.95");
        svg.appendChild(under);
        var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        path.setAttribute("d", d);
        path.setAttribute("fill", "none");
        path.setAttribute("stroke", color);
        path.setAttribute("stroke-width", "5");
        path.setAttribute("stroke-linecap", "round");
        path.setAttribute("stroke-opacity", "1");
        svg.appendChild(path);
      });
      board.appendChild(svg);

      var leftCol = document.createElement("div");
      leftCol.className = "quest-pathword__col is-left";
      left.forEach(function (item) {
        var chip = document.createElement("div");
        chip.className = "quest-pathword__chip";
        chip.textContent = item;
        leftCol.appendChild(chip);
      });

      var rightCol = document.createElement("div");
      rightCol.className = "quest-pathword__col is-right";
      right.forEach(function (item) {
        var chip = document.createElement("div");
        chip.className = "quest-pathword__chip";
        chip.textContent = item;
        rightCol.appendChild(chip);
      });

      board.appendChild(leftCol);
      board.appendChild(rightCol);
      box.appendChild(board);
      return box;
    }

    function showRound() {
      openPlayfield(station);
      var field = elBody.querySelector(".quest-playfield");
      if (field) field.classList.add("quest-playfield--pathword");
      enableNext(false);
      selected = [];
      var r = rounds[roundIdx];
      if (r.prompt_text) {
        var prompt = document.createElement("p");
        prompt.className = "quest-hint quest-pathword__prompt";
        prompt.textContent = r.prompt_text;
        root().appendChild(prompt);
      }
      root().appendChild(renderBoard(r));
      var opts = renderOptions(r.options || [], function (id, btn) {
        btn.classList.toggle("is-selected");
        var pos = selected.indexOf(id);
        if (pos >= 0) selected.splice(pos, 1);
        else selected.push(id);
        var correct = Array.isArray(r.correct) ? r.correct : [r.correct];
        if (selected.length >= correct.length) {
          var ok = correct.every(function (val) { return selected.indexOf(val) >= 0; }) && selected.length === correct.length;
          if (ok) {
            roundIdx += 1;
            if (roundIdx >= rounds.length) {
              coachReact("found", true);
              enableNext(true);
            } else {
              coachReact("yes", true);
              setTimeout(showRound, 500);
            }
          } else {
            coachReact("more", false);
            selected = [];
            root().querySelectorAll(".quest-opt").forEach(function (el) { el.classList.remove("is-selected"); });
          }
        }
      }, true);
      opts.classList.add("quest-grid--pathword-opts");
      root().appendChild(opts);
    }

    showRound();
  }

  function videoSrc(station) {
    var v = station && station.video;
    if (!v) return "";
    if (typeof v === "string") return assetUrl(v);
    if (v.src) return assetUrl(v.src);
    if (v.url) return assetUrl(v.url);
    return "";
  }

  function setIntroMode(on) {
    var board = document.querySelector(".quest-board");
    if (board) board.classList.toggle("quest-board--intro", !!on);
  }

  function renderIntroVideo(station) {
    setIntroMode(true);
    enableNext(false);
    parkFooter();
    elBody.innerHTML = "";
    contentRoot = elBody;
    var box = document.createElement("div");
    box.className = "quest-intro is-idle";
    var src = videoSrc(station);
    var vid = null;
    var ended = false;

    function setState(name) {
      box.classList.remove("is-idle", "is-playing", "is-paused", "is-ended");
      box.classList.add(name);
    }

    var poster = (station.video && station.video.poster) || station.scene_image;
    if (poster) {
      var posterUrl = assetUrl(poster);
      box.style.backgroundImage = "url(" + posterUrl + ")";
      box.style.backgroundSize = "cover";
      box.style.backgroundPosition = "center";
    }

    if (src) {
      vid = document.createElement("video");
      vid.className = "quest-intro__video";
      vid.src = src;
      vid.autoplay = false;
      vid.muted = false;
      vid.loop = false;
      vid.playsInline = true;
      vid.preload = "metadata";
      vid.controls = false;
      vid.setAttribute("playsinline", "");
      vid.setAttribute("webkit-playsinline", "");
      if (poster) vid.setAttribute("poster", assetUrl(poster));
      if (station.video && station.video.title) {
        vid.setAttribute("aria-label", station.video.title);
      }
      box.appendChild(vid);
      vid.addEventListener("loadedmetadata", function () {
        if (vid.videoWidth && vid.videoHeight) {
          box.style.aspectRatio = vid.videoWidth + " / " + vid.videoHeight;
        }
      });
    }

    var top = document.createElement("p");
    top.className = "quest-intro__hello";
    top.textContent = cfg.childName ? ("Привет, " + cfg.childName + "!") : "Привет!";
    box.appendChild(top);

    var play = document.createElement("button");
    play.type = "button";
    play.className = "quest-intro__play";
    play.setAttribute("aria-label", "Воспроизвести");
    play.textContent = "Воспроизвести";
    play.addEventListener("click", function (e) {
      e.stopPropagation();
      if (!vid || ended) return;
      vid.muted = false;
      vid.play().then(function () {
        setState("is-playing");
      }).catch(function () {
        setState("is-idle");
      });
    });

    var pause = document.createElement("button");
    pause.type = "button";
    pause.className = "quest-intro__pause";
    pause.setAttribute("aria-label", "Пауза");
    pause.textContent = "Пауза";
    pause.addEventListener("click", function (e) {
      e.stopPropagation();
      if (!vid || ended) return;
      vid.pause();
      setState("is-paused");
    });

    var center = document.createElement("div");
    center.className = "quest-intro__center";
    center.appendChild(play);
    center.appendChild(pause);
    box.appendChild(center);

    var endUi = document.createElement("div");
    endUi.className = "quest-intro__end";
    var line = document.createElement("p");
    line.className = "quest-intro__line";
    line.textContent = station.slovik_line || "Помоги мне вернуть звуки!";
    var cta = document.createElement("button");
    cta.type = "button";
    cta.className = "quest-intro__cta";
    cta.textContent = station.cta_label || "Начать приключение";
    cta.addEventListener("click", function () {
      if (cta.disabled) return;
      cta.disabled = true;
      if (vid) vid.pause();
      setIntroMode(false);
      goNext();
    });
    endUi.appendChild(line);
    endUi.appendChild(cta);
    box.appendChild(endUi);

    if (vid) {
      vid.addEventListener("ended", function () {
        ended = true;
        setState("is-ended");
      });
      vid.addEventListener("pause", function () {
        if (!ended && vid.currentTime > 0 && vid.currentTime < vid.duration) {
          setState("is-paused");
        }
      });
      vid.addEventListener("playing", function () {
        if (!ended) setState("is-playing");
      });
    }

    elBody.appendChild(box);
  }

  function renderLetterMaze(station, onDone) {
    var grid = station.grid || [];
    var letter = station.letter || "А";
    var start = (station.start || [0, 0]).slice();
    var end = (station.end || [grid.length - 1, (grid[0] || []).length - 1]).slice();
    var path = [start[0] + "," + start[1]];
    var done = false;
    var wrap = document.createElement("div");
    wrap.className = "quest-maze";
    if (String(letter).length > 1) wrap.classList.add("is-syllable");
    if (grid[0]) wrap.style.gridTemplateColumns = "repeat(" + grid[0].length + ", 1fr)";
    var cells = {};

    function key(r, c) { return r + "," + c; }
    function lastPos() {
      var p = path[path.length - 1].split(",");
      return [parseInt(p[0], 10), parseInt(p[1], 10)];
    }
    function adjacent(a, b) {
      return Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]) === 1;
    }
    function paint() {
      Object.keys(cells).forEach(function (k) {
        cells[k].classList.toggle("is-path", path.indexOf(k) >= 0);
        cells[k].classList.toggle("is-current", k === path[path.length - 1]);
      });
    }
    function finish() {
      if (done) return;
      done = true;
      wrap.classList.add("is-done");
      coachReact("good", true);
      if (typeof onDone === "function") onDone();
      else enableNext(true);
    }

    grid.forEach(function (row, r) {
      row.forEach(function (ch, c) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "quest-maze__cell";
        var glyph = document.createElement("span");
        glyph.className = "quest-maze__letter";
        glyph.textContent = ch;
        btn.appendChild(glyph);
        if (r === start[0] && c === start[1]) {
          btn.classList.add("is-start");
          var mark = document.createElement("span");
          mark.className = "quest-maze__tag";
          mark.textContent = "старт";
          btn.appendChild(mark);
        }
        if (r === end[0] && c === end[1]) {
          btn.classList.add("is-end");
          var fin = document.createElement("span");
          fin.className = "quest-maze__tag";
          fin.textContent = "финиш";
          btn.appendChild(fin);
        }
        btn.addEventListener("click", function () {
          if (done) return;
          var k = key(r, c);
          var already = path.indexOf(k);
          if (already >= 0) {
            path = path.slice(0, already + 1);
            paint();
            return;
          }
          if (String(ch) !== String(letter)) {
            btn.classList.add("is-wrong");
            coachReact("wrong", false);
            setTimeout(function () { btn.classList.remove("is-wrong"); }, 450);
            return;
          }
          if (!adjacent(lastPos(), [r, c])) {
            coachReact("try", false);
            return;
          }
          path.push(k);
          paint();
          if (r === end[0] && c === end[1]) finish();
        });
        cells[key(r, c)] = btn;
        wrap.appendChild(btn);
      });
    });
    root().appendChild(wrap);
    paint();
  }

  function renderEnter(station) {
    var box = document.createElement("div");
    box.className = "quest-enter";
    var hint = document.createElement("p");
    hint.className = "quest-hint";
    hint.textContent = station.hint || "Нажми кнопку — войти в страну звуков!";
    var cta = document.createElement("button");
    cta.type = "button";
    cta.className = "quest-enter__cta";
    cta.textContent = station.cta_label || "Войти!";
    cta.addEventListener("click", function () {
      if (cta.disabled) return;
      cta.disabled = true;
      showMsg("Здорово!", true);
      goNext();
    });
    box.appendChild(hint);
    box.appendChild(cta);
    root().appendChild(box);
  }

  function renderMiniQuest(station) {
    var steps = station.steps || [];
    var stepIdx = 0;
    var together = station.show_all_steps === true && steps.length > 1;

    function finishMini(ok) {
      miniSkip = null;
      if (ok) {
        coachReact("good", true);
        enableNext(true);
      } else {
        stationCleared = false;
        goNext();
      }
    }

    function nextStep(ok) {
      if (together) {
        if (ok) finishMini(true);
        else showMsg(station.hint || "Сначала выбери картинку и слог.", false);
        return;
      }
      stepIdx += 1;
      if (stepIdx >= steps.length) finishMini(ok);
      else setTimeout(showStep, ok ? 400 : 0);
    }

    // Trial / early quests: «Дальше» always lets the child skip without a correct answer.
    miniSkip = function () {
      finishMini(false);
    };

    function showStep() {
      var step = steps[stepIdx] || {};
      var stepAudio = Object.prototype.hasOwnProperty.call(step, "audio")
        ? (step.audio || "")
        : (together || stepIdx === 0 ? (station.audio || "") : "");
      var view = {
        slovik_line: together ? station.slovik_line : (step.slovik_line || station.slovik_line),
        slovik_pose: station.slovik_pose,
        scene_image: station.scene_image,
        audio: stepAudio
      };
      openPlayfield(view);
      enableNext(false);
      if (together) {
        var doneMap = {};
        steps.forEach(function (one, i) {
          var block = document.createElement("div");
          block.className = "quest-mini-block";
          if (one.prompt) {
            var prompt = document.createElement("p");
            prompt.className = "quest-mini-block__prompt";
            prompt.textContent = one.prompt;
            block.appendChild(prompt);
          }
          var grid = renderOptions(one.options || [], function (id, btn) {
            if (doneMap[i]) return;
            if (String(id) === String(one.correct)) {
              doneMap[i] = true;
              btn.classList.add("is-correct");
              block.querySelectorAll(".quest-opt").forEach(function (el) {
                if (el !== btn) el.disabled = true;
              });
              var left = steps.filter(function (_, k) { return !doneMap[k]; });
              if (!left.length) finishMini(true);
            } else {
              coachReact("wrong", false);
              checkSingle(one.correct, id, btn);
            }
          }, false, { picture_only: !!one.picture_only });
          block.appendChild(grid);
          root().appendChild(block);
        });
        return;
      }
      var kind = step.kind || "find";
      if (kind === "listen_pick") renderListenPick(step);
      else if (kind === "word_picture") renderWordPicture(step);
      else if (kind === "phrase_picture") renderPhrase(step);
      else if (kind === "shape_rebus") renderShapeRebus(step);
      else if (kind === "path_word") renderPathWord(step);
      else if (kind === "letter_maze") {
        renderLetterMaze(step, function () {
          nextStep(true);
        });
      }
      else {
        // "find" and unknown steps: show image + options grid (not scattered)
        if (step.prompt_text) {
          var findPrompt = document.createElement("p");
          findPrompt.className = "quest-prompt-line";
          findPrompt.textContent = step.prompt_text;
          root().appendChild(findPrompt);
        }
        appendPromptPic(step);
        var grid = renderOptions(step.options || [], function (id, btn) {
          if (String(id) === String(step.correct)) {
            btn.classList.add("is-correct");
            nextStep(true);
          } else {
            coachReact("wrong", false);
            checkSingle(step.correct, id, btn);
          }
        }, false, { picture_only: !!step.picture_only });
        root().appendChild(grid);
      }
      if (kind === "listen_pick" || kind === "word_picture" || kind === "phrase_picture" || kind === "shape_rebus" || kind === "path_word") {
        var check = setInterval(function () {
          if (stationCleared) {
            clearInterval(check);
            btnNext.onclick = function () {
              btnNext.onclick = goNext;
              nextStep(true);
            };
          }
        }, 200);
        setTimeout(function () { clearInterval(check); }, 20000);
      }
    }
    showStep();
  }

  function renderBookPage(station) {
    var field = elBody.querySelector(".quest-playfield");
    if (field) field.classList.add("quest-playfield--book");
    enableNext(false);
    var lines = station.lines || [];
    var pageIdx = 0;
    var flipping = false;
    var FLIP_MS = 780;

    var book = document.createElement("div");
    book.className = "quest-book quest-book--flip";
    book.setAttribute("role", "region");
    book.setAttribute("aria-label", station.book_title || station.book_label || "Книжка");

    var stage = document.createElement("div");
    stage.className = "quest-book__stage";

    var cover = document.createElement("div");
    cover.className = "quest-book__cover";

    var spread = document.createElement("div");
    spread.className = "quest-book__spread";

    var pageArt = document.createElement("div");
    pageArt.className = "quest-book__page quest-book__page--art";
    var artFrame = document.createElement("figure");
    artFrame.className = "quest-book__art";
    var artImg = document.createElement("img");
    artImg.className = "quest-book__art-img";
    artImg.alt = "";
    artFrame.appendChild(artImg);
    pageArt.appendChild(artFrame);

    var pageText = document.createElement("div");
    pageText.className = "quest-book__page quest-book__page--text";
    var eyebrow = document.createElement("p");
    eyebrow.className = "quest-book__eyebrow";
    pageText.appendChild(eyebrow);
    if (station.book_title) {
      var title = document.createElement("h3");
      title.className = "quest-book__title";
      title.textContent = station.book_title;
      pageText.appendChild(title);
    }
    var sentence = document.createElement("p");
    sentence.className = "quest-book__sentence";
    pageText.appendChild(sentence);

    var fullFrame = document.createElement("figure");
    fullFrame.className = "quest-book__full";
    fullFrame.hidden = true;
    var fullImg = document.createElement("img");
    fullImg.className = "quest-book__full-img";
    fullImg.alt = "";
    fullFrame.appendChild(fullImg);

    var leaf = document.createElement("div");
    leaf.className = "quest-book__leaf";
    leaf.setAttribute("aria-hidden", "true");
    var leafFace = document.createElement("div");
    leafFace.className = "quest-book__leaf-face";
    leaf.appendChild(leafFace);

    spread.appendChild(pageArt);
    spread.appendChild(pageText);
    spread.appendChild(fullFrame);
    spread.appendChild(leaf);
    cover.appendChild(spread);
    stage.appendChild(cover);
    book.appendChild(stage);

    var nav = document.createElement("div");
    nav.className = "quest-book__nav";
    var prevBtn = document.createElement("button");
    prevBtn.type = "button";
    prevBtn.className = "quest-book__nav-btn";
    prevBtn.setAttribute("aria-label", "Предыдущая страница");
    prevBtn.textContent = "←";
    var pager = document.createElement("p");
    pager.className = "quest-book__pager";
    var nextBtn = document.createElement("button");
    nextBtn.type = "button";
    nextBtn.className = "quest-book__nav-btn quest-book__nav-btn--next";
    nextBtn.setAttribute("aria-label", "Следующая страница");
    nextBtn.textContent = "→";
    nav.appendChild(prevBtn);
    nav.appendChild(pager);
    nav.appendChild(nextBtn);
    book.appendChild(nav);

    var dots = document.createElement("div");
    dots.className = "quest-book__dots";
    lines.forEach(function (_, i) {
      var dot = document.createElement("button");
      dot.type = "button";
      dot.className = "quest-book__dot";
      dot.setAttribute("aria-label", "Страница " + (i + 1));
      dot.addEventListener("click", function () {
        if (flipping || i === pageIdx) return;
        goTo(i, i > pageIdx ? 1 : -1);
      });
      dots.appendChild(dot);
    });
    book.appendChild(dots);

    var foot = document.createElement("div");
    foot.className = "quest-book__foot";
    var hint = document.createElement("p");
    hint.className = "quest-book__hint";
    hint.textContent = station.read_hint || "Листай страницы и прочитай каждое предложение.";
    foot.appendChild(hint);
    if (station.finale) {
      var finale = document.createElement("p");
      finale.className = "quest-book__finale";
      finale.hidden = true;
      finale.textContent = station.finale;
      foot.appendChild(finale);
    }
    var cta = document.createElement("button");
    cta.type = "button";
    cta.className = "chit-btn chit-btn--primary quest-book__cta";
    cta.textContent = station.cta_label || "Я прочитал!";
    cta.disabled = lines.length > 1;
    cta.addEventListener("click", function () {
      if (cta.disabled) return;
      cta.disabled = true;
      book.classList.add("is-read");
      if (!station.success_msg) coachReact("good", true);
      enableNext(true);
    });
    foot.appendChild(cta);
    book.appendChild(foot);

    function paint(idx) {
      var line = lines[idx] || {};
      var spreadSrc = line.spread_image || line.full_image || "";
      var isFull = !!spreadSrc;
      spread.classList.toggle("is-full-spread", isFull);
      fullFrame.hidden = !isFull;
      pageArt.hidden = isFull;
      pageText.hidden = isFull;
      if (isFull) {
        fullImg.src = assetUrl(spreadSrc);
        fullImg.alt = line.alt || line.text || station.book_title || "";
      } else {
        artImg.src = line.image ? assetUrl(line.image) : "";
        artImg.alt = line.alt || line.text || "";
        artImg.style.display = line.image ? "" : "none";
        sentence.textContent = line.text || line || "";
      }
      eyebrow.textContent =
        (station.book_label || "Книжка") + " · " + (idx + 1) + " / " + Math.max(lines.length, 1);
      pager.textContent = (idx + 1) + " из " + Math.max(lines.length, 1);
      prevBtn.disabled = idx <= 0;
      nextBtn.disabled = idx >= lines.length - 1;
      Array.prototype.forEach.call(dots.children, function (dot, i) {
        dot.classList.toggle("is-active", i === idx);
        dot.classList.toggle("is-done", i < idx);
      });
      if (idx >= lines.length - 1) {
        cta.disabled = false;
        hint.textContent = station.finale || "Ура, история прочитана!";
        var finaleEl = foot.querySelector(".quest-book__finale");
        if (finaleEl) finaleEl.hidden = false;
      } else {
        cta.disabled = lines.length > 1;
        hint.textContent = station.read_hint || "Листай страницы и прочитай каждое предложение.";
        var finaleHide = foot.querySelector(".quest-book__finale");
        if (finaleHide) finaleHide.hidden = true;
      }
    }

    function goTo(idx, dir) {
      if (flipping) return;
      idx = Math.max(0, Math.min(lines.length - 1, idx));
      if (idx === pageIdx) return;
      flipping = true;
      leaf.classList.remove("is-turn-next", "is-turn-prev");
      void leaf.offsetWidth;
      leaf.classList.add(dir >= 0 ? "is-turn-next" : "is-turn-prev");
      setTimeout(function () {
        pageIdx = idx;
        paint(pageIdx);
      }, Math.floor(FLIP_MS * 0.45));
      setTimeout(function () {
        leaf.classList.remove("is-turn-next", "is-turn-prev");
        flipping = false;
      }, FLIP_MS);
    }

    prevBtn.addEventListener("click", function () {
      goTo(pageIdx - 1, -1);
    });
    nextBtn.addEventListener("click", function () {
      goTo(pageIdx + 1, 1);
    });

    paint(0);
    root().appendChild(book);
  }

  function appendNextPaths(box, paths) {
    if (!paths || !paths.length) return;
    var wrap = document.createElement("div");
    wrap.className = "quest-reward__next";
    var heading = document.createElement("p");
    heading.className = "quest-reward__next-title";
    heading.textContent = "Куда дальше?";
    wrap.appendChild(heading);
    var row = document.createElement("div");
    row.className = "quest-reward__next-row";
    paths.forEach(function (item) {
      if (!item) return;
      var card = document.createElement("div");
      card.className = "quest-reward__next-card";
      if (item.eyebrow) {
        var eye = document.createElement("p");
        eye.className = "quest-reward__next-eye";
        eye.textContent = item.eyebrow;
        card.appendChild(eye);
      }
      if (item.text) {
        var text = document.createElement("p");
        text.className = "quest-reward__next-text";
        text.textContent = item.text;
        card.appendChild(text);
      }
      if (item.cta) {
        var href = resolveLessonLink(item);
        if (href) {
          var link = document.createElement("a");
          link.className = "quest-reward__link quest-reward__link--next";
          link.href = href;
          link.textContent = item.cta;
          card.appendChild(link);
        }
      }
      row.appendChild(card);
    });
    wrap.appendChild(row);
    box.appendChild(wrap);
  }

  function renderReward(station) {
    var field = elBody.querySelector(".quest-playfield");
    if (field) field.classList.add("quest-playfield--reward");
    var earned = allSparksEarned();
    var spark = document.createElement("img");
    spark.className = "quest-spark-fly" + (earned ? "" : " is-dim");
    spark.src = assetUrl(station.spark_image || "/static/early/letters/spark.png");
    spark.alt = "Искорка";
    var box = document.createElement("div");
    box.className = "quest-reward";
    box.appendChild(spark);
    var title = document.createElement("strong");
    title.textContent = earned ? "Ура!" : (station.fail_title || "Ещё чуть-чуть");
    box.appendChild(title);
    if (!earned) {
      var line = document.createElement("p");
      line.className = "quest-reward__lead";
      line.textContent = station.fail_line || "Искорки ещё не все. Пройди задания ещё раз.";
      box.appendChild(line);
    }
    if (earned && station.parent_note) {
      var note = document.createElement("p");
      note.className = "quest-reward__note";
      note.textContent = station.parent_note;
      box.appendChild(note);
    }
    var links = document.createElement("div");
    links.className = "quest-reward__links";
    var chestHref = cfg.chestUrl || "";
    if (!chestHref && cfg.progressUrl) {
      chestHref = cfg.progressUrl + (String(cfg.progressUrl).indexOf("?") >= 0 ? "&" : "?") + "chest=" + encodeURIComponent(cfg.taleSlug || cfg.slug || "");
    }
    if (earned && chestHref) {
      var chestLink = document.createElement("a");
      chestLink.className = "quest-reward__link quest-reward__link--chest";
      chestLink.href = chestHref;
      var chestIcon = document.createElement("img");
      chestIcon.className = "quest-reward__chest-icon";
      chestIcon.src = assetUrl("/static/chest/chest-closed.png");
      chestIcon.alt = "";
      chestLink.appendChild(chestIcon);
      chestLink.appendChild(document.createTextNode(station.chest_cta || "Открыть сундук"));
      links.appendChild(chestLink);
    }
    if (incompleteIndices().length) {
      var retry = document.createElement("button");
      retry.type = "button";
      retry.className = "quest-reward__link quest-reward__link--retry";
      retry.textContent = station.retry_cta || "Пройти ещё раз";
      retry.addEventListener("click", retryIncomplete);
      links.insertBefore(retry, links.firstChild);
    }
    if (station.module_url) {
      var moduleLink = document.createElement("a");
      moduleLink.className = "quest-reward__link quest-reward__link--quiet";
      moduleLink.href = station.module_url;
      moduleLink.target = "_blank";
      moduleLink.rel = "noopener";
      moduleLink.textContent = station.module_cta || "О модуле и записи";
      links.appendChild(moduleLink);
    }
    if (links.childNodes.length) box.appendChild(links);
    if (earned) appendNextPaths(box, station.next_paths || []);
    root().appendChild(box);
    if (btnNext) btnNext.hidden = true;
    if (btnAudio) btnAudio.hidden = true;
    bindFinishButton();
    completeLesson();
  }

  function renderListenRounds(station) {
    var rIdx = 0;
    function showR() {
      openPlayfield(station);
      enableNext(false);
      selected = [];
      renderListenPick(station, station.rounds[rIdx]);
      var checker = setInterval(function () {
        if (stationCleared) {
          clearInterval(checker);
          btnNext.onclick = function () {
            rIdx += 1;
            if (rIdx >= station.rounds.length) {
              btnNext.onclick = goNext;
              goNext();
            } else {
              btnNext.onclick = goNext;
              showR();
            }
          };
        }
      }, 150);
      setTimeout(function () { clearInterval(checker); }, 30000);
    }
    showR();
  }

  function render() {
    var station = stations[idx];
    if (!station) {
      parkFooter();
      elBody.innerHTML = "<p>Станции урока пока готовятся.</p>";
      return;
    }
    updateProgress();
    stationCleared = false;
    miniSkip = null;
    enableNext(false);
    elTitle.textContent = station.chapter || station.title || ("Станция " + (idx + 1));
    if (elLine) elLine.textContent = "";

    var kind = station.kind || "find";
    var playView = kind === "reward" ? rewardSpeakView(station) : station;
    if (playView.slovik_pose) setSlovikPose(playView.slovik_pose);
    var board = document.querySelector(".quest-board");
    if (board) board.classList.toggle("quest-board--reward", kind === "reward");

    if (kind === "intro_video") {
      renderIntroVideo(station);
    } else {
      setIntroMode(false);
    }

    if (kind === "find") {
      renderFind(station);
    } else if (kind === "word_picture") {
      renderWordPicture(station);
    } else if (kind === "mini_quest") {
      renderMiniQuest(station);
    } else if (kind === "listen_pick" && station.rounds && station.rounds.length > 1) {
      renderListenRounds(station);
    } else if (kind !== "intro_video") {
      openPlayfield(playView);
      if (kind === "enter") {
        renderEnter(station);
      } else if (kind === "break") {
        var h = document.createElement("p");
        h.className = "quest-hint";
        h.textContent = station.hint || "Отойди от экрана на минутку.";
        root().appendChild(h);
        enableNext(true);
      } else if (kind === "reward") {
        renderReward(station);
      } else if (kind === "repeat_sound") {
        renderEcho(station);
      } else if (kind === "meet_letter") {
        renderMeetLetter(station);
      } else if (kind === "build_letter") {
        renderBuildLetter(station);
      } else if (kind === "catch_letter") {
        renderCatchLetter(station);
      } else if (kind === "letter_maze") {
        renderLetterMaze(station);
      } else if (kind === "scene_hunt") {
        renderSceneHunt(station);
      } else if (kind === "drag_basket") {
        renderDragBasket(station);
      } else if (kind === "sort_two") {
        renderSortTwo(station);
      } else if (kind === "letter_puzzle") {
        renderLetterPuzzle(station);
      } else if (kind === "slot_build") {
        renderSlotBuild(station);
      } else if (kind === "listen_pick") {
        renderListenPick(station);
      } else if (kind === "trace") {
        renderTrace(station);
      } else if (kind === "drag_join") {
        renderJoin(station);
      } else if (kind === "match_pairs") {
        renderMatchPairs(station);
      } else if (kind === "phrase_picture") {
        renderPhrase(station);
      } else if (kind === "shape_rebus") {
        renderShapeRebus(station);
      } else if (kind === "path_word") {
        renderPathWord(station);
      } else if (kind === "book_page") {
        renderBookPage(station);
      } else {
        var p = document.createElement("p");
        p.className = "quest-hint";
        p.textContent = "Станция: " + kind;
        root().appendChild(p);
        enableNext(true);
      }
    }

    if (btnAudio) {
      btnAudio.onclick = function () { speakTask(playView); };
      btnAudio.hidden = kind === "intro_video" || kind === "reward";
      if (!btnAudio.hidden) btnAudio.textContent = "Послушать Словика";
    }
    if (btnNext && kind === "reward") {
      btnNext.hidden = true;
    } else if (btnNext && kind !== "intro_video") {
      btnNext.onclick = onNextClick;
      btnNext.textContent = "Дальше";
    }
  }

  if (!stations.length) {
    elBody.innerHTML = "<p>Станции урока пока готовятся.</p>";
  } else {
    render();
  }
})();
