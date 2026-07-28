"""Сборка урока «Царь Салтан» (3 класс, этап 1) в формат плеера."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "lessons" / "catalog" / "grade-3-self_paced-stage-1-lesson-01.json"
WITH_TEACHER = ROOT / "lessons" / "catalog" / "grade-3-with_teacher-stage-1-lesson-01.json"
LEGACY = ROOT / "lessons" / "skazka-o-tsare-saltane.json"
IMG = "/static/lessons/tsare-saltane"


def opt(oid: str, text: str) -> dict:
    return {"id": oid, "text": text}


CONTENT = {
    "title": "Сказка о царе Салтане",
    "tale_title": "Сказка о царе Салтане",
    "meaning_one_phrase": "Зависть и ложь разрушают, а правда и доброта возвращают родных.",
    "video": {
        "type": "kinescope",
        "id": "",
        "title": "Сказка «О царе Салтане»",
        "duration_min": "8-15",
        "pass_condition": "просмотр >= 50%",
    },
    "emotion_quiz": {
        "title": "Эмоции героя",
        "character": "князь Гвидон",
        "question": {
            "id": "e1",
            "text": (
                "Что почувствовал Гвидон, когда впервые увидел корабль с царём Салтаном — "
                "своим отцом, которого никогда не знал?"
            ),
            "pick": 2,
            "min_correct": 2,
            "correct": ["interest", "sadness", "surprise", "joy"],
        },
        "feedback_ok": "Верно.",
        "feedback_retry_hint": (
            "Подумай: отец рядом, но Гвидон его ещё не знает. Какие чувства смешиваются?"
        ),
        "feedback_retry": (
            "Гвидон видит отца впервые — и не может подойти как сын. "
            "Тут и любопытство, и грусть, и удивление, и радость. Какие два ближе?"
        ),
    },
    "comprehension_quiz": {
        "title": "Мини-тест по сказке",
        "pass_score": 6,
        "questions": [
            {
                "id": "q1",
                "type": "single",
                "text": "Почему молодую царицу отправили в бочке в море?",
                "options": [
                    opt("a", "Потому что Салтан сам так приказал в письме с войны"),
                    opt("b", "Потому что сёстры и Бабариха подменили письмо ложным приказом"),
                    opt("c", "Потому что народ восстал против царицы"),
                    opt("d", "Потому что царица сама захотела уехать"),
                ],
                "correct": "b",
            },
            {
                "id": "q2",
                "type": "single",
                "text": "Что сильнее всего помогло Гвидону выжить и вырасти после бури?",
                "options": [
                    opt("a", "Забота матери и его собственный труд на пустынном острове"),
                    opt("b", "Золото, которое мать спрятала в бочке"),
                    opt("c", "Приказ Салтана спасти их"),
                    opt("d", "Доброта ткачихи, которая потом раскаялась"),
                ],
                "correct": "a",
            },
            {
                "id": "q3",
                "type": "single",
                "text": "Зачем Гвидон трижды летал к Салтану не человеком, а насекомым?",
                "options": [
                    opt(
                        "a",
                        "Чтобы незаметно увидеть отца и наказать клеветниц, не открываясь сразу",
                    ),
                    opt("b", "Чтобы украсть сокровища из дворца"),
                    opt("c", "Чтобы найти невесту среди служанок"),
                    opt("d", "Чтобы отомстить Салтану за бочку"),
                ],
                "correct": "a",
            },
            {
                "id": "q4",
                "type": "single",
                "text": (
                    "Почему чудеса острова (белка, богатыри, княгиня) важны для сюжета "
                    "не только как «красота»?"
                ),
                "options": [
                    opt(
                        "a",
                        "Они нужны, чтобы купцы разнесли славу и Салтан захотел приплыть",
                    ),
                    opt("b", "Они нужны только чтобы напугать врагов"),
                    opt("c", "Они нужны, чтобы Гвидон забыл о родителях"),
                    opt("d", "Они нужны как награда завистницам"),
                ],
                "correct": "a",
            },
            {
                "id": "q5",
                "type": "single",
                "text": "В чём главная ошибка Салтана в начале сказки?",
                "options": [
                    opt("a", "Он слишком быстро поверил клевете и не проверил правду"),
                    opt("b", "Он не любил сына"),
                    opt("c", "Он сам написал злой приказ"),
                    opt("d", "Он боялся моря и поэтому не искал семью"),
                ],
                "correct": "a",
            },
            {
                "id": "q6",
                "type": "single",
                "text": "Как Гвидон отвечает на зло клеветниц — и почему это важно для смысла?",
                "options": [
                    opt("a", "Он мстит им войной и забирает их богатство"),
                    opt(
                        "b",
                        "Он не губит их, а добивается, чтобы правда открылась самому отцу",
                    ),
                    opt("c", "Он прощает их сразу и зовёт жить на остров"),
                    opt("d", "Он забывает о них и живёт только чудесами"),
                ],
                "correct": "b",
            },
            {
                "id": "q7",
                "type": "single",
                "text": "Какая пословица точнее всего про завистниц?",
                "hint": "Выбери одну.",
                "options": [
                    opt("a", "Не рой яму другому — сам в неё попадёшь."),
                    opt("b", "Семь раз отмерь, один раз отрежь."),
                    opt("c", "Тише едешь — дальше будешь."),
                    opt("d", "В гостях хорошо, а дома лучше."),
                ],
                "correct": "a",
            },
            {
                "id": "q8",
                "type": "single",
                "text": "Что для Гвидона важнее всех чудес Буяна?",
                "options": [
                    opt("a", "Чтобы весь мир завидовал его острову"),
                    opt("b", "Чтобы отец узнал правду и семья снова была вместе"),
                    opt("c", "Чтобы стать богаче Салтана"),
                    opt("d", "Чтобы наказать сестёр публично на площади"),
                ],
                "correct": "b",
            },
        ],
    },
    "meaning_quiz": {
        "title": "Задания по смыслу сказки",
        "pass_score": 4,
        "questions": [
            {
                "id": "m1",
                "type": "multi",
                "text": "Кто в сказке действует из зависти и желания «чужого места»?",
                "hint": "Отметь всех, кем двигала зависть.",
                "options": [
                    opt("weaver", "Ткачиха"),
                    opt("cook", "Повариха"),
                    opt("babarikha", "Сватья баба Бабариха"),
                    opt("swan", "Царевна Лебедь"),
                    opt("queen", "Молодая царица"),
                ],
                "correct": ["weaver", "cook", "babarikha"],
            },
            {
                "id": "m2",
                "type": "matching",
                "text": "Соедини героя и его главную черту.",
                "left": [
                    opt("saltan", "Царь Салтан"),
                    opt("gvidon", "Князь Гвидон"),
                    opt("babarikha", "Баба Бабариха"),
                    opt("queen", "Молодая царица"),
                ],
                "right": [
                    opt("trust", "доверчивость без проверки"),
                    opt("loyalty", "верность семье без жестокой мести"),
                    opt("cunning", "хитрость и ложь"),
                    opt("patience", "достоинство в беде"),
                ],
                "correct": {
                    "saltan": "trust",
                    "gvidon": "loyalty",
                    "babarikha": "cunning",
                    "queen": "patience",
                },
            },
            {
                "id": "m3",
                "type": "matching",
                "text": "Соедини поступок и то, к чему он привёл.",
                "left": [
                    opt("letter", "Подмена письма"),
                    opt("save", "Спасение Лебеди"),
                    opt("stings", "Укусы комара, мухи и шмеля"),
                    opt("fame", "Слава о чудесах острова"),
                ],
                "right": [
                    opt("split", "разлука семьи"),
                    opt("helper", "появляется верный помощник"),
                    opt("truth", "клевета начинает рушиться"),
                    opt("father", "отец сам тянется к сыну"),
                ],
                "correct": {
                    "letter": "split",
                    "save": "helper",
                    "stings": "truth",
                    "fame": "father",
                },
            },
            {
                "id": "m4",
                "type": "multi",
                "text": "Какая пословица о том, как зло возвращается к тому, кто его затеял?",
                "hint": "Выбери одну.",
                "options": [
                    opt("p1", "Не рой яму другому — сам в неё попадёшь."),
                    opt("p2", "Без труда не вытащишь и рыбку из пруда."),
                    opt("p3", "Друзья познаются в беде."),
                    opt("p4", "Ученье — свет, а неученье — тьма."),
                ],
                "correct": ["p1"],
            },
            {
                "id": "m5",
                "type": "multi",
                "text": "Какая пословица о победе правды?",
                "hint": "Выбери одну.",
                "options": [
                    opt("p1", "Правда всегда наружу выйдет."),
                    opt("p2", "Поспешишь — людей насмешишь."),
                    opt("p3", "Слово не воробей, вылетит — не поймаешь."),
                    opt("p4", "В тихом омуте черти водятся."),
                ],
                "correct": ["p1"],
            },
            {
                "id": "m6",
                "type": "multi",
                "text": "Что верно про путь Гвидона к счастью?",
                "hint": "Отметь всё верное.",
                "options": [
                    opt("truth", "Он добивается правды, но без жестокой мести"),
                    opt(
                        "build",
                        "Он сначала строит свою жизнь на острове, а не только ждёт чуда",
                    ),
                    opt("ally", "Ему помогает союз с Царевной Лебедью"),
                    opt(
                        "revenge",
                        "Он становится счастлив только после мести завистникам",
                    ),
                ],
                "correct": ["truth", "build", "ally"],
            },
        ],
    },
    "retelling_quiz": {
        "title": "Пробуем пересказать сказку",
        "pass_score": 1,
        "questions": [
            {
                "id": "r1",
                "type": "ordering",
                "text": "Расставь события по порядку.",
                "hint": (
                    "Перетащи картинки в шаги 1–8 по порядку сказки. "
                    "На телефоне: нажми картинку, затем шаг."
                ),
                "items": [
                    {
                        "id": "e1",
                        "text": "Сёстры подменяют письмо — клевещут на царицу.",
                        "image": f"{IMG}/event-01.png",
                        "alt": "Сёстры пишут ложное письмо",
                    },
                    {
                        "id": "e2",
                        "text": "Царицу с сыном бросают в бочке в море.",
                        "image": f"{IMG}/event-02.png",
                        "alt": "Бочка в море",
                    },
                    {
                        "id": "e3",
                        "text": "Гвидон спасает Лебедь от коршуна.",
                        "image": f"{IMG}/event-03.png",
                        "alt": "Гвидон спасает Лебедь",
                    },
                    {
                        "id": "e4",
                        "text": "На острове вырастает чудесный город.",
                        "image": f"{IMG}/event-04.png",
                        "alt": "Город на острове Буян",
                    },
                    {
                        "id": "e5",
                        "text": "Гвидон в облике комара прилетает к отцу.",
                        "image": f"{IMG}/event-05.png",
                        "alt": "Комар у Салтана",
                    },
                    {
                        "id": "e6",
                        "text": "Царевна-Лебедь помогает Гвидону.",
                        "image": f"{IMG}/event-06.png",
                        "alt": "Царевна-Лебедь",
                    },
                    {
                        "id": "e7",
                        "text": "Салтан плывёт к острову Буяну.",
                        "image": f"{IMG}/event-07.png",
                        "alt": "Салтан плывёт к острову",
                    },
                    {
                        "id": "e8",
                        "text": "Семья воссоединяется — правда открывается.",
                        "image": f"{IMG}/event-08.png",
                        "alt": "Встреча семьи",
                    },
                ],
                "correct": [
                    "e1",
                    "e2",
                    "e3",
                    "e4",
                    "e5",
                    "e6",
                    "e7",
                    "e8",
                ],
            }
        ],
    },
    "creative_tasks": {
        "title": "Творческие задания",
        "items": [
            "Сделай комикс на 3 кадра: ложь → испытание → правда",
            "Напиши письмо Салтану от Гвидона: 4–5 предложений с правдой и без злости",
            "Нарисуй свой остров: придумай ещё одно чудо, которого нет в сказке, но которое подошло бы Буяну",
        ],
    },
    "live_lesson": {
        "next_meeting_label": None,
        "price_rub": 799,
        "meeting_url": None,
        "enabled": False,
        "quest_idea": (
            "Мини-квест: разбор клеветы и правды, сценки «письмо» и «встреча на Буяне»"
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
        "slug": "grade-3-self_paced-stage-1-lesson-01",
        "module_id": 8,
        "group_code": "grade-3",
        "group_label": "3 класс",
        "tariff_code": "self_paced",
        "tariff_label": "Индивидуальное обучение",
        "stage": "stage-1",
        "stage_label": "Этап 1",
        "lesson_number": 36,
        "tale_number": 1,
        "tale_slug": "grade-3-stage1-tale-01",
        "module_week": 1,
        "meeting_number": 0,
        "badge": "Первый шаг",
        "points": 2,
        "active": True,
        "status": "тест",
        "note": (
            "3 класс, этап 1, сказка 1. Без практики чтения. "
            "Пересказ по картинкам (исключение)."
        ),
    }
    teacher_meta = {
        "slug": "grade-3-with_teacher-stage-1-lesson-01",
        "module_id": 9,
        "group_code": "grade-3",
        "group_label": "3 класс",
        "tariff_code": "with_teacher",
        "tariff_label": "Модуль с преподавателем",
        "stage": "stage-1",
        "stage_label": "Этап 1",
        "lesson_number": 44,
        "tale_number": 1,
        "tale_slug": "grade-3-stage1-tale-01",
        "module_week": 1,
        "meeting_number": 1,
        "badge": "Первый шаг",
        "points": 2,
        "active": True,
        "status": "тест",
        "note": "Тот же контент, что self_paced; встреча с преподавателем по расписанию.",
    }
    legacy_meta = {
        "slug": "skazka-o-tsare-saltane",
        "tale_slug": "grade-3-stage1-tale-01",
        "group_code": "grade-3",
        "stage": "stage-1",
        "tale_number": 1,
        "module_week": 1,
        "active": True,
        "status": "тест",
        "note": "Legacy-slug. Зеркало grade-3-self_paced-stage-1-lesson-01.",
    }

    write_json(CATALOG, {**catalog_meta, **deepcopy(CONTENT)})
    write_json(WITH_TEACHER, {**teacher_meta, **deepcopy(CONTENT)})
    write_json(LEGACY, {**legacy_meta, **deepcopy(CONTENT)})


if __name__ == "__main__":
    main()
