"""Простой RAG: разбивка markdown на чанки и поиск по ключевым словам."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from gamification.config import RAG_DIR, RAG_TOP_K

_WORD_RE = re.compile(r"[а-яёa-z0-9]+", re.IGNORECASE)

# Какие файлы RAG релевантны для типа события
_EVENT_FILES: dict[str, list[str]] = {
    "first_task": ["pravila_shkoly.md", "formuly_pohvaly.md", "shablony_zadaniy.md"],
    "lesson_complete": ["pravila_shkoly.md", "formuly_pohvaly.md", "shablony_zadaniy.md"],
    "comprehension": ["formuly_pohvaly.md", "shablony_zadaniy.md", "skazochnye_motivy.md"],
    "meaning_analysis": ["formuly_pohvaly.md", "arhetipy.md", "skazochnye_motivy.md"],
    "creative_task": ["formuly_pohvaly.md", "arhetipy.md", "shablony_zadaniy.md"],
    "retelling": ["formuly_pohvaly.md", "arhetipy.md", "shablony_zadaniy.md"],
    "mini_check": ["shablony_zadaniy.md", "pravila_shkoly.md"],
    "live_meeting": ["formuly_pohvaly.md", "shablony_zadaniy.md", "pravila_shkoly.md"],
    "initiative": ["formuly_pohvaly.md", "pravila_shkoly.md"],
    "streak_3": ["pravila_shkoly.md", "formuly_pohvaly.md"],
    "streak_5": ["pravila_shkoly.md", "formuly_pohvaly.md"],
    "module_complete": ["pravila_shkoly.md", "formuly_pohvaly.md", "skazochnye_motivy.md"],
}

_EVENT_KEYWORDS: dict[str, list[str]] = {
    "first_task": ["первый", "шаг", "начало", "задание"],
    "lesson_complete": ["урок", "сказка", "читатель", "видео", "лист"],
    "comprehension": ["понимание", "вопрос", "ответ", "следопыт", "текст"],
    "meaning_analysis": ["смысл", "анализ", "мотив", "почему", "ловец"],
    "creative_task": ["творческ", "история", "конец", "сказочник", "придумай"],
    "retelling": ["пересказ", "рассказ", "своими словами", "мастер"],
    "mini_check": ["проверка", "тест", "вопрос"],
    "live_meeting": ["встреча", "слушатель", "обсуждение", "жив"],
    "initiative": ["инициатива", "вопрос", "любопытство"],
    "streak_3": ["серия", "подряд", "три", "непрерывная"],
    "streak_5": ["серия", "подряд", "пять"],
    "module_complete": ["модуль", "заверш", "исследователь сказки", "детектив"],
}


@dataclass
class RagChunk:
    source: str
    title: str
    text: str
    score: float = 0.0


def _tokenize(text: str) -> set[str]:
    return {w.lower() for w in _WORD_RE.findall(text)}


def _split_markdown(path: Path) -> list[RagChunk]:
    raw = path.read_text(encoding="utf-8")
    parts = re.split(r"(?=^## )", raw, flags=re.MULTILINE)
    chunks: list[RagChunk] = []
    for part in parts:
        part = part.strip()
        if not part or part.startswith("# ") and "\n" not in part:
            continue
        lines = part.splitlines()
        title = lines[0].lstrip("#").strip() if lines else path.stem
        chunks.append(RagChunk(source=path.name, title=title, text=part))
    if not chunks:
        chunks.append(RagChunk(source=path.name, title=path.stem, text=raw))
    return chunks


def load_chunks(rag_dir: Path = RAG_DIR) -> list[RagChunk]:
    chunks: list[RagChunk] = []
    for path in sorted(rag_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        chunks.extend(_split_markdown(path))
    return chunks


def retrieve_context(
    event_type: str,
    *,
    tale_title: str = "",
    extra_query: str = "",
    top_k: int = RAG_TOP_K,
    rag_dir: Path = RAG_DIR,
) -> str:
    """Возвращает текстовый контекст для LLM."""
    chunks = load_chunks(rag_dir)
    preferred = set(_EVENT_FILES.get(event_type, []))
    query_tokens = _tokenize(
        " ".join(
            [
                event_type,
                tale_title,
                extra_query,
                " ".join(_EVENT_KEYWORDS.get(event_type, [])),
            ]
        )
    )

    scored: list[RagChunk] = []
    for chunk in chunks:
        text_tokens = _tokenize(chunk.text)
        overlap = len(query_tokens & text_tokens)
        score = float(overlap)
        if chunk.source in preferred:
            score += 2.0
        if overlap == 0 and chunk.source not in preferred:
            continue
        scored.append(RagChunk(chunk.source, chunk.title, chunk.text, score))

    if not scored:
        scored = [RagChunk(c.source, c.title, c.text, 0.0) for c in chunks[:top_k]]

    scored.sort(key=lambda c: c.score, reverse=True)
    selected = scored[:top_k]

    blocks = []
    for i, chunk in enumerate(selected, 1):
        blocks.append(f"### Фрагмент {i}: {chunk.source} — {chunk.title}\n{chunk.text}")
    return "\n\n".join(blocks)
