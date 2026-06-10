import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

RAG_DIR = ROOT / "rag"
PROMPTS_DIR = ROOT / "prompts"
SYSTEM_PROMPT_PATH = PROMPTS_DIR / "gamification_system.txt"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
GAMIFICATION_TEMPERATURE = float(os.getenv("GAMIFICATION_TEMPERATURE", "0.4"))

# Сколько фрагментов RAG подставлять в промпт
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "6"))
