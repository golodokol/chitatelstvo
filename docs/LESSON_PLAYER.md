# Плеер урока — автоматические баллы

Видео и квизы засчитываются **сами**. Творчество и живая встреча — **кнопки для родителя** внизу урока.

---

## Что автоматизировано

| Шаг | Событие | Как засчитывается |
|-----|---------|-------------------|
| Видео ≥50% | `lesson_complete` | **Kinescope** / **Yandex** / HTML5 |
| Квиз «Понимание» | `comprehension` | ≥4 из 5 правильных |
| Квиз «Смысл» | `meaning_analysis` | ≥2 из 3 правильных |
| Творческое | `creative_task` | Кнопка родителя |
| Встреча | `live_meeting` | Кнопка родителя |

Старые webhook-события `lesson_complete`, `comprehension`, `meaning_analysis` **заблокированы** — только через плеер.

---

## Открытие уроков по неделям

Каждый файл `lessons/{сказка}.json` содержит поле **`module_week`** (1, 2, 3, 4…).

| Неделя | Когда открывается |
|--------|-------------------|
| 1 | **Понедельник старта модуля** (`MODULE_START_DATE`) |
| 2 | +7 дней (следующий понедельник) |
| 3 | +14 дней |
| 4 | +21 день |

В `.env` укажите **один понедельник для всего набора**:

```env
MODULE_START_DATE=2026-06-15
LESSON_WEEK_DAYS=7
```

Если `MODULE_START_DATE` не задан — старт = понедельник недели регистрации ребёнка (по одному).

До даты старта все уроки закрыты (кроме досрочного `module_week > 1` в БД).

**На странице прогресса:** открытые уроки — кнопки, закрытые — «с ДД.ММ.ГГГГ».

**Досрочное открытие:** в БД у ребёнка поле `module_week` (через webhook или SQL). Если поставить `3`, откроются недели 1–3 раньше календаря.

Логика: `lessons/access.py`.

---

## Ссылка на урок

Генерируется автоматически на странице прогресса `/progress/{token}` (только для **открытых** недель).

Формат:

```
https://ВАШ_ДОМЕН/lesson/kolobok?child=UUID&exp=TIMESTAMP&sig=HMAC
```

Подпись: `LESSON_SIGNING_SECRET` (по умолчанию = `WEBHOOK_SECRET`).

---

## Настройка видео (РФ без VPN)

### Kinescope — рекомендуется

1. Загрузите ролик в [kinescope.ru](https://kinescope.ru/)
2. Скопируйте ID видео из URL (`https://kinescope.io/XXXX`)
3. В `lessons/kolobok.json`:

```json
"video": {
  "type": "kinescope",
  "id": "ВАШ_ID_KINESCOPE",
  "title": "Сказка «Колобок»"
}
```

Плеер использует [IFrame Player API](https://docs.kinescope.ru/instrukcii-dlya-razrabotchikov/iframe-player-api/) — событие `TimeUpdate` с `percent` для автоматических баллов.

### Yandex Object Storage — резерв

**Вариант A — публичный бакет:**

```json
"video": {
  "type": "yandex",
  "src": "https://storage.yandexcloud.net/ВАШ_БАКЕТ/lessons/kolobok.mp4",
  "title": "Сказка «Колобок»"
}
```

**Вариант B — приватный бакет (presigned URL):**

```json
"video": {
  "type": "yandex",
  "object_key": "lessons/kolobok.mp4",
  "presign": true,
  "title": "Сказка «Колобок»"
}
```

В `.env`:

```env
YANDEX_ACCESS_KEY=...
YANDEX_SECRET_KEY=...
YANDEX_BUCKET=literary-school-videos
YANDEX_ENDPOINT=https://storage.yandexcloud.net
```

Пример: `lessons/kolobok.yandex.example.json`

### Другие типы (не для РФ)

`youtube`, `vimeo`, `html5` — оставлены для совместимости, в РФ не рекомендуются.

Порог просмотра: `VIDEO_WATCH_THRESHOLD=0.5` в `.env` (50% длительности).

---

## Добавить новую сказку

1. Скопируйте `lessons/kolobok.json` → `lessons/repka.json`
2. Измените slug, title, video, вопросы
3. Урок появится на странице прогресса автоматически

---

## API (для отладки)

| Метод | URL |
|-------|-----|
| GET | `/lesson/{slug}?child=&exp=&sig=` |
| POST | `/api/lesson/{slug}/video-complete` |
| POST | `/api/lesson/{slug}/quiz` |
| POST | `/api/lesson/{slug}/manual` |

Тело POST всегда содержит: `child_id`, `exp`, `sig` + данные шага.

---

## Tilda

На странице урока в Tilda — одна кнопка:

**`Открыть интерактивный урок`**

Ссылка ведёт на страницу прогресса родителя (там кнопки уроков)  
или напрямую на `/lesson/kolobok?...` из письма после регистрации.

Форму «отметить задание» для видео и квизов **уберите** — они больше не нужны.

---

## Запуск

```powershell
uvicorn api.main:app --reload --port 8000
python worker/run_worker.py
```

Откройте страницу прогресса → кнопка «Колобок».
