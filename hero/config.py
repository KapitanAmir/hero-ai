import os

from dotenv import load_dotenv

load_dotenv()

# =========================
# TELEGRAM
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()


# =========================
# AION
# =========================

AION_API_KEY = os.getenv("AION_API_KEY", "").strip()
AION_MODEL = (
    os.getenv("AION_MODEL", "").strip()
    or "aion-labs/aion-3.0-mini"
)


# =========================
# OPENROUTER
# =========================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_MODEL = (
    os.getenv("OPENROUTER_MODEL", "").strip()
    or "minimax/minimax-m3:free"
)


# =========================
# CEREBRAS
# =========================

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "").strip()
CEREBRAS_MODEL = (
    os.getenv("CEREBRAS_MODEL", "").strip()
    or "gpt-oss-120b"
)


# =========================
# CLOUDFLARE
# =========================

CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY", "").strip()
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()

CLOUDFLARE_MODEL = (
    os.getenv("CLOUDFLARE_MODEL", "").strip()
    or "@cf/openai/gpt-oss-120b"
)


# =========================
# GROQ
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

GROQ_MODEL = (
    os.getenv("GROQ_MODEL", "").strip()
    or "openai/gpt-oss-20b"
)


# =========================
# DATABASE
# =========================

DATABASE_PATH = (
    os.getenv("DATABASE_PATH", "hero_ai.db").strip()
)


# =========================
# MEMORY
# =========================

MAX_HISTORY = int(
    os.getenv("MAX_HISTORY", "12")
)

MAX_MEMORIES = int(
    os.getenv("MAX_MEMORIES", "20")
)


# =========================
# VALIDATION
# =========================

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN در فایل .env تنظیم نشده است."
    )


if not AION_API_KEY:
    print(
        "⚠️ AION_API_KEY تنظیم نشده؛ Aion در دسترس نخواهد بود."
    )


if not OPENROUTER_API_KEY:
    print(
        "⚠️ OPENROUTER_API_KEY تنظیم نشده؛ "
        "OpenRouter در دسترس نخواهد بود."
    )


if not CEREBRAS_API_KEY:
    print(
        "⚠️ CEREBRAS_API_KEY تنظیم نشده؛ "
        "Cerebras در دسترس نخواهد بود."
    )


if not CLOUDFLARE_API_KEY:
    print(
        "⚠️ CLOUDFLARE_API_KEY تنظیم نشده؛ "
        "Cloudflare در دسترس نخواهد بود."
    )


if not CLOUDFLARE_ACCOUNT_ID:
    print(
        "⚠️ CLOUDFLARE_ACCOUNT_ID تنظیم نشده؛ "
        "Cloudflare در دسترس نخواهد بود."
    )


if not GROQ_API_KEY:
    print(
        "⚠️ GROQ_API_KEY تنظیم نشده؛ "
        "Groq در دسترس نخواهد بود."
    )


print(f"🧠 Aion Model: {AION_MODEL}")
print(f"🌐 OpenRouter Model: {OPENROUTER_MODEL}")
print(f"⚡ Cerebras Model: {CEREBRAS_MODEL}")
print(f"☁️ Cloudflare Model: {CLOUDFLARE_MODEL}")
print(f"🚀 Groq Model: {GROQ_MODEL}")