"""Сборка урока «Плюшевый заяц» (внеклассное 6–8 лет, этап 1)."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "lessons" / "catalog" / "extra-6-8-self_paced-stage-1-lesson-01.json"
WITH_TEACHER = ROOT / "lessons" / "catalog" / "extra-6-8-with_teacher-stage-1-lesson-01.json"
LEGACY = ROOT / "lessons" / "plyushevyy-zayats.json"
IMG = "/static/lessons/plyushevyy-zayats"


def opt(oid: str, text: str) -> dict:
    return {"id": oid, "text": text}


def s(text: str) -> str:
    """Короткие фразы с ударениями (combining acute)."""
    return text


CONTENT = {
    "title": "Плюшевый заяц",
    "tale_title": "Плюшевый заяц, или как игрушки становятся настоящими",
    "meaning_one_phrase": "Игрушка становится настоящей, когда её по-настоящему любят.",
    "video": {
        "type": "kinescope",
        "id": "",
        "title": "Плюшевый заяц",
        "duration_min": "5-12",
        "pass_condition": "просмотр >= 50%",
    },
    "emotion_quiz": {
        "title": "Эмоции героя",
        "character": "плюшевый заяц",
        "question": {
            "id": "e1",
            "text": (
                "Что чувствовал плюшевый заяц, когда мальчик крепко обнимал его "
                "и брал с собой играть каждый день?"
            ),
            "pick": 2,
            "min_correct": 2,
            "correct": ["joy", "calm", "pride"],
        },
        "feedback_ok": "Верно!",
        "feedback_retry_hint": "Подумай: его любят и не оставляют одного. Какие чувства появятся?",
        "feedback_retry": (
            "Мальчик обнимает зайца и играет с ним. Зайцу тепло и хорошо. "
            "Какие два чувства ближе всего?"
        ),
    },
    "reading_practice": {
        "title": "Практика чтения",
        "intro": (
            "В твоём возрасте прочитать целую книжку бывает непросто. "
            "Поэтому мы предлагаем прочитать сказку по коротким предложениям — с картинками. "
            "Отмечай каждое, когда прочитаешь!"
        ),
        "cards": [
            {
                "id": "rp1",
                "text": "Мальчику подари́ли плю́шевого за́йца.",
                "image": f"{IMG}/reading/reading-01.png",
                "alt": "Мальчик получил зайца",
            },
            {
                "id": "rp2",
                "text": "Други́е игру́шки смея́лись над ни́м.",
                "image": f"{IMG}/reading/reading-02.png",
                "alt": "Игрушки смеются",
            },
            {
                "id": "rp3",
                "text": "Ста́рый ко́нь сказа́л: настоя́щим де́лает любо́вь.",
                "image": f"{IMG}/reading/reading-03.png",
                "alt": "Старый конь учит зайца",
            },
            {
                "id": "rp4",
                "text": "Ма́льчик си́льно полюби́л за́йца.",
                "image": f"{IMG}/reading/reading-04.png",
                "alt": "Мальчик обнимает зайца",
            },
            {
                "id": "rp5",
                "text": "За́яц стал потрёпанным, но о́чень дороги́м.",
                "image": f"{IMG}/reading/reading-05.png",
                "alt": "Потрёпанный любимый заяц",
            },
            {
                "id": "rp6",
                "text": "Ма́льчик заболе́л, и за́йца хоте́ли сжечь.",
                "image": f"{IMG}/reading/reading-06.png",
                "alt": "Зайца собираются выбросить",
            },
            {
                "id": "rp7",
                "text": "Фе́я сде́лала за́йца настоя́щим.",
                "image": f"{IMG}/reading/reading-07.png",
                "alt": "Фея и настоящий заяц",
            },
        ],
    },
    "comprehension_quiz": {
        "title": "Понимание сказки",
        "pass_score": 4,
        "questions": [
            {
                "id": "q1",
                "type": "single",
                "text": "Кого подарили мальчику?",
                "options": [
                    opt("a", "плюшевого зайца"),
                    opt("b", "медведя"),
                    opt("c", "машинку"),
                ],
                "correct": "a",
            },
            {
                "id": "q2",
                "type": "single",
                "text": "Кто объяснил зайцу, как стать настоящим?",
                "options": [
                    opt("a", "старый конь"),
                    opt("b", "кукла"),
                    opt("c", "кот"),
                ],
                "correct": "a",
            },
            {
                "id": "q3",
                "type": "single",
                "text": "От чего игрушка становится настоящей?",
                "options": [
                    opt("a", "от любви ребёнка"),
                    opt("b", "от новой одежды"),
                    opt("c", "от золота"),
                ],
                "correct": "a",
            },
            {
                "id": "q4",
                "type": "single",
                "text": "Почему заяц стал потрёпанным?",
                "options": [
                    opt("a", "потому что с ним много играли и любили"),
                    opt("b", "потому что его забыли в шкафу"),
                    opt("c", "потому что он упал в лужу"),
                ],
                "correct": "a",
            },
            {
                "id": "q5",
                "type": "single",
                "text": "Что случилось с мальчиком?",
                "options": [
                    opt("a", "он заболел"),
                    opt("b", "он уехал в лес"),
                    opt("c", "он потерял зайца"),
                ],
                "correct": "a",
            },
            {
                "id": "q6",
                "type": "single",
                "text": "Кто помог зайцу стать настоящим в конце?",
                "options": [
                    opt("a", "фея"),
                    opt("b", "доктор"),
                    opt("c", "медведь"),
                ],
                "correct": "a",
            },
        ],
    },
    "meaning_quiz": {
        "title": "Задания по сказке",
        "pass_score": 4,
        "questions": [
            {
                "id": "m1",
                "type": "multi",
                "text": "Кого нет в этой сказке?",
                "hint": "Отметь одного.",
                "options": [
                    opt("rabbit", "плюшевый заяц"),
                    opt("horse", "старый конь"),
                    opt("boy", "мальчик"),
                    opt("dragon", "дракон"),
                ],
                "correct": ["dragon"],
            },
            {
                "id": "m2",
                "type": "multi",
                "text": "Что помогает узнать эту сказку?",
                "hint": "Отметь всё верное.",
                "options": [
                    opt("love", "любовь мальчика"),
                    opt("toy", "плюшевая игрушка"),
                    opt("real", "стать настоящим"),
                    opt("ship", "корабль"),
                ],
                "correct": ["love", "toy", "real"],
            },
            {
                "id": "m3",
                "type": "matching",
                "text": "Соедини героя и то, что он делает.",
                "left": [
                    opt("boy", "мальчик"),
                    opt("horse", "старый конь"),
                    opt("fairy", "фея"),
                ],
                "right": [
                    opt("loves", "любит и обнимает зайца"),
                    opt("teaches", "учит, как стать настоящим"),
                    opt("helps", "помогает стать настоящим"),
                ],
                "correct": {
                    "boy": "loves",
                    "horse": "teaches",
                    "fairy": "helps",
                },
            },
            {
                "id": "m4",
                "type": "matching",
                "text": "Соедини начало и конец.",
                "left": [
                    opt("a1", "Игрушку любят —"),
                    opt("a2", "Игрушку бросают —"),
                    opt("a3", "Фея приходит —"),
                ],
                "right": [
                    opt("b1", "она становится настоящей"),
                    opt("b2", "ей грустно и одиноко"),
                    opt("b3", "заяц получает чудо"),
                ],
                "correct": {
                    "a1": "b1",
                    "a2": "b2",
                    "a3": "b3",
                },
            },
            {
                "id": "m5",
                "type": "multi",
                "text": "Какая пословица подходит к сказке?",
                "hint": (
                    "В сказке любовь важнее блеска новых игрушек. "
                    "Пословица говорит об этом же — это метафора. Выбери одну."
                ),
                "options": [
                    opt("p1", "Не всё то золото, что блестит."),
                    opt("p2", "В гостях хорошо, а дома лучше."),
                    opt("p3", "Утро вечера мудренее."),
                    opt("p4", "Дело мастера боится."),
                ],
                "correct": ["p1"],
            },
            {
                "id": "m6",
                "type": "multi",
                "text": "Что главное в сказке?",
                "hint": "Выбери верное.",
                "options": [
                    opt("a", "настоящая любовь делает дорогим даже потрёпанное"),
                    opt("b", "нужно покупать только новые игрушки"),
                    opt("c", "фея важнее дружбы"),
                    opt("d", "игрушки должны быть всегда чистыми"),
                ],
                "correct": ["a"],
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
                "items": [
                    {
                        "id": "e1",
                        "text": "Мальчику подарили плюшевого зайца",
                        "image": f"{IMG}/event-01.png",
                        "alt": "Подарок",
                    },
                    {
                        "id": "e2",
                        "text": "Старый конь рассказал про любовь",
                        "image": f"{IMG}/event-02.png",
                        "alt": "Урок коня",
                    },
                    {
                        "id": "e3",
                        "text": "Мальчик полюбил зайца",
                        "image": f"{IMG}/event-03.png",
                        "alt": "Дружба",
                    },
                    {
                        "id": "e4",
                        "text": "Мальчик заболел, зайца хотели сжечь",
                        "image": f"{IMG}/event-04.png",
                        "alt": "Беда",
                    },
                    {
                        "id": "e5",
                        "text": "Фея сделала зайца настоящим",
                        "image": f"{IMG}/event-05.png",
                        "alt": "Чудо",
                    },
                ],
                "correct": ["e1", "e2", "e3", "e4", "e5"],
            }
        ],
    },
    "creative_tasks": {
        "title": "Творческие задания",
        "items": [
            "Нарисуй своего плюшевого зайца — каким ты его представил",
            "Сделай комикс на 3 кадра: подарок → любовь → чудо",
            "Придумай свою игрушку, которая стала настоящей, и нарисуй её",
        ],
    },
    "live_lesson": {
        "next_meeting_label": None,
        "price_rub": 799,
        "meeting_url": None,
        "enabled": False,
        "quest_idea": "Мини-квест: любовь делает настоящим, сценки «заяц и мальчик»",
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
        "slug": "extra-6-8-self_paced-stage-1-lesson-01",
        "module_id": 14,
        "group_code": "extra-6-8",
        "group_label": "Внеклассное чтение 6–8 лет",
        "tariff_code": "self_paced",
        "tariff_label": "Индивидуальное обучение",
        "stage": "stage-1",
        "stage_label": "Этап 1",
        "lesson_number": 70,
        "tale_number": 1,
        "tale_slug": "extra-6-8-stage1-tale-01",
        "module_week": 1,
        "meeting_number": 0,
        "badge": "Первый шаг",
        "points": 2,
        "active": False,
        "status": "черновик",
        "note": (
            "Внеклассное 6–8 лет, этап 1, сказка 1. "
            "Простые задания + практика чтения. Видео и картинки — заглушки."
        ),
    }
    teacher_meta = {
        "slug": "extra-6-8-with_teacher-stage-1-lesson-01",
        "module_id": 15,
        "group_code": "extra-6-8",
        "group_label": "Внеклассное чтение 6–8 лет",
        "tariff_code": "with_teacher",
        "tariff_label": "Модуль с преподавателем",
        "stage": "stage-1",
        "stage_label": "Этап 1",
        "lesson_number": 78,
        "tale_number": 1,
        "tale_slug": "extra-6-8-stage1-tale-01",
        "module_week": 1,
        "meeting_number": 1,
        "badge": "Первый шаг",
        "points": 2,
        "active": False,
        "status": "черновик",
        "note": "Тот же контент, что self_paced; встреча с преподавателем по расписанию.",
    }
    legacy_meta = {
        "slug": "plyushevyy-zayats",
        "tale_slug": "extra-6-8-stage1-tale-01",
        "group_code": "extra-6-8",
        "stage": "stage-1",
        "tale_number": 1,
        "module_week": 1,
        "active": False,
        "status": "черновик",
        "note": "Legacy-slug. Зеркало extra-6-8-self_paced-stage-1-lesson-01.",
    }

    write_json(CATALOG, {**catalog_meta, **deepcopy(CONTENT)})
    write_json(WITH_TEACHER, {**teacher_meta, **deepcopy(CONTENT)})
    write_json(LEGACY, {**legacy_meta, **deepcopy(CONTENT)})


if __name__ == "__main__":
    main()
