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
SCENE_TRAIL = f"{L}/scene-trail-path.jpg"
SCENE_BOARD = f"{L}/scene-forest-board.jpg"
SCENE_WATER = f"{L}/scene-water-count.jpg"
SCENE_COMIC = f"{L}/scene-comic-book.jpg"
SCENE_HOME = f"{ST}/scene-home-floor.jpg"
SCENE_RAIN = f"{ST}/scene-window-rain.jpg"
SPARK = f"{L}/spark.png"


def where_map(lesson_n: int) -> str:
    """Карта «где сейчас» для входа в урок букв (площадка 1–8)."""
    n = max(1, min(8, int(lesson_n)))
    return f"{L}/scene-map-sounds-where-{n:02d}.png"

IMG = {
    "motor": f"{L}/motor.png",
    "rain": f"{L}/rain.png",
    "ball": f"{L}/ball.png",
    "cup": f"{L}/cup.png",
    "round_ball": f"{L}/round-ball.png",
    "round_cup": f"{L}/round-cup.png",
    "round_lake": f"{L}/round-lake.png",
    "mama": f"{L}/mama.png",
    "carrot": f"{L}/carrot.png",
    "kot": f"{L}/kot.png",
    "house": f"{L}/house.png",
    "syr": f"{L}/syr.png",
    "bird": f"{L}/bird.png",
    "sun": f"{L}/sun-smile.png",
    "sun_clear": f"{ST}/sun-clear.png",
    "tree": f"{L}/tree.png",
    "aist": f"{L}/aist.png",
    "wind": f"{L}/wind-howl.png",
    "duck": f"{L}/duck.png",
    "cow": f"{L}/cow.png",
    "wasp": f"{L}/wasp.png",
    "snake": f"{L}/snake-hiss.png",
    "bear": f"{L}/bear-wise.png",
    "som": f"{L}/som-fish.png",
    "box_sq": f"{L}/box-square.png",
    "letter_u": f"{L}/letter-u-hero.png",
    "letter_o": f"{L}/letter-o-hero.png",
    "letter_s": f"{L}/letter-s-hero.png",
    "sleep": f"{ST}/kot-sleep.png",
    "run": f"{ST}/cat-run.png",
    "eat": f"{ST}/kot-eat.png",
    "catch": f"{ST}/cat-catch.png",
    "happy": f"{ST}/cat-happy.png",
    "box": f"{ST}/box-closed.png",
    "box_empty": f"{ST}/box-empty.png",
    "box_ball": f"{ST}/box-ball.png",
    "window": f"{ST}/window-frame.png",
    "ball_under": f"{ST}/ball-under-chair.png",
    "ball_sofa": f"{ST}/ball-on-sofa.png",
    "slovik_screen": f"{ST}/slovik-screen.png",
    "kitchen": f"{ST}/scene-kitchen.jpg",
    "room": f"{ST}/scene-room.jpg",
    "hall": f"{ST}/scene-hall.jpg",
    "night": f"{ST}/scene-night-sleep.jpg",
    "cover_home": f"{ST}/book-cover-home.png",
    "cover_box": f"{ST}/cover-box.jpg",
    "cover_rain": f"{ST}/cover-rain.jpg",
    "cover_ball": f"{ST}/cover-ball.jpg",
    "shelf": f"{ST}/shelf-four.jpg",
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


def _sort_big_small(
    letter: str,
    *,
    audio: str,
    scene: str = SCENE_L,
    spark: bool = False,
    spark_kind: str | None = None,
    chapter: str = "Искорка 2 · Буква",
) -> dict[str, Any]:
    """Общая станция: большая / маленькая буква."""
    big = letter.upper()
    small = letter.lower()
    st: dict[str, Any] = {
        "id": "sort",
        "title": f"Большая и маленькая {big}",
        "chapter": chapter,
        "kind": "sort_two",
        "slovik_line": f"Большая {big} и маленькая {small} — одна буква. Разложи.",
        "slovik_pose": "hint",
        "scene_image": scene,
        "audio": audio,
        "left": {"label": big, "correct": [f"{big}1", f"{big}2", f"{big}3"]},
        "right": {"label": small, "correct": [f"{small}1", f"{small}2", f"{small}3"]},
        "options": [
            {"id": f"{big}1", "label": big},
            {"id": f"{small}1", "label": small},
            {"id": f"{big}2", "label": big},
            {"id": f"{small}2", "label": small},
            {"id": f"{big}3", "label": big},
            {"id": f"{small}3", "label": small},
        ],
        "spark": spark,
        "spark_group": "letter",
    }
    if spark and spark_kind:
        st["spark_kind"] = spark_kind
    return st


def _chase_meadow(
    letter: str,
    *,
    audio: str,
    scene: str = SCENE_L,
    slovik_line: str | None = None,
) -> dict[str, Any]:
    """Общая станция: ловля большой и маленькой буквы на поляне."""
    big = letter.upper()
    small = letter.lower()
    pool = ["А", "М", "У", "О", "С"]
    distractors = [x for x in pool if x != big][:3]
    hotspots = [
        {"id": f"{big}1", "label": big, "x": 14, "y": 10},
        {"id": f"{distractors[0]}1", "label": distractors[0], "x": 34, "y": 8},
        {"id": f"{distractors[1]}1", "label": distractors[1], "x": 54, "y": 12},
        {"id": f"{distractors[2]}1", "label": distractors[2], "x": 74, "y": 9},
        {"id": f"{small}1", "label": small, "x": 91, "y": 20, "size": "sm"},
        {"id": f"{distractors[0]}2", "label": distractors[0], "x": 10, "y": 42},
        {"id": f"{distractors[1]}2", "label": distractors[1], "x": 90, "y": 46},
        {"id": f"{big}2", "label": big, "x": 12, "y": 78},
        {"id": f"{small}2", "label": small, "x": 48, "y": 86, "size": "sm"},
        {"id": f"{distractors[2]}2", "label": distractors[2], "x": 88, "y": 82},
        {"id": f"{big}3", "label": big, "x": 30, "y": 90},
    ]
    return {
        "id": "chase",
        "title": f"Поймай {big} на поляне",
        "chapter": "Искорка 2 · Буква",
        "kind": "scene_hunt",
        "mechanic": "letter_chase",
        "slovik_line": slovik_line
        or (
            f"Теперь поймай их на поляне. Найди большую {big} и маленькую {small}. "
            "Не спутай с другими буквами."
        ),
        "slovik_pose": "hint",
        "scene_image": scene,
        "audio": audio,
        "moving": True,
        "move_speed": 5,
        "success_msg": f"Поймал и {big}, и маленькую {small}!",
        "wrong_msg": f"Это не {big} и не {small}. Ищи дальше.",
        "correct_ids": [f"{big}1", f"{small}1", f"{big}2", f"{small}2", f"{big}3"],
        "hotspots": hotspots,
        "spark": False,
        "spark_group": "letter",
    }


def _board_letters(letter: str, *, audio: str, scene: str = SCENE_BOARD) -> dict[str, Any]:
    big = letter.upper()
    grid = [
        "А", big, "О", "М", "У",
        "К", big, "Н", "А", "О",
        "М", big, "С", "К", "А",
        "О", big, "М", "Н", big,
    ]
    hotspots = []
    correct = []
    counts: dict[str, int] = {}
    for i, lab in enumerate(grid):
        counts[lab] = counts.get(lab, 0) + 1
        hid = f"{lab.lower()}{counts[lab]}"
        hotspots.append({"id": hid, "label": lab})
        if lab == big:
            correct.append(hid)
    return {
        "id": "board",
        "title": "Доска букв",
        "chapter": "Буква",
        "kind": "scene_hunt",
        "mechanic": "letter_board",
        "board_panel": True,
        "slovik_line": f"Найди на доске все буквы {big}. Их несколько.",
        "slovik_pose": "hint",
        "scene_image": scene,
        "audio": audio,
        "layout": "grid",
        "grid_cols": 5,
        "moving": False,
        "correct_ids": correct,
        "hotspots": hotspots,
        "spark": False,
        "spark_group": "letter",
    }


def _meadow_catch(letter: str, *, audio: str, scene: str = SCENE_L) -> dict[str, Any]:
    big = letter.upper()
    return {
        "id": "catch",
        "title": f"Поймай {big}",
        "chapter": "Буква",
        "kind": "catch_letter",
        "mechanic": "letter_meadow",
        "slovik_line": f"На поляне появится буква {big}. Нажми на неё — три раза в разных местах!",
        "slovik_pose": "talk",
        "scene_image": scene,
        "audio": audio,
        "letter": big,
        "appear_on_scene": True,
        "catches": 3,
        "spots": [
            {"x": 22, "y": 28},
            {"x": 74, "y": 26},
            {"x": 48, "y": 40},
            {"x": 18, "y": 58},
            {"x": 78, "y": 56},
            {"x": 58, "y": 70},
            {"x": 34, "y": 66},
        ],
        "spark": False,
        "spark_group": "letter",
    }


def _letters_1() -> list[dict[str, Any]]:
    return [
        {
            "id": "trail",
            "title": "Тропа букв",
            "kind": "intro_video",
            "slovik_line": "На тропе зажглась новая буква. Помнишь машину? Она говорит: м-м-м. Познакомься с буквой М.",
            "slovik_pose": "wave",
            "scene_image": f"{L}/scene-m-meadow-intro.jpg",
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
            "letter_image": f"{L}/letter-m-hero.png",
            "hint": "Нажми на букву — услышишь звук.",
            "coach_success": "М-м-м! Это буква М. Дальше соберём искорки.",
            "spark": False,
        },
        {
            "id": "spread",
            "title": "Первая азбука",
            "chapter": "Буква",
            "kind": "alphabet_book",
            "mechanic": "azbuka_fill",
            "slovik_line": "Сложи свою первую азбуку. Выбери картинки, которые начинаются на букву М.",
            "slovik_pose": "talk",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-spread",
            "letter": "М",
            "letter_image": f"{L}/letter-m-hero.png",
            "book_title": "Медведь и Машина",
            "picture_only": False,
            "hint": "Картинка должна начинаться на М.",
            "success_msg": "Страница М готова!",
            "rounds": [
                {
                    "correct": "motor",
                    "options": [
                        _opt("motor", "машина", IMG["motor"]),
                        _opt("sun", "солнце", IMG["sun"]),
                    ],
                },
                {
                    "correct": "bear",
                    "options": [
                        _opt("bear", "медведь", IMG["bear"]),
                        _opt("kot", "кот", IMG["kot"]),
                    ],
                },
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "motor",
            "title": "Кто гудит?",
            "chapter": "Искорка 1 · Звук",
            "kind": "listen_pick",
            "slovik_line": "Что гудит м-м-м? Машина или дождь?",
            "slovik_pose": "listen",
            "scene_image": SCENE_MISS,
            "audio": "bo-m1-l01-motor",
            "picture_only": True,
            "rounds": [
                {
                    "sound": "snd-m",
                    "correct": "motor",
                    "options": [
                        _opt("motor", "Машина", IMG["motor"]),
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
            "title": "Лабиринт из М",
            "chapter": "Буква",
            "kind": "letter_maze",
            "mechanic": "letter_hop",
            "slovik_line": "Прыгай только на букву, которая говорит м-м-м.",
            "slovik_pose": "talk",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l01-hop",
            "letter": "М",
            "start": [0, 0],
            "end": [4, 4],
            "grid": [
                ["М", "А", "У", "О", "С"],
                ["М", "М", "А", "У", "О"],
                ["А", "М", "М", "М", "С"],
                ["О", "М", "А", "М", "А"],
                ["С", "О", "У", "М", "М"],
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "build",
            "title": "Обведи М",
            "chapter": "Буква",
            "kind": "dot_connect",
            "mechanic": "dot_connect",
            "slovik_line": "Соедини точки по порядку — получится буква М.",
            "slovik_pose": "hint",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l01-build",
            "letter": "М",
            "hint": "Жми точки по номерам: 1, 2, 3…",
            "success_msg": "Буква М получилась!",
            "dots": [
                {"n": 1, "x": 18, "y": 88},
                {"n": 2, "x": 18, "y": 12},
                {"n": 3, "x": 50, "y": 72},
                {"n": 4, "x": 82, "y": 12},
                {"n": 5, "x": 82, "y": 88},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        _sort_big_small("М", audio="bo-m1-l01-sort"),
        _chase_meadow("М", audio="bo-m1-l01-chase"),
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
            "id": "or",
            "title": "Машина или солнце",
            "chapter": "Искорка 2 · Буква",
            "kind": "listen_pick",
            "mechanic": "or_choice",
            "slovik_line": "Буква М. Что начинается на букву М — машина или солнце?",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-or",
            "picture_only": True,
            "rounds": [
                {
                    "sound": "snd-m",
                    "correct": "motor",
                    "options": [
                        _opt("motor", "Машина", IMG["motor"]),
                        _opt("sun", "Солнце", IMG["sun"]),
                    ],
                }
            ],
            "spark": True,
            "spark_kind": "letter",
            "spark_group": "letter",
        },
        {
            "id": "first_letter",
            "title": "Первая буква",
            "chapter": "Буква",
            "kind": "find",
            "mechanic": "picture_first_letter",
            "slovik_line": "Смотри картинку. С какой буквы начинается слово? Нажми букву.",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-first",
            "spark": False,
            "spark_group": "letter",
            "hint": "Скажи слово вслух и найди первую букву.",
            "rounds": [
                {
                    "prompt_text": "С какой буквы?",
                    "prompt_image": IMG["bear"],
                    "prompt_alt": "медведь",
                    "correct": "М",
                    "options": ["А", "О", "М", "У"],
                },
                {
                    "prompt_text": "С какой буквы?",
                    "prompt_image": IMG["motor"],
                    "prompt_alt": "машина",
                    "correct": "М",
                    "options": ["С", "М", "А", "О"],
                },
                {
                    "prompt_text": "С какой буквы?",
                    "prompt_image": IMG["carrot"],
                    "prompt_alt": "морковка",
                    "correct": "М",
                    "options": ["У", "А", "М", "О"],
                },
            ],
        },
        {
            "id": "board",
            "title": "Доска букв",
            "chapter": "Буква",
            "kind": "scene_hunt",
            "mechanic": "letter_board",
            "board_panel": True,
            "slovik_line": "Найди на доске все буквы М. Их несколько.",
            "slovik_pose": "hint",
            "scene_image": SCENE_BOARD,
            "audio": "bo-m1-l01-board",
            "layout": "grid",
            "grid_cols": 5,
            "moving": False,
            "correct_ids": ["m1", "m2", "m3", "m4", "m5"],
            "hotspots": [
                {"id": "a1", "label": "А"},
                {"id": "m1", "label": "М"},
                {"id": "o1", "label": "О"},
                {"id": "u1", "label": "У"},
                {"id": "s1", "label": "С"},
                {"id": "k1", "label": "К"},
                {"id": "m2", "label": "М"},
                {"id": "n1", "label": "Н"},
                {"id": "a2", "label": "А"},
                {"id": "o2", "label": "О"},
                {"id": "u2", "label": "У"},
                {"id": "m3", "label": "М"},
                {"id": "s2", "label": "С"},
                {"id": "k2", "label": "К"},
                {"id": "a3", "label": "А"},
                {"id": "o3", "label": "О"},
                {"id": "m4", "label": "М"},
                {"id": "u3", "label": "У"},
                {"id": "n2", "label": "Н"},
                {"id": "m5", "label": "М"},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "catch",
            "title": "Поймай М",
            "chapter": "Буква",
            "kind": "catch_letter",
            "mechanic": "letter_meadow",
            "slovik_line": "На поляне появится буква М. Нажми на неё — три раза в разных местах!",
            "slovik_pose": "talk",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-catch",
            "letter": "М",
            "appear_on_scene": True,
            "catches": 3,
            "spots": [
                {"x": 22, "y": 28},
                {"x": 74, "y": 26},
                {"x": 48, "y": 40},
                {"x": 18, "y": 58},
                {"x": 78, "y": 56},
                {"x": 58, "y": 70},
                {"x": 34, "y": 66},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "pause",
            "title": "Пауза",
            "kind": "break",
            "slovik_line": "Встань. Погуди как машина: м-м-м. Без экрана.",
            "audio": "bo-m1-l01-pause",
            "spark": False,
            "hint": "Встань и тихо скажи м-м-м, как машина. Потом вернёмся.",
        },
        {
            "id": "join_am",
            "title": "Мост дружбы",
            "chapter": "Искорка 3 · Слог",
            "kind": "drag_join",
            "slovik_line": "Познакомь А и М. Веди А по мостику к М — получится ам.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-join",
            "hint": "Перетащи А к М по мостику",
            "left": {"id": "A", "label": "А"},
            "right": {"id": "M", "label": "М"},
            "result": {"label": "АМ", "sound": "snd-ma", "image": IMG["bear"], "image_alt": "медведь"},
            "spark": True,
            "spark_kind": "syllable",
            "spark_group": "syllable",
        },
        {
            "id": "slot_am",
            "title": "Слог АМ",
            "chapter": "Искорка 3 · Слог",
            "kind": "slot_build",
            "slovik_line": "Сложим слог ам. А и М рядом — получается ам.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-slots",
            "result_sound": "snd-ma",
            "targets": ["А", "М"],
            "options": ["О", "М", "У", "А"],
            "result_label": "АМ",
            "result_image": IMG["bear"],
            "spark": False,
            "spark_group": "syllable",
        },
        {
            "id": "quest",
            "title": "Слог АМ",
            "chapter": "Мини-квест",
            "kind": "mini_quest",
            "slovik_line": "Медведь начинается на М. Найди его. Потом слог ам.",
            "slovik_pose": "joy",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l01-quest",
            "spark": False,
            "show_all_steps": True,
            "hint": "Картинка медведя. Потом слог АМ.",
            "steps": [
                {
                    "kind": "find",
                    "prompt": "Картинка на М",
                    "correct": "bear",
                    "options": [
                        _opt("bear", "Медведь", IMG["bear"]),
                        _opt("sun", "Солнце", IMG["sun"]),
                        _opt("kot", "Кот", IMG["kot"]),
                    ],
                },
                {
                    "kind": "find",
                    "prompt": "Слог",
                    "correct": "АМ",
                    "options": ["АМ", "МА", "М", "А"],
                },
            ],
        },
        _reward(
            audio="bo-m1-l01-reward",
            line="Буква М с нами! Три искорки. Ты знаешь букву М.",
            parent="Урок «Машина на поляне». Дома: м-м-м и слог АМ.",
            badge_line="Знаю букву М",
        ),
    ]


def _letters_2() -> list[dict[str, Any]]:
    return [
        {
            "id": "trail",
            "title": "Тропа букв",
            "kind": "intro_video",
            "slovik_line": "Новая буква на тропе.\nОна любит петь: у-у-у.",
            "slovik_pose": "wave",
            "scene_image": f"{L}/scene-u-echo-intro.jpg",
            "audio": "bo-m1-l02-hi",
            "cta_label": "Начать",
            "spark": False,
        },
        {
            "id": "meet",
            "title": "Буква У",
            "chapter": "Знакомство",
            "kind": "meet_letter",
            "mechanic": "meet_letter",
            "slovik_line": "Это У. Нажми и пропой вместе: у-у-у.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-meet",
            "sound": "snd-u",
            "letter": "У",
            "letter_image": IMG["letter_u"],
            "hint": "Нажми на букву — услышишь звук.",
            "coach_success": "У-у-у! Это буква У. Дальше соберём искорки.",
            "spark": False,
        },
        {
            "id": "azbuka",
            "title": "Азбука У",
            "chapter": "Буква",
            "kind": "alphabet_book",
            "mechanic": "azbuka_fill",
            "slovik_line": "Сложи страницу У. Выбери картинки, которые начинаются на букву У.",
            "slovik_pose": "talk",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-azbuka",
            "letter": "У",
            "letter_image": IMG["letter_u"],
            "book_title": "Утка и Ветер",
            "picture_only": False,
            "hint": "Картинка должна начинаться на У.",
            "success_msg": "Страница У готова!",
            "rounds": [
                {
                    "correct": "duck",
                    "options": [
                        _opt("duck", "утка", IMG["duck"]),
                        _opt("bear", "медведь", IMG["bear"]),
                        _opt("wind", "ветер", IMG["wind"]),
                        _opt("rain", "дождь", IMG["rain"]),
                    ],
                },
                {
                    "correct": "duck2",
                    "options": [
                        _opt("duck2", "утка", IMG["duck"]),
                        _opt("bear2", "медведь", IMG["bear"]),
                        _opt("sun", "солнце", IMG["sun"]),
                        _opt("kot", "кот", IMG["kot"]),
                    ],
                },
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "echo",
            "title": "Пещера эха",
            "chapter": "Искорка 1 · Звук",
            "kind": "catch_letter",
            "slovik_line": "Пещера эха. Здесь пропал звук у-у-у. Лови только букву У — три раза!",
            "slovik_pose": "talk",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l02-echo",
            "letter": "У",
            "letters": ["У", "А", "О", "М"],
            "letter_sounds": {"У": "snd-u", "А": "snd-a", "О": "snd-o", "М": "snd-m"},
            "catches": 3,
            "spark": True,
            "spark_kind": "sound",
            "spark_group": "sound",
        },
        {
            "id": "hop",
            "title": "Поймай У",
            "chapter": "Буква",
            "kind": "scene_hunt",
            "mechanic": "letter_chase",
            "slovik_line": "Буквы бегают по поляне! Лови большую У и маленькую у. Другие буквы не трогай.",
            "slovik_pose": "hint",
            "scene_image": SCENE_SP,
            "audio": "bo-m1-l02-hop",
            "moving": True,
            "move_speed": 5,
            "success_msg": "Поймал и У, и маленькую у!",
            "wrong_msg": "Это не У и не у. Ищи дальше.",
            "correct_ids": ["U1", "u1", "U2", "u2", "U3"],
            "hotspots": [
                {"id": "U1", "label": "У", "x": 14, "y": 12},
                {"id": "A1", "label": "А", "x": 34, "y": 10},
                {"id": "O1", "label": "О", "x": 54, "y": 14},
                {"id": "M1", "label": "М", "x": 74, "y": 11},
                {"id": "u1", "label": "у", "x": 90, "y": 22, "size": "sm"},
                {"id": "S1", "label": "С", "x": 12, "y": 44},
                {"id": "M2", "label": "М", "x": 88, "y": 48},
                {"id": "U2", "label": "У", "x": 16, "y": 76},
                {"id": "u2", "label": "у", "x": 48, "y": 84, "size": "sm"},
                {"id": "A2", "label": "А", "x": 86, "y": 80},
                {"id": "U3", "label": "У", "x": 32, "y": 90},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "build",
            "title": "Обведи У",
            "chapter": "Буква",
            "kind": "dot_connect",
            "mechanic": "dot_connect",
            "slovik_line": "Соедини точки по порядку — получится буква У.",
            "slovik_pose": "hint",
            "scene_image": SCENE_TRAIL,
            "audio": "bo-m1-l02-build",
            "letter": "У",
            "hint": "Жми точки по номерам: 1, 2, 3…",
            "success_msg": "Буква У получилась!",
            "dots": [
                {"n": 1, "x": 24, "y": 14},
                {"n": 2, "x": 50, "y": 48},
                {"n": 3, "x": 76, "y": 14},
                {"n": 4, "x": 50, "y": 48},
                {"n": 5, "x": 50, "y": 90},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "maze",
            "title": "Большая и маленькая У",
            "chapter": "Искорка 2 · Буква",
            "kind": "sort_two",
            "slovik_line": "Большая У и маленькая у — одна буква. Разложи.",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-maze",
            "left": {"label": "У", "correct": ["U1", "U2", "U3"]},
            "right": {"label": "у", "correct": ["u1", "u2", "u3"]},
            "options": [
                {"id": "U1", "label": "У"},
                {"id": "u1", "label": "у"},
                {"id": "U2", "label": "У"},
                {"id": "u2", "label": "у"},
                {"id": "U3", "label": "У"},
                {"id": "u3", "label": "у"},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "chase",
            "title": "Поймай У на поляне",
            "chapter": "Искорка 2 · Буква",
            "kind": "scene_hunt",
            "mechanic": "letter_chase",
            "slovik_line": "Теперь поймай их на поляне. Найди большую У и маленькую у. Не спутай с другими буквами.",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-chase",
            "moving": True,
            "move_speed": 5,
            "success_msg": "Поймал и У, и маленькую у!",
            "wrong_msg": "Это не У и не у. Ищи дальше.",
            "correct_ids": ["U1", "u1", "U2", "u2", "U3"],
            "hotspots": [
                {"id": "U1", "label": "У", "x": 14, "y": 10},
                {"id": "A1", "label": "А", "x": 34, "y": 8},
                {"id": "O1", "label": "О", "x": 54, "y": 12},
                {"id": "M1", "label": "М", "x": 74, "y": 9},
                {"id": "u1", "label": "у", "x": 91, "y": 20, "size": "sm"},
                {"id": "S1", "label": "С", "x": 10, "y": 42},
                {"id": "M2", "label": "М", "x": 90, "y": 46},
                {"id": "U2", "label": "У", "x": 12, "y": 78},
                {"id": "u2", "label": "у", "x": 48, "y": 86, "size": "sm"},
                {"id": "A2", "label": "А", "x": 88, "y": 82},
                {"id": "U3", "label": "У", "x": 30, "y": 90},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "grid",
            "title": "Найди все У",
            "kind": "letter_puzzle",
            "mechanic": "letter_grid",
            "slovik_line": "Найди на доске все буквы У. Их несколько.",
            "scene_image": SCENE_BOARD,
            "audio": "bo-m1-l02-grid",
            "pieces_on_board": True,
            "slots": 3,
            "pieces": [
                {"id": "u1", "label": "У", "correct": True},
                {"id": "m1", "label": "М", "correct": False},
                {"id": "u2", "label": "У", "correct": True},
                {"id": "a1", "label": "А", "correct": False},
                {"id": "o1", "label": "О", "correct": False},
                {"id": "u3", "label": "У", "correct": True},
            ],
            "spark": True,
            "spark_kind": "letter",
            "spark_group": "letter",
        },
        {
            "id": "first_letter",
            "title": "Первая буква",
            "chapter": "Буква",
            "kind": "find",
            "mechanic": "picture_first_letter",
            "slovik_line": "Смотри картинку. С какой буквы начинается слово? Нажми букву.",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-first",
            "spark": False,
            "spark_group": "letter",
            "hint": "Скажи слово вслух и найди первую букву.",
            "rounds": [
                {
                    "prompt_text": "С какой буквы?",
                    "prompt_image": IMG["duck"],
                    "prompt_alt": "утка",
                    "correct": "У",
                    "options": ["А", "О", "У", "М"],
                },
                {
                    "prompt_text": "Какая буква поёт у-у-у?",
                    "sound": "snd-u",
                    "correct": "У",
                    "options": ["М", "У", "А", "О"],
                },
                {
                    "prompt_text": "С какой буквы?",
                    "prompt_image": IMG["duck"],
                    "prompt_alt": "утка",
                    "correct": "У",
                    "options": ["С", "А", "У", "О"],
                },
            ],
        },
        {
            "id": "board",
            "title": "Доска букв",
            "chapter": "Буква",
            "kind": "scene_hunt",
            "mechanic": "letter_board",
            "board_panel": True,
            "slovik_line": "Найди на доске все буквы У. Их несколько.",
            "slovik_pose": "hint",
            "scene_image": SCENE_BOARD,
            "audio": "bo-m1-l02-board",
            "layout": "grid",
            "grid_cols": 5,
            "moving": False,
            "correct_ids": ["u1", "u2", "u3", "u4", "u5"],
            "hotspots": [
                {"id": "a1", "label": "А"},
                {"id": "u1", "label": "У"},
                {"id": "o1", "label": "О"},
                {"id": "m1", "label": "М"},
                {"id": "s1", "label": "С"},
                {"id": "k1", "label": "К"},
                {"id": "u2", "label": "У"},
                {"id": "n1", "label": "Н"},
                {"id": "a2", "label": "А"},
                {"id": "o2", "label": "О"},
                {"id": "m2", "label": "М"},
                {"id": "u3", "label": "У"},
                {"id": "s2", "label": "С"},
                {"id": "k2", "label": "К"},
                {"id": "a3", "label": "А"},
                {"id": "o3", "label": "О"},
                {"id": "u4", "label": "У"},
                {"id": "m3", "label": "М"},
                {"id": "n2", "label": "Н"},
                {"id": "u5", "label": "У"},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "catch",
            "title": "Поймай У",
            "chapter": "Буква",
            "kind": "catch_letter",
            "mechanic": "letter_meadow",
            "slovik_line": "На поляне появится буква У. Нажми на неё — три раза в разных местах!",
            "slovik_pose": "talk",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-catch",
            "letter": "У",
            "appear_on_scene": True,
            "catches": 3,
            "spots": [
                {"x": 22, "y": 28},
                {"x": 74, "y": 26},
                {"x": 48, "y": 40},
                {"x": 18, "y": 58},
                {"x": 78, "y": 56},
                {"x": 58, "y": 70},
                {"x": 34, "y": 66},
            ],
            "spark": False,
            "spark_group": "letter",
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
            "id": "join_mu",
            "title": "Мост дружбы",
            "chapter": "Искорка 3 · Слог",
            "kind": "drag_join",
            "slovik_line": "Познакомь М и У. Веди М по мостику к У — получится му.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-join",
            "hint": "Перетащи М к У по мостику",
            "left": {"id": "M", "label": "М"},
            "right": {"id": "U", "label": "У"},
            "result": {"label": "МУ", "sound": "snd-mu", "image": IMG["cow"], "image_alt": "корова"},
            "spark": False,
            "spark_group": "syllable",
        },
        {
            "id": "slots",
            "title": "МУ и УМ",
            "chapter": "Искорка 3 · Слог",
            "kind": "slot_build",
            "slovik_line": "Склеим: му и ум. Сначала му.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-slots",
            "result_sound": "snd-mu",
            "targets": ["М", "У"],
            "options": ["М", "А", "У", "О"],
            "result_label": "МУ",
            "result_image": IMG["cow"],
            "spark": False,
            "spark_group": "syllable",
        },
        {
            "id": "slots_um",
            "title": "Слог УМ",
            "chapter": "Искорка 3 · Слог",
            "kind": "slot_build",
            "slovik_line": "Теперь ум. У и М рядом — получается ум.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-slots-um",
            "targets": ["У", "М"],
            "options": ["А", "У", "О", "М"],
            "result_label": "УМ",
            "spark": True,
            "spark_kind": "syllable",
            "spark_group": "syllable",
        },
        {
            "id": "or",
            "title": "Как говорит корова?",
            "kind": "find",
            "mechanic": "cow_moo",
            "slovik_line": "Как говорит корова? Нажми слог.",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-cow",
            "spark": False,
            "hint": "Корова говорит му.",
            "rounds": [
                {
                    "prompt_text": "Как говорит корова?",
                    "prompt_image": IMG["cow"],
                    "prompt_alt": "корова",
                    "correct": "МУ",
                    "options": ["МУ", "УМ", "МА", "МО"],
                }
            ],
        },
        {
            "id": "quest",
            "title": "Слог МУ",
            "kind": "mini_quest",
            "slovik_line": "Слог му. Найди корову и слог му.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l02-quest",
            "spark": False,
            "show_all_steps": True,
            "hint": "Картинка коровы и слог МУ.",
            "steps": [
                {
                    "kind": "find",
                    "prompt": "Картинка",
                    "correct": "cow",
                    "options": [
                        _opt("cow", "Корова", IMG["cow"]),
                        _opt("motor", "Машина", IMG["motor"]),
                        _opt("kot", "Кот", IMG["kot"]),
                    ],
                },
                {
                    "kind": "find",
                    "prompt": "Слог",
                    "correct": "МУ",
                    "options": ["МУ", "УМ", "МА", "АМ"],
                },
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
            "slovik_line": "Круглая буква О.\nОна тоже поёт: о-о-о.",
            "slovik_pose": "wave",
            "scene_image": f"{L}/scene-o-pond-intro.jpg",
            "audio": "bo-m1-l03-hi",
            "cta_label": "Начать",
            "spark": False,
        },
        {
            "id": "meet",
            "title": "Буква О",
            "chapter": "Знакомство",
            "kind": "meet_letter",
            "mechanic": "meet_letter",
            "slovik_line": "Нажми на О. Скажи о-о-о.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-meet",
            "sound": "snd-o",
            "letter": "О",
            "letter_image": IMG["letter_o"],
            "hint": "Нажми на букву — услышишь звук.",
            "coach_success": "О-о-о! Это буква О. Дальше соберём искорки.",
            "spark": False,
        },
        {
            "id": "azbuka",
            "title": "Азбука О",
            "chapter": "Буква",
            "kind": "alphabet_book",
            "mechanic": "azbuka_fill",
            "slovik_line": "Сложи страницу О. Выбери картинки, которые начинаются на букву О.",
            "slovik_pose": "talk",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-azbuka",
            "letter": "О",
            "letter_image": IMG["letter_o"],
            "book_title": "О",
            "picture_only": False,
            "hint": "Картинка должна начинаться на О.",
            "success_msg": "Страница О готова!",
            "rounds": [
                {
                    "correct": "window",
                    "options": [
                        _opt("window", "окно", IMG["window"]),
                        _opt("tree", "дерево", IMG["tree"]),
                    ],
                },
                {
                    "correct": "wasp",
                    "options": [
                        _opt("wasp", "оса", IMG["wasp"]),
                        _opt("motor", "машина", IMG["motor"]),
                    ],
                },
            ],
            "spark": False,
            "spark_group": "letter",
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
            "correct_ids": ["ball", "lake"],
            "wrong_msg": "Это не круглое. Ищи ещё.",
            "hotspots": [
                {"id": "ball", "label": "Мяч", "image": IMG["round_ball"], "x": 20, "y": 28},
                {"id": "box", "label": "Короб", "image": IMG["box_sq"], "x": 50, "y": 28},
                {"id": "lake", "label": "Озеро", "image": IMG["round_lake"], "x": 80, "y": 28},
                {"id": "tree", "label": "Дерево", "image": IMG["tree"], "x": 20, "y": 72},
                {"id": "motor", "label": "Машина", "image": IMG["motor"], "x": 50, "y": 72},
                {"id": "house", "label": "Дом", "image": IMG["house"], "x": 80, "y": 72},
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
            "scene_image": SCENE_TRAIL,
            "audio": "bo-m1-l03-hop",
            "letter": "О",
            "start": [0, 0],
            "end": [3, 2],
            "grid": [
                ["О", "А", "У"],
                ["О", "М", "О"],
                ["О", "О", "О"],
                ["М", "У", "О"],
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "build",
            "title": "Обведи О",
            "chapter": "Буква",
            "kind": "dot_connect",
            "mechanic": "dot_connect",
            "slovik_line": "Соедини точки по порядку — получится буква О.",
            "slovik_pose": "hint",
            "scene_image": SCENE_WATER,
            "audio": "bo-m1-l03-build",
            "letter": "О",
            "hint": "Жми точки по номерам: 1, 2, 3…",
            "success_msg": "Буква О получилась!",
            "dots": [
                {"n": 1, "x": 50, "y": 12},
                {"n": 2, "x": 18, "y": 30},
                {"n": 3, "x": 18, "y": 70},
                {"n": 4, "x": 50, "y": 88},
                {"n": 5, "x": 82, "y": 70},
                {"n": 6, "x": 82, "y": 30},
                {"n": 7, "x": 58, "y": 14},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "sort",
            "title": "Большая и маленькая О",
            "chapter": "Искорка 2 · Буква",
            "kind": "sort_two",
            "slovik_line": "Большая О и маленькая о — одна буква. Разложи.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-sort",
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
            "id": "chase",
            "title": "Поймай О на поляне",
            "chapter": "Искорка 2 · Буква",
            "kind": "scene_hunt",
            "mechanic": "letter_chase",
            "slovik_line": "Теперь поймай их на поляне. Найди большую О и маленькую о. Не спутай с другими буквами.",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-chase",
            "moving": True,
            "move_speed": 5,
            "success_msg": "Поймал и О, и маленькую о!",
            "wrong_msg": "Это не О и не о. Ищи дальше.",
            "correct_ids": ["O1", "o1", "O2", "o2", "O3"],
            "hotspots": [
                {"id": "O1", "label": "О", "x": 14, "y": 10},
                {"id": "A1", "label": "А", "x": 34, "y": 8},
                {"id": "U1", "label": "У", "x": 54, "y": 12},
                {"id": "M1", "label": "М", "x": 74, "y": 9},
                {"id": "o1", "label": "о", "x": 91, "y": 20, "size": "sm"},
                {"id": "S1", "label": "С", "x": 10, "y": 42},
                {"id": "M2", "label": "М", "x": 90, "y": 46},
                {"id": "O2", "label": "О", "x": 12, "y": 78},
                {"id": "o2", "label": "о", "x": 48, "y": 86, "size": "sm"},
                {"id": "A2", "label": "А", "x": 88, "y": 82},
                {"id": "O3", "label": "О", "x": 30, "y": 90},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "count",
            "title": "Шесть О",
            "kind": "catch_letter",
            "mechanic": "letter_count",
            "slovik_line": "Поймай шесть букв О. Считай вместе со мной.",
            "scene_image": SCENE_WATER,
            "audio": "bo-m1-l03-count",
            "letter": "О",
            "letters": ["О", "А", "У", "М"],
            "letter_sounds": {"О": "snd-o", "А": "snd-a", "У": "snd-u", "М": "snd-m"},
            "catches": 6,
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "first_letter",
            "title": "Первая буква",
            "chapter": "Буква",
            "kind": "find",
            "mechanic": "picture_first_letter",
            "slovik_line": "Смотри картинку. С какой буквы начинается слово? Нажми букву.",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-first",
            "spark": False,
            "spark_group": "letter",
            "hint": "Скажи слово вслух и найди первую букву.",
            "rounds": [
                {
                    "prompt_text": "С какой буквы?",
                    "prompt_image": IMG["wasp"],
                    "prompt_alt": "оса",
                    "correct": "О",
                    "options": ["А", "О", "М", "У"],
                },
                {
                    "prompt_text": "Какая буква поёт о-о-о?",
                    "sound": "snd-o",
                    "correct": "О",
                    "options": ["У", "М", "О", "А"],
                },
                {
                    "prompt_text": "С какой буквы?",
                    "prompt_image": IMG["wasp"],
                    "prompt_alt": "оса",
                    "correct": "О",
                    "options": ["С", "А", "О", "М"],
                },
            ],
        },
        {
            "id": "board",
            "title": "Доска букв",
            "chapter": "Буква",
            "kind": "scene_hunt",
            "mechanic": "letter_board",
            "board_panel": True,
            "slovik_line": "Найди на доске все буквы О. Их несколько.",
            "slovik_pose": "hint",
            "scene_image": SCENE_BOARD,
            "audio": "bo-m1-l03-board",
            "layout": "grid",
            "grid_cols": 5,
            "moving": False,
            "correct_ids": ["o1", "o2", "o3", "o4", "o5"],
            "hotspots": [
                {"id": "a1", "label": "А"},
                {"id": "o1", "label": "О"},
                {"id": "m1", "label": "М"},
                {"id": "u1", "label": "У"},
                {"id": "s1", "label": "С"},
                {"id": "k1", "label": "К"},
                {"id": "o2", "label": "О"},
                {"id": "n1", "label": "Н"},
                {"id": "a2", "label": "А"},
                {"id": "m2", "label": "М"},
                {"id": "u2", "label": "У"},
                {"id": "o3", "label": "О"},
                {"id": "s2", "label": "С"},
                {"id": "k2", "label": "К"},
                {"id": "a3", "label": "А"},
                {"id": "m3", "label": "М"},
                {"id": "o4", "label": "О"},
                {"id": "u3", "label": "У"},
                {"id": "n2", "label": "Н"},
                {"id": "o5", "label": "О"},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "catch",
            "title": "Поймай О",
            "chapter": "Буква",
            "kind": "catch_letter",
            "mechanic": "letter_meadow",
            "slovik_line": "На поляне появится буква О. Нажми на неё — три раза в разных местах!",
            "slovik_pose": "talk",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-catch",
            "letter": "О",
            "appear_on_scene": True,
            "catches": 3,
            "spots": [
                {"x": 22, "y": 28},
                {"x": 74, "y": 26},
                {"x": 48, "y": 40},
                {"x": 18, "y": 58},
                {"x": 78, "y": 56},
                {"x": 58, "y": 70},
                {"x": 34, "y": 66},
            ],
            "spark": False,
            "spark_group": "letter",
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
            "id": "join_mo",
            "title": "Мост дружбы",
            "chapter": "Искорка 3 · Слог",
            "kind": "drag_join",
            "slovik_line": "Познакомь М и О. Веди М по мостику к О — получится мо.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-join",
            "hint": "Перетащи М к О по мостику",
            "left": {"id": "M", "label": "М"},
            "right": {"id": "O", "label": "О"},
            "result": {"label": "МО", "sound": "snd-mo"},
            "spark": False,
            "spark_group": "syllable",
        },
        {
            "id": "slots",
            "title": "Слог МО",
            "chapter": "Искорка 3 · Слог",
            "kind": "slot_build",
            "slovik_line": "Сложим слог мо. М и О рядом.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-slots",
            "result_sound": "snd-mo",
            "targets": ["М", "О"],
            "options": ["С", "М", "О", "А"],
            "result_label": "МО",
            "spark": True,
            "spark_kind": "syllable",
            "spark_group": "syllable",
        },
        {
            "id": "spread",
            "title": "Азбука М, У, О",
            "chapter": "Буква",
            "kind": "alphabet_book",
            "mechanic": "azbuka_fill",
            "slovik_line": "Вспомним буквы в азбуке. Выбери картинку на каждую букву: М, У и О.",
            "slovik_pose": "talk",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-review",
            "picture_only": False,
            "hint": "Картинка должна начинаться на нужную букву.",
            "success_msg": "Буквы М, У и О с нами!",
            "rounds": [
                {
                    "letter": "М",
                    "letter_image": f"{L}/letter-m-hero.png",
                    "correct": "motor",
                    "hint": "Картинка на букву М.",
                    "options": [
                        _opt("motor", "машина", IMG["motor"]),
                        _opt("kot", "кот", IMG["kot"]),
                    ],
                },
                {
                    "letter": "У",
                    "letter_image": IMG["letter_u"],
                    "correct": "duck",
                    "hint": "Картинка на букву У.",
                    "options": [
                        _opt("duck", "утка", IMG["duck"]),
                        _opt("bear", "медведь", IMG["bear"]),
                    ],
                },
                {
                    "letter": "О",
                    "letter_image": IMG["letter_o"],
                    "correct": "wasp",
                    "hint": "Картинка на букву О.",
                    "options": [
                        _opt("wasp", "оса", IMG["wasp"]),
                        _opt("tree", "дерево", IMG["tree"]),
                    ],
                },
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "quest",
            "title": "С какой буквы?",
            "kind": "find",
            "mechanic": "picture_first_letter",
            "slovik_line": "Это оса. С какой буквы начинается слово? Нажми букву.",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l03-quest",
            "spark": False,
            "hint": "Оса начинается на О.",
            "rounds": [
                {
                    "prompt_text": "С какой буквы?",
                    "prompt_image": IMG["wasp"],
                    "prompt_alt": "оса",
                    "correct": "О",
                    "options": ["А", "М", "О", "У"],
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
            "scene_image": where_map(4),
            "audio": "bo-m1-l04-hi",
            "cta_label": "Начать",
            "spark": False,
        },
        {
            "id": "meet",
            "title": "Буква С",
            "kind": "meet_letter",
            "mechanic": "meet_letter",
            "slovik_line": "Буква С. Тихо: с-с-с. Как тонкая струйка воздуха.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-meet",
            "sound": "snd-s",
            "letter": "С",
            "letter_image": IMG["letter_s"],
            "hint": "Нажми на букву — услышишь звук.",
            "coach_success": "С-с-с! Это буква С. Дальше соберём искорки.",
            "spark": False,
        },
        {
            "id": "azbuka",
            "title": "Азбука С",
            "chapter": "Буква",
            "kind": "alphabet_book",
            "mechanic": "azbuka_fill",
            "slovik_line": "Сложи страницу С. Выбери картинки, которые начинаются на букву С.",
            "slovik_pose": "talk",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-azbuka",
            "letter": "С",
            "letter_image": IMG["letter_s"],
            "book_title": "С",
            "picture_only": False,
            "hint": "Картинка должна начинаться на С.",
            "success_msg": "Страница С готова!",
            "rounds": [
                {
                    "correct": "snake",
                    "options": [
                        _opt("snake", "змейка", IMG["snake"]),
                        _opt("motor", "машина", IMG["motor"]),
                    ],
                },
                {
                    "correct": "som",
                    "options": [
                        _opt("som", "сом", IMG["som"]),
                        _opt("bear", "медведь", IMG["bear"]),
                    ],
                },
            ],
            "spark": False,
            "spark_group": "letter",
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
                    "correct": "snake",
                    "options": [
                        _opt("snake", "Змейка", IMG["snake"]),
                        _opt("motor", "Машина", IMG["motor"]),
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
            "scene_image": SCENE_TRAIL,
            "audio": "bo-m1-l04-hop",
            "letter": "С",
            "start": [0, 0],
            "end": [3, 3],
            "grid": [
                ["С", "М", "А", "У"],
                ["С", "С", "С", "О"],
                ["А", "М", "С", "С"],
                ["О", "У", "М", "С"],
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "build",
            "title": "Обведи С",
            "chapter": "Буква",
            "kind": "dot_connect",
            "mechanic": "dot_connect",
            "slovik_line": "Соедини точки по порядку — получится буква С.",
            "slovik_pose": "hint",
            "scene_image": SCENE_WATER,
            "audio": "bo-m1-l04-build",
            "letter": "С",
            "hint": "Жми точки по номерам: 1, 2, 3…",
            "success_msg": "Буква С получилась!",
            "dots": [
                {"n": 1, "x": 78, "y": 20},
                {"n": 2, "x": 50, "y": 10},
                {"n": 3, "x": 20, "y": 28},
                {"n": 4, "x": 14, "y": 55},
                {"n": 5, "x": 24, "y": 82},
                {"n": 6, "x": 55, "y": 92},
                {"n": 7, "x": 80, "y": 78},
            ],
            "spark": False,
            "spark_group": "letter",
        },
        _sort_big_small("С", audio="bo-m1-l04-sort"),
        _chase_meadow("С", audio="bo-m1-l04-chase"),
        {
            "id": "grid",
            "title": "Найди все С",
            "chapter": "Искорка 2 · Буква",
            "kind": "letter_puzzle",
            "mechanic": "letter_grid",
            "slovik_line": "Найди все буквы С на доске.",
            "scene_image": SCENE_BOARD,
            "audio": "bo-m1-l04-grid",
            "pieces_on_board": True,
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
            "id": "first_letter",
            "title": "Первая буква",
            "chapter": "Буква",
            "kind": "find",
            "mechanic": "picture_first_letter",
            "slovik_line": "Смотри картинку. С какой буквы начинается слово? Нажми букву.",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-first",
            "spark": False,
            "spark_group": "letter",
            "hint": "Скажи слово вслух и найди первую букву.",
            "rounds": [
                {
                    "prompt_text": "С какой буквы?",
                    "prompt_image": IMG["snake"],
                    "prompt_alt": "змейка",
                    "correct": "С",
                    "options": ["А", "М", "С", "У"],
                },
                {
                    "prompt_text": "Какая буква говорит с-с-с?",
                    "sound": "snd-s",
                    "correct": "С",
                    "options": ["М", "С", "О", "А"],
                },
                {
                    "prompt_text": "С какой буквы?",
                    "prompt_image": IMG["som"],
                    "prompt_alt": "сом",
                    "correct": "С",
                    "options": ["О", "С", "М", "У"],
                },
            ],
        },
        _board_letters("С", audio="bo-m1-l04-board"),
        _meadow_catch("С", audio="bo-m1-l04-catch"),
        {
            "id": "count",
            "title": "Шесть С",
            "kind": "catch_letter",
            "mechanic": "letter_count",
            "slovik_line": "Собери шесть С у воды.",
            "scene_image": SCENE_WATER,
            "audio": "bo-m1-l04-count",
            "letter": "С",
            "letters": ["С", "М", "А", "О", "У"],
            "letter_sounds": {"С": "snd-s", "М": "snd-m", "А": "snd-a", "О": "snd-o", "У": "snd-u"},
            "catches": 6,
            "spark": False,
            "spark_group": "letter",
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
            "id": "join_sa",
            "title": "Мост дружбы",
            "chapter": "Искорка 3 · Слог",
            "kind": "drag_join",
            "slovik_line": "Познакомь С и А. Веди С по мостику к А — получится са.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-join",
            "hint": "Перетащи С к А по мостику",
            "left": {"id": "S", "label": "С"},
            "right": {"id": "A", "label": "А"},
            "result": {"label": "СА", "sound": "snd-s", "image": IMG["snake"], "image_alt": "змейка"},
            "spark": False,
            "spark_group": "syllable",
        },
        {
            "id": "slots",
            "title": "Слог СА",
            "chapter": "Искорка 3 · Слог",
            "kind": "slot_build",
            "slovik_line": "Склеим слог са. Сначала са.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-slots",
            "targets": ["С", "А"],
            "options": ["С", "О", "А", "М"],
            "result_label": "СА",
            "result_image": IMG["snake"],
            "spark": False,
            "spark_group": "syllable",
        },
        {
            "id": "slots_so",
            "title": "Слог СО",
            "chapter": "Искорка 3 · Слог",
            "kind": "slot_build",
            "slovik_line": "Теперь со. С и О рядом — получается со.",
            "slovik_pose": "invite",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-slots-so",
            "targets": ["С", "О"],
            "options": ["А", "С", "М", "О"],
            "result_label": "СО",
            "result_image": IMG["som"],
            "spark": True,
            "spark_kind": "syllable",
            "spark_group": "syllable",
        },
        {
            "id": "or",
            "title": "Как говорит змейка?",
            "kind": "find",
            "mechanic": "snake_hiss",
            "slovik_line": "Как говорит змейка? Нажми слог.",
            "slovik_pose": "hint",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-or",
            "spark": False,
            "hint": "Змейка говорит с-с-с. Выбери слог СА.",
            "rounds": [
                {
                    "prompt_text": "Как говорит змейка?",
                    "prompt_image": IMG["snake"],
                    "prompt_alt": "змейка",
                    "correct": "СА",
                    "options": ["СА", "СО", "МА", "МО"],
                }
            ],
        },
        {
            "id": "spread",
            "title": "Азбука М, У, О, С",
            "chapter": "Буква",
            "kind": "alphabet_book",
            "mechanic": "azbuka_fill",
            "slovik_line": "Вспомним буквы в азбуке. Выбери картинку на каждую: М, У, О и С.",
            "slovik_pose": "talk",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-review",
            "picture_only": False,
            "hint": "Картинка должна начинаться на нужную букву.",
            "success_msg": "Буквы М, У, О и С с нами!",
            "rounds": [
                {
                    "letter": "М",
                    "letter_image": f"{L}/letter-m-hero.png",
                    "correct": "bear",
                    "hint": "Картинка на букву М.",
                    "options": [
                        _opt("bear", "медведь", IMG["bear"]),
                        _opt("kot", "кот", IMG["kot"]),
                    ],
                },
                {
                    "letter": "У",
                    "letter_image": IMG["letter_u"],
                    "correct": "duck",
                    "hint": "Картинка на букву У.",
                    "options": [
                        _opt("duck", "утка", IMG["duck"]),
                        _opt("sun", "солнце", IMG["sun"]),
                    ],
                },
                {
                    "letter": "О",
                    "letter_image": IMG["letter_o"],
                    "correct": "wasp",
                    "hint": "Картинка на букву О.",
                    "options": [
                        _opt("wasp", "оса", IMG["wasp"]),
                        _opt("tree", "дерево", IMG["tree"]),
                    ],
                },
                {
                    "letter": "С",
                    "letter_image": IMG["letter_s"],
                    "correct": "som",
                    "hint": "Картинка на букву С.",
                    "options": [
                        _opt("som", "сом", IMG["som"]),
                        _opt("motor", "машина", IMG["motor"]),
                    ],
                },
            ],
            "spark": False,
            "spark_group": "letter",
        },
        {
            "id": "quest",
            "title": "Слог СО",
            "kind": "mini_quest",
            "slovik_line": "Сом начинается на С. Найди его. Потом слог со.",
            "scene_image": SCENE_L,
            "audio": "bo-m1-l04-quest",
            "spark": False,
            "show_all_steps": True,
            "hint": "Картинка сома и слог СО.",
            "steps": [
                {
                    "kind": "find",
                    "prompt": "Картинка на С",
                    "correct": "som",
                    "options": [
                        _opt("som", "Сом", IMG["som"]),
                        _opt("sun", "Солнце", IMG["sun"]),
                        _opt("kot", "Кот", IMG["kot"]),
                    ],
                },
                {
                    "kind": "find",
                    "prompt": "Слог",
                    "correct": "СО",
                    "options": ["СА", "СО", "ОС", "МО"],
                },
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
            "scene_image": SCENE_HOME,
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
            "scene_image": IMG["slovik_screen"],
            "audio": "ph-m1-l01-screen",
            "spark": False,
            "items": [
                {
                    "word": "КОРОБ",
                    "correct": "box",
                    "options": [
                        _opt("box", "Короб", IMG["box"]),
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
            "scene_image": SCENE_HOME,
            "audio": "ph-m1-l01-what",
            "rounds": [
                {
                    "prompt_text": "Сначала короб пустой.",
                    "correct": "empty",
                    "options": [
                        _opt("empty", "ПУСТО", IMG["box_empty"]),
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
            "scene_image": SCENE_HOME,
            "audio": "ph-m1-l01-drag",
            "hint": "Нажми на слово, потом на картинку.",
            "pairs": [
                {"id": "korob", "label": "КОРОБ", "image": IMG["box"]},
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
            "scene_image": SCENE_HOME,
            "audio": "ph-m1-l01-open",
            "spark": False,
            "steps": [
                {
                    "kind": "find",
                    "prompt": "СМОТРИ",
                    "correct": "empty",
                    "options": [
                        _opt("empty", "ПУСТО", IMG["box_empty"]),
                        _opt("sleep", "СПИТ", IMG["sleep"]),
                    ],
                },
                {
                    "kind": "find",
                    "prompt": "Что в коробе?",
                    "correct": "ball",
                    "options": [
                        _opt("empty", "ПУСТО", IMG["box_empty"]),
                        _opt("ball", "ВОТ МЯЧ", IMG["box_ball"]),
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
            "scene_image": SCENE_HOME,
            "audio": "ph-m1-l01-slots",
            "targets": ["ВОТ", "МЯЧ"],
            "options": ["ДОМ", "ВОТ", "СЫР", "МЯЧ"],
            "result_label": "ВОТ МЯЧ",
            "result_image": IMG["box_ball"],
            "spark": False,
            "spark_group": "phrase",
        },
        {
            "id": "feel",
            "title": "Кот рад",
            "kind": "phrase_picture",
            "slovik_line": "Кот рад. Где такая картинка?",
            "scene_image": SCENE_HOME,
            "audio": "ph-m1-l01-feel",
            "phrase": "КОТ РАД",
            "correct": "happy",
            "picture_only": True,
            "options": [
                _opt("sleep", "Спит", IMG["sleep"]),
                _opt("happy", "Рад", IMG["happy"]),
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
            "scene_image": IMG["cover_box"],
            "audio": "ph-m1-l01-book",
            "book_title": "Кот и коробка",
            "cta_label": "Я прочитал!",
            "lines": [
                {"text": "ВОТ КОРОБ.", "spread_image": f"{ST}/book-box-01.jpg", "alt": "Короб", "audio": "ph-m1-l01-p1"},
                {"text": "ЧТО ТАМ?", "spread_image": f"{ST}/book-box-02.jpg", "alt": "Кот смотрит", "audio": "ph-m1-l01-p2"},
                {"text": "НЕ ТУТ.", "spread_image": f"{ST}/book-box-03.jpg", "alt": "Пусто", "audio": "ph-m1-l01-p3"},
                {"text": "ВОТ МЯЧ!", "spread_image": f"{ST}/book-box-04.jpg", "alt": "Мяч", "audio": "ph-m1-l01-p4"},
                {"text": "КОТ РАД.", "spread_image": f"{ST}/book-box-05.jpg", "alt": "Кот рад", "audio": "ph-m1-l01-p5"},
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
            "scene_image": SCENE_RAIN,
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
            "scene_image": IMG["slovik_screen"],
            "audio": "ph-m1-l02-screen",
            "items": [
                {
                    "word": "ДОЖДЬ",
                    "correct": "rain",
                    "options": [
                        _opt("rain", "Дождь", IMG["rain"]),
                        _opt("sun", "Солнце", IMG["sun_clear"]),
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
            "scene_image": SCENE_RAIN,
            "audio": "ph-m1-l02-weather",
            "picture_only": True,
            "rounds": [{"correct": "rain", "options": [_opt("rain", "Дождь", IMG["rain"]), _opt("sun", "Солнце", IMG["sun_clear"])]}],
            "spark": True,
            "spark_kind": "word",
            "spark_group": "word",
        },
        {
            "id": "who",
            "title": "Кто у окна?",
            "kind": "find",
            "slovik_line": "Кто у окна?",
            "scene_image": SCENE_RAIN,
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
            "scene_image": SCENE_RAIN,
            "audio": "ph-m1-l02-drag",
            "pairs": [
                {"id": "okno", "label": "ОКНО", "image": IMG["window"]},
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
            "scene_image": SCENE_RAIN,
            "audio": "ph-m1-l02-slots",
            "targets": ["КОТ", "У", "ОКНА"],
            "options": ["МЯЧ", "КОТ", "СЫР", "У", "ОКНА"],
            "result_label": "КОТ У ОКНА",
            "result_image": IMG["window"],
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
            "scene_image": IMG["cover_rain"],
            "audio": "ph-m1-l02-book",
            "book_title": "Дождь за окном",
            "cta_label": "Я прочитал!",
            "lines": [
                {"text": "ИДЁТ ДОЖДЬ.", "spread_image": f"{ST}/book-rain-01.jpg", "audio": "ph-m1-l02-p1"},
                {"text": "КОТ У ОКНА.", "spread_image": f"{ST}/book-rain-02.jpg", "audio": "ph-m1-l02-p2"},
                {"text": "ТИХО ДОМА.", "spread_image": f"{ST}/book-rain-03.jpg", "audio": "ph-m1-l02-p3"},
                {"text": "КОТ СПИТ.", "spread_image": f"{ST}/book-rain-04.jpg", "audio": "ph-m1-l02-p4"},
                {"text": "НОЧЬ.", "spread_image": f"{ST}/book-rain-05.jpg", "audio": "ph-m1-l02-p5"},
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
            "scene_image": IMG["cover_ball"],
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
            "scene_image": SCENE_HOME,
            "audio": "ph-m1-l03-hunt",
            "layout": "grid",
            "grid_cols": 3,
            "correct_ids": ["hall"],
            "wrong_msg": "Не тут.",
            "success_msg": "Вот мяч!",
            "hotspots": [
                {"id": "kitchen", "label": "Кухня", "image": IMG["kitchen"], "x": 20, "y": 50},
                {"id": "room", "label": "Комната", "image": IMG["room"], "x": 50, "y": 50},
                {"id": "hall", "label": "Коридор", "image": IMG["hall"], "x": 80, "y": 50},
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
            "scene_image": SCENE_HOME,
            "audio": "ph-m1-l03-under",
            "rounds": [
                {
                    "prompt_text": "ПОД",
                    "correct": "under",
                    "options": [
                        _opt("sofa", "НА диване", IMG["ball_sofa"]),
                        _opt("under", "ПОД стулом", IMG["ball_under"]),
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
            "scene_image": SCENE_HOME,
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
            "scene_image": SCENE_HOME,
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
                        _opt("run", "Бежит", IMG["run"]),
                    ],
                },
                {
                    "kind": "phrase_picture",
                    "phrase": "КОТ ЛОВИТ",
                    "correct": "catch",
                    "options": [
                        _opt("eat", "Ест", IMG["eat"]),
                        _opt("catch", "Ловит", IMG["catch"]),
                    ],
                },
                {
                    "kind": "phrase_picture",
                    "phrase": "КОТ РАД",
                    "correct": "happy",
                    "options": [
                        _opt("sleep", "Спит", IMG["sleep"]),
                        _opt("happy", "Рад", IMG["happy"]),
                    ],
                },
            ],
        },
        {
            "id": "where",
            "title": "Картинка к вопросу",
            "kind": "phrase_picture",
            "slovik_line": "Где мяч? Выбери картинку.",
            "scene_image": SCENE_HOME,
            "audio": "ph-m1-l03-where",
            "phrase": "ГДЕ МЯЧ?",
            "correct": "under",
            "picture_only": True,
            "options": [
                _opt("sofa", "На диване", IMG["ball_sofa"]),
                _opt("under", "Под стулом", IMG["ball_under"]),
            ],
            "spark": False,
        },
        {
            "id": "book",
            "title": "Где мяч?",
            "kind": "book_page",
            "slovik_line": "История про мяч. Читай.",
            "scene_image": IMG["cover_ball"],
            "audio": "ph-m1-l03-book",
            "book_title": "Где мяч?",
            "cta_label": "Я прочитал!",
            "lines": [
                {"text": "ГДЕ МЯЧ?", "spread_image": f"{ST}/book-ball-01.jpg", "audio": "ph-m1-l03-p1"},
                {"text": "НЕ ТУТ.", "spread_image": f"{ST}/book-ball-02.jpg", "audio": "ph-m1-l03-p2"},
                {"text": "НЕ ТУТ.", "spread_image": f"{ST}/book-ball-03.jpg", "audio": "ph-m1-l03-p3"},
                {"text": "ВОТ МЯЧ!", "spread_image": f"{ST}/book-ball-04.jpg", "audio": "ph-m1-l03-p4"},
                {"text": "КОТ РАД.", "spread_image": f"{ST}/book-ball-05.jpg", "audio": "ph-m1-l03-p5"},
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
            "scene_image": IMG["shelf"],
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
            "scene_image": IMG["shelf"],
            "audio": "ph-m1-l04-which",
            "rounds": [
                {
                    "prompt_image": IMG["ball"],
                    "prompt_alt": "Мяч",
                    "correct": "ball_book",
                    "options": [
                        _opt("home", "Дома", IMG["cover_home"]),
                        _opt("box", "Кот и коробка", IMG["cover_box"]),
                        _opt("rain", "Дождь за окном", IMG["cover_rain"]),
                        _opt("ball_book", "Где мяч?", IMG["cover_ball"]),
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
            "scene_image": SCENE_RAIN,
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
            "scene_image": f"{ST}/scene-wave-stones.jpg",
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


LETTERS_ORDER: dict[int, list[str]] = {
    # Порядок и искорки — из docs/early-courses/09-voice-actor-letters-module1.docx
    # Станции без номера в листе сюда не входят (удалены как лишние/повторы).
    1: [
        "trail",
        "meet",
        "motor",
        "or",
        "spread",  # ★ звук
        "build",
        "quest",
        "grid",
        "hop",
        "chase",
        "first_letter",
        "catch",
        "sort",  # ★ буква
        "join_am",
        "slot_am",  # ★ слог
        "chest",
    ],
    2: [
        "trail",
        "meet",
        "echo",
        "azbuka",  # ★ звук
        "build",
        "hop",
        "grid",
        "catch",
        "maze",
        "first_letter",  # ★ буква
        "join_mu",
        "slots",
        "or",
        "quest",
        "slots_um",  # ★ слог
        "chest",
    ],
    3: [
        "trail",
        "meet",
        "round",
        "azbuka",  # ★ звук
        "build",
        "hop",
        "chase",
        "quest",
        "count",
        "board",
        "catch",
        "sort",
        "first_letter",  # ★ буква
        "spread",  # review (в листе тоже 13 — сразу после first)
        "join_mo",
        "slots",  # ★ слог
        "chest",
    ],
    4: [
        "trail",
        "meet",
        "hiss",
        "hop",
        "pause",
        "azbuka",  # ★ звук
        "build",
        "grid",
        "chase",
        "first_letter",
        "catch",
        "count",
        "sort",  # ★ буква
        "spread",
        "join_sa",
        "slots",
        "slots_so",
        "quest",  # ★ слог
        "chest",
    ],
}

LETTERS_SPARKS: dict[int, dict[str, str]] = {
    1: {"spread": "sound", "sort": "letter", "slot_am": "syllable"},
    2: {"azbuka": "sound", "first_letter": "letter", "slots_um": "syllable"},
    3: {"azbuka": "sound", "first_letter": "letter", "slots": "syllable"},
    4: {"azbuka": "sound", "sort": "letter", "quest": "syllable"},
}

LETTERS_LINES: dict[int, dict[str, str]] = {
    1: {
        "trail": "На тропе зажглась новая буква. Помнишь машину? Она гудит: м-м-м. Познакомься с буквой М.",
        "motor": "Что гудит м-м-м?",
        "chase": "Теперь поймай их на поляне. Найди букву М. Не спутай с другими буквами.",
        "quest": "Медведь начинается на М. Найди его.",
    },
    2: {
        "hop": "Буквы бегают по поляне! Лови букву У. Другие буквы не трогай.",
        "slots": "Склеим: му, М и У рядом — получается МУ",
    },
    3: {
        "chase": "Теперь поймай их на поляне. Найди все буквы О. Не спутай с другими буквами.",
    },
    4: {
        "hop": "Найди букву С. Она говорит с-с-с.",
        "grid": "Теперь найди все буквы С на доске.",
        "chase": "Теперь поймай их на поляне. Найди все буквы С. Не спутай с другими буквами.",
        "chest": "Ура, все искорки с нами! Теперь ты знаешь букву С.",
    },
}

_CHAPTER_BY_KIND = {
    "sound": "Искорка 1 · Звук",
    "letter": "Искорка 2 · Буква",
    "syllable": "Искорка 3 · Слог",
}


def _finalize_letter_lesson(
    stations: list[dict[str, Any]],
    order: list[str],
    sparks: dict[str, str],
    lines: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Собирает урок в порядке листа: только нумерованные станции, искорки как помечено."""
    by_id = {s["id"]: deepcopy(s) for s in stations}
    missing = [sid for sid in order if sid not in by_id]
    if missing:
        raise KeyError(f"letter stations missing ids: {missing}")

    spark_ids = set(sparks)
    # Секции по ближайшей следующей искорке в порядке.
    section_for: dict[str, str] = {}
    pending_kind = "sound"
    spark_kinds_in_order = [sparks[sid] for sid in order if sid in sparks]
    kind_iter = iter(spark_kinds_in_order)
    pending_kind = next(kind_iter, "letter")
    for sid in order:
        section_for[sid] = pending_kind
        if sid in sparks:
            pending_kind = next(kind_iter, "syllable")

    out: list[dict[str, Any]] = []
    for sid in order:
        st = by_id[sid]
        st["spark"] = False
        st.pop("spark_kind", None)
        if sid in sparks:
            kind = sparks[sid]
            st["spark"] = True
            st["spark_kind"] = kind
            st["spark_group"] = kind
        elif "spark_group" not in st and sid not in ("trail", "meet", "chest", "pause"):
            st["spark_group"] = section_for[sid]
        if sid not in ("trail", "meet", "chest") and sid != "pause":
            st["chapter"] = _CHAPTER_BY_KIND.get(section_for[sid], st.get("chapter") or "Буква")
        if lines and sid in lines:
            st["slovik_line"] = lines[sid]
        # М · квест только картинка медведя (без слога) — по тексту листа.
        if sid == "quest" and st.get("audio") == "bo-m1-l01-quest":
            st["title"] = "Медведь на М"
            st["steps"] = [
                {
                    "kind": "find",
                    "prompt": "Картинка на М",
                    "correct": "bear",
                    "options": [
                        _opt("bear", "Медведь", IMG["bear"]),
                        _opt("sun", "Солнце", IMG["sun"]),
                        _opt("kot", "Кот", IMG["kot"]),
                    ],
                }
            ]
            st["hint"] = "Картинка медведя."
        out.append(st)
    return out


LETTERS: dict[int, list[dict[str, Any]]] = {
    1: _finalize_letter_lesson(_letters_1(), LETTERS_ORDER[1], LETTERS_SPARKS[1], LETTERS_LINES[1]),
    2: _finalize_letter_lesson(_letters_2(), LETTERS_ORDER[2], LETTERS_SPARKS[2], LETTERS_LINES[2]),
    3: _finalize_letter_lesson(_letters_3(), LETTERS_ORDER[3], LETTERS_SPARKS[3], LETTERS_LINES[3]),
    4: _finalize_letter_lesson(_letters_4(), LETTERS_ORDER[4], LETTERS_SPARKS[4], LETTERS_LINES[4]),
}

STORIES: dict[int, list[dict[str, Any]]] = {
    1: _stories_1(),
    2: _stories_2(),
    3: _stories_3(),
    4: _stories_4(),
}

LETTERS_META = {
    1: {"title": "Машина на поляне", "badge": "Знаю букву М"},
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
