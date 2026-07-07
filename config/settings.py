import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

# --- API ---
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))

# --- Auth (OTP + JWT для приложения) ---
JWT_SECRET = os.getenv("JWT_SECRET", WEBHOOK_SECRET).strip()
JWT_TTL_SECONDS = int(os.getenv("JWT_TTL_SECONDS", str(60 * 60 * 24 * 30)))
OTP_TTL_SECONDS = int(os.getenv("OTP_TTL_SECONDS", "600"))
OTP_MAX_SENDS_PER_HOUR = int(os.getenv("OTP_MAX_SENDS_PER_HOUR", "5"))
OTP_MAX_VERIFY_ATTEMPTS = int(os.getenv("OTP_MAX_VERIFY_ATTEMPTS", "8"))

# --- Database ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://literary:literary@localhost:5432/literary_school",
)

# --- Redis ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_KEY = os.getenv("QUEUE_KEY", "literary_school:jobs")

# --- Gamification ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
USE_LLM = os.getenv("USE_LLM", "1").strip().lower() in ("1", "true", "yes")

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "").strip()
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "").strip()
# Пока с VPS нет доступа к api.telegram.org (нужен VPN) — держите 0
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "0").strip().lower() in ("1", "true", "yes")


def resolve_notification_channel(channel: str) -> str:
    """telegram/both → web/email, если Telegram отключён."""
    if TELEGRAM_ENABLED:
        return channel
    if channel == "telegram":
        return "web"
    if channel == "both":
        return "email"
    return channel

# --- Email (SMTP) ---
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
SMTP_FROM = os.getenv("SMTP_FROM", "school@example.com").strip()
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "1").strip().lower() in ("1", "true", "yes")

# Каналы: email | telegram | both | web
# web = только личная страница прогресса (без push)
DEFAULT_NOTIFICATION_CHANNEL = os.getenv("DEFAULT_NOTIFICATION_CHANNEL", "email")

# --- Плеер урока ---
LESSON_SIGNING_SECRET = os.getenv("LESSON_SIGNING_SECRET", WEBHOOK_SECRET).strip()
LESSON_LINK_TTL_SECONDS = int(os.getenv("LESSON_LINK_TTL_SECONDS", str(60 * 60 * 24 * 90)))
# Порог бейджа «Читатель» (lesson_complete): доля длительности видео.
VIDEO_BADGE_THRESHOLD = float(os.getenv("VIDEO_BADGE_THRESHOLD", "0.7"))
# Сколько секунд видео нужно для перехода к заданиям (без бейджа).
VIDEO_UNLOCK_SECONDS = int(os.getenv("VIDEO_UNLOCK_SECONDS", "180"))
# Обратная совместимость: старый порог = бейдж.
VIDEO_WATCH_THRESHOLD = float(os.getenv("VIDEO_WATCH_THRESHOLD", str(VIDEO_BADGE_THRESHOLD)))
# Секрет для /test/urok/{secret} — приватная страница теста урока (пусто = выключено)
TEST_LESSON_SECRET = os.getenv("TEST_LESSON_SECRET", "").strip()
# Новая сказка открывается каждые N дней (обычно 7 = понедельник)
LESSON_WEEK_DAYS = int(os.getenv("LESSON_WEEK_DAYS", "7"))
# Общий старт модуля для всех семей (понедельник): YYYY-MM-DD
_MODULE_START_RAW = os.getenv("MODULE_START_DATE", "").strip()


def _parse_module_start_date(raw: str) -> date | None:
    if not raw:
        return None
    return date.fromisoformat(raw)


MEETING_ADDON_MODULE_ID = int(os.getenv("MEETING_ADDON_MODULE_ID", "19"))
MEETING_ADDON_PRICE_RUB = int(os.getenv("MEETING_ADDON_PRICE_RUB", "799"))

MODULE_START_DATE = _parse_module_start_date(_MODULE_START_RAW)

# --- Yandex Object Storage (видео) ---
YANDEX_ACCESS_KEY = os.getenv("YANDEX_ACCESS_KEY", "").strip()
YANDEX_SECRET_KEY = os.getenv("YANDEX_SECRET_KEY", "").strip()
YANDEX_BUCKET = os.getenv("YANDEX_BUCKET", "").strip()
YANDEX_ENDPOINT = os.getenv("YANDEX_ENDPOINT", "https://storage.yandexcloud.net").strip()
YANDEX_PUBLIC_BASE = os.getenv("YANDEX_PUBLIC_BASE", "").strip()
YANDEX_PRESIGN_TTL = int(os.getenv("YANDEX_PRESIGN_TTL", "14400"))
