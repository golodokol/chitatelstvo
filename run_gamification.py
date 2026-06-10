#!/usr/bin/env python3
"""CLI: событие обучения → JSON с наградой и сообщениями."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Корень проекта в PYTHONPATH при запуске из папки ЧИТАТЕЛЬСТВО
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gamification.engine import (  # noqa: E402
    GamificationRequest,
    LearnerState,
    generate_reward,
    request_from_dict,
    response_to_dict,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Геймификация литературной школы онлайн")
    p.add_argument(
        "--event",
        required=False,
        choices=[
            "first_task",
            "lesson_complete",
            "comprehension",
            "meaning_analysis",
            "creative_task",
            "retelling",
            "mini_check",
            "live_meeting",
            "initiative",
            "streak_3",
            "streak_5",
            "module_complete",
        ],
        help="Тип события обучения",
    )
    p.add_argument("--child", default="", help="Имя ребёнка")
    p.add_argument("--tale", default="", help="Название сказки")
    p.add_argument("--level", default="Старт", help="Текущий уровень")
    p.add_argument("--badges", default="", help="Бейджи через запятую")
    p.add_argument("--points", type=int, default=0, help="Текущие баллы")
    p.add_argument("--week", type=int, default=1, help="Неделя модуля")
    p.add_argument("--notes", default="", help="Комментарий или ответ ребёнка")
    p.add_argument(
        "--input",
        type=Path,
        help="JSON-файл с запросом (перекрывает флаги CLI)",
    )
    p.add_argument(
        "--rules-only",
        action="store_true",
        help="Только правила, без LLM (для тестов без API-ключа)",
    )
    return p


def main() -> int:
    args = build_parser().parse_args()

    if args.input:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        req = request_from_dict(data)
    elif args.event:
        badges = [b.strip() for b in args.badges.split(",") if b.strip()]
        req = GamificationRequest(
            event_type=args.event,
            learner=LearnerState(
                child_name=args.child,
                current_level=args.level,
                current_badges=badges,
                total_points=args.points,
                tale_title=args.tale,
                module_week=args.week,
            ),
            notes=args.notes,
        )
    else:
        build_parser().error("Укажите --event или --input")

    use_llm = not args.rules_only
    result = generate_reward(req, use_llm=use_llm)
    print(json.dumps(response_to_dict(result), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
