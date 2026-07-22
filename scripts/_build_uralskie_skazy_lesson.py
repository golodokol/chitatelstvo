"""Сборка урока «Уральские сказы» (4 класс, этап 1) — стержень: Хозяйка Медной горы."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "lessons" / "catalog" / "grade-4-self_paced-stage-1-lesson-01.json"
WITH_TEACHER = ROOT / "lessons" / "catalog" / "grade-4-with_teacher-stage-1-lesson-01.json"
LEGACY = ROOT / "lessons" / "uralskie-skazy.json"
IMG = "/static/lessons/uralskie-skazy"


def opt(oid: str, text: str) -> dict:
    return {"id": oid, "text": text}


CONTENT = {
    "title": "Уральские сказы",
    "tale_title": "Хозяйка Медной горы",
    "meaning_one_phrase": (
        "Хозяйка Медной горы испытывает человека: нарушенное слово "
        "и жадность к чуду губят, а правда выбора всегда имеет цену."
    ),
    "video": {
        "type": "kinescope",
        "id": "",
        "title": "Хозяйка Медной горы",
        "duration_min": "8-15",
        "pass_condition": "просмотр >= 50%",
    },
    "emotion_quiz": {
        "title": "Эмоции героя",
        "character": "Степан",
        "question": {
            "id": "e1",
            "text": (
                "Что почувствовал Степан, когда Хозяйка Медной горы "
                "показала ему несметные богатства горы и поставила условие?"
            ),
            "pick": 2,
            "min_correct": 2,
            "correct": ["surprise", "fear", "interest", "sadness"],
        },
        "feedback_ok": "Верно.",
        "feedback_retry_hint": (
            "Подумай: чудо рядом, но оно требует выбора. Какие чувства смешиваются?"
        ),
        "feedback_retry": (
            "Степан видит силу Хозяйки и понимает, что лёгкой удачи не будет. "
            "Тут могут быть удивление, страх, интерес и грусть. Какие два ближе?"
        ),
    },
    "comprehension_quiz": {
        "title": "Мини-тест по сказу",
        "pass_score": 6,
        "questions": [
            {
                "id": "q1",
                "type": "single",
                "text": "Кем впервые предстаёт перед Степаном Хозяйка Медной горы?",
                "options": [
                    opt("a", "Ящеркой в короне, которая потом оборачивается красавицей в малахитовом платье"),
                    opt("b", "Старой знахаркой из соседней деревни"),
                    opt("c", "Царицей, приехавшей из столицы"),
                    opt("d", "Обычной девушкой с завода"),
                ],
                "correct": "a",
            },
            {
                "id": "q2",
                "type": "single",
                "text": "Зачем Хозяйка ведёт Степана в гору?",
                "options": [
                    opt(
                        "a",
                        "Чтобы испытать его и показать силу и тайну Медной горы",
                    ),
                    opt("b", "Чтобы подарить ему завод и сделать хозяином"),
                    opt("c", "Чтобы он украл малахит для приказчика"),
                    opt("d", "Чтобы спрятать его от Насти"),
                ],
                "correct": "a",
            },
            {
                "id": "q3",
                "type": "single",
                "text": "Какое главное условие ставит Хозяйка Степану?",
                "options": [
                    opt(
                        "a",
                        "Не жениться на другой — ждать её и держать слово перед горой",
                    ),
                    opt("b", "Уехать навсегда в Москву"),
                    opt("c", "Стать приказчиком на заводе"),
                    opt("d", "Никому не рассказывать сказки"),
                ],
                "correct": "a",
            },
            {
                "id": "q4",
                "type": "single",
                "text": "Кто такая Настя в сказе «Хозяйка Медной горы»?",
                "options": [
                    opt(
                        "a",
                        "Невеста Степана, с которой связан его земной выбор",
                    ),
                    opt("b", "Сестра Хозяйки Медной горы"),
                    opt("c", "Жена приказчика"),
                    opt("d", "Дочь заводского хозяина"),
                ],
                "correct": "a",
            },
            {
                "id": "q5",
                "type": "single",
                "text": "В чём трагедия выбора Степана?",
                "options": [
                    opt(
                        "a",
                        "Он не смог совместить слово, данное горе, и жизнь с Настей — и за это платит",
                    ),
                    opt("b", "Он слишком рано разбогател"),
                    opt("c", "Он отказался работать на заводе"),
                    opt("d", "Он победил Хозяйку и остался без друзей"),
                ],
                "correct": "a",
            },
            {
                "id": "q6",
                "type": "single",
                "text": "Почему встреча с Хозяйкой — не просто «подарок судьбы»?",
                "options": [
                    opt(
                        "a",
                        "Потому что она проверяет человека: выдержит ли он закон горы и своё слово",
                    ),
                    opt("b", "Потому что она раздаёт золото всем подряд"),
                    opt("c", "Потому что Степан сам вызвал её заклинанием"),
                    opt("d", "Потому что она боится людей и прячется"),
                ],
                "correct": "a",
            },
            {
                "id": "q7",
                "type": "single",
                "text": "Какая пословица точнее всего про нарушенное слово в этом сказе?",
                "hint": "Выбери одну.",
                "options": [
                    opt("a", "Дал слово — держись, а не дал — крепись."),
                    opt("b", "Тише едешь — дальше будешь."),
                    opt("c", "В гостях хорошо, а дома лучше."),
                    opt("d", "Семь раз отмерь, один раз отрежь."),
                ],
                "correct": "a",
            },
            {
                "id": "q8",
                "type": "single",
                "text": "Что сказу важнее лёгкого богатства из горы?",
                "options": [
                    opt("a", "Честность выбора и уважение к тайне Хозяйки"),
                    opt("b", "Как быстрее продать малахит"),
                    opt("c", "Как заставить Хозяйку служить приказчику"),
                    opt("d", "Как спрятать камни от Насти"),
                ],
                "correct": "a",
            },
        ],
    },
    "meaning_quiz": {
        "title": "Задания по смыслу сказа",
        "pass_score": 4,
        "questions": [
            {
                "id": "m1",
                "type": "multi",
                "text": "Что в «Хозяйке Медной горы» связано с настоящей силой человека, а не с жадностью?",
                "hint": "Отметь всё верное.",
                "options": [
                    opt("word", "Умение держать данное слово"),
                    opt("choice", "Осознание цены своего выбора"),
                    opt("respect", "Уважение к тайне Медной горы"),
                    opt("grab", "Желание забрать все камни и сразу"),
                ],
                "correct": ["word", "choice", "respect"],
            },
            {
                "id": "m2",
                "type": "matching",
                "text": "Соедини героя или силу и его главную черту.",
                "left": [
                    opt("stepan", "Степан"),
                    opt("khozyayka", "Хозяйка Медной горы"),
                    opt("nastya", "Настя"),
                    opt("office", "Приказчик / жадность хозяев"),
                ],
                "right": [
                    opt("torn", "раздвоенность между горой и земной жизнью"),
                    opt("trial", "испытание и строгий закон горы"),
                    opt("earth", "земная любовь и обычная судьба"),
                    opt("greed", "давление выгоды и силы над людьми"),
                ],
                "correct": {
                    "stepan": "torn",
                    "khozyayka": "trial",
                    "nastya": "earth",
                    "office": "greed",
                },
            },
            {
                "id": "m3",
                "type": "matching",
                "text": "Соедини поступок и то, к чему он ведёт в сказе.",
                "left": [
                    opt("promise", "Дать слово Хозяйке"),
                    opt("break", "Нарушить условие горы"),
                    opt("marry", "Выбрать жизнь с Настей"),
                    opt("greed", "Гнаться только за богатством горы"),
                ],
                "right": [
                    opt("bind", "связать себя законом Медной горы"),
                    opt("pay", "заплатить тяжёлой ценой"),
                    opt("human", "остаться в мире людей, но с последствиями"),
                    opt("blind", "ослепнуть и потерять настоящее"),
                ],
                "correct": {
                    "promise": "bind",
                    "break": "pay",
                    "marry": "human",
                    "greed": "blind",
                },
            },
            {
                "id": "m4",
                "type": "multi",
                "text": "Какая пословица о цене данного слова?",
                "hint": "Выбери одну.",
                "options": [
                    opt("p1", "Слово — не воробей, вылетит — не поймаешь."),
                    opt("p2", "Друзья познаются в беде."),
                    opt("p3", "Тише едешь — дальше будешь."),
                    opt("p4", "В тихом омуте черти водятся."),
                ],
                "correct": ["p1"],
            },
            {
                "id": "m5",
                "type": "multi",
                "text": "Какая пословица о том, что не всё измеряется деньгами и блеском камня?",
                "hint": "Выбери одну.",
                "options": [
                    opt("p1", "Не всё то золото, что блестит."),
                    opt("p2", "Поспешишь — людей насмешишь."),
                    opt("p3", "Семь раз отмерь, один раз отрежь."),
                    opt("p4", "Ученье — свет, а неученье — тьма."),
                ],
                "correct": ["p1"],
            },
            {
                "id": "m6",
                "type": "multi",
                "text": "Что верно про смысл «Хозяйки Медной горы»?",
                "hint": "Отметь всё верное.",
                "options": [
                    opt(
                        "trial",
                        "Хозяйка испытывает человека, а не просто дарит счастье",
                    ),
                    opt(
                        "word",
                        "Нарушенное слово перед горой имеет тяжёлую цену",
                    ),
                    opt(
                        "choice",
                        "Выбор между горой и земной жизнью нельзя сделать «в шутку»",
                    ),
                    opt(
                        "easy",
                        "Степан легко обманул Хозяйку и стал счастлив без последствий",
                    ),
                ],
                "correct": ["trial", "word", "choice"],
            },
        ],
    },
    "retelling_quiz": {
        "title": "Пробуем пересказать сказ",
        "pass_score": 1,
        "questions": [
            {
                "id": "r1",
                "type": "ordering",
                "text": "Расставь смысловые узлы сказа по порядку.",
                "items": [
                    {
                        "id": "e1",
                        "text": "Степан встречает Хозяйку Медной горы",
                        "image": f"{IMG}/event-01.png",
                        "alt": "Встреча с Хозяйкой",
                    },
                    {
                        "id": "e2",
                        "text": "Хозяйка показывает богатства и ставит условие",
                        "image": f"{IMG}/event-02.png",
                        "alt": "Условие горы",
                    },
                    {
                        "id": "e3",
                        "text": "Степан стоит между горой и Настей",
                        "image": f"{IMG}/event-03.png",
                        "alt": "Выбор Степана",
                    },
                    {
                        "id": "e4",
                        "text": "Нарушенное слово и тяжёлая цена выбора",
                        "image": f"{IMG}/event-04.png",
                        "alt": "Цена выбора",
                    },
                    {
                        "id": "e5",
                        "text": "Вывод: закон горы строг к тому, кто дал слово",
                        "image": f"{IMG}/event-05.png",
                        "alt": "Смысл сказа",
                    },
                ],
                "correct": ["e1", "e2", "e3", "e4", "e5"],
            }
        ],
    },
    "creative_tasks": {
        "title": "Творческие задания",
        "items": [
            "Сделай комикс на 3 кадра: встреча с Хозяйкой → условие → цена выбора",
            "Придумай условие Хозяйки, которого нет в сказе, и нарисуй его на «табличке закона горы»",
            "Что было бы, если Степан сдержал слово? Напиши короткий финал на 4–5 предложений и добавь маленькую картинку",
        ],
    },
    "live_lesson": {
        "next_meeting_label": None,
        "price_rub": 799,
        "meeting_url": None,
        "enabled": False,
        "quest_idea": (
            "Мини-квест: встреча с Хозяйкой, условие горы, выбор Степана"
        ),
    },
}


def write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    catalog_meta = {
        "slug": "grade-4-self_paced-stage-1-lesson-01",
        "module_id": 11,
        "group_code": "grade-4",
        "group_label": "4 класс",
        "tariff_code": "self_paced",
        "tariff_label": "Индивидуальное обучение",
        "stage": "stage-1",
        "stage_label": "Этап 1",
        "lesson_number": 53,
        "tale_number": 1,
        "tale_slug": "grade-4-stage1-tale-01",
        "module_week": 1,
        "meeting_number": 0,
        "badge": "Первый шаг",
        "points": 2,
        "active": True,
        "status": "тест",
        "note": (
            "4 класс, этап 1, сказка 1. Стержень — Хозяйка Медной горы. "
            "Без практики чтения. Видео и картинки — заглушки."
        ),
    }
    teacher_meta = {
        "slug": "grade-4-with_teacher-stage-1-lesson-01",
        "module_id": 12,
        "group_code": "grade-4",
        "group_label": "4 класс",
        "tariff_code": "with_teacher",
        "tariff_label": "Модуль с преподавателем",
        "stage": "stage-1",
        "stage_label": "Этап 1",
        "lesson_number": 61,
        "tale_number": 1,
        "tale_slug": "grade-4-stage1-tale-01",
        "module_week": 1,
        "meeting_number": 1,
        "badge": "Первый шаг",
        "points": 2,
        "active": True,
        "status": "тест",
        "note": "Тот же контент, что self_paced; встреча с преподавателем по расписанию.",
    }
    legacy_meta = {
        "slug": "uralskie-skazy",
        "tale_slug": "grade-4-stage1-tale-01",
        "group_code": "grade-4",
        "stage": "stage-1",
        "tale_number": 1,
        "module_week": 1,
        "active": True,
        "status": "тест",
        "note": "Legacy-slug. Зеркало grade-4-self_paced-stage-1-lesson-01.",
    }

    write_json(CATALOG, {**catalog_meta, **deepcopy(CONTENT)})
    write_json(WITH_TEACHER, {**teacher_meta, **deepcopy(CONTENT)})
    write_json(LEGACY, {**legacy_meta, **deepcopy(CONTENT)})


if __name__ == "__main__":
    main()
