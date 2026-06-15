"""Правила склонения имён и возраста для писем (упрощённые, без pymorphy)."""

from __future__ import annotations

# После «в» — числительные, не «шести-семи лет»:
#   ✓ «В шесть–семь лет», ✗ «В шести-семи лет»
# После «для» — родительный падеж имени:
#   ✓ «для Полины», ✗ «для Полина»
# После «о» — предложный:
#   ✓ «о Полине», ✗ «о Полина»
# Подлежащее / «что ребёнок…» — именительный:
#   ✓ «Полина редко читает»


def _normalize_name(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return "ребёнок"
    return name[0].upper() + name[1:]


def _lower_stem(name: str) -> str:
    return _normalize_name(name).lower()


def name_genitive(name: str) -> str:
    """Родительный: для Полины, про чтение Полины."""
    n = _normalize_name(name)
    lower = _lower_stem(n)
    if len(lower) < 2:
        return n

    if lower.endswith("ия"):
        return n[:-2] + "ии"
    if lower.endswith("ья"):
        return n[:-2] + "ьи"
    if lower.endswith("я"):
        return n[:-1] + "и"
    if lower.endswith("а"):
        stem = lower[:-1]
        if stem.endswith(("ш", "ж", "ч", "щ", "ц")):
            return n[:-1] + "и"
        return n[:-1] + "ы"
    if lower.endswith("й"):
        return n[:-1] + "я"
    if lower.endswith("ь"):
        return n[:-1] + "я"
    return n + "а"


def name_dative(name: str) -> str:
    """Дательный: Полине трудно понять."""
    n = _normalize_name(name)
    lower = _lower_stem(n)
    if len(lower) < 2:
        return n

    if lower.endswith("ия"):
        return n[:-2] + "ии"
    if lower.endswith("ья"):
        return n[:-2] + "ьи"
    if lower.endswith("я"):
        return n[:-1] + "е"
    if lower.endswith("а"):
        return n[:-1] + "е"
    if lower.endswith("й"):
        return n[:-1] + "ю"
    if lower.endswith("ь"):
        return n[:-1] + "ю"
    return n + "у"


def name_prepositional(name: str) -> str:
    """Предложный: о Полине."""
    n = _normalize_name(name)
    lower = _lower_stem(n)
    if len(lower) < 2:
        return n

    if lower.endswith("ия"):
        return n[:-2] + "ии"
    if lower.endswith("ья"):
        return n[:-2] + "ьи"
    if lower.endswith("я"):
        return n[:-1] + "е"
    if lower.endswith("а"):
        return n[:-1] + "е"
    if lower.endswith("й"):
        return n[:-1] + "е"
    if lower.endswith("ь"):
        return n[:-1] + "е"
    return n + "е"


def age_years_phrase(age: int) -> str:
    """«6 лет», «7 лет», «11 лет» — согласование числительного."""
    n = abs(int(age))
    mod10, mod100 = n % 10, n % 100
    if mod10 == 1 and mod100 != 11:
        word = "год"
    elif mod10 in (2, 3, 4) and mod100 not in (12, 13, 14):
        word = "года"
    else:
        word = "лет"
    return f"{n} {word}"


def age_band_intro(age: int | None) -> str:
    """Вводный абзац по возрастной группе."""
    if age is None:
        return (
            "Наши программы рассчитаны на детей 6–11 лет — "
            "именно в этом возрасте закладывается привычка не только читать, "
            "но и понимать, о чём текст."
        )
    if age <= 7:
        return (
            "В шесть–семь лет как раз закладывается привычка не только читать, "
            "но и понимать, о чём текст."
        )
    if age <= 9:
        return (
            "В восемь–девять лет дети часто читают бегло — "
            "и именно понимание прочитанного может отставать."
        )
    return (
        "В десять–одиннадцать лет важно сохранить интерес к книге "
        "и научиться думать о прочитанном."
    )
