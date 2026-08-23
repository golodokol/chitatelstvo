# -*- coding: utf-8 -*-
"""Generate early-course catalog modules, tales, and lesson JSON files."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog"
LESSONS = ROOT / "lessons" / "catalog"

LETTERS_TITLES = [
    "Мотор на поляне",
    "Поющая У",
    "Круглая О",
    "Змейка: с-с-с!",
    "Рычит буква Р",
    "Слоги дружат",
    "Первые слова",
    "Праздник у Словика",
]

STORIES_TITLES = [
    "Кот и коробка",
    "Дождь за окном",
    "Где мяч?",
    "Словик проверяет память",
    "Мокрый кот",
    "Кот и плед",
    "Словик пришёл",
    "Словик дома",
]

LETTERS_STATIONS_TRIAL = [
    {"id": "gate", "title": "Врата страны звуков", "kind": "intro_video", "slovik_line": "Помоги мне вернуть звуки!", "audio": "bo-trial-intro", "spark": False},
    {"id": "whispers", "title": "Поляна шёпотов", "kind": "listen_pick", "slovik_line": "Послушай и угадай звук.", "audio": "bo-s1-enter", "spark": True,
     "rounds": [
         {"prompt_audio": "bo-s1-q1", "sound": "bo-s1-rain", "correct": "rain", "options": [
             {"id": "rain", "label": "Дождь", "image": "/static/early/letters/rain.png"},
             {"id": "ball", "label": "Мяч", "image": "/static/early/letters/ball.png"},
             {"id": "house", "label": "Дом", "image": "/static/early/letters/house.png"},
         ]},
         {"prompt_audio": "bo-s1-q1", "sound": "bo-s1-motor", "correct": "motor", "options": [
             {"id": "motor", "label": "Мотор", "image": "/static/early/letters/motor.png"},
             {"id": "bird", "label": "Птица", "image": "/static/early/letters/bird.png"},
             {"id": "cup", "label": "Чашка", "image": "/static/early/letters/cup.png"},
         ]},
         {"prompt_audio": "bo-s1-q1", "sound": "bo-s1-snake", "correct": "snake", "options": [
             {"id": "snake", "label": "Змейка", "image": "/static/early/letters/snake.png"},
             {"id": "drum", "label": "Барабан", "image": "/static/early/letters/drum.png"},
             {"id": "tree", "label": "Дерево", "image": "/static/early/letters/tree.png"},
         ]},
     ]},
    {"id": "echo", "title": "Пещера эха", "kind": "repeat_sound", "slovik_line": "Повтори: а-а-а.", "audio": "bo-s2-enter", "sound": "bo-s2-sound-a", "spark": False},
    {"id": "workshop", "title": "Мастерская буквы", "kind": "trace", "slovik_line": "Обведи букву пальчиком.", "audio": "bo-s3-enter", "letter": "А", "spark": False},
    {"id": "hunt", "title": "Охота на А", "kind": "find", "slovik_line": "Найди букву со звуком а-а-а.", "audio": "bo-s4-enter", "spark": False,
     "rounds": [
         {"correct": "A", "options": ["A", "O", "M", "U"]},
         {"correct": "A", "options": ["M", "A", "C", "O"]},
     ]},
    {"id": "basket", "title": "Корзина слов", "kind": "listen_pick", "slovik_line": "Где живёт звук а-а-а?", "audio": "bo-s5-enter", "spark": True, "multi": True,
     "rounds": [
         {"prompt_audio": "bo-s5-enter", "correct": ["aist", "arbuz"], "pick": 2, "options": [
             {"id": "aist", "label": "Аист", "image": "/static/early/letters/aist.png", "word_audio": "bo-s5-word-aist"},
             {"id": "arbuz", "label": "Арбуз", "image": "/static/early/letters/arbuz.png", "word_audio": "bo-s5-word-arbuz"},
             {"id": "myach", "label": "Мяч", "image": "/static/early/letters/ball.png", "word_audio": "bo-s5-word-myach"},
             {"id": "dom", "label": "Дом", "image": "/static/early/letters/house.png", "word_audio": "bo-s5-word-dom"},
         ]},
     ]},
    {"id": "bridge", "title": "Мост дружбы", "kind": "drag_join", "slovik_line": "Веди м-м-м к а-а-а.", "audio": "bo-s6-enter", "spark": True,
     "left": {"id": "M", "label": "М", "sound": "bo-s6-sound-m"},
     "right": {"id": "A", "label": "А", "sound": "bo-s6-sound-a"},
     "result": {"label": "МА", "sound": "bo-s6-syllable-ma"}},
    {"id": "grass", "title": "Пауза в траве", "kind": "break", "slovik_line": "Отойдём от экрана на минутку.", "audio": "bo-s7-enter", "spark": False,
     "hint": "Встань, скажи а-а-а. Найди дома предмет и скажи первый звук взрослому."},
    {"id": "chest", "title": "Финишный сундук", "kind": "mini_quest", "slovik_line": "Быстрый квест!", "audio": "bo-s8-enter", "spark": False,
     "steps": [
         {"kind": "listen_pick", "sound": "bo-s2-sound-a", "correct": "a_sound", "options": [
             {"id": "a_sound", "label": "а-а-а"}, {"id": "m_sound", "label": "м-м-м"}
         ]},
         {"kind": "find", "correct": "A", "options": ["A", "M", "O"]},
         {"kind": "find", "correct": "MA", "options": ["MA", "SA", "MO"]},
     ]},
    {"id": "reward", "title": "Награда Словика", "kind": "reward", "slovik_line": "Ты вернул звуки!", "audio": "bo-s9-reward", "spark": False,
     "parent_note": "Продолжайте занятия: в модуле — 8 таких маршрутов.",
     "module_url": "https://chitatelstvo.ru/#programs",
     "module_cta": "О модуле и записи",
     "chest_cta": "Открыть сундук"},
]

STORIES_STATIONS_TRIAL = [
    {"id": "closed_book", "title": "Закрытая книжка", "kind": "intro_video", "slovik_line": "Помоги спасти первую историю!", "audio": "ph-trial-intro", "spark": False},
    {"id": "letter_stones", "title": "Камни букв", "kind": "find", "slovik_line": "Покажи букву и послушай звук.", "audio": "ph-s1-enter", "spark": False,
     "rounds": [
         {"prompt_audio": "ph-s1-prompt-m", "correct": "M", "sound": "ph-s1-sound-m", "options": ["M", "A", "S", "O"]},
         {"prompt_audio": "ph-s1-prompt-a", "correct": "A", "sound": "ph-s1-sound-a", "options": ["S", "O", "A", "M"]},
         {"prompt_audio": "ph-s1-prompt-s", "correct": "S", "sound": "ph-s1-sound-s", "options": ["A", "S", "M", "O"]},
     ]},
    {"id": "sound_path", "title": "Звуковая тропа", "kind": "drag_join", "slovik_line": "Веди звук по дорожке.", "audio": "ph-s2-enter", "spark": True,
     "left": {"id": "M", "label": "М", "sound": "ph-s1-sound-m"},
     "right": {"id": "A", "label": "А", "sound": "ph-s1-sound-a"},
     "result": {"label": "МА", "sound": "ph-s2-syllable-ma"},
     "extra_joins": [
         {"left": {"id": "S", "label": "С", "sound": "ph-s1-sound-s"},
          "right": {"id": "O", "label": "О", "sound": "ph-s1-sound-o"},
          "result": {"label": "СО", "sound": "ph-s2-syllable-so"}}
     ]},
    {"id": "syllable_meadow", "title": "Поляна слогов", "kind": "listen_pick", "slovik_line": "Что я сказал? Нажми на слог.", "audio": "ph-s3-enter", "spark": False,
     "rounds": [
         {"sound": "ph-s3-say-ma", "correct": "ma", "options": [{"id": "ma", "label": "МА"}, {"id": "mo", "label": "МО"}, {"id": "sa", "label": "СА"}]},
         {"sound": "ph-s3-say-so", "correct": "so", "options": [{"id": "sa", "label": "СА"}, {"id": "so", "label": "СО"}, {"id": "mo", "label": "МО"}]},
         {"sound": "ph-s3-say-mo", "correct": "mo", "options": [{"id": "ma", "label": "МА"}, {"id": "mo", "label": "МО"}, {"id": "sa", "label": "СА"}]},
     ]},
    {"id": "path_break", "title": "Пауза на тропе", "kind": "break", "slovik_line": "Два шага — и скажи ма.", "audio": "ph-s4-enter", "spark": False,
     "hint": "Пройди два шага по полу и проговори «ма»."},
    {"id": "word_house", "title": "Домик слов", "kind": "word_picture", "slovik_line": "Прочитай и найди картинку.", "audio": "ph-s5-enter", "spark": True,
     "items": [
         {"word": "МАМА", "audio": "ph-s5-word-mama", "correct": "mama", "options": [
             {"id": "mama", "label": "Мама", "image": "/static/early/stories/mama.png"},
             {"id": "sok", "label": "Сок", "image": "/static/early/stories/sok.png"},
             {"id": "kot", "label": "Кот", "image": "/static/early/stories/kot.png"},
         ]},
         {"word": "СОК", "audio": "ph-s5-word-sok", "correct": "sok", "options": [
             {"id": "mama", "label": "Мама", "image": "/static/early/stories/mama.png"},
             {"id": "sok", "label": "Сок", "image": "/static/early/stories/sok.png"},
             {"id": "kot", "label": "Кот", "image": "/static/early/stories/kot.png"},
         ]},
         {"word": "КОТ", "audio": "ph-s5-word-kot", "correct": "kot", "options": [
             {"id": "sok", "label": "Сок", "image": "/static/early/stories/sok.png"},
             {"id": "kot", "label": "Кот", "image": "/static/early/stories/kot.png"},
             {"id": "mama", "label": "Мама", "image": "/static/early/stories/mama.png"},
         ]},
     ]},
    {"id": "story_window", "title": "Окно истории", "kind": "phrase_picture", "slovik_line": "Прочитай фразу.", "audio": "ph-s6-enter", "spark": False,
     "phrase": "КОТ СПИТ", "phrase_audio": "ph-s6-phrase", "correct": "sleep",
     "options": [
         {"id": "sleep", "label": "Кот спит", "image": "/static/early/stories/kot-sleep.png"},
         {"id": "run", "label": "Кот бежит", "image": "/static/early/stories/kot-run.png"},
     ]},
    {"id": "book_key", "title": "Ключ от книжки", "kind": "mini_quest", "slovik_line": "Собери путь ещё раз.", "audio": "ph-s7-enter", "spark": False,
     "steps": [
         {"kind": "find", "correct": "MA", "options": ["MA", "SO", "MO"]},
         {"kind": "word_picture", "word": "КОТ", "correct": "kot", "options": [
             {"id": "kot", "label": "Кот", "image": "/static/early/stories/kot.png"},
             {"id": "sok", "label": "Сок", "image": "/static/early/stories/sok.png"},
         ]},
         {"kind": "phrase_picture", "phrase": "КОТ СПИТ", "correct": "sleep", "options": [
             {"id": "sleep", "label": "Кот спит", "image": "/static/early/stories/kot-sleep.png"},
             {"id": "run", "label": "Кот бежит", "image": "/static/early/stories/kot-run.png"},
         ]},
     ]},
    {"id": "reward", "title": "Награда Словика", "kind": "reward", "slovik_line": "Ты спас первую историю!", "audio": "ph-s8-reward", "spark": False,
     "parent_note": "Дома ещё раз прочитайте МАМА и КОТ СПИТ. Дальше — модуль из 8 уроков."},
]


def skeleton_stations(course: str, lesson_n: int, title: str) -> list[dict]:
    prefix = "bo" if course == "letters" else "ph"
    return [
        {"id": "hello", "title": "Приветствие", "kind": "intro_video", "slovik_line": f"Сегодня: {title}", "audio": f"{prefix}-m1-l{lesson_n:02d}-hi", "spark": False},
        {"id": "warm", "title": "Разминка", "kind": "find", "slovik_line": "Вспомним прошлое.", "audio": f"{prefix}-m1-l{lesson_n:02d}-warm", "spark": False,
         "rounds": [{"correct": "A", "options": ["A", "M", "O"]}]},
        {"id": "new", "title": "Новое", "kind": "repeat_sound", "slovik_line": "Новый навык.", "audio": f"{prefix}-m1-l{lesson_n:02d}-new", "sound": f"{prefix}-m1-l{lesson_n:02d}-sound", "spark": False},
        {"id": "game1", "title": "Игра 1", "kind": "listen_pick", "slovik_line": "Поиграем!", "audio": f"{prefix}-m1-l{lesson_n:02d}-g1", "spark": True,
         "rounds": [{"correct": "yes", "options": [{"id": "yes", "label": "Да"}, {"id": "no", "label": "Нет"}]}]},
        {"id": "break", "title": "Пауза", "kind": "break", "slovik_line": "Отойдём от экрана.", "audio": "shared-pause-start", "spark": False, "hint": "Короткая пауза без экрана."},
        {"id": "game2", "title": "Игра 2", "kind": "find", "slovik_line": "Ещё практика.", "audio": f"{prefix}-m1-l{lesson_n:02d}-g2", "spark": True,
         "rounds": [{"correct": "A", "options": ["A", "M", "S"]}]},
        {"id": "quest", "title": "Мини-квест", "kind": "mini_quest", "slovik_line": "Почти финиш!", "audio": f"{prefix}-m1-l{lesson_n:02d}-quest", "spark": False,
         "steps": [{"kind": "find", "correct": "A", "options": ["A", "O"]}]},
        {"id": "reward", "title": "Награда", "kind": "reward", "slovik_line": "Молодец!", "audio": "shared-reward", "spark": False,
         "parent_note": f"Урок «{title}» пройден. Повторите дома главный навык."},
    ]


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def lesson_meta(
    *,
    slug: str,
    title: str,
    module_id: int,
    group_code: str,
    group_label: str,
    tariff_code: str,
    tariff_label: str,
    lesson_number: int,
    tale_number: int,
    tale_slug: str,
    module_week: int,
    stations: list[dict],
    active: bool,
    note: str,
) -> dict:
    lesson = {
        "slug": slug,
        "title": title,
        "tale_title": title,
        "module_id": module_id,
        "group_code": group_code,
        "group_label": group_label,
        "tariff_code": tariff_code,
        "tariff_label": tariff_label,
        "stage": "stage-1",
        "stage_label": "Модуль 1",
        "lesson_number": lesson_number,
        "tale_number": tale_number,
        "tale_slug": tale_slug,
        "module_week": module_week,
        "meeting_number": ((module_week - 1) // 2) + 1 if tariff_code == "with_teacher" else 0,
        "badge": "Первый шаг",
        "points": 2,
        "active": active,
        "status": "черновик" if not active else "тест",
        "note": note,
        "lesson_format": "quest",
        "stations": stations,
        "quest": {
            "goal_label": "искорки" if group_code == "early-letters" else "слоги на тропе",
            "goal_count": 3,
        },
    }
    if tariff_code == "with_teacher":
        from lessons.schedule import meeting_date_label

        lesson["live_lesson"] = {
            "next_meeting_label": meeting_date_label(
                module_week,
                weekday="четверг",
                group_code=group_code,
            )
        }
    return lesson


def main() -> None:
    # --- modules.json ---
    modules_path = CATALOG / "modules.json"
    modules_data = json.loads(modules_path.read_text(encoding="utf-8"))
    modules_data["modules"] = [m for m in modules_data["modules"] if m["id"] < 20 or m["id"] == 19]
    # keep 19, append 20-25 after sorting
    early_modules = [
        {"id": 20, "group_code": "early-letters", "group_label": "Буквы оживают", "tariff_code": "trial", "tariff_label": "Пробный урок", "title": "Пробный урок, Буквы оживают", "tales_count": 1, "stages": "Модуль 1", "tale_numbers": "пробный", "meetings": 0, "price_rub": 0, "status": "тест", "note": "Бесплатный пробный: авто-доступ после заявки."},
        {"id": 21, "group_code": "early-letters", "group_label": "Буквы оживают", "tariff_code": "self_paced", "tariff_label": "Индивидуальное обучение", "title": "Модуль 1 самостоятельно, Буквы оживают", "tales_count": 8, "stages": "Модуль 1 (вт/чт с 1 сентября)", "tale_numbers": "1–8", "meetings": 0, "price_rub": 1990, "status": "черновик", "note": "8 интерактивных уроков, без встреч. Открытие: вт/чт."},
        {"id": 22, "group_code": "early-letters", "group_label": "Буквы оживают", "tariff_code": "with_teacher", "tariff_label": "Модуль с преподавателем", "title": "Модуль 1 с преподавателем, Буквы оживают", "tales_count": 8, "stages": "Модуль 1 (вт/чт с 1 сентября)", "tale_numbers": "1–8", "meetings": 4, "price_rub": 4990, "status": "черновик", "note": "8 уроков + 4 встречи по четвергам: 3, 10, 17, 24 сентября 2026."},
        {"id": 23, "group_code": "early-stories", "group_label": "Первые истории", "tariff_code": "trial", "tariff_label": "Пробный урок", "title": "Пробный урок, Первые истории", "tales_count": 1, "stages": "Модуль 1", "tale_numbers": "пробный", "meetings": 0, "price_rub": 0, "status": "тест", "note": "Бесплатный пробный: авто-доступ после заявки."},
        {"id": 24, "group_code": "early-stories", "group_label": "Первые истории", "tariff_code": "self_paced", "tariff_label": "Индивидуальное обучение", "title": "Модуль 1 самостоятельно, Первые истории", "tales_count": 8, "stages": "Модуль 1 (вт/чт с 1 сентября)", "tale_numbers": "1–8", "meetings": 0, "price_rub": 1990, "status": "черновик", "note": "8 интерактивных уроков, без встреч. Открытие: вт/чт."},
        {"id": 25, "group_code": "early-stories", "group_label": "Первые истории", "tariff_code": "with_teacher", "tariff_label": "Модуль с преподавателем", "title": "Модуль 1 с преподавателем, Первые истории", "tales_count": 8, "stages": "Модуль 1 (вт/чт с 1 сентября)", "tale_numbers": "1–8", "meetings": 4, "price_rub": 4990, "status": "черновик", "note": "8 уроков + 4 встречи по четвергам: 3, 10, 17, 24 сентября 2026."},
    ]
    # Re-read to keep 1-19 intact
    modules_data = json.loads(modules_path.read_text(encoding="utf-8"))
    existing_ids = {m["id"] for m in modules_data["modules"]}
    for m in early_modules:
        if m["id"] in existing_ids:
            modules_data["modules"] = [x for x in modules_data["modules"] if x["id"] != m["id"]]
        modules_data["modules"].append(m)
    modules_data["modules"].sort(key=lambda x: x["id"])
    write_json(modules_path, modules_data)

    # --- tales.json ---
    tales_path = CATALOG / "tales.json"
    tales_data = json.loads(tales_path.read_text(encoding="utf-8"))
    tales_data["tales"] = [t for t in tales_data["tales"] if t["group_code"] not in ("early-letters", "early-stories")]
    next_id = max(t["id"] for t in tales_data["tales"]) + 1
    new_tales = []
    # trial + 8 for letters
    new_tales.append({"id": next_id, "group_code": "early-letters", "group_label": "Буквы оживают", "stage": "stage-1", "stage_label": "Модуль 1", "tale_number": 0, "tale_title": "Словик и пропавшие звуки", "lesson_title": "Словик и пропавшие звуки", "slug": "early-letters-stage1-tale-00"})
    next_id += 1
    for i, title in enumerate(LETTERS_TITLES, start=1):
        new_tales.append({"id": next_id, "group_code": "early-letters", "group_label": "Буквы оживают", "stage": "stage-1", "stage_label": "Модуль 1", "tale_number": i, "tale_title": title, "lesson_title": title, "slug": f"early-letters-stage1-tale-{i:02d}"})
        next_id += 1
    new_tales.append({"id": next_id, "group_code": "early-stories", "group_label": "Первые истории", "stage": "stage-1", "stage_label": "Модуль 1", "tale_number": 0, "tale_title": "Спаси первую историю", "lesson_title": "Спаси первую историю", "slug": "early-stories-stage1-tale-00"})
    next_id += 1
    for i, title in enumerate(STORIES_TITLES, start=1):
        new_tales.append({"id": next_id, "group_code": "early-stories", "group_label": "Первые истории", "stage": "stage-1", "stage_label": "Модуль 1", "tale_number": i, "tale_title": title, "lesson_title": title, "slug": f"early-stories-stage1-tale-{i:02d}"})
        next_id += 1
    tales_data["tales"].extend(new_tales)
    write_json(tales_path, tales_data)

    # --- lesson JSON ---
    # Trials
    write_json(LESSONS / "early-letters-trial-lesson-01.json", lesson_meta(
        slug="early-letters-trial-lesson-01", title="Словик и пропавшие звуки", module_id=20,
        group_code="early-letters", group_label="Буквы оживают", tariff_code="trial", tariff_label="Пробный урок",
        lesson_number=1, tale_number=0, tale_slug="early-letters-stage1-tale-00", module_week=1,
        stations=LETTERS_STATIONS_TRIAL, active=True, note="Бесплатный пробный квест.",
    ))
    # Trial JSON is hand-edited in lessons/catalog/early-stories-trial-lesson-01.json
    # Do not overwrite from STORIES_STATIONS_TRIAL.

    for tariff_code, tariff_label, mid_letters, mid_stories in (
        ("self_paced", "Индивидуальное обучение", 21, 24),
        ("with_teacher", "Модуль с преподавателем", 22, 25),
    ):
        for i, title in enumerate(LETTERS_TITLES, start=1):
            slug = f"early-letters-{tariff_code}-stage-1-lesson-{i:02d}"
            write_json(LESSONS / f"{slug}.json", lesson_meta(
                slug=slug, title=title, module_id=mid_letters,
                group_code="early-letters", group_label="Буквы оживают",
                tariff_code=tariff_code, tariff_label=tariff_label,
                lesson_number=i, tale_number=i, tale_slug=f"early-letters-stage1-tale-{i:02d}",
                module_week=i, stations=skeleton_stations("letters", i, title),
                active=False, note="Каркас станций модуля 1.",
            ))
        for i, title in enumerate(STORIES_TITLES, start=1):
            slug = f"early-stories-{tariff_code}-stage-1-lesson-{i:02d}"
            write_json(LESSONS / f"{slug}.json", lesson_meta(
                slug=slug, title=title, module_id=mid_stories,
                group_code="early-stories", group_label="Первые истории",
                tariff_code=tariff_code, tariff_label=tariff_label,
                lesson_number=i, tale_number=i, tale_slug=f"early-stories-stage1-tale-{i:02d}",
                module_week=i, stations=skeleton_stations("stories", i, title),
                active=False, note="Каркас станций модуля 1.",
            ))

    print("OK modules", len(modules_data["modules"]))
    print("OK tales", len(tales_data["tales"]))
    print("OK lessons early", len(list(LESSONS.glob("early-*.json"))))


if __name__ == "__main__":
    main()
