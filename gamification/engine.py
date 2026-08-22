"""Движок геймификации: RAG + LLM + fallback."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field

from gamification.config import (
    GAMIFICATION_TEMPERATURE,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    SYSTEM_PROMPT_PATH,
)
from gamification.rag import retrieve_context
from gamification.rules import EVENT_RULES, apply_badge_rules, fallback_messages

logger = logging.getLogger(__name__)

VALID_EVENTS = frozenset(EVENT_RULES.keys())
_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class LearnerState:
    child_name: str = ""
    current_level: str = "Старт"
    current_badges: list[str] = field(default_factory=list)
    total_points: int = 0
    tale_title: str = ""
    module_week: int = 1


@dataclass
class GamificationRequest:
    event_type: str
    learner: LearnerState = field(default_factory=LearnerState)
    notes: str = ""  # комментарий педагога или ответ ребёнка


@dataclass
class GamificationResponse:
    reward_type: str
    points: int
    badge_name: str | None
    level_change: str | None
    child_message: str
    parent_message: str
    next_action: str
    source: str = "rules"  # "llm" | "rules"


def _load_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def _build_user_prompt(req: GamificationRequest, rag_context: str) -> str:
    learner = req.learner
    return f"""## Событие
Тип: {req.event_type}
Сказка: {learner.tale_title or "не указана"}
Неделя модуля: {learner.module_week}

## Ребёнок
Имя: {learner.child_name or "не указано"}
Текущий уровень: {learner.current_level}
Уже полученные бейджи: {", ".join(learner.current_badges) or "нет"}
Всего баллов: {learner.total_points}

## Дополнительно
{req.notes or "—"}

## Контекст из базы знаний (RAG)
{rag_context}
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = _JSON_RE.search(text)
        if not match:
            raise
        return json.loads(match.group(0))


def _validate_response(data: dict) -> GamificationResponse:
    required = {
        "reward_type",
        "points",
        "badge_name",
        "level_change",
        "child_message",
        "parent_message",
        "next_action",
    }
    missing = required - data.keys()
    if missing:
        raise ValueError(f"В ответе LLM нет полей: {missing}")

    points = int(data["points"])
    badge = data["badge_name"]
    if badge in ("", "null", None):
        badge = None

    level = data["level_change"]
    if level in ("", "null", None):
        level = None

    return GamificationResponse(
        reward_type=str(data["reward_type"]),
        points=points,
        badge_name=badge,
        level_change=level,
        child_message=str(data["child_message"]).strip(),
        parent_message=str(data["parent_message"]).strip(),
        next_action=str(data["next_action"]).strip(),
        source="llm",
    )


def _call_openai(system: str, user: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=GAMIFICATION_TEMPERATURE,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content or ""


def generate_reward(req: GamificationRequest, *, use_llm: bool = True) -> GamificationResponse:
    """Главная точка входа: событие → награда + сообщения."""
    if req.event_type not in VALID_EVENTS:
        raise ValueError(
            f"Неизвестный event_type: {req.event_type}. "
            f"Допустимые: {', '.join(sorted(VALID_EVENTS))}"
        )

    rag_context = retrieve_context(
        req.event_type,
        tale_title=req.learner.tale_title,
        extra_query=req.notes,
    )

    if use_llm and OPENAI_API_KEY:
        try:
            raw = _call_openai(_load_system_prompt(), _build_user_prompt(req, rag_context))
            result = _validate_response(_extract_json(raw))
            result = _merge_with_rules(result, req)
            return result
        except Exception as exc:
            logger.warning("LLM недоступен, fallback на правила: %s", exc)

    return _generate_from_rules(req)


def _merge_with_rules(llm: GamificationResponse, req: GamificationRequest) -> GamificationResponse:
    """Подстраховка: не выдавать уже имеющийся бейдж, не понижать уровень."""
    rules = apply_badge_rules(
        req.event_type,
        req.learner.current_badges,
        req.learner.current_level,
        tale_title=req.learner.tale_title,
    )

    badge = llm.badge_name
    if badge and badge in req.learner.current_badges:
        badge = rules["badge_name"]
    if badge == "Читатель" and rules["badge_name"] is None:
        badge = None

    level = llm.level_change
    if level:
        from gamification.rules import LEVELS

        try:
            if LEVELS.index(level) <= LEVELS.index(req.learner.current_level):
                level = rules["level_change"]
        except ValueError:
            level = rules["level_change"]

    points = llm.points if llm.points >= 0 else rules["points"]

    return GamificationResponse(
        reward_type=llm.reward_type or rules["reward_type"],
        points=points,
        badge_name=badge,
        level_change=level,
        child_message=llm.child_message,
        parent_message=llm.parent_message,
        next_action=llm.next_action or rules["next_action"],
        source="llm",
    )


def _generate_from_rules(req: GamificationRequest) -> GamificationResponse:
    reward = apply_badge_rules(
        req.event_type,
        req.learner.current_badges,
        req.learner.current_level,
        tale_title=req.learner.tale_title,
    )
    messages = fallback_messages(
        req.event_type,
        req.learner.child_name,
        req.learner.tale_title,
        reward,
    )
    return GamificationResponse(
        reward_type=reward["reward_type"],
        points=reward["points"],
        badge_name=reward["badge_name"],
        level_change=reward["level_change"],
        child_message=messages["child_message"],
        parent_message=messages["parent_message"],
        next_action=reward["next_action"],
        source="rules",
    )


def request_from_dict(data: dict) -> GamificationRequest:
    learner_data = data.get("learner", {})
    learner = LearnerState(
        child_name=learner_data.get("child_name", ""),
        current_level=learner_data.get("current_level", "Старт"),
        current_badges=list(learner_data.get("current_badges", [])),
        total_points=int(learner_data.get("total_points", 0)),
        tale_title=learner_data.get("tale_title", ""),
        module_week=int(learner_data.get("module_week", 1)),
    )
    return GamificationRequest(
        event_type=data["event_type"],
        learner=learner,
        notes=data.get("notes", ""),
    )


def response_to_dict(resp: GamificationResponse) -> dict:
    return asdict(resp)
