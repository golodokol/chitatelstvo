"""Подбор правила из recommendation-rules.csv по ответам квиза."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from config.settings import ROOT

RULES_PATH = ROOT / "docs" / "email-templates" / "recommendation-rules.csv"


@dataclass(frozen=True)
class RecommendationRule:
    rule_id: str
    priority: int
    quiz_variant: str
    child_age_min: int | None
    child_age_max: int | None
    quiz_signal_id: str
    quiz_signal_value: str
    grade_or_group: str
    recommended_course_title: str
    recommended_course_group: str
    trial_lesson_slug: str
    trial_lesson_title: str
    program_url: str
    subject_line: str
    founder_note_template: str

    def as_dict(self) -> dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "priority": str(self.priority),
            "quiz_variant": self.quiz_variant,
            "child_age_min": "" if self.child_age_min is None else str(self.child_age_min),
            "child_age_max": "" if self.child_age_max is None else str(self.child_age_max),
            "quiz_signal_id": self.quiz_signal_id,
            "quiz_signal_value": self.quiz_signal_value,
            "grade_or_group": self.grade_or_group,
            "recommended_course_title": self.recommended_course_title,
            "recommended_course_group": self.recommended_course_group,
            "trial_lesson_slug": self.trial_lesson_slug,
            "trial_lesson_title": self.trial_lesson_title,
            "program_url": self.program_url,
            "subject_line": self.subject_line,
            "founder_note_template": self.founder_note_template,
        }


def _parse_int(value: str) -> int | None:
    value = (value or "").strip().lower()
    if not value or value == "any":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_rule(row: dict[str, str]) -> RecommendationRule:
    return RecommendationRule(
        rule_id=row["rule_id"].strip(),
        priority=int(row["priority"]),
        quiz_variant=(row["quiz_variant"] or "any").strip(),
        child_age_min=_parse_int(row.get("child_age_min", "")),
        child_age_max=_parse_int(row.get("child_age_max", "")),
        quiz_signal_id=(row["quiz_signal_id"] or "").strip(),
        quiz_signal_value=(row["quiz_signal_value"] or "").strip(),
        grade_or_group=(row["grade_or_group"] or "any").strip(),
        recommended_course_title=(row["recommended_course_title"] or "").strip(),
        recommended_course_group=(row["recommended_course_group"] or "").strip(),
        trial_lesson_slug=(row["trial_lesson_slug"] or "").strip(),
        trial_lesson_title=(row["trial_lesson_title"] or "").strip(),
        program_url=(row["program_url"] or "").strip(),
        subject_line=(row["subject_line"] or "").strip(),
        founder_note_template=(row["founder_note_template"] or "").strip(),
    )


@lru_cache(maxsize=1)
def load_recommendation_rules() -> tuple[RecommendationRule, ...]:
    if not RULES_PATH.is_file():
        return ()
    with RULES_PATH.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter=";"))
    return tuple(_parse_rule(row) for row in rows)


def _age_matches(rule: RecommendationRule, child_age: int | None) -> bool:
    if rule.child_age_min is None and rule.child_age_max is None:
        return True
    if child_age is None:
        return False
    if rule.child_age_min is not None and child_age < rule.child_age_min:
        return False
    if rule.child_age_max is not None and child_age > rule.child_age_max:
        return False
    return True


def _variant_matches(rule: RecommendationRule, quiz_variant: str | None) -> bool:
    variant = (quiz_variant or "").strip() or "any"
    if rule.quiz_variant == "any":
        return True
    return rule.quiz_variant == variant


def _signal_matches(rule: RecommendationRule, answers_by_id: dict[str, str]) -> bool:
    signal_id = rule.quiz_signal_id
    if not signal_id:
        return False
    answer = (answers_by_id.get(signal_id) or "").strip()
    return answer == rule.quiz_signal_value


def fallback_trial_slug(*, quiz_variant: str | None, child_age: int | None) -> str:
    """Пробник, если у правила нет slug — квиз всё равно открывает урок сам."""
    variant = (quiz_variant or "").strip()
    if variant == "early":
        if child_age is not None and child_age >= 6:
            return "early-stories-trial-lesson-01"
        return "early-letters-trial-lesson-01"
    if child_age is not None and child_age >= 9:
        return "extra-9-11-self_paced-stage-1-lesson-01"
    return "extra-6-8-self_paced-stage-1-lesson-01"


def match_recommendation_rule_by_trial_slug(trial_slug: str) -> RecommendationRule | None:
    slug = (trial_slug or "").strip()
    if not slug:
        return None
    for rule in load_recommendation_rules():
        if rule.trial_lesson_slug == slug:
            return rule
    return None


def match_recommendation_rule(
    *,
    quiz_variant: str | None,
    child_age: int | None,
    answers_by_id: dict[str, str],
) -> RecommendationRule | None:
    """Первое подходящее правило с наименьшим priority."""
    matched: list[RecommendationRule] = []
    for rule in load_recommendation_rules():
        if rule.quiz_signal_id == "trial_completed":
            continue
        if not _variant_matches(rule, quiz_variant):
            continue
        if not _age_matches(rule, child_age):
            continue
        if not _signal_matches(rule, answers_by_id):
            continue
        matched.append(rule)
    if not matched:
        return None
    matched.sort(key=lambda r: r.priority)
    return matched[0]
