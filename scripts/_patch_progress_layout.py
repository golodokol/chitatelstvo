from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates" / "progress.html"
t = p.read_text(encoding="utf-8")

old_loop = """        {% if cab.tracks %}
          {% set multi_track_treasury = cab.tracks|length > 1 and cab.treasury %}
          {% if multi_track_treasury %}
          <section class="chit-panel chit-panel--treasury" id="treasury-all">
            <h2 class="chit-section-title">Моя сокровищница</h2>
            <p class="chit-section-sub">Творческие задания из всех открытых сундуков — можно скачать снова.</p>
            <div class="chit-treasury" data-treasury>
              <div class="chit-treasury-grid">
                {% for item in cab.treasury %}
                <article class="chit-treasury-item"
                  role="button"
                  tabindex="0"
                  data-treasury-preview
                  data-label="{{ item.label }}"
                  data-caption="{{ item.lesson_caption or ('Урок «' ~ item.tale_title ~ '»') }}"
                  data-image="{{ item.image_url or '' }}"
                  data-download="{{ item.download_url if item.downloadable and item.download_url else '' }}"
                  data-download-name="{{ item.download_name or '' }}"
                  data-kind="{{ item.kind or '' }}"
                  data-tale-slug="{{ item.tale_slug or '' }}">
                  {% if item.image_url %}<img src="{{ item.image_url }}" alt="" loading="lazy">{% endif %}
                  <strong>{{ item.label }}</strong>
                  <span>{{ item.lesson_caption or ('Урок «' ~ item.tale_title ~ '»') }}</span>
                </article>
                {% endfor %}
              </div>
              <nav class="chit-treasury-pager" data-treasury-pager hidden aria-label="Страницы сокровищницы">
                <button type="button" class="chit-treasury-pager__btn" data-treasury-prev aria-label="Предыдущая страница">‹</button>
                <span class="chit-treasury-pager__label" data-treasury-label></span>
                <button type="button" class="chit-treasury-pager__btn" data-treasury-next aria-label="Следующая страница">›</button>
              </nav>
            </div>
          </section>
          {% endif %}
          {% for track in cab.tracks %}
          {{ render_chest(track, child, loop.index, '#treasury-all' if multi_track_treasury else none) }}
          {{ render_weekly_lessons(track) }}
          {% if not multi_track_treasury %}
          {{ render_treasury(track, loop.index) }}
          {% endif %}"""

new_loop = """        {% if cab.tracks %}
          <section class="chit-panel chit-panel--treasury" id="treasury-all">
            <h2 class="chit-section-title">Моя сокровищница</h2>
            <p class="chit-section-sub">Единая копилка наград из всех уроков — можно скачать снова.</p>
            {% if cab.treasury %}
            <div class="chit-treasury" data-treasury>
              <div class="chit-treasury-grid">
                {% for item in cab.treasury %}
                <article class="chit-treasury-item"
                  role="button"
                  tabindex="0"
                  data-treasury-preview
                  data-label="{{ item.label }}"
                  data-caption="{{ item.lesson_caption or ('Урок «' ~ item.tale_title ~ '»') }}"
                  data-image="{{ item.image_url or '' }}"
                  data-download="{{ item.download_url if item.downloadable and item.download_url else '' }}"
                  data-download-name="{{ item.download_name or '' }}"
                  data-kind="{{ item.kind or '' }}"
                  data-tale-slug="{{ item.tale_slug or '' }}">
                  {% if item.image_url %}<img src="{{ item.image_url }}" alt="" loading="lazy">{% endif %}
                  <strong>{{ item.label }}</strong>
                  <span>{{ item.lesson_caption or ('Урок «' ~ item.tale_title ~ '»') }}</span>
                </article>
                {% endfor %}
              </div>
              <nav class="chit-treasury-pager" data-treasury-pager hidden aria-label="Страницы сокровищницы">
                <button type="button" class="chit-treasury-pager__btn" data-treasury-prev aria-label="Предыдущая страница">‹</button>
                <span class="chit-treasury-pager__label" data-treasury-label></span>
                <button type="button" class="chit-treasury-pager__btn" data-treasury-next aria-label="Следующая страница">›</button>
              </nav>
            </div>
            {% else %}
            <p class="chit-treasury-empty">Открой сундук ниже — награды появятся здесь.</p>
            {% endif %}
          </section>
          {% for track in cab.tracks %}
          {{ render_weekly_lessons(track) }}
          {{ render_chest(track, child, loop.index, '#treasury-all') }}"""

old_legacy = """        {{ render_weekly_lessons(legacy_track) }}
        {{ render_chest(legacy_track, child, loop.index) }}
        {{ render_treasury(legacy_track, loop.index) }}"""

new_legacy = """        <section class="chit-panel chit-panel--treasury" id="treasury-all">
          <h2 class="chit-section-title">Моя сокровищница</h2>
          <p class="chit-section-sub">Единая копилка наград из всех уроков — можно скачать снова.</p>
          {% if cab.treasury and cab.chest.claimed %}
          <div class="chit-treasury" data-treasury>
            <div class="chit-treasury-grid">
              {% for item in cab.treasury %}
              <article class="chit-treasury-item"
                role="button"
                tabindex="0"
                data-treasury-preview
                data-label="{{ item.label }}"
                data-caption="{{ item.lesson_caption or ('Урок «' ~ item.tale_title ~ '»') }}"
                data-image="{{ item.image_url or '' }}"
                data-download="{{ item.download_url if item.downloadable and item.download_url else '' }}"
                data-download-name="{{ item.download_name or '' }}"
                data-kind="{{ item.kind or '' }}"
                data-tale-slug="{{ item.tale_slug or '' }}">
                {% if item.image_url %}<img src="{{ item.image_url }}" alt="" loading="lazy">{% endif %}
                <strong>{{ item.label }}</strong>
                <span>{{ item.lesson_caption or ('Урок «' ~ item.tale_title ~ '»') }}</span>
              </article>
              {% endfor %}
            </div>
          </div>
          {% else %}
          <p class="chit-treasury-empty">Открой сундук ниже — награды появятся здесь.</p>
          {% endif %}
        </section>
        {{ render_weekly_lessons(legacy_track) }}
        {{ render_chest(legacy_track, child, 1, '#treasury-all') }}"""

old_weekly_head = """        <section class="chit-panel chit-panel--mission">
          <h2 class="chit-section-title">{{ track.weekly_lessons_label or 'Сказка этой недели' }}</h2>
          {% if track.group_label %}
          <p class="chit-section-sub">{{ track.group_label }}</p>
          {% endif %}
          {% for weekly in track.weekly_lessons %}"""

new_weekly_head = """        <section class="chit-panel chit-panel--mission">
          <h2 class="chit-section-title">{{ track.weekly_lessons_label or 'Урок этой недели' }}</h2>
          {% if track.group_label %}
          <p class="chit-section-sub">{{ track.group_label }}</p>
          {% endif %}
          {% set current_lesson = track.weekly_lessons[0] %}
          {% if current_lesson and (current_lesson.headline or current_lesson.title) %}
          <p class="chit-current-lesson-name">{{ current_lesson.headline or current_lesson.title }}</p>
          {% endif %}
          {% for weekly in track.weekly_lessons %}"""

changes = []
if old_loop in t:
    t = t.replace(old_loop, new_loop, 1)
    changes.append("loop")
else:
    raise SystemExit("OLD LOOP NOT FOUND")

if old_legacy in t:
    t = t.replace(old_legacy, new_legacy, 1)
    changes.append("legacy")
else:
    raise SystemExit("LEGACY NOT FOUND")

if old_weekly_head in t:
    t = t.replace(old_weekly_head, new_weekly_head, 1)
    changes.append("weekly")
else:
    raise SystemExit("WEEKLY HEAD NOT FOUND")

t = t.replace(
    "Открой сундук выше — награды появятся здесь.",
    "Открой сундук ниже — награды появятся здесь.",
)

p.write_text(t, encoding="utf-8")
print("patched:", ", ".join(changes))
