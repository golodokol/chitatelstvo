(function () {
  var cfg = window.CHIT_QUEST || {};
  var stations = Array.isArray(cfg.stations) ? cfg.stations : [];
  var idx = 0;
  var sparks = 0;
  var goalCount = (cfg.quest && cfg.quest.goal_count) || 3;
  var selected = [];
  var audio = new Audio();

  var elTitle = document.getElementById("quest-station-title");
  var elLine = document.getElementById("quest-slovik-line");
  var elBody = document.getElementById("quest-body");
  var elMsg = document.getElementById("quest-msg");
  var elFill = document.getElementById("quest-progress-fill");
  var elLabel = document.getElementById("quest-progress-label");
  var elSparks = document.getElementById("quest-sparks");
  var btnNext = document.getElementById("quest-btn-next");
  var btnAudio = document.getElementById("quest-btn-audio");

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

  function audioUrl(id) {
    if (!id) return "";
    if (String(id).indexOf("/") === 0 || String(id).indexOf("http") === 0) return id;
    var base = (cfg.assetsBase || "").replace(/\/$/, "");
    return base + "/static/early/audio/" + id + ".mp3";
  }

  function playId(id) {
    var url = audioUrl(id);
    if (!url) return;
    try {
      audio.pause();
      audio.src = url;
      audio.play().catch(function () {});
    } catch (e) {}
  }

  function updateProgress() {
    var total = Math.max(stations.length, 1);
    var pct = Math.round(((idx + 1) / total) * 100);
    if (elFill) elFill.style.width = pct + "%";
    if (elLabel) {
      var st = stations[idx];
      elLabel.textContent = "Станция " + (idx + 1) + " из " + total + (st && st.title ? " · " + st.title : "");
    }
    if (elSparks) {
      var label = (cfg.quest && cfg.quest.goal_label) || "искорки";
      elSparks.textContent = "Собрано: " + sparks + " / " + goalCount + " (" + label + ")";
    }
  }

  function enableNext(show) {
    if (!btnNext) return;
    btnNext.hidden = !show;
  }

  function awardSpark(station) {
    if (station && station.spark) sparks += 1;
    updateProgress();
  }

  function completeLesson() {
    fetch("/api/lesson/" + encodeURIComponent(cfg.slug) + "/quest-complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(authBody({ sparks: sparks })),
    })
      .then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function () {
        showMsg("Урок пройден! Можно вернуться к странице уроков.", true);
        enableNext(true);
        btnNext.textContent = "К странице уроков";
        btnNext.onclick = function () {
          window.location.href = cfg.progressUrl || "/";
        };
      })
      .catch(function () {
        showMsg("Урок почти готов. Можно вернуться назад.", true);
        enableNext(true);
        btnNext.textContent = "К странице уроков";
        btnNext.onclick = function () {
          window.location.href = cfg.progressUrl || "/";
        };
      });
  }

  function goNext() {
    var cur = stations[idx];
    awardSpark(cur);
    if (idx >= stations.length - 1) {
      completeLesson();
      return;
    }
    idx += 1;
    selected = [];
    if (elMsg) elMsg.style.display = "none";
    render();
  }

  function renderOptions(options, onPick, multi) {
    var grid = document.createElement("div");
    grid.className = "quest-grid";
    (options || []).forEach(function (opt) {
      var id = typeof opt === "string" ? opt : opt.id;
      var label = typeof opt === "string" ? opt : (opt.label || opt.id);
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "quest-opt";
      btn.dataset.id = id;
      if (opt && opt.image) {
        var img = document.createElement("img");
        img.src = opt.image;
        img.alt = label;
        img.onerror = function () { img.style.display = "none"; };
        btn.appendChild(img);
      }
      var span = document.createElement("span");
      span.className = /[A-Za-zА-Яа-яЁё]/.test(label) && label.length <= 3 ? "quest-letter" : "";
      span.textContent = label;
      btn.appendChild(span);
      btn.addEventListener("click", function () {
        if (opt && opt.word_audio) playId(opt.word_audio);
        onPick(id, btn, multi);
      });
      grid.appendChild(btn);
    });
    return grid;
  }

  function checkSingle(correct, picked, btn) {
    var ok = String(picked) === String(correct) ||
      (Array.isArray(correct) && correct.indexOf(picked) >= 0);
    document.querySelectorAll(".quest-opt").forEach(function (el) {
      el.disabled = true;
    });
    if (ok) {
      btn.classList.add("is-correct");
      showMsg("Да! Ты смог!", true);
      enableNext(true);
    } else {
      btn.classList.add("is-wrong");
      showMsg("Попробуй ещё раз. Я рядом.", false);
      setTimeout(function () {
        document.querySelectorAll(".quest-opt").forEach(function (el) {
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
      elBody.appendChild(play);
    }
    elBody.appendChild(renderOptions(r.options || [], function (id, btn, multi) {
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
            showMsg("Да! Ты смог!", true);
            enableNext(true);
          } else {
            showMsg("Почти! Давай ещё разочек.", false);
            selected = [];
            document.querySelectorAll(".quest-opt").forEach(function (el) { el.classList.remove("is-selected"); });
          }
        }
      } else {
        checkSingle(r.correct, id, btn);
      }
    }, station.multi));
  }

  function renderFind(station) {
    var rounds = station.rounds || [station];
    var roundIdx = 0;
    function showRound() {
      elBody.innerHTML = "";
      selected = [];
      enableNext(false);
      var r = rounds[roundIdx];
      if (r.sound) playId(r.sound);
      if (r.prompt_audio) playId(r.prompt_audio);
      elBody.appendChild(renderOptions(r.options || [], function (id, btn) {
        var ok = String(id) === String(r.correct);
        if (ok) {
          btn.classList.add("is-correct");
          roundIdx += 1;
          if (roundIdx >= rounds.length) {
            showMsg("Нашёл!", true);
            enableNext(true);
          } else {
            showMsg("Ещё раунд!", true);
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
    elBody.appendChild(canvas);
    var letter = document.createElement("p");
    letter.className = "quest-letter";
    letter.style.textAlign = "center";
    letter.textContent = station.letter || "А";
    elBody.appendChild(letter);
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
        showMsg("Буква зажглась!", true);
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

  function renderJoin(station) {
    var wrap = document.createElement("div");
    wrap.className = "quest-join";
    var left = document.createElement("button");
    left.type = "button";
    left.className = "quest-join__chip";
    left.textContent = (station.left && station.left.label) || "М";
    var arrow = document.createElement("span");
    arrow.textContent = "→";
    var right = document.createElement("button");
    right.type = "button";
    right.className = "quest-join__chip";
    right.textContent = (station.right && station.right.label) || "А";
    wrap.appendChild(left);
    wrap.appendChild(arrow);
    wrap.appendChild(right);
    elBody.appendChild(wrap);
    var joined = false;
    function join() {
      if (joined) return;
      joined = true;
      left.classList.add("is-done");
      right.classList.add("is-done");
      if (station.result && station.result.sound) playId(station.result.sound);
      var res = document.createElement("p");
      res.className = "quest-letter";
      res.style.textAlign = "center";
      res.textContent = (station.result && station.result.label) || "МА";
      elBody.appendChild(res);
      showMsg("Получилось!", true);
      enableNext(true);
    }
    left.addEventListener("click", function () {
      if (station.left && station.left.sound) playId(station.left.sound);
      join();
    });
    right.addEventListener("click", function () {
      if (station.right && station.right.sound) playId(station.right.sound);
      join();
    });
  }

  function renderWordPicture(station) {
    var items = station.items || [station];
    var itemIdx = 0;
    function showItem() {
      elBody.innerHTML = "";
      enableNext(false);
      var item = items[itemIdx];
      var word = document.createElement("p");
      word.className = "quest-letter";
      word.style.textAlign = "center";
      word.textContent = item.word || station.word || "";
      elBody.appendChild(word);
      if (item.audio) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "chit-btn";
        b.textContent = "▶ Слушать слово";
        b.addEventListener("click", function () { playId(item.audio); });
        elBody.appendChild(b);
      }
      elBody.appendChild(renderOptions(item.options || [], function (id, btn) {
        if (String(id) === String(item.correct)) {
          btn.classList.add("is-correct");
          itemIdx += 1;
          if (itemIdx >= items.length) {
            showMsg("Слово нашло картинку!", true);
            enableNext(true);
          } else {
            setTimeout(showItem, 450);
          }
        } else {
          checkSingle(item.correct, id, btn);
        }
      }));
    }
    showItem();
  }

  function renderPhrase(station) {
    var word = document.createElement("p");
    word.className = "quest-letter";
    word.style.textAlign = "center";
    word.style.fontSize = "1.6rem";
    word.textContent = station.phrase || "";
    elBody.appendChild(word);
    if (station.phrase_audio) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "chit-btn";
      b.textContent = "▶ Слушать фразу";
      b.addEventListener("click", function () { playId(station.phrase_audio); });
      elBody.appendChild(b);
    }
    elBody.appendChild(renderOptions(station.options || [], function (id, btn) {
      checkSingle(station.correct, id, btn);
    }));
  }

  function renderMiniQuest(station) {
    var steps = station.steps || [];
    var stepIdx = 0;
    function showStep() {
      elBody.innerHTML = "";
      enableNext(false);
      var step = steps[stepIdx] || {};
      var kind = step.kind || "find";
      if (kind === "listen_pick") renderListenPick(step);
      else if (kind === "word_picture") renderWordPicture(step);
      else if (kind === "phrase_picture") renderPhrase(step);
      else {
        elBody.appendChild(renderOptions(step.options || [], function (id, btn) {
          if (String(id) === String(step.correct)) {
            btn.classList.add("is-correct");
            stepIdx += 1;
            if (stepIdx >= steps.length) {
              showMsg("Сундук открывается!", true);
              enableNext(true);
            } else {
              setTimeout(showStep, 400);
            }
          } else {
            checkSingle(step.correct, id, btn);
          }
        }));
      }
      // For nested renderers that call enableNext themselves on success of whole block:
      var orig = enableNext;
      // When nested kinds finish, advance mini-quest steps
      if (kind === "listen_pick" || kind === "word_picture" || kind === "phrase_picture") {
        var check = setInterval(function () {
          if (!btnNext.hidden) {
            clearInterval(check);
            btnNext.onclick = function () {
              stepIdx += 1;
              btnNext.onclick = goNext;
              if (stepIdx >= steps.length) {
                showMsg("Готово!", true);
                enableNext(true);
              } else {
                showStep();
              }
            };
          }
        }, 200);
        setTimeout(function () { clearInterval(check); }, 20000);
      }
    }
    showStep();
  }

  function render() {
    var station = stations[idx];
    if (!station) {
      elBody.innerHTML = "<p>Станции урока пока готовятся.</p>";
      return;
    }
    updateProgress();
    enableNext(false);
    elTitle.textContent = station.title || ("Станция " + (idx + 1));
    elLine.textContent = station.slovik_line || "";
    elBody.innerHTML = "";
    if (station.audio) playId(station.audio);

    var kind = station.kind || "find";
    if (kind === "intro_video") {
      var p = document.createElement("p");
      p.className = "quest-hint";
      p.textContent = "Короткое приключение начинается. Нажми «Дальше», когда будешь готов.";
      elBody.appendChild(p);
      enableNext(true);
    } else if (kind === "break") {
      var h = document.createElement("p");
      h.className = "quest-hint";
      h.textContent = station.hint || "Отойди от экрана на минутку.";
      elBody.appendChild(h);
      enableNext(true);
    } else if (kind === "reward") {
      var box = document.createElement("div");
      box.className = "quest-reward";
      box.innerHTML = "<strong>Ура!</strong><p>" + (station.slovik_line || "Молодец!") + "</p>";
      if (station.parent_note) {
        var note = document.createElement("p");
        note.className = "quest-hint";
        note.textContent = station.parent_note;
        box.appendChild(note);
      }
      elBody.appendChild(box);
      enableNext(true);
      btnNext.textContent = "Завершить";
    } else if (kind === "repeat_sound") {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "chit-btn";
      b.textContent = "▶ Послушать звук";
      b.addEventListener("click", function () { playId(station.sound); });
      elBody.appendChild(b);
      var done = document.createElement("button");
      done.type = "button";
      done.className = "chit-btn chit-btn--primary";
      done.textContent = "Я повторил!";
      done.addEventListener("click", function () {
        showMsg("Слышу!", true);
        enableNext(true);
      });
      elBody.appendChild(done);
    } else if (kind === "listen_pick") {
      // multi-round support
      if (station.rounds && station.rounds.length > 1) {
        var rIdx = 0;
        function showR() {
          elBody.innerHTML = "";
          enableNext(false);
          renderListenPick(station, station.rounds[rIdx]);
          var checker = setInterval(function () {
            if (!btnNext.hidden) {
              clearInterval(checker);
              var old = btnNext.onclick;
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
      } else {
        renderListenPick(station);
      }
    } else if (kind === "find") renderFind(station);
    else if (kind === "trace") renderTrace(station);
    else if (kind === "drag_join") renderJoin(station);
    else if (kind === "word_picture") renderWordPicture(station);
    else if (kind === "phrase_picture") renderPhrase(station);
    else if (kind === "mini_quest") renderMiniQuest(station);
    else {
      elBody.innerHTML = "<p class='quest-hint'>Станция: " + kind + "</p>";
      enableNext(true);
    }

    if (btnAudio) {
      btnAudio.onclick = function () { playId(station.audio); };
      btnAudio.hidden = !station.audio;
    }
    if (btnNext && kind !== "mini_quest") {
      btnNext.onclick = goNext;
      if (kind === "reward") btnNext.textContent = "Завершить";
      else btnNext.textContent = "Дальше";
    }
  }

  if (!stations.length) {
    elBody.innerHTML = "<p>Станции урока пока готовятся.</p>";
  } else {
    render();
  }
})();
