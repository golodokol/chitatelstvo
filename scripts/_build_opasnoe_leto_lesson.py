"""Сборка урока «Опасное лето» (внеклассное 9–11 лет, этап 1)."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "lessons" / "catalog" / "extra-9-11-self_paced-stage-1-lesson-01.json"
WITH_TEACHER = ROOT / "lessons" / "catalog" / "extra-9-11-with_teacher-stage-1-lesson-01.json"
LEGACY = ROOT / "lessons" / "opasnoe-leto.json"
IMG = "/static/lessons/opasnoe-leto"


def opt(oid: str, text: str) -> dict:
    return {"id": oid, "text": text}


CONTENT = {
    "title": "Опасное лето",
    "tale_title": "Опасное лето",
    "meaning_one_phrase": (
        "Когда дом уносит буря, настоящую опору дают семья, друзья и умение "
        "найти своё место даже на чужой сцене."
    ),
    "video": {
        "type": "kinescope",
        "id": "fuDHSoEgHwZtSt57eraez5",
        "title": "Опасное лето",
        "duration_min": "8-15",
        "pass_condition": "просмотр >= 50%",
    },
    "emotion_quiz": {
        "title": "Эмоции героя",
        "character": "Муми-тролль",
        "question": {
            "id": "e1",
            "text": (
                "Что почувствовал Муми-тролль, когда вода унесла дом "
                "и семья оказалась в неизвестности?"
            ),
            "pick": 2,
            "min_correct": 2,
            "correct": ["fear", "sadness", "surprise", "interest"],
        },
        "feedback_ok": "Верно.",
        "feedback_retry_hint": (
            "Подумай: дом пропал, но впереди ещё и приключение. Какие чувства смешиваются?"
        ),
        "feedback_retry": (
            "Дом унесло — страшно и грустно, но мир вокруг странный и новый. "
            "Тут могут быть страх, грусть, удивление и интерес. Какие два ближе?"
        ),
    },
    "comprehension_quiz": {
        "title": "Мини-тест по книге",
        "pass_score": 7,
        "questions": [
            {
                "id": "heroes",
                "type": "picture_match",
                "text": "Давайте вспомним основных героев этой истории",
                "hint": "Сопоставь фото с именем героя.",
                "match_tip": "Нажми фото слева, потом имя справа. Стрелка покажет пару.",
                "pictures": [
                    {
                        "id": "p1",
                        "image": "/static/lessons/opasnoe-leto/moomin.png",
                        "alt": "Муми-тролль в лодке с фонарём",
                    },
                    {
                        "id": "p2",
                        "image": "/static/lessons/opasnoe-leto/moominmamma.png",
                        "alt": "Муми-мама в фартуке с сумкой",
                    },
                    {
                        "id": "p3",
                        "image": "/static/lessons/opasnoe-leto/moominpappa.png",
                        "alt": "Муми-папа в шляпе с тростью",
                    },
                    {
                        "id": "p4",
                        "image": "/static/lessons/opasnoe-leto/little-my.png",
                        "alt": "Малышка Мю в красном платье",
                    },
                    {
                        "id": "p5",
                        "image": "/static/lessons/opasnoe-leto/snorkmaiden.png",
                        "alt": "Фрекен Снорк с букетом цветов",
                    },
                    {
                        "id": "p6",
                        "image": "/static/lessons/opasnoe-leto/snufkin.png",
                        "alt": "Снусмумрик в зелёной шляпе",
                    },
                    {
                        "id": "p7",
                        "image": "/static/lessons/opasnoe-leto/emma.png",
                        "alt": "Эмма с метлой",
                    },
                ],
                "labels": [
                    {"id": "moomin", "text": "Муми-тролль"},
                    {"id": "mamma", "text": "Муми-мама"},
                    {"id": "pappa", "text": "Муми-папа"},
                    {"id": "my", "text": "Малышка Мю"},
                    {"id": "snork", "text": "Фрекен Снорк"},
                    {"id": "snufkin", "text": "Снусмумрик"},
                    {"id": "emma", "text": "Эмма"},
                ],
                "correct": {
                    "p1": "moomin",
                    "p2": "mamma",
                    "p3": "pappa",
                    "p4": "my",
                    "p5": "snork",
                    "p6": "snufkin",
                    "p7": "emma",
                },
            },
            {
                "id": "q1",
                "type": "single",
                "text": "Почему семья муми-троллей оказалась без дома?",
                "options": [
                    opt(
                        "a",
                        "Потому что после извержения и наводнения дом унесло водой",
                    ),
                    opt("b", "Потому что они сами захотели переехать в город"),
                    opt("c", "Потому что дом сгорел от свечи"),
                    opt("d", "Потому что соседи выгнали их"),
                ],
                "correct": "a",
            },
            {
                "id": "q2",
                "type": "single",
                "text": "Что становится «новым миром» для героев после наводнения?",
                "options": [
                    opt("a", "Плавучий театр, который они принимают за странный дом-сцену"),
                    opt("b", "Дворец короля"),
                    opt("c", "Подводная пещера"),
                    opt("d", "Школа в городе"),
                ],
                "correct": "a",
            },
            {
                "id": "q3",
                "type": "single",
                "text": "Почему театр в книге — не только «развлечение»?",
                "options": [
                    opt(
                        "a",
                        "Потому что на сцене герои ищут роли, смысл и способ держаться вместе",
                    ),
                    opt("b", "Потому что там раздают золото"),
                    opt("c", "Потому что театр запрещён"),
                    opt("d", "Потому что без билета нельзя спастись"),
                ],
                "correct": "a",
            },
            {
                "id": "q4",
                "type": "single",
                "text": "В чём сила семьи муми-троллей в опасном лете?",
                "options": [
                    opt(
                        "a",
                        "Они не бросают друг друга и ищут выход вместе",
                    ),
                    opt("b", "Они прячут все запасы только для себя"),
                    opt("c", "Они убегают каждый в свою сторону"),
                    opt("d", "Они ждут, пока кто-то чужой всё решит"),
                ],
                "correct": "a",
            },
            {
                "id": "q5",
                "type": "single",
                "text": "Что для Снусмумрика важнее удобного «вечного дома»?",
                "options": [
                    opt("a", "Свобода пути и право уходить, когда зовёт дорога"),
                    opt("b", "Самая мягкая подушка в театре"),
                    opt("c", "Слава актёра"),
                    opt("d", "Власть над сценой"),
                ],
                "correct": "a",
            },
            {
                "id": "q6",
                "type": "single",
                "text": "Почему «опасное» лето всё же не только про страх?",
                "options": [
                    opt(
                        "a",
                        "Потому что испытание открывает приключение, дружбу и новые роли",
                    ),
                    opt("b", "Потому что вода сразу ушла и ничего не случилось"),
                    opt("c", "Потому что герои забыли про семью"),
                    opt("d", "Потому что опасность всегда смешная и пустая"),
                ],
                "correct": "a",
            },
            {
                "id": "q7",
                "type": "single",
                "text": "Какая пословица точнее всего про семью в беде?",
                "hint": "Выбери одну.",
                "options": [
                    opt("a", "Друзья познаются в беде."),
                    opt("b", "Тише едешь — дальше будешь."),
                    opt("c", "Семь раз отмерь, один раз отрежь."),
                    opt("d", "В гостях хорошо, а дома лучше."),
                ],
                "correct": "a",
            },
            {
                "id": "q8",
                "type": "single",
                "text": "Что в конце важнее вернувшегося дома?",
                "options": [
                    opt(
                        "a",
                        "Что герои прошли путь вместе и поняли цену близости",
                    ),
                    opt("b", "Что театр сгорел дотла"),
                    opt("c", "Что все стали богатыми"),
                    opt("d", "Что Снусмумрик остался сторожем сцены"),
                ],
                "correct": "a",
            },
        ],
    },
    "meaning_quiz": {
        "title": "Задания по смыслу книги",
        "pass_score": 4,
        "questions": [
            {
                "id": "m1",
                "type": "multi",
                "text": "Что в «Опасном лете» помогает выдержать потерю дома?",
                "hint": "Отметь всё верное.",
                "options": [
                    opt("family", "Близость семьи"),
                    opt("friends", "Друзья рядом"),
                    opt("play", "Умение играть роль и искать смысл"),
                    opt("greed", "Желание забрать сцену себе одному"),
                ],
                "correct": ["family", "friends", "play"],
            },
            {
                "id": "m2",
                "type": "matching",
                "text": "Соедини героя и его главную черту.",
                "left": [
                    opt("moomin", "Муми-тролль"),
                    opt("mamma", "Муми-мама"),
                    opt("snufkin", "Снусмумрик"),
                    opt("emma", "Эмма / мир театра"),
                ],
                "right": [
                    opt("seek", "поиск опоры и приключения"),
                    opt("care", "забота и спокойная сила дома"),
                    opt("free", "свобода и свой путь"),
                    opt("stage", "закон сцены и чужих ролей"),
                ],
                "correct": {
                    "moomin": "seek",
                    "mamma": "care",
                    "snufkin": "free",
                    "emma": "stage",
                },
            },
            {
                "id": "m3",
                "type": "matching",
                "text": "Соедини событие и то, к чему оно ведёт.",
                "left": [
                    opt("flood", "Наводнение уносит дом"),
                    opt("theater", "Герои попадают в театр"),
                    opt("roles", "Каждый ищет свою роль"),
                    opt("alone", "Думать только о себе"),
                ],
                "right": [
                    opt("start", "начало опасного пути"),
                    opt("new", "новый мир правил и чудес"),
                    opt("grow", "рост и понимание себя"),
                    opt("lose", "потеря связи с другими"),
                ],
                "correct": {
                    "flood": "start",
                    "theater": "new",
                    "roles": "grow",
                    "alone": "lose",
                },
            },
            {
                "id": "m4",
                "type": "multi",
                "text": "Какая пословица о доме подходит к книге?",
                "hint": (
                    "В книге дом — это не стены, а близкие рядом. "
                    "Пословица говорит об этом же — это метафора. Выбери одну."
                ),
                "options": [
                    opt("p1", "Не красна изба углами, а красна пирогами."),
                    opt("p2", "Не место красит человека, а человек — место."),
                    opt("p3", "Где любовь и совет, там и горя нет."),
                    opt("p4", "Поспешишь — людей насмешишь."),
                ],
                "correct": ["p1"],
            },
            {
                "id": "m5",
                "type": "multi",
                "text": "Какая пословица подходит к главной мысли книги?",
                "hint": (
                    "В книге опасность становится путём роста: через беду герои лучше понимают "
                    "дом и друг друга. Пословица говорит об этом же — это метафора. Выбери одну."
                ),
                "options": [
                    opt("p1", "Не бывает худа без добра."),
                    opt("p2", "Поспешишь — людей насмешишь."),
                    opt("p3", "Слово не воробей, вылетит — не поймаешь."),
                    opt("p4", "Ученье — свет, а неученье — тьма."),
                ],
                "correct": ["p1"],
            },
            {
                "id": "m6",
                "type": "multi",
                "text": "Что верно про смысл «Опасного лета»?",
                "hint": "Отметь всё верное.",
                "options": [
                    opt(
                        "home",
                        "Дом — не только стены, но и люди рядом",
                    ),
                    opt(
                        "trial",
                        "Опасность может стать путём роста, а не только бедой",
                    ),
                    opt(
                        "role",
                        "Найти свою роль — значит понять себя среди других",
                    ),
                    opt(
                        "easy",
                        "Главное — поскорее забыть семью и остаться одному навсегда",
                    ),
                ],
                "correct": ["home", "trial", "role"],
            },
        ],
    },
    "retelling_quiz": {
        "title": "Пробуем пересказать книгу",
        "pass_score": 1,
        "questions": [
            {
                "id": "r1",
                "type": "ordering",
                "text": "Расставь события по порядку.",
                "hint": (
                    "Перетащи события в шаги 1–6 по порядку книги. "
                    "На телефоне: нажми событие, затем шаг."
                ),
                "prompt_image": f"{IMG}/retelling-cover.png",
                "prompt_image_alt": "Иллюстрация к пересказу «Опасного лета»",
                "items": [
                    {
                        "id": "e1",
                        "text": "Наводнение заливает долину, семья спасается.",
                        "image": f"{IMG}/event-01.png",
                        "alt": "Семья в лодке во время наводнения",
                    },
                    {
                        "id": "e2",
                        "text": "Находят плавучий театр и поселяются.",
                        "image": f"{IMG}/event-02.png",
                        "alt": "Плавучий театр на воде",
                    },
                    {
                        "id": "e3",
                        "text": "Крыса Эмма объясняет, что это театр.",
                        "image": f"{IMG}/event-03.png",
                        "alt": "Крыса Эмма в театре",
                    },
                    {
                        "id": "e4",
                        "text": "Готовят спектакль.",
                        "image": f"{IMG}/event-04.png",
                        "alt": "Репетиция спектакля",
                    },
                    {
                        "id": "e5",
                        "text": "Показывают придуманный спектакль.",
                        "image": f"{IMG}/event-05.png",
                        "alt": "Спектакль на сцене",
                    },
                    {
                        "id": "e6",
                        "text": "Вода спадает, возвращаются в муми-дом.",
                        "image": f"{IMG}/event-06.png",
                        "alt": "Возвращение в муми-дом",
                    },
                ],
                "correct": ["e1", "e2", "e3", "e4", "e5", "e6"],
            }
        ],
    },
    "creative_tasks": {
        "title": "Творческие задания",
        "items": [
            "Сделай комикс на 3 кадра: потоп → театр → своя роль",
            "Нарисуй свой театр — такой, в котором могла бы оказаться семья муми-троллей после наводнения",
            "Напиши письмо другу: расскажи, что пережили герои за опасное лето и чему они научились",
        ],
    },
    "live_lesson": {
        "next_meeting_label": None,
        "price_rub": 799,
        "meeting_url": None,
        "enabled": False,
        "quest_idea": (
            "Мини-квест: потеря дома, театр ролей, сцена «что для меня дом»"
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
        "slug": "extra-9-11-self_paced-stage-1-lesson-01",
        "module_id": 17,
        "group_code": "extra-9-11",
        "group_label": "Внеклассное чтение 9–11 лет",
        "tariff_code": "self_paced",
        "tariff_label": "Индивидуальное обучение",
        "stage": "stage-1",
        "stage_label": "Этап 1",
        "lesson_number": 87,
        "tale_number": 1,
        "tale_slug": "extra-9-11-stage1-tale-01",
        "module_week": 1,
        "meeting_number": 0,
        "badge": "Первый шаг",
        "points": 2,
        "active": True,
        "status": "тест",
        "note": (
            "Внеклассное 9–11 лет, этап 1, книга 1. Без практики чтения."
        ),
    }
    teacher_meta = {
        "slug": "extra-9-11-with_teacher-stage-1-lesson-01",
        "module_id": 18,
        "group_code": "extra-9-11",
        "group_label": "Внеклассное чтение 9–11 лет",
        "tariff_code": "with_teacher",
        "tariff_label": "Модуль с преподавателем",
        "stage": "stage-1",
        "stage_label": "Этап 1",
        "lesson_number": 95,
        "tale_number": 1,
        "tale_slug": "extra-9-11-stage1-tale-01",
        "module_week": 1,
        "meeting_number": 1,
        "badge": "Первый шаг",
        "points": 2,
        "active": True,
        "status": "тест",
        "note": "Тот же контент, что self_paced; встреча с преподавателем по расписанию.",
    }
    legacy_meta = {
        "slug": "opasnoe-leto",
        "tale_slug": "extra-9-11-stage1-tale-01",
        "group_code": "extra-9-11",
        "stage": "stage-1",
        "tale_number": 1,
        "module_week": 1,
        "active": True,
        "status": "тест",
        "note": "Legacy-slug. Зеркало extra-9-11-self_paced-stage-1-lesson-01.",
    }

    write_json(CATALOG, {**catalog_meta, **deepcopy(CONTENT)})
    write_json(WITH_TEACHER, {**teacher_meta, **deepcopy(CONTENT)})
    write_json(LEGACY, {**legacy_meta, **deepcopy(CONTENT)})


if __name__ == "__main__":
    main()
