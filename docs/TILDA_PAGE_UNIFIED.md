# Tilda: одна страница записи (класс + тариф + опции)

Одной страницы достаточно. **18 отдельных лендингов не нужны** — они были «шаблоном на каждый модуль», если делать отдельные рекламные URL. Ваш вариант проще для родителя и для вас.

**API:** `https://api.chitatelstvo.ru/webhook/register`  
**Рекомендуемый URL страницы:** `https://chitatelstvo.ru/zapis`

**Красивый макет (Business + Zero Block):** `docs/TILDA_ZAPIS_DESIGN.md` · код: `docs/tilda_zero_zapis.html`

---

## Что должно уйти в webhook

| Поле | Когда нужно |
|------|-------------|
| `parent_name`, `parent_email`, `child_name`, … | всегда |
| `module_id` | **всегда** (число 1–18) |
| `chosen_stage` | **все тарифы** — период `1` (29 июня) или `2` (20 июля) |
| `chosen_tale_number` | только **разовое** занятие (`1`–`4`) |

Без `module_id` — режим пилота (только «Колобок»). Для новых модулей `module_id` обязателен.

---

## Схема формы на одной странице

```
1. Класс / группа          → select group_code (или сразу считает module_id)
2. Формат обучения         → select tariff
3. Дата старта          → chosen_stage (29 июня = 1, 20 июля = 2)
4. [если разовое] Сказка → chosen_tale_number
5. Данные родителя/ребёнка
6. notification_channel
7. hidden module_id        → заполняется скриптом из п.1 + п.2
```

---

## Таблица: класс + тариф → module_id

Используйте в скрипте или в одном большом select.

| Класс / группа | value `group_code` | Разовое | Индивидуальное | С преподавателем |
|----------------|-------------------|---------|----------------|------------------|
| 1 класс | `grade-1` | **1** | **2** | **3** |
| 2 класс | `grade-2` | **4** | **5** | **6** |
| 3 класс | `grade-3` | **7** | **8** | **9** |
| 4 класс | `grade-4` | **10** | **11** | **12** |
| Внекл. 6–8 лет | `extra-6-8` | **13** | **14** | **15** |
| Внекл. 9–11 лет | `extra-9-11` | **16** | **17** | **18** |

**Select «Формат»** — value строго:

| Подпись | value |
|---------|-------|
| Разовое занятие (1 сказка) | `single` |
| Индивидуальное (4 сказки, свой темп) | `self_paced` |
| С преподавателем (4 сказки + 4 встречи) | `with_teacher` |

---

## Zero Block: класс + тариф → hidden module_id

Добавьте блок **T123 / Zero Block** **над** формой или внутри неё.

**Два select (видимые):**

- `group_code` — класс  
- `tariff_code` — формат  

**Скрытые (в форме):**

- `module_id`  
- `chosen_stage`  
- `chosen_tale_number`  

**Блоки «Этап» и «Сказка»** — показывайте только когда `tariff_code === 'single'` (класс `tilda-hide` / display через JS).

```html
<select name="group_code" id="group_code">
  <option value="">Выберите класс</option>
  <option value="grade-1">1 класс</option>
  <option value="grade-2">2 класс</option>
  <option value="grade-3">3 класс</option>
  <option value="grade-4">4 класс</option>
  <option value="extra-6-8">Внеклассное чтение 6–8 лет</option>
  <option value="extra-9-11">Внеклассное чтение 9–11 лет</option>
</select>

<select name="tariff_code" id="tariff_code">
  <option value="">Выберите формат</option>
  <option value="single">Разовое занятие — 1 490 ₽</option>
  <option value="self_paced">Индивидуальное — 1 990 ₽</option>
  <option value="with_teacher">С преподавателем — 4 990 ₽</option>
</select>

<div id="single-options" style="display:none">
  <select name="chosen_stage" id="chosen_stage">
    <option value="">Когда начать</option>
    <option value="1">Старт курса 29 июня (4 сказки)</option>
    <option value="2">Старт 20 июля (4 сказки)</option>
  </select>
  <select name="chosen_tale_number" id="chosen_tale_number">
    <option value="">Сказка №</option>
    <option value="1">1</option>
    <option value="2">2</option>
    <option value="3">3</option>
    <option value="4">4</option>
  </select>
  <p id="tale-hint" style="font-size:14px;color:#666"></p>
</div>

<input type="hidden" name="module_id" id="module_id" value="">
```

```html
<script>
(function () {
  var MAP = {
    'grade-1': { single: 1, self_paced: 2, with_teacher: 3 },
    'grade-2': { single: 4, self_paced: 5, with_teacher: 6 },
    'grade-3': { single: 7, self_paced: 8, with_teacher: 9 },
    'grade-4': { single: 10, self_paced: 11, with_teacher: 12 },
    'extra-6-8': { single: 13, self_paced: 14, with_teacher: 15 },
    'extra-9-11': { single: 16, self_paced: 17, with_teacher: 18 }
  };

  // Названия сказок для подсказки (разовое)
  var TALES = {
    'grade-1': {
      '1': ['Царевна лягушка','Рассказы из Азбуки Л.Н. Толстой','Рассказы Н. Носова','Кот в сапогах, Мальчик с пальчик'],
      '2': ['По щучьему велению','Мёртвая царевна и семь богатырей','Принцесса на горошине, Дюймовочка','Аля, Кляксич и буква А']
    },
    'grade-2': {
      '1': ['Сказка о рыбаке и рыбке','Цветик-семицветик','Как муравьишка…, Где раки зимуют','Гадкий утёнок'],
      '2': ['Филипок + Азбука','Незнайка на Луне','Рикки-Тикки-Тави','Маленькая Баба-Яга, Маленький водяной']
    },
    'grade-3': {
      '1': ['Сказка о царе Салтане','Серая шейка','Чёрная курица','Чудесный доктор'],
      '2': ['Молодильные яблоки','Серебряный рубль','Аленький цветочек','Королевство кривых зеркал']
    },
    'grade-4': {
      '1': ['Уральские сказы','Сказка о потерянном времени','Три толстяка','Остров Сокровищ'],
      '2': ['Том Сойер','Белый Бим','Пеппи','Гулливер']
    },
    'extra-6-8': {
      '1': ['Плюшевый заяц','Муми-тролль и комета','Шляпа волшебника','Паддингтон'],
      '2': ['Кролик Эдвард','Тутта Карлссон…','Карлик Нос','Чарли и шоколадная фабрика']
    },
    'extra-9-11': {
      '1': ['Мемуары папы Муми-тролля, Опасное лето','На острове Сальткрока','Собака Пес','Вафельное сердце'],
      '2': ['Нильс с дикими гусями','Нильс 2 часть','Полианна','Калиф-аист, Маленький Мук']
    }
  };

  var g = document.getElementById('group_code');
  var t = document.getElementById('tariff_code');
  var mid = document.getElementById('module_id');
  var singleBox = document.getElementById('single-options');
  var stage = document.getElementById('chosen_stage');
  var taleNum = document.getElementById('chosen_tale_number');
  var hint = document.getElementById('tale-hint');

  function syncModuleId() {
    var gc = g.value;
    var tc = t.value;
    mid.value = (MAP[gc] && MAP[gc][tc]) ? MAP[gc][tc] : '';
    singleBox.style.display = (tc === 'single') ? 'block' : 'none';
    updateTaleHint();
  }

  function updateTaleHint() {
    if (!hint) return;
    var gc = g.value, st = stage.value, n = taleNum.value;
    if (t.value !== 'single' || !gc || !st || !n) { hint.textContent = ''; return; }
    var list = (TALES[gc] && TALES[gc][st]) ? TALES[gc][st] : [];
    hint.textContent = list[n - 1] ? ('Вы выбрали: «' + list[n - 1] + '»') : '';
  }

  g.addEventListener('change', syncModuleId);
  t.addEventListener('change', syncModuleId);
  stage.addEventListener('change', updateTaleHint);
  taleNum.addEventListener('change', updateTaleHint);
})();
</script>
```

> **Важно:** в webhook обязательны `module_id` и `chosen_stage` (для всех тарифов). Для разового — ещё `chosen_tale_number`.

---

## Альтернатива без JavaScript

Один select **«Программа»** — 18 options, value = `module_id`:

| Подпись option | value |
|----------------|-------|
| 1 класс · Разовое | `1` |
| 1 класс · Индивидуальное | `2` |
| 1 класс · С преподавателем | `3` |
| 2 класс · Разовое | `4` |
| … | … |
| 9–11 лет · С преподавателем | `18` |

Variable name: `module_id`.  
Для разового добавьте ещё два select: `chosen_stage`, `chosen_tale_number` (подсказки по сказкам — в блоке «Программа» на странице).

---

## Остальные поля формы (как раньше)

| Variable name | Подпись |
|---------------|---------|
| `parent_name` | Ваше имя |
| `parent_email` | Email |
| `parent_telegram` | Telegram |
| `child_name` | Имя ребёнка |
| `child_age` | Возраст |
| `notification_channel` | Как присылать новости |

Webhook:

```
URL: https://api.chitatelstvo.ru/webhook/register
Header: X-Webhook-Secret: …
```

---

## Блоки на одной странице (контент)

1. **Обложка** — «Запись в Читательство»  
2. **Как выбрать** — класс → формат → (для разового) этап и сказка  
3. **Таблица тарифов** — 3 колонки, 6 строк классов, цены  
4. **Программы по классам** — 6 раскрывающихся блоков (accordion) со списком 8 сказок — тексты из `catalog/tales.json`  
5. **Форма** — selects + поля родителя  
6. **Спасибо** — success page  

Отдельные URL `/zapis/1-klass/individualnoe` **не нужны**, пока не захотите вести рекламу на конкретный тариф.

---

## Проверка

1. Выберите: 1 класс + Индивидуальное → в заявке `module_id=2`  
2. Выберите: 1 класс + Разовое + Этап 1 + Сказка 2 → `module_id=1`, `chosen_stage=1`, `chosen_tale_number=2`  
3. Прогресс: правильный модуль и список уроков  

---

## Пилот «Колобок»

Если на **этой же** странице нужен старый пилот без модулей — добавьте option «Пробный урок (Колобок)» **без** `module_id` или с отдельной формой. Не смешивайте: либо hidden `module_id` пустой, либо не отправляйте поле.

---

*См. также: `docs/TILDA_FORMS.md`, `docs/TILDA_TEXTS.md`*
