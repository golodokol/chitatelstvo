"""Обновить урок «Рыбак и рыбка» из контент-черновика в формат плеера."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "lessons" / "catalog" / "grade-2-self_paced-stage-1-lesson-01.json"
LEGACY = ROOT / "lessons" / "skazka-o-rybake-i-rybke.json"
IMG = "/static/lessons/rybaka-i-rybke"


def opt(oid: str, text: str) -> dict:
    return {"id": oid, "text": text}


def stress_reading(text: str) -> str:
    """Добавить ударения там, где уже были в прежней версии; иначе оставить как есть."""
    mapping = {
        "Жил старик со старухой у синего моря.": "Жил стари́к со стару́хой у си́него мо́ря.",
        "Старик ловил неводом рыбу.": "Старик лови́л не́водом ры́бу.",
        "В невод попалась золотая рыбка.": "В не́вод попа́лась золота́я ры́бка.",
        "Рыбка попросила отпустить её.": "Ры́бка попроси́ла отпусти́ть её.",
        "Старик рассказал всё старухе.": "Старик рассказа́л всё стару́хе.",
        "Старуха потребовала новое корыто.": "Стару́ха потре́бовала но́вое коры́то.",
        "Потом старуха захотела стать царицей.": "Пото́м стару́ха захоте́ла стать цари́цей.",
        "В конце старуха осталась у разбитого корыта.": "В конце́ стару́ха оста́лась у разби́того коры́та.",
    }
    return mapping.get(text, text)


CONTENT = {
    "title": "Сказка о рыбаке и рыбке",
    "tale_title": "Сказка о рыбаке и рыбке",
    "meaning_one_phrase": "Жадность разрушает, а доброта и мера сохраняют добро.",
    "video": {
        "type": "kinescope",
        "id": "",
        "title": "Сказка «О рыбаке и рыбке»",
        "duration_min": "5-12",
        "pass_condition": "просмотр >= 50%",
    },
    "emotion_quiz": {
        "title": "Эмоции героя",
        "character": "старик",
        "question": {
            "id": "e1",
            "text": (
                "Что чувствовал старик, когда поймал необычную золотую рыбку "
                "и увидел, что она говорит?"
            ),
            "pick": 2,
            "correct": ["surprise", "interest"],
        },
        "feedback_ok": "Верно.",
        "feedback_retry_hint": "Подумай, что чувствует человек, когда видит говорящую рыбку.",
        "feedback_retry": (
            "Старик не ждал чуда: в неводе оказалась золотая рыбка, да ещё и заговорила. "
            "Какие чувства появятся первыми?"
        ),
    },
    "reading_practice": {
        "title": "Практика чтения",
        "intro": (
            "Прочитай сказку по коротким предложениям — с картинками. "
            "Отмечай каждое, когда прочитаешь!"
        ),
        "cards": [
            {
                "id": "rp1",
                "text": stress_reading("Жил старик со старухой у синего моря."),
                "image": f"{IMG}/reading/reading-01.png",
                "alt": "Старик и старуха у моря",
            },
            {
                "id": "rp2",
                "text": stress_reading("Старик ловил неводом рыбу."),
                "image": f"{IMG}/reading/reading-02.png",
                "alt": "Старик с неводом",
            },
            {
                "id": "rp3",
                "text": stress_reading("В невод попалась золотая рыбка."),
                "image": f"{IMG}/reading/reading-03.png",
                "alt": "Золотая рыбка в неводе",
            },
            {
                "id": "rp4",
                "text": stress_reading("Рыбка попросила отпустить её."),
                "image": f"{IMG}/reading/reading-04.png",
                "alt": "Рыбка просит отпустить",
            },
            {
                "id": "rp5",
                "text": stress_reading("Старик рассказал всё старухе."),
                "image": f"{IMG}/reading/reading-05.png",
                "alt": "Старик рассказывает старухе",
            },
            {
                "id": "rp6",
                "text": stress_reading("Старуха потребовала новое корыто."),
                "image": f"{IMG}/reading/reading-06.png",
                "alt": "Старуха требует корыто",
            },
            {
                "id": "rp7",
                "text": stress_reading("Потом старуха захотела стать царицей."),
                "image": f"{IMG}/reading/reading-07.png",
                "alt": "Старуха хочет стать царицей",
            },
            {
                "id": "rp8",
                "text": stress_reading("В конце старуха осталась у разбитого корыта."),
                "image": f"{IMG}/reading/reading-08.png",
                "alt": "Старуха у разбитого корыта",
            },
        ],
    },
    "comprehension_quiz": {
        "title": "Понимание сказки",
        "pass_score": 5,
        "questions": [
            {
                "id": "q1",
                "type": "single",
                "text": "Кого старик поймал в море?",
                "options": [
                    opt("a", "щуку"),
                    opt("b", "золотую рыбку"),
                    opt("c", "рака"),
                    opt("d", "карася"),
                ],
                "correct": "b",
            },
            {
                "id": "q2",
                "type": "single",
                "text": "Как рыбка повела себя, когда попала в невод?",
                "options": [
                    opt("a", "заплакала"),
                    opt("b", "заговорила"),
                    opt("c", "убежала"),
                    opt("d", "спряталась"),
                ],
                "correct": "b",
            },
            {
                "id": "q3",
                "type": "single",
                "text": "Что сделал старик с рыбкой?",
                "options": [
                    opt("a", "отнёс домой"),
                    opt("b", "отпустил в море"),
                    opt("c", "отдал старухе"),
                    opt("d", "положил в ведро"),
                ],
                "correct": "b",
            },
            {
                "id": "q4",
                "type": "single",
                "text": "Что попросила старуха в первый раз?",
                "options": [
                    opt("a", "новое корыто"),
                    opt("b", "новый дом"),
                    opt("c", "золото"),
                    opt("d", "корону"),
                ],
                "correct": "a",
            },
            {
                "id": "q5",
                "type": "single",
                "text": "Кем захотела стать старуха потом?",
                "options": [
                    opt("a", "боярыней"),
                    opt("b", "царицей"),
                    opt("c", "королевой"),
                    opt("d", "княгиней"),
                ],
                "correct": "b",
            },
            {
                "id": "q6",
                "type": "single",
                "text": "Что было у старухи в конце?",
                "options": [
                    opt("a", "дворец"),
                    opt("b", "разбитое корыто"),
                    opt("c", "новая изба"),
                    opt("d", "золотая корона"),
                ],
                "correct": "b",
            },
            {
                "id": "q7",
                "type": "single",
                "text": "Кто исполнял желания старухи?",
                "options": [
                    opt("a", "старик"),
                    opt("b", "рыбка"),
                    opt("c", "море"),
                    opt("d", "царь"),
                ],
                "correct": "b",
            },
        ],
    },
    "meaning_quiz": {
        "title": "Задания по сказке",
        "pass_score": 6,
        "questions": [
            {
                "id": "m1",
                "type": "multi",
                "text": "Выбери, кого нет в сказке.",
                "hint": "Отметь того героя, которого в этой сказке не было.",
                "options": [
                    opt("old_man", "старик"),
                    opt("old_woman", "старуха"),
                    opt("fish", "золотая рыбка"),
                    opt("bunny", "зайчик"),
                ],
                "correct": ["bunny"],
            },
            {
                "id": "m2",
                "type": "multi",
                "text": "Выбери лишний предмет.",
                "hint": "Отметь предмет, которого нет в сказке.",
                "options": [
                    opt("trough", "корыто"),
                    opt("net", "невод"),
                    opt("izba", "изба"),
                    opt("samovar", "самовар"),
                ],
                "correct": ["samovar"],
            },
            {
                "id": "m3",
                "type": "multi",
                "text": "Выбери предметы, которые помогают узнать сказку.",
                "hint": "Отметь всё, что относится к этой сказке.",
                "options": [
                    opt("sea", "море"),
                    opt("dugout", "землянка"),
                    opt("trough", "корыто"),
                    opt("plane", "самолёт"),
                ],
                "correct": ["sea", "dugout", "trough"],
            },
            {
                "id": "m4",
                "type": "matching",
                "text": "Соедини героя и место.",
                "left": [
                    opt("old_man", "старик"),
                    opt("old_woman", "старуха"),
                    opt("fish", "золотая рыбка"),
                ],
                "right": [
                    opt("sea", "море"),
                    opt("dugout", "землянка"),
                    opt("palace", "дворец"),
                ],
                "correct": {
                    "old_man": "sea",
                    "old_woman": "dugout",
                    "fish": "sea",
                },
            },
            {
                "id": "m5",
                "type": "matching",
                "text": "Соедини, кто что просил.",
                "hint": "Слева — три просьбы старухи по порядку, справа — желания.",
                "left": [
                    opt("ask1", "старуха · 1"),
                    opt("ask2", "старуха · 2"),
                    opt("ask3", "старуха · 3"),
                ],
                "right": [
                    opt("trough", "новое корыто"),
                    opt("izba", "новую избу"),
                    opt("queen", "стать царицей"),
                ],
                "correct": {
                    "ask1": "trough",
                    "ask2": "izba",
                    "ask3": "queen",
                },
            },
            {
                "id": "m6",
                "type": "matching",
                "text": "Соедини героя и действие.",
                "left": [
                    opt("man1", "старик · 1"),
                    opt("man2", "старик · 2"),
                    opt("woman", "старуха"),
                ],
                "right": [
                    opt("caught", "поймал рыбку"),
                    opt("freed", "отпустил рыбку"),
                    opt("asked", "просила желания"),
                ],
                "correct": {
                    "man1": "caught",
                    "man2": "freed",
                    "woman": "asked",
                },
            },
            {
                "id": "m7",
                "type": "picture_match",
                "text": "Кто на картинке?",
                "pictures": [
                    {
                        "id": "p1",
                        "image": f"{IMG}/starik.png",
                        "alt": "Старик",
                    },
                    {
                        "id": "p2",
                        "image": f"{IMG}/starukha.png",
                        "alt": "Старуха",
                    },
                    {
                        "id": "p3",
                        "image": f"{IMG}/rybka.png",
                        "alt": "Золотая рыбка",
                    },
                    {
                        "id": "p4",
                        "image": f"{IMG}/tsaritsa.png",
                        "alt": "Царица",
                    },
                ],
                "labels": [
                    opt("l1", "старик"),
                    opt("l2", "старуха"),
                    opt("l3", "золотая рыбка"),
                    opt("l4", "царица"),
                ],
                "correct": {"p1": "l1", "p2": "l2", "p3": "l3", "p4": "l4"},
            },
            {
                "id": "m9",
                "type": "multi",
                "text": "Какая пословица подходит к сказке «О рыбаке и рыбке»?",
                "hint": "Выбери одну.",
                "options": [
                    opt("p1", "Без труда не вытащишь и рыбку из пруда."),
                    opt("p2", "Семь раз отмерь, один раз отрежь."),
                    opt("p3", "Друзья познаются в беде."),
                    opt("p4", "Делу время, потехе час."),
                ],
                "correct": ["p1"],
            },
            {
                "id": "m10",
                "type": "multi",
                "text": "Что значит выражение «остаться у разбитого корыта»?",
                "hint": "Выбери верное значение.",
                "options": [
                    opt("a", "получить много подарков"),
                    opt("b", "остаться ни с чем"),
                    opt("c", "стать богатым и знаменитым"),
                    opt("d", "уехать к морю"),
                ],
                "correct": ["b"],
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
                        "text": "Старик жил со старухой у синего моря.",
                        "image": f"{IMG}/event-01.png",
                        "alt": "Старик и старуха у моря",
                    },
                    {
                        "id": "e2",
                        "text": "Старик пошёл ловить рыбу.",
                        "image": f"{IMG}/event-02.png",
                        "alt": "Старик идёт ловить рыбу",
                    },
                    {
                        "id": "e3",
                        "text": "В невод попалась золотая рыбка.",
                        "image": f"{IMG}/event-03.png",
                        "alt": "Золотая рыбка в неводе",
                    },
                    {
                        "id": "e4",
                        "text": "Старик отпустил рыбку.",
                        "image": f"{IMG}/event-04.png",
                        "alt": "Старик отпускает рыбку",
                    },
                    {
                        "id": "e5",
                        "text": "Старуха всё больше требовала.",
                        "image": f"{IMG}/event-05.png",
                        "alt": "Старуха требует всё больше",
                    },
                    {
                        "id": "e6",
                        "text": "В конце старуха осталась у разбитого корыта.",
                        "image": f"{IMG}/event-06.png",
                        "alt": "Разбитое корыто",
                    },
                ],
                "correct": ["e1", "e2", "e3", "e4", "e5", "e6"],
            }
        ],
    },
    "creative_tasks": {
        "title": "Творческие задания",
        "items": [
            "нарисовать золотую рыбку",
            "раскрасить море спокойным и бурным",
            "придумать, что сказал бы старик, если бы не отпустил рыбку",
            "объяснить родителю одной фразой, почему старуха осталась у разбитого корыта",
        ],
    },
    "live_lesson": {
        "next_meeting_label": None,
        "price_rub": 799,
        "meeting_url": None,
        "enabled": False,
        "quest_idea": "мини-квест по сказке с обсуждением желаний и сценками",
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
        "slug": "grade-2-self_paced-stage-1-lesson-01",
        "module_id": 5,
        "group_code": "grade-2",
        "group_label": "2 класс",
        "tariff_code": "self_paced",
        "tariff_label": "Индивидуальное обучение",
        "stage": "stage-1",
        "stage_label": "Этап 1",
        "lesson_number": 19,
        "tale_number": 1,
        "tale_slug": "grade-2-stage1-tale-01",
        "module_week": 1,
        "meeting_number": 0,
        "badge": "Первый шаг",
        "points": 2,
        "active": True,
        "status": "опубликован",
        "note": (
            "Первый урок 2 класса, этап 1. Видео и картинки — заглушки (пути готовы)."
        ),
    }
    legacy_meta = {
        "slug": "skazka-o-rybake-i-rybke",
        "tale_slug": "grade-2-stage1-tale-01",
        "group_code": "grade-2",
        "stage": "stage-1",
        "tale_number": 1,
        "module_week": 1,
        "active": True,
        "status": "опубликован",
        "note": (
            "Legacy-slug. Полный контент зеркалит grade-2-self_paced-stage-1-lesson-01."
        ),
    }

    catalog = {**catalog_meta, **deepcopy(CONTENT)}
    legacy = {**legacy_meta, **deepcopy(CONTENT)}
    write_json(CATALOG, catalog)
    write_json(LEGACY, legacy)


if __name__ == "__main__":
    main()
