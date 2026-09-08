# -*- coding: utf-8 -*-
"""Станции уроков 1–4 модуля 1 (1, 3, 8, 10 сентября).

Новые механики из ТЗ (`letter_hop`, `letter_grid`, …) играются существующими
`kind` плеера; исходное имя — в поле `mechanic`.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

L = "/static/early/letters"
ST = "/static/early/stories"
SCENE_L = f"{L}/scene-invite.jpg"
SCENE_SP = f"{L}/scene-sparks.jpg"
SCENE_MISS = f"{L}/scene-missing.jpg"
SCENE_ST = f"{ST}/scene-lesson.jpg"
SPARK = f"{L}/spark.png"

IMG = {
    "motor": f"{L}/motor.png",
    "rain": f"{L}/rain.png",
    "ball": f"{L}/ball.png",
    "cup": f"{L}/cup.png",
    "mama": f"{L}/mama.png",
    "kot": f"{L}/kot.png",
    "house": f"{L}/house.png",
    "syr": f"{L}/syr.png",
    "bird": f"{L}/bird.png",
    "tree": f"{L}/tree.png",
    "aist": f"{L}/aist.png",
    "sleep": f"{ST}/kot-sleep.png",
    "run": f"{ST}/kot-run.png",
    "eat": f"{ST}/kot-eat.png",
    "night": f"{ST}/scene-night-sleep.jpg",
    "cover_home": f"{ST}/book-cover-home.png",
}


def _opt(oid: str, label: str, image: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"id": oid, "label": label}
    if image:
        row["image"] = image
    return row


def _reward(*, audio: str, line: str, parent: str, badge_line: str) -> dict[str, Any]:
    return {
        "id": "chest",
        "title": "Награда Словика",
        "chapter": "Три искорки",
        "kind": "reward",
        "slovik_line": line,
        "slovik_pose": "chest",
        "scene_image": SCENE_L,
        "spark_image": SPARK,
        "audio": audio,
        "fail_audio": "vo-retry",
        "spark": False,
        "fail_title": "Ещё чуть-чуть",
        "fail_line": "Искорки ещё не все. Давай пройдём ещё раз.",
        "fail_slovik_line": "Искорки ещё не все. Давай пройдём ещё раз.",
        "fail_pose": "worry",
        "retry_cta": "Попробовать ещё раз",
        "parent_note": parent,
        "chest_cta": "Открыть сундук",
        "tech_msg": badge_line,
    }


def _letters_1() -> list[dict[str, Any]]:
    return [
        {
            "id": "trail",
            "title": "Тропа букв",
            "kind": "intro_video",
            "slovik_line": "На тропе зажглась новая буква. Помнишь мотор? Он говорит: м-м-м. Познакомься с буквой М.",
            "slovik_pose": "wave",
            "scene_image": f"{L}/scene-gate.jpg",
            "audio": "bo-m1-l01-hi",
            "cta_label": "Начать",
            "spark": False,
        },
        {
            "id": "meet",
            "title": "Буква М",
            "chapter": "Знакомство",
            "kind": "meet_letter",
            "mechanic": "meet_letter",
            "slovik_line": "Это буква М. Нажми — услышишь м-м-м. Большая и маленькая — одна буква.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-meet",
            "sound": "snd-m",
            "letter": "М",
            "hint": "Нажми на букву — услышишь звук.",
            "spark": False,
        },
        {
            "id": "motor",
            "title": "Кто гудит?",
            "chapter": "Искорка 1 · Звук",
            "kind": "listen_pick",
            "slovik_line": "Что гудит м-м-м? Мотор или дождь?",
            "slovik_pose": "listen",
            "scene_image": SCENE_MISS,
            "audio": "bo-m1-l01-motor",
            "picture_only": True,
            "rounds": [
                {
                    "sound": "snd-m",
                    "correct": "motor",
                    "options": [
                        _opt("motor", "Мотор", IMG["motor"]),
                        _opt("rain", "Дождь", IMG["rain"]),
                    ],
                }
            ],
            "spark": True,
            "spark_kind": "sound",
            "spark_group": "sound",
        },
        {
            "id": "hop",
            "title": "Прыжки по кустам",
            "chapter": "Буква",
            "kind": "letter_maze",
            "mechanic": "letter_hop",
            "slovik_line": "Прыгай только на букву, которая говорит м-м-м. Чужие кусты — не туда.",
            "slovik_pose": "talk",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l01-hop",
            "letter": "М",
            "start": [0, 0],
            "end": [3, 2],
            "grid": [
                ["М", "А", "У"],
                ["М", "О", "С"],
                ["М", "М", "М"],
                ["А", "С", "М"]
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "build",
            "title": "Собери М",
            "chapter": "Искорка 2 · Буква",
            "kind": "build_letter",
            "slovik_line": "Собери М: две стойки и перекладина посередине.",
            "slovik_pose": "hint",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l01-build",
            "letter": "М",
            "hint": "Нажми на часть, потом на её место.",
            "success_msg": "Буква М собралась!",
            "spark": True,
            "spark_kind": "letter",
            "spark_group": "letter",
        },
        {
            "id": "grid",
            "title": "Найди все М",
            "chapter": "Буква",
            "kind": "letter_puzzle",
            "mechanic": "letter_grid",
            "slovik_line": "Найди на доске все буквы М. Их несколько.",
            "slovik_pose": "hint",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l01-grid",
            "slots": 4,
            "pieces": [
                {"id": "m1", "label": "М", "correct": True},
                {"id": "a1", "label": "А", "correct": False},
                {"id": "m2", "label": "М", "correct": True},
                {"id": "u1", "label": "У", "correct": False},
                {"id": "m3", "label": "М", "correct": True},
                {"id": "o1", "label": "О", "correct": False},
                {"id": "s1", "label": "С", "correct": False},
                {"id": "m4", "label": "М", "correct": True},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "pause",
            "title": "Пауза",
            "kind": "break",
            "slovik_line": "Встань. Погуди как мотор: м-м-м. Без экрана.",
            "audio": "bo-m1-l01-pause",
            "spark": False,
            "hint": "Встань и тихо скажи м-м-м, как мотор. Потом вернёмся.",
        },
        {
            "id": "slot_ma",
            "title": "Слог МА",
            "chapter": "Искорка 3 · Слог",
            "kind": "slot_build",
            "slovik_line": "Сложим слоги. Сначала ма — это уже знакомо.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-slots",
            "result_sound": "snd-ma",
            "targets": ["М", "А"],
            "options": ["О", "М", "У", "А"],
            "result_label": "МА",
            "result_image": IMG["mama"],
            "spark": False,
            "spark_group": "syllable",
        },
        {
            "id": "slot_mo",
            "title": "Слоги МО и МУ",
            "chapter": "Искорка 3 · Слог",
            "kind": "slot_build",
            "slovik_line": "Теперь мо. Потом му.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-slots",
            "result_sound": "snd-mo",
            "targets": ["М", "О"],
            "options": ["М", "А", "О", "У"],
            "result_label": "МО",
            "result_image": IMG["motor"],
            "spark": True,
            "spark_kind": "syllable",
            "spark_group": "syllable",
        },
        {
            "id": "spread",
            "title": "Книжечка звука",
            "chapter": "Слог",
            "kind": "book_page",
            "mechanic": "letter_spread",
            "slovik_line": "В книжке сначала звук мотора. Потом слово мама: ма-ма.",
            "slovik_pose": "talk",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-spread",
            "book_label": "Разворот",
            "book_title": "М",
            "cta_label": "Дальше",
            "lines": [
                {"text": "м-м-м", "image": IMG["motor"], "alt": "Мотор"},
                {"text": "МАМА", "image": IMG["mama"], "alt": "Мама"},
            ],
            "spark": False,
        },
        {
            "id": "or",
            "title": "Мотор или солнце",
            "chapter": "Звук",
            "kind": "listen_pick",
            "mechanic": "or_choice",
            "slovik_line": "Буква М. Кто говорит м-м-м — мотор или солнце?",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-or",
            "picture_only": True,
            "rounds": [
                {
                    "sound": "snd-m",
                    "correct": "motor",
                    "options": [
                        _opt("motor", "Мотор", IMG["motor"]),
                        _opt("sun", "Солнце", IMG["bird"]),
                    ],
                }
            ],
            "spark": False,
        },
        {
            "id": "quest",
            "title": "Слог МА",
            "chapter": "Мини-квест",
            "kind": "mini_quest",
            "slovik_line": "Где слог ма? Выбери ма, не мо.",
            "slovik_pose": "joy",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-quest",
            "spark": False,
            "show_all_steps": True,
            "hint": "Картинка «мама» и слог МА.",
            "steps": [
                {
                    "kind": "find",
                    "prompt": "Картинка",
                    "correct": "mama",
                    "options": [
                        _opt("mama", "Мама", IMG["mama"]),
                        _opt("motor", "Мотор", IMG["motor"]),
                        _opt("kot", "Кот", IMG["kot"]),
                    ],
                },
                {
                    "kind": "find",
                    "prompt": "Слог",
                    "correct": "МА",
                    "options": ["МО", "МА", "МУ", "АМ"],
                },
            ],
        },
        _reward(
            audio="bo-m1-l01-reward",
            line="Буква М с нами! Три искорки. Ты знаешь букву М.",
            parent="Урок «Мотор на поляне». Дома: м-м-м и слог МА. Слово МАМА можно прочитать вместе.",
            badge_line="Знаю букву М",
        ),
    ]


def _letters_2() -> list[dict[str, Any]]:
    return [
        {
            "id": "trail",
            "title": "Тропа букв",
            "kind": "intro_video",
            "slovik_line": "Новая буква на тропе. Она любит петь: у-у-у.",
            "slovik_pose": "wave",
            "scene_image": f"{L}/scene-gate.jpg",
            "audio": "bo-m1-l02-hi",
            "cta_label": "Начать",
            "spark": False,
        },
        {
            "id": "meet",
            "title": "Буква У",
            "kind": "meet_letter",
            "slovik_line": "Это У. Нажми и пропой вместе: у-у-у.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-meet",
            "sound": "snd-u",
            "letter": "У",
            "spark": False,
        },
        {
            "id": "echo",
            "title": "Эхо",
            "chapter": "Искорка 1 · Звук",
            "kind": "repeat_sound",
            "slovik_line": "Как в пещере эха. Повтори: у-у-у.",
            "slovik_pose": "listen",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l02-echo",
            "sound": "snd-u",
            "spark": True,
            "spark_kind": "sound",
            "spark_group": "sound",
        },
        {
            "id": "hop",
            "title": "Прыжки",
            "kind": "letter_maze",
            "mechanic": "letter_hop",
            "slovik_line": "Прыгай на букву, которая поёт у-у-у.",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l02-hop",
            "letter": "У",
            "start": [0, 0],
            "end": [3, 3],
            "grid": [
                ["У", "У", "У", "О"],
                ["М", "А", "У", "М"],
                ["А", "О", "У", "У"],
                ["М", "А", "М", "У"]
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "maze",
            "title": "Лабиринт У и А",
            "chapter": "Искорка 2 · Буква",
            "kind": "letter_maze",
            "slovik_line": "Иди только по У и А. Другие буквы — стена.",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l02-maze",
            "letter": "У",
            "start": [0, 0],
            "end": [2, 2],
            "grid": [
                ["У", "М", "А"],
                ["У", "У", "У"],
                ["А", "М", "У"]
            ],
            "spark": True,
            "spark_kind": "letter",
            "spark_group": "letter",
        },
        {
            "id": "grid",
            "title": "Найди все У",
            "kind": "letter_puzzle",
            "mechanic": "letter_grid",
            "slovik_line": "Найди все буквы У.",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l02-grid",
            "slots": 3,
            "pieces": [
                {"id": "u1", "label": "У", "correct": True},
                {"id": "m1", "label": "М", "correct": False},
                {"id": "u2", "label": "У", "correct": True},
                {"id": "a1", "label": "А", "correct": False},
                {"id": "o1", "label": "О", "correct": False},
                {"id": "u3", "label": "У", "correct": True},
            ],
            "spark": False,
        },
        {
            "id": "pause",
            "title": "Пауза",
            "kind": "break",
            "slovik_line": "Отойди. Пропой у-у-у тихо, как ветер.",
            "audio": "bo-m1-l02-pause",
            "spark": False,
            "hint": "Тихо пропой у-у-у у окна. Потом вернёмся.",
        },
        {
            "id": "slots",
            "title": "МУ и УМ",
            "chapter": "Искорка 3 · Слог",
            "kind": "slot_build",
            "slovik_line": "Склеим: му и ум.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-slots",
            "result_sound": "snd-mu",
            "targets": ["М", "У"],
            "options": ["М", "А", "У", "О"],
            "result_label": "МУ",
            "spark": True,
            "spark_kind": "syllable",
            "spark_group": "syllable",
        },
        {
            "id": "or",
            "title": "Кто поёт?",
            "kind": "listen_pick",
            "mechanic": "or_choice",
            "slovik_line": "Кто поёт у-у-у? Не спутай с мотором.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-or",
            "picture_only": True,
            "rounds": [
                {
                    "sound": "snd-u",
                    "correct": "wind",
                    "options": [
                        _opt("wind", "Ветер", IMG["tree"]),
                        _opt("motor", "Мотор", IMG["motor"]),
                    ],
                }
            ],
            "spark": False,
        },
        {
            "id": "quest",
            "title": "Слог УМ",
            "kind": "mini_quest",
            "slovik_line": "Где слог ум?",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-quest",
            "spark": False,
            "steps": [
                {
                    "kind": "find",
                    "prompt": "Слог",
                    "correct": "УМ",
                    "options": ["МУ", "УМ", "МА", "МО"],
                }
            ],
        },
        _reward(
            audio="bo-m1-l02-reward",
            line="Буква У умеет петь — и ты тоже. Искорки с нами!",
            parent="Урок «Поющая У». Дома протяните у-у-у и сложите МУ.",
            badge_line="Знаю букву У",
        ),
    ]


def _letters_3() -> list[dict[str, Any]]:
    return [
        {
            "id": "trail",
            "title": "Тропа букв",
            "kind": "intro_video",
            "slovik_line": "Круглая буква О. Она тоже поёт: о-о-о.",
            "slovik_pose": "wave",
            "scene_image": f"{L}/scene-gate.jpg",
            "audio": "bo-m1-l03-hi",
            "cta_label": "Начать",
            "spark": False,
        },
        {
            "id": "meet",
            "title": "Буква О",
            "kind": "meet_letter",
            "slovik_line": "Нажми на О. Скажи о-о-о.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-meet",
            "sound": "snd-o",
            "letter": "О",
            "spark": False,
        },
        {
            "id": "round",
            "title": "Круглое на поляне",
            "chapter": "Искорка 1 · Звук",
            "kind": "scene_hunt",
            "slovik_line": "Найди на поляне всё круглое. Как буква О.",
            "slovik_pose": "listen",
            "scene_image": SCENE_MISS,
            "audio": "bo-m1-l03-round",
            "layout": "grid",
            "grid_cols": 3,
            "correct_ids": ["ball", "cup"],
            "wrong_msg": "Это не круглое. Ищи ещё.",
            "hotspots": [
                {"id": "ball", "label": "Мяч", "image": IMG["ball"], "x": 20, "y": 28},
                {"id": "house", "label": "Дом", "image": IMG["house"], "x": 50, "y": 28},
                {"id": "cup", "label": "Чашка", "image": IMG["cup"], "x": 80, "y": 28},
                {"id": "tree", "label": "Дерево", "image": IMG["tree"], "x": 20, "y": 72},
                {"id": "motor", "label": "Мотор", "image": IMG["motor"], "x": 50, "y": 72},
                {"id": "bird", "label": "Птица", "image": IMG["bird"], "x": 80, "y": 72},
            ],
            "spark": True,
            "spark_kind": "sound",
            "spark_group": "sound",
        },
        {
            "id": "hop",
            "title": "Прыжки",
            "kind": "letter_maze",
            "mechanic": "letter_hop",
            "slovik_line": "Прыгай на круглую О.",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l03-hop",
            "letter": "О",
            "start": [0, 0],
            "end": [3, 2],
            "grid": [
                ["О", "А", "У"],
                ["О", "М", "О"],
                ["О", "О", "О"],
                ["М", "У", "О"]
            ],
            "spark": False,
        },
        {
            "id": "sort",
            "title": "Большая и маленькая О",
            "chapter": "Искорка 2 · Буква",
            "kind": "sort_two",
            "slovik_line": "Большая О и маленькая о — одна буква. Разложи.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-build",
            "left": {"label": "О", "correct": ["O1", "O2", "O3"]},
            "right": {"label": "о", "correct": ["o1", "o2", "o3"]},
            "options": [
                {"id": "O1", "label": "О"},
                {"id": "o1", "label": "о"},
                {"id": "O2", "label": "О"},
                {"id": "o2", "label": "о"},
                {"id": "O3", "label": "О"},
                {"id": "o3", "label": "о"},
            ],
            "spark": True,
            "spark_kind": "letter",
            "spark_group": "letter",
        },
        {
            "id": "count",
            "title": "Шесть О",
            "kind": "catch_letter",
            "mechanic": "letter_count",
            "slovik_line": "Поймай шесть букв О. Считай вместе со мной.",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l03-count",
            "letter": "О",
            "letters": ["О", "А", "У", "М"],
            "letter_sounds": {"О": "snd-o", "А": "snd-a", "У": "snd-u", "М": "snd-m"},
            "catches": 6,
            "spark": False,
        },
        {
            "id": "pause",
            "title": "Пауза",
            "kind": "break",
            "slovik_line": "Найди дома что-то круглое. Потом вернёмся.",
            "audio": "bo-m1-l03-pause",
            "spark": False,
            "hint": "Найди дома круглую вещь и скажи о-о-о.",
        },
        {
            "id": "slots",
            "title": "Слоги МО и ОС",
            "chapter": "Искорка 3 · Слог",
            "kind": "slot_build",
            "slovik_line": "Слоги: мо и ос.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-slots",
            "result_sound": "snd-mo",
            "targets": ["М", "О"],
            "options": ["С", "М", "О", "А"],
            "result_label": "МО",
            "result_image": IMG["motor"],
            "spark": True,
            "spark_kind": "syllable",
            "spark_group": "syllable",
        },
        {
            "id": "spread",
            "title": "Круг и слог",
            "kind": "book_page",
            "mechanic": "letter_spread",
            "slovik_line": "Смотри: круглый мяч — и буква О. Потом слог мо.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-spread",
            "book_title": "О",
            "cta_label": "Дальше",
            "lines": [
                {"text": "О", "image": IMG["ball"], "alt": "Мяч"},
                {"text": "МО", "image": IMG["motor"], "alt": "Мотор"},
            ],
            "spark": False,
        },
        {
            "id": "quest",
            "title": "МО — к мотору",
            "kind": "mini_quest",
            "slovik_line": "Слог мо — к мотору.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-quest",
            "spark": False,
            "steps": [
                {
                    "kind": "find",
                    "correct": "МО",
                    "options": ["МА", "МО", "МУ"],
                }
            ],
        },
        _reward(
            audio="bo-m1-l03-reward",
            line="Круглая О зажглась на тропе!",
            parent="Урок «Круглая О». Дома найдите круглое и скажите о-о-о.",
            badge_line="Знаю букву О",
        ),
    ]


def _letters_4() -> list[dict[str, Any]]:
    return [
        {
            "id": "trail",
            "title": "Тропа букв",
            "kind": "intro_video",
            "slovik_line": "Ш-ш-ш… то не наш звук. А вот с-с-с — это буква С.",
            "slovik_pose": "wave",
            "scene_image": f"{L}/scene-gate.jpg",
            "audio": "bo-m1-l04-hi",
            "cta_label": "Начать",
            "spark": False,
        },
        {
            "id": "meet",
            "title": "Буква С",
            "kind": "meet_letter",
            "slovik_line": "Буква С. Тихо: с-с-с. Как тонкая струйка воздуха.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-meet",
            "sound": "snd-s",
            "letter": "С",
            "spark": False,
        },
        {
            "id": "hiss",
            "title": "с-с-с или м-м-м",
            "chapter": "Искорка 1 · Звук",
            "kind": "listen_pick",
            "slovik_line": "Что слышишь: с-с-с или м-м-м?",
            "scene_image": SCENE_MISS,
            "audio": "bo-m1-l04-hiss",
            "picture_only": True,
            "rounds": [
                {
                    "sound": "snd-s",
                    "correct": "tree",
                    "options": [
                        _opt("tree", "Ветер в траве", IMG["tree"]),
                        _opt("motor", "Мотор", IMG["motor"]),
                    ],
                }
            ],
            "spark": True,
            "spark_kind": "sound",
            "spark_group": "sound",
        },
        {
            "id": "hop",
            "title": "Прыжки",
            "kind": "letter_maze",
            "mechanic": "letter_hop",
            "slovik_line": "Прыгай на С. Она говорит с-с-с.",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l04-hop",
            "letter": "С",
            "start": [0, 0],
            "end": [3, 3],
            "grid": [
                ["С", "М", "А", "У"],
                ["С", "С", "С", "О"],
                ["А", "М", "С", "С"],
                ["О", "У", "М", "С"]
            ],
            "spark": False,
        },
        {
            "id": "grid",
            "title": "Найди все С",
            "chapter": "Искорка 2 · Буква",
            "kind": "letter_puzzle",
            "mechanic": "letter_grid",
            "slovik_line": "Найди все буквы С на доске.",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l04-grid",
            "slots": 5,
            "pieces": [
                {"id": "s1", "label": "С", "correct": True},
                {"id": "m1", "label": "М", "correct": False},
                {"id": "s2", "label": "С", "correct": True},
                {"id": "a1", "label": "А", "correct": False},
                {"id": "s3", "label": "С", "correct": True},
                {"id": "o1", "label": "О", "correct": False},
                {"id": "s4", "label": "С", "correct": True},
                {"id": "u1", "label": "У", "correct": False},
                {"id": "s5", "label": "С", "correct": True},
            ],
            "spark": True,
            "spark_kind": "letter",
            "spark_group": "letter",
        },
        {
            "id": "count",
            "title": "Шесть С",
            "kind": "catch_letter",
            "mechanic": "letter_count",
            "slovik_line": "Собери шесть С у воды.",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l04-count",
            "letter": "С",
            "letters": ["С", "М", "А", "О", "У"],
            "letter_sounds": {"С": "snd-s", "М": "snd-m", "А": "snd-a", "О": "snd-o", "У": "snd-u"},
            "catches": 6,
            "spark": False,
        },
        {
            "id": "pause",
            "title": "Пауза",
            "kind": "break",
            "slovik_line": "Тихое с-с-с, как ветер в траве.",
            "audio": "bo-m1-l04-pause",
            "spark": False,
            "hint": "Тихо скажи с-с-с. Не путай с ш-ш-ш.",
        },
        {
            "id": "slots",
            "title": "СА, СО, ОС",
            "chapter": "Искорка 3 · Слог",
            "kind": "slot_build",
            "slovik_line": "Слоги: са, со, ос.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-slots",
            "targets": ["С", "А"],
            "options": ["С", "О", "А", "М"],
            "result_label": "СА",
            "spark": True,
            "spark_kind": "syllable",
            "spark_group": "syllable",
        },
        {
            "id": "or",
            "title": "Змейка или мотор",
            "kind": "listen_pick",
            "mechanic": "or_choice",
            "slovik_line": "Кто говорит с-с-с — змейка или мотор?",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-or",
            "picture_only": True,
            "rounds": [
                {
                    "sound": "snd-s",
                    "correct": "snake",
                    "options": [
                        _opt("snake", "Змейка", IMG["tree"]),
                        _opt("motor", "Мотор", IMG["motor"]),
                    ],
                }
            ],
            "spark": False,
        },
        {
            "id": "quest",
            "title": "Слог СО",
            "kind": "mini_quest",
            "slovik_line": "Слог со. Где рыбка?",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-quest",
            "spark": False,
            "steps": [
                {"kind": "find", "correct": "СО", "options": ["СА", "СО", "ОС", "МО"]},
            ],
        },
        _reward(
            audio="bo-m1-l04-reward",
            line="Змейка С с нами! Ты знаешь букву С.",
            parent="Урок «Змейка: с-с-с!». Дома тихое с-с-с, не ш-ш-ш.",
            badge_line="Знаю букву С",
        ),
    ]


def _stories_1() -> list[dict[str, Any]]:
    return [
        {
            "id": "hello",
            "title": "Короб на полу",
            "kind": "intro_video",
            "slovik_line": "В доме что-то новое. Посмотрим!",
            "slovik_pose": "wave",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l01-hi",
            "cta_label": "Начать",
            "spark": False,
        },
        {
            "id": "screen",
            "title": "Слово КОРОБ",
            "chapter": "Слово",
            "kind": "word_picture",
            "mechanic": "word_screen",
            "slovik_line": "Прочитай слово. Короб.",
            "slovik_pose": "talk",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l01-screen",
            "spark": False,
            "items": [
                {
                    "word": "КОРОБ",
                    "correct": "box",
                    "options": [
                        _opt("box", "Короб", IMG["house"]),
                        _opt("kot", "Кот", IMG["kot"]),
                        _opt("ball", "Мяч", IMG["ball"]),
                    ],
                }
            ],
        },
        {
            "id": "what",
            "title": "Что там?",
            "kind": "find",
            "slovik_line": "Что там? Выбери картинку.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l01-what",
            "rounds": [
                {
                    "prompt_text": "Сначала короб пустой.",
                    "correct": "empty",
                    "options": [
                        _opt("empty", "ПУСТО"),
                        _opt("kot", "КОТ", IMG["kot"]),
                        _opt("ball", "МЯЧ", IMG["ball"]),
                    ],
                }
            ],
            "spark": False,
        },
        {
            "id": "drag",
            "title": "Слово к картинке",
            "kind": "match_pairs",
            "mechanic": "drag_match",
            "slovik_line": "Перетащи слово к картинке.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l01-drag",
            "hint": "Нажми на слово, потом на картинку.",
            "pairs": [
                {"id": "korob", "label": "КОРОБ", "image": IMG["house"]},
                {"id": "kot", "label": "КОТ", "image": IMG["kot"]},
                {"id": "myach", "label": "МЯЧ", "image": IMG["ball"]},
            ],
            "spark": True,
            "spark_kind": "word",
            "spark_group": "word",
        },
        {
            "id": "open",
            "title": "Открой короб",
            "kind": "mini_quest",
            "slovik_line": "Открой короб. Смотри… вот мяч!",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l01-open",
            "spark": False,
            "steps": [
                {"kind": "find", "prompt": "СМОТРИ", "correct": "look", "options": [_opt("look", "СМОТРИ"), _opt("sleep", "СПИТ")]},
                {
                    "kind": "find",
                    "prompt": "Что в коробе?",
                    "correct": "ball",
                    "options": [
                        _opt("empty", "ПУСТО"),
                        _opt("ball", "ВОТ МЯЧ", IMG["ball"]),
                        _opt("syr", "СЫР", IMG["syr"]),
                    ],
                },
            ],
        },
        {
            "id": "slots",
            "title": "Вот мяч",
            "kind": "slot_build",
            "mechanic": "phrase_slots",
            "slovik_line": "Собери: вот мяч.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l01-slots",
            "targets": ["ВОТ", "МЯЧ"],
            "options": ["ДОМ", "ВОТ", "СЫР", "МЯЧ"],
            "result_label": "ВОТ МЯЧ",
            "spark": False,
            "spark_group": "phrase",
        },
        {
            "id": "feel",
            "title": "Кот рад",
            "kind": "phrase_picture",
            "slovik_line": "Кот рад. Где такая картинка?",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l01-feel",
            "phrase": "КОТ РАД",
            "correct": "happy",
            "picture_only": True,
            "options": [
                _opt("sleep", "Спит", IMG["sleep"]),
                _opt("happy", "Рад", IMG["kot"]),
                _opt("eat", "Ест", IMG["eat"]),
            ],
            "spark": True,
            "spark_kind": "phrase",
            "spark_group": "phrase",
        },
        {
            "id": "book",
            "title": "Кот и коробка",
            "kind": "book_page",
            "slovik_line": "Теперь книжка. Читай сам. Я рядом.",
            "slovik_pose": "joy",
            "scene_image": f"{ST}/scene-book.jpg",
            "audio": "ph-m1-l01-book",
            "book_title": "Кот и коробка",
            "cta_label": "Я прочитал!",
            "lines": [
                {"text": "ВОТ КОРОБ.", "image": IMG["house"], "alt": "Короб", "audio": "ph-m1-l01-p1"},
                {"text": "ЧТО ТАМ?", "image": IMG["kot"], "alt": "Кот смотрит", "audio": "ph-m1-l01-p2"},
                {"text": "НЕ ТУТ.", "image": IMG["house"], "alt": "Пусто", "audio": "ph-m1-l01-p3"},
                {"text": "ВОТ МЯЧ!", "image": IMG["ball"], "alt": "Мяч", "audio": "ph-m1-l01-p4"},
                {"text": "КОТ РАД.", "image": IMG["kot"], "alt": "Кот рад", "audio": "ph-m1-l01-p5"},
            ],
            "finale": "Книжка прочитана!",
            "spark": False,
        },
        _reward(
            audio="ph-m1-l01-reward",
            line="Книжка встала на полку. Молодец!",
            parent="Урок «Кот и коробка». Дома ещё раз: ВОТ КОРОБ. ВОТ МЯЧ. КОТ РАД.",
            badge_line="Книжка на полке",
        ),
    ]


def _stories_2() -> list[dict[str, Any]]:
    return [
        {
            "id": "hello",
            "title": "Окно",
            "kind": "intro_video",
            "slovik_line": "Посмотри в окно вместе со мной.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l02-hi",
            "cta_label": "Начать",
            "spark": False,
        },
        {
            "id": "screen",
            "title": "Слово ДОЖДЬ",
            "kind": "word_picture",
            "mechanic": "word_screen",
            "slovik_line": "Это слово: дождь.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l02-screen",
            "items": [
                {
                    "word": "ДОЖДЬ",
                    "correct": "rain",
                    "options": [
                        _opt("rain", "Дождь", IMG["rain"]),
                        _opt("sun", "Солнце", IMG["bird"]),
                    ],
                }
            ],
            "spark": False,
        },
        {
            "id": "weather",
            "title": "Дождь или солнце",
            "chapter": "Искорка 1",
            "kind": "listen_pick",
            "slovik_line": "Дождь или солнце?",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l02-weather",
            "picture_only": True,
            "rounds": [{"correct": "rain", "options": [_opt("rain", "Дождь", IMG["rain"]), _opt("sun", "Солнце", IMG["bird"])]}],
            "spark": True,
            "spark_kind": "word",
            "spark_group": "word",
        },
        {
            "id": "who",
            "title": "Кто у окна?",
            "kind": "find",
            "slovik_line": "Кто у окна?",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l02-who",
            "rounds": [
                {
                    "correct": "kot",
                    "options": [
                        _opt("mama", "МАМА", IMG["mama"]),
                        _opt("kot", "КОТ", IMG["kot"]),
                        _opt("ball", "МЯЧ", IMG["ball"]),
                    ],
                }
            ],
            "spark": False,
        },
        {
            "id": "drag",
            "title": "Слова к картинкам",
            "kind": "match_pairs",
            "mechanic": "drag_match",
            "slovik_line": "Слово к картинке.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l02-drag",
            "pairs": [
                {"id": "okno", "label": "ОКНО", "image": IMG["house"]},
                {"id": "dozhd", "label": "ДОЖДЬ", "image": IMG["rain"]},
                {"id": "kot", "label": "КОТ", "image": IMG["kot"]},
            ],
            "spark": False,
        },
        {
            "id": "slots",
            "title": "Кот у окна",
            "kind": "slot_build",
            "mechanic": "phrase_slots",
            "slovik_line": "Собери: кот у окна.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l02-slots",
            "targets": ["КОТ", "У", "ОКНА"],
            "options": ["МЯЧ", "КОТ", "СЫР", "У", "ОКНА"],
            "result_label": "КОТ У ОКНА",
            "spark": True,
            "spark_kind": "phrase",
            "spark_group": "phrase",
        },
        {
            "id": "extra",
            "title": "Лишнее слово",
            "kind": "find",
            "slovik_line": "Какое слово лишнее?",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l02-extra",
            "rounds": [
                {
                    "prompt_text": "Слова про окно и дождь.",
                    "correct": "syr",
                    "options": [
                        _opt("okno", "ОКНО"),
                        _opt("dozhd", "ДОЖДЬ"),
                        _opt("kot", "КОТ"),
                        _opt("syr", "СЫР"),
                    ],
                }
            ],
            "spark": False,
        },
        {
            "id": "book",
            "title": "Дождь за окном",
            "kind": "book_page",
            "slovik_line": "Книжка про дождь. Читай.",
            "scene_image": f"{ST}/scene-book.jpg",
            "audio": "ph-m1-l02-book",
            "book_title": "Дождь за окном",
            "cta_label": "Я прочитал!",
            "lines": [
                {"text": "ИДЁТ ДОЖДЬ.", "image": IMG["rain"], "audio": "ph-m1-l02-p1"},
                {"text": "КОТ У ОКНА.", "image": IMG["kot"], "audio": "ph-m1-l02-p2"},
                {"text": "ТИХО ДОМА.", "image": IMG["house"], "audio": "ph-m1-l02-p3"},
                {"text": "КОТ СПИТ.", "image": IMG["sleep"], "audio": "ph-m1-l02-p4"},
                {"text": "НОЧЬ.", "image": IMG["night"], "audio": "ph-m1-l02-p5"},
            ],
            "spark": False,
        },
        _reward(
            audio="ph-m1-l02-reward",
            line="Ещё одна книжка на полке.",
            parent="Урок «Дождь за окном». Дома: ИДЁТ ДОЖДЬ. КОТ У ОКНА.",
            badge_line="Книжка на полке",
        ),
    ]


def _stories_3() -> list[dict[str, Any]]:
    return [
        {
            "id": "hello",
            "title": "Мяч пропал",
            "kind": "intro_video",
            "slovik_line": "Мяч снова пропал! Поищем по дому.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l03-hi",
            "cta_label": "Начать",
            "spark": False,
        },
        {
            "id": "hunt",
            "title": "Где мяч?",
            "chapter": "Искорка 1",
            "kind": "scene_hunt",
            "slovik_line": "Где мяч? Загляни в комнаты.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l03-hunt",
            "layout": "grid",
            "grid_cols": 3,
            "correct_ids": ["hall"],
            "wrong_msg": "Не тут.",
            "success_msg": "Вот мяч!",
            "hotspots": [
                {"id": "kitchen", "label": "Кухня", "image": IMG["syr"], "x": 20, "y": 50},
                {"id": "room", "label": "Комната", "image": IMG["sleep"], "x": 50, "y": 50},
                {"id": "hall", "label": "Коридор", "image": IMG["ball"], "x": 80, "y": 50},
            ],
            "spark": True,
            "spark_kind": "word",
            "spark_group": "word",
        },
        {
            "id": "under",
            "title": "Под стулом",
            "kind": "find",
            "slovik_line": "Мяч под стулом или на диване?",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l03-under",
            "rounds": [
                {
                    "prompt_text": "ПОД",
                    "correct": "under",
                    "options": [
                        _opt("sofa", "НА диване", IMG["sleep"]),
                        _opt("under", "ПОД стулом", IMG["ball"]),
                    ],
                }
            ],
            "spark": False,
        },
        {
            "id": "slots",
            "title": "Где мяч — вот мяч",
            "kind": "slot_build",
            "mechanic": "phrase_slots",
            "slovik_line": "Собери вопрос: где мяч? Потом: вот мяч!",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l03-slots",
            "targets": ["ГДЕ", "МЯЧ"],
            "options": ["ВОТ", "ГДЕ", "КОТ", "МЯЧ"],
            "result_label": "ГДЕ МЯЧ",
            "spark": False,
        },
        {
            "id": "run",
            "title": "Бежит, ловит, рад",
            "kind": "mini_quest",
            "slovik_line": "Кот бежит. Кот ловит. Кот рад.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l03-run",
            "spark": True,
            "spark_kind": "phrase",
            "spark_group": "phrase",
            "steps": [
                {
                    "kind": "phrase_picture",
                    "phrase": "КОТ БЕЖИТ",
                    "correct": "run",
                    "options": [
                        _opt("sleep", "Спит", IMG["sleep"]),
                        _opt("run", "Бежит", IMG["kot"]),
                    ],
                },
                {
                    "kind": "phrase_picture",
                    "phrase": "КОТ РАД",
                    "correct": "happy",
                    "options": [
                        _opt("eat", "Ест", IMG["eat"]),
                        _opt("happy", "Рад", IMG["kot"]),
                    ],
                },
            ],
        },
        {
            "id": "where",
            "title": "Картинка к вопросу",
            "kind": "phrase_picture",
            "slovik_line": "Где мяч? Выбери картинку.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l03-where",
            "phrase": "ГДЕ МЯЧ?",
            "correct": "ball",
            "picture_only": True,
            "options": [
                _opt("kot", "Кот", IMG["kot"]),
                _opt("ball", "Мяч", IMG["ball"]),
                _opt("house", "Дом", IMG["house"]),
            ],
            "spark": False,
        },
        {
            "id": "book",
            "title": "Где мяч?",
            "kind": "book_page",
            "slovik_line": "История про мяч. Читай.",
            "scene_image": f"{ST}/scene-book.jpg",
            "audio": "ph-m1-l03-book",
            "book_title": "Где мяч?",
            "cta_label": "Я прочитал!",
            "lines": [
                {"text": "ГДЕ МЯЧ?", "image": IMG["kot"], "audio": "ph-m1-l03-p1"},
                {"text": "НЕ ТУТ.", "image": IMG["syr"], "audio": "ph-m1-l03-p2"},
                {"text": "НЕ ТУТ.", "image": IMG["sleep"], "audio": "ph-m1-l03-p3"},
                {"text": "ВОТ МЯЧ!", "image": IMG["ball"], "audio": "ph-m1-l03-p4"},
                {"text": "КОТ РАД.", "image": IMG["kot"], "audio": "ph-m1-l03-p5"},
            ],
            "spark": False,
        },
        _reward(
            audio="ph-m1-l03-reward",
            line="Мяч нашёлся. Книжка на полке.",
            parent="Урок «Где мяч?». Дома: ГДЕ МЯЧ? НЕ ТУТ. ВОТ МЯЧ!",
            badge_line="Книжка на полке",
        ),
    ]


def _stories_4() -> list[dict[str, Any]]:
    return [
        {
            "id": "hello",
            "title": "Память",
            "kind": "intro_video",
            "slovik_line": "Сегодня без новой книжки. Проверим, что ты помнишь.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l04-hi",
            "cta_label": "Начать",
            "spark": False,
        },
        {
            "id": "which",
            "title": "Какая книжка?",
            "chapter": "Искорка 1",
            "kind": "find",
            "slovik_line": "Какая это книжка? Найди обложку.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l04-which",
            "rounds": [
                {
                    "prompt_image": IMG["ball"],
                    "prompt_alt": "Мяч",
                    "correct": "ball_book",
                    "options": [
                        _opt("home", "Дома", IMG["cover_home"]),
                        _opt("box", "Кот и коробка", IMG["house"]),
                        _opt("rain", "Дождь за окном", IMG["rain"]),
                        _opt("ball_book", "Где мяч?", IMG["ball"]),
                    ],
                }
            ],
            "spark": True,
            "spark_kind": "word",
            "spark_group": "word",
        },
        {
            "id": "phrase",
            "title": "Фраза к картинке",
            "kind": "phrase_picture",
            "slovik_line": "Какая фраза подходит к картинке?",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l04-phrase",
            "phrase": "?",
            "prompt_image": IMG["rain"],
            "prompt_alt": "Дождь",
            "correct": "rain",
            "options": [
                _opt("box", "ВОТ КОРОБ"),
                _opt("rain", "ИДЁТ ДОЖДЬ"),
                _opt("ball", "ВОТ МЯЧ!"),
            ],
            "spark": False,
        },
        {
            "id": "order",
            "title": "По порядку",
            "kind": "slot_build",
            "mechanic": "order_step",
            "slovik_line": "Расставь по порядку. Сначала первое, потом второе, потом третье.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l04-order",
            "targets": ["ГДЕ МЯЧ?", "НЕ ТУТ", "ВОТ МЯЧ!"],
            "options": ["ВОТ МЯЧ!", "ГДЕ МЯЧ?", "КОТ РАД", "НЕ ТУТ"],
            "result_label": "ГДЕ МЯЧ? НЕ ТУТ ВОТ МЯЧ!",
            "spark": True,
            "spark_kind": "phrase",
            "spark_group": "phrase",
        },
        {
            "id": "who",
            "title": "Кто? Что делает?",
            "kind": "find",
            "slovik_line": "Кто? Что делает?",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l04-who",
            "rounds": [
                {
                    "prompt_text": "Кто?",
                    "correct": "kot",
                    "options": [_opt("kot", "КОТ", IMG["kot"]), _opt("ball", "МЯЧ", IMG["ball"])],
                },
                {
                    "prompt_text": "Что делает?",
                    "correct": "sleep",
                    "options": [_opt("sleep", "СПИТ"), _opt("wait", "ЖДЁТ"), _opt("run", "БЕЖИТ")],
                },
            ],
            "spark": False,
        },
        {
            "id": "drag",
            "title": "Слова из книжек",
            "kind": "match_pairs",
            "mechanic": "drag_match",
            "slovik_line": "Слово к картинке. Ты это уже читал.",
            "scene_image": SCENE_ST,
            "audio": "ph-m1-l04-drag",
            "pairs": [
                {"id": "dom", "label": "ДОМ", "image": IMG["house"]},
                {"id": "kot", "label": "КОТ", "image": IMG["kot"]},
                {"id": "myach", "label": "МЯЧ", "image": IMG["ball"]},
                {"id": "dozhd", "label": "ДОЖДЬ", "image": IMG["rain"]},
            ],
            "spark": False,
        },
        {
            "id": "spread",
            "title": "Открой книжку",
            "kind": "book_page",
            "slovik_line": "Открой любую книжку и прочитай разворот.",
            "scene_image": f"{ST}/scene-book.jpg",
            "audio": "ph-m1-l04-spread",
            "book_title": "Дома",
            "cta_label": "Я прочитал!",
            "lines": [
                {"text": "ВОТ МОЙ ДОМ.", "spread_image": f"{ST}/book-home-01.jpg", "image": IMG["house"]},
                {"text": "ВОТ МОЙ КОТ.", "spread_image": f"{ST}/book-home-02.jpg", "image": IMG["kot"]},
                {"text": "КОТ ЕСТ СЫР.", "spread_image": f"{ST}/book-home-03.jpg", "image": IMG["eat"]},
            ],
            "spark": False,
        },
        _reward(
            audio="ph-m1-l04-reward",
            line="Ты помнишь мои книжки! Искорка с нами.",
            parent="Урок «Словик проверяет память». Новой книжки нет — перечитайте любую из четырёх.",
            badge_line="Помню книжки",
        ),
    ]


LETTERS: dict[int, list[dict[str, Any]]] = {
    1: _letters_1(),
    2: _letters_2(),
    3: _letters_3(),
    4: _letters_4(),
}

STORIES: dict[int, list[dict[str, Any]]] = {
    1: _stories_1(),
    2: _stories_2(),
    3: _stories_3(),
    4: _stories_4(),
}

LETTERS_META = {
    1: {"title": "Мотор на поляне", "badge": "Знаю букву М"},
    2: {"title": "Поющая У", "badge": "Знаю букву У"},
    3: {"title": "Круглая О", "badge": "Знаю букву О"},
    4: {"title": "Змейка: с-с-с!", "badge": "Знаю букву С"},
}

STORIES_META = {
    1: {"title": "Кот и коробка", "badge": "Первый шаг"},
    2: {"title": "Дождь за окном", "badge": "Первый шаг"},
    3: {"title": "Где мяч?", "badge": "Первый шаг"},
    4: {"title": "Словик проверяет память", "badge": "Первый шаг"},
}


def stations_for(course: str, lesson_n: int) -> list[dict[str, Any]] | None:
    table = LETTERS if course == "letters" else STORIES
    rows = table.get(lesson_n)
    return deepcopy(rows) if rows else None


def apply_to_catalog(lessons_dir) -> list[str]:
    """Пишет станции уроков 1–4 в self_paced и with_teacher JSON."""
    import json
    from pathlib import Path

    root = Path(lessons_dir)
    written: list[str] = []
    note = "Станции модуля 1 · уроки 1–4 (1, 3, 8, 10 сентября). Новые механики — поле mechanic."
    jobs = (
        ("letters", "early-letters", LETTERS, LETTERS_META, "искорки"),
        ("stories", "early-stories", STORIES, STORIES_META, "искорки"),
    )
    for course, group, table, meta, goal in jobs:
        for n, stations in table.items():
            info = meta[n]
            for tariff in ("self_paced", "with_teacher"):
                path = root / f"{group}-{tariff}-stage-1-lesson-{n:02d}.json"
                data = json.loads(path.read_text(encoding="utf-8"))
                data["title"] = info["title"]
                data["tale_title"] = info["title"]
                data["badge"] = info["badge"]
                data["stations"] = deepcopy(stations)
                data["note"] = note
                data["quest"] = {"goal_label": goal, "goal_count": 3}
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                written.append(path.name)
    return written


if __name__ == "__main__":
    from pathlib import Path

    out = apply_to_catalog(Path(__file__).resolve().parent / "catalog")
    print("updated", len(out), "files")
    for name in out:
        print(" ", name)
