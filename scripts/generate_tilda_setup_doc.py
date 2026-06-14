"""Генератор docs/TILDA_SETUP_FULL.md — инструкции Tilda по модулям и урокам."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog"
LESSONS = ROOT / "lessons" / "catalog"
OUT = ROOT / "docs" / "TILDA_SETUP_FULL.md"

TARIFF_PAGES = {
    "single": "razovoe",
    "self_paced": "individualnoe",
    "with_teacher": "s-prepodavatelem",
}

GROUP_PAGES = {
    "grade-1": "1-klass",
    "grade-2": "2-klass",
    "grade-3": "3-klass",
    "grade-4": "4-klass",
    "extra-6-8": "vneshk-6-8",
    "extra-9-11": "vneshk-9-11",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    modules = load_json(CATALOG / "modules.json")["modules"]
    tales = load_json(CATALOG / "tales.json")["tales"]
    lessons = []
    for path in sorted(LESSONS.glob("*.json")):
        lessons.append(json.loads(path.read_text(encoding="utf-8")))

    lines: list[str] = []
    w = lines.append

    w("# Tilda: подробная настройка по модулям и урокам")
    w("")
    w("> Автогенерация из `catalog/` и `lessons/catalog/`. Запуск: `python scripts/generate_tilda_setup_doc.py`")
    w("")
    w("**API:** `https://api.chitatelstvo.ru`  ")
    w("**Сайт:** `https://chitatelstvo.ru` (ваш домен Tilda)")
    w("")
    w("---")
    w("")
    w("## Главное: где что живёт")
    w("")
    w("| Что | Где | Нужна страница Tilda? |")
    w("|-----|-----|----------------------|")
    w("| Запись на модуль | Форма на лендинге тарифа | **Да** — 18 страниц (6 групп × 3 тарифа) |")
    w("| Страница «Спасибо» | Success page формы | **Да** — 1 общая или 18 копий |")
    w("| Прогресс, баллы, кнопки уроков | `progress_url` на API | **Нет** — только ссылка с Tilda |")
    w("| Видео, квизы, творчество | Плеер на API | **Нет** — открывается с прогресса |")
    w("| Пилот «Колобок» | API, без `module_id` | Старая форма без скрытого поля |")
    w("")
    w("**102 урока не требуют 102 страниц на Tilda.** На Tilda — только лендинги записи и маркетинг. Урок открывается по кнопке на личной странице прогресса.")
    w("")
    w("---")
    w("")
    w("## Часть 1. Один раз на весь сайт")
    w("")
    w("### 1.1 Webhook (в настройках каждой формы записи)")
    w("")
    w("| Параметр | Значение |")
    w("|----------|----------|")
    w("| URL | `https://api.chitatelstvo.ru/webhook/register` |")
    w("| Метод | POST |")
    w("| Заголовок | `X-Webhook-Secret` = значение из `.env` на сервере |")
    w("")
    w("### 1.2 Обязательные поля формы (Variable name — точно так)")
    w("")
    w("| Подпись для родителя | Variable name | Тип |")
    w("|----------------------|---------------|-----|")
    w("| Ваше имя | `parent_name` | text |")
    w("| Email | `parent_email` | email |")
    w("| Telegram (необяз.) | `parent_telegram` | text |")
    w("| Имя ребёнка | `child_name` | text |")
    w("| Возраст | `child_age` | number |")
    w("| Как присылать новости | `notification_channel` | select |")
    w("")
    w("**Select `notification_channel`** — в value только код:")
    w("")
    w("| Подпись | value |")
    w("|---------|-------|")
    w("| На email | `email` |")
    w("| В Telegram | `telegram` |")
    w("| Email и Telegram | `both` |")
    w("| Только личная страница | `web` |")
    w("")
    w("### 1.3 Страница «Спасибо» (Success page)")
    w("")
    w("Тексты — в `docs/TILDA_TEXTS.md` §3. Обязательно:")
    w("- объяснить, что ссылка на прогресс придёт на email / будет на странице;")
    w("- кнопка «На главную» → `https://chitatelstvo.ru`.")
    w("")
    w("> Tilda не подставляет `progress_url` из ответа API автоматически — ссылка уходит в email и на личную страницу (канал `web`).")
    w("")
    w("---")
    w("")
    w("## Часть 2. Восемнадцать страниц записи (по одной на модуль)")
    w("")
    w("Рекомендуемая структура URL на Tilda:")
    w("")
    w("```")
    w("https://chitatelstvo.ru/zapis/{группа}/{тариф}")
    w("# пример: /zapis/1-klass/individualnoe")
    w("```")
    w("")
    w("На каждой странице — **своя форма** (или копия шаблона) со **скрытым полем** `module_id`.")
    w("")

    for mod in modules:
        mid = mod["id"]
        gc = mod["group_code"]
        tc = mod["tariff_code"]
        slug_hint = f"/zapis/{GROUP_PAGES[gc]}/{TARIFF_PAGES[tc]}"
        group_tales = [t for t in tales if t["group_code"] == gc]

        w(f"### Модуль {mid}: {mod['title']}")
        w("")
        w(f"| | |")
        w(f"|---|---|")
        w(f"| **module_id** (скрытое поле) | `{mid}` |")
        w(f"| Группа | {mod['group_label']} |")
        w(f"| Тариф | {mod['tariff_label']} |")
        w(f"| Цена (для текста) | {mod['price_rub']} ₽ |")
        w(f"| Сказок в модуле | {mod['tales_count']} |")
        w(f"| Встреч с преподавателем | {mod['meetings']} |")
        w(f"| URL страницы (рекомендация) | `{slug_hint}` |")
        w("")

        w("**Шаги в Tilda:**")
        w("")
        w("1. Создайте страницу (или скопируйте шаблон «Запись»).")
        w(f"2. Заголовок H1: **{mod['title']}**")
        w("3. Блок «Программа» — таблица сказок (см. ниже в Части 4 для этой группы).")
        w("4. Блок **Form** → добавьте поля из §1.2.")
        w(f"5. **Hidden field:** name=`module_id`, value=`{mid}`.")
        w("6. Webhook — §1.1.")
        w("7. Success page — §1.3.")
        w("8. Кнопки с главной и страницы тарифа ведут **сюда**, не на общую форму.")
        w("")

        if tc == "single":
            w("**Дополнительно для разового занятия** — два видимых поля:")
            w("")
            w("| Подпись | Variable name | Тип | value в option |")
            w("|---------|---------------|-----|----------------|")
            w("| Выберите этап | `chosen_stage` | select | `1` или `2` |")
            w("| Выберите сказку | `chosen_tale_number` | select | `1`, `2`, `3` или `4` |")
            w("")
            w("**Опции select «Сказка»** — зависят от этапа. Варианты:")
            w("")
            w("- **Простой:** два select; в подсказке написать «сначала этап, потом номер 1–4» и продублировать названия в блоке «Программа».")
            w("- **Удобный:** один select с двумя hidden-полями через Zero Block (см. Часть 3).")
            w("")
            w("Таблица сказок для подписей select:")
            w("")
            w("| Этап | № | Подпись option | chosen_stage | chosen_tale_number |")
            w("|------|---|----------------|--------------|-------------------|")
            for t in group_tales:
                stage_num = "1" if t["stage"] == "stage-1" else "2"
                w(
                    f"| {t['stage_label']} | {t['tale_number']} | "
                    f"{t['tale_title']} | `{stage_num}` | `{t['tale_number']}` |"
                )
            w("")
        else:
            w("**Скрытых полей кроме `module_id` не нужно** — все 8 сказок включены автоматически.")
            w("")

        mod_lessons = [l for l in lessons if l.get("module_id") == mid and l.get("tariff_code") != "single"]
        if tc == "single":
            mod_lessons = [l for l in lessons if l.get("module_id") == mid]
        w(f"**После записи** родитель видит на прогрессе **{len(mod_lessons)}** кнопок урока (пока уроки не активированы — подпись «скоро»).")
        w("")
        w("---")
        w("")

    w("## Часть 3. Разовое занятие: один select «Этап + сказка» (Zero Block)")
    w("")
    w("Если не хотите два select, сделайте один с value в формате `этап:номер`:")
    w("")
    w("```html")
    w('<select name="tale_choice" id="tale_choice">')
    w('  <option value="">Выберите сказку</option>')
    for t in tales:
        stage_num = "1" if t["stage"] == "stage-1" else "2"
        label = f"{t['group_label']} · {t['stage_label']} · {t['tale_title']}"
        w(f'  <option value="{stage_num}:{t["tale_number"]}">{label}</option>')
    w("</select>")
    w('<input type="hidden" name="chosen_stage" id="chosen_stage">')
    w('<input type="hidden" name="chosen_tale_number" id="chosen_tale_number">')
    w("<script>")
    w("document.getElementById('tale_choice').addEventListener('change', function () {")
    w("  var p = this.value.split(':');")
    w("  document.getElementById('chosen_stage').value = p[0] || '';")
    w("  document.getElementById('chosen_tale_number').value = p[1] || '';")
    w("});")
    w("</script>")
    w("```")
    w("")
    w("> На **отдельной странице каждой группы** оставьте в `<select>` только 8 option этой группы (см. таблицы в §2).")
    w("")
    w("---")
    w("")
    w("## Часть 4. Все 102 урока: что делать на Tilda")
    w("")
    w("Для **каждого** урока ниже:")
    w("")
    w("| Действие на Tilda | Нужно? |")
    w("|-------------------|--------|")
    w("| Отдельная страница урока | **Нет** |")
    w("| Форма webhook `/webhook/event` | **Нет** (баллы в плеере) |")
    w("| Упоминание в таблице «Программа» на лендинге | По желанию |")
    w("| Активация урока (`active: true` + видео в JSON на сервере) | **Да**, когда готов контент |")
    w("")
    w("---")
    w("")

    by_group: dict[str, list[dict]] = {}
    for les in lessons:
        by_group.setdefault(les["group_code"], []).append(les)

    for gc in ["grade-1", "grade-2", "grade-3", "grade-4", "extra-6-8", "extra-9-11"]:
        group_lessons = sorted(
            by_group.get(gc, []),
            key=lambda x: (
                x.get("tariff_code", ""),
                x.get("stage", ""),
                x.get("module_week", 0),
            ),
        )
        if not group_lessons:
            continue
        gl = group_lessons[0].get("group_label", gc)
        w(f"### {gl} (`{gc}`)")
        w("")

        for les in group_lessons:
            mid = les.get("module_id")
            tariff = les.get("tariff_label", les.get("tariff_code"))
            stage = les.get("stage_label", "")
            week = les.get("module_week", "?")
            title = les.get("title", "")
            slug = les.get("slug", "")
            active = les.get("active", False)
            meetings = les.get("meeting_number", 0)

            w(f"#### {title}")
            w("")
            w(f"- **slug (API):** `{slug}`")
            w(f"- **module_id:** {mid} ({tariff})")
            w(f"- **{stage}, неделя {week}**")
            if meetings:
                w(f"- **Встреча №{meetings}** (тариф с преподавателем)")
            w(f"- **Статус:** {'активен' if active else 'черновик — на прогрессе «скоро»'}")
            w("")
            w("**На Tilda:**")
            w("")
            if les.get("tariff_code") == "single":
                w("- Страница записи модуля «Разовое» — option в select сказки (см. §2).")
                w("- Отдельной страницы урока **не создавать**.")
            else:
                w(f"- Лендинг модуля **{mid}** — строка в таблице программы: «{stage}, нед. {week}: {title}».")
                w("- Кнопка «Записаться» → форма с hidden `module_id`.")
                w("- После активации на сервере кнопка урока появится на `progress_url` автоматически.")
            w("")
            w("**На сервере (не Tilda), когда урок готов:**")
            w("")
            w(f"1. Отредактировать `lessons/catalog/{slug}.json`")
            w('2. `"active": true`, добавить `video`, `comprehension_quiz`, `meaning_quiz`')
            w("3. `docker compose restart api worker`")
            w("")
            w("---")
            w("")

    w("## Часть 5. Пилот «Колобок» (legacy)")
    w("")
    w("| | |")
    w("|---|---|")
    w("| Страница Tilda | Старая форма набора **без** hidden `module_id` |")
    w("| Webhook | тот же `/webhook/register` |")
    w("| Прогресс | Только урок «Колobok» |")
    w("| Урок на API | `lessons/kolobok.json`, уже активен |")
    w("")
    w("---")
    w("")
    w("## Часть 6. Чеклист перед публикацией каждой страницы")
    w("")
    w("- [ ] Hidden `module_id` — правильное число")
    w("- [ ] Для разового — `chosen_stage` + `chosen_tale_number` или Zero Block")
    w("- [ ] Webhook URL и `X-Webhook-Secret`")
    w("- [ ] Variable name полей — латиница, как в таблице")
    w("- [ ] Success page настроена")
    w("- [ ] Тестовая отправка → email / прогресс → модуль и уроки видны")
    w("- [ ] Оплата (Tilda Payments / внешняя) — до или после webhook по вашей логике")
    w("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
