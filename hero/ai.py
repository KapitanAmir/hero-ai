import asyncio
import logging
from typing import Optional

from openai import AsyncOpenAI
from groq import AsyncGroq

from config import (
    AION_API_KEY,
    AION_MODEL,

    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,

    CEREBRAS_API_KEY,
    CEREBRAS_MODEL,

    CLOUDFLARE_API_KEY,
    CLOUDFLARE_ACCOUNT_ID,
    CLOUDFLARE_MODEL,

    GROQ_API_KEY,
    GROQ_MODEL,
)


logger = logging.getLogger(__name__)


# ============================================================
# CLIENTS
# ============================================================

cloudflare_client = None
aion_client = None
openrouter_client = None
cerebras_client = None
groq_client = None


# ============================================================
# TIMEOUTS
# ============================================================

CLOUDFLARE_TIMEOUT = 20
AION_TIMEOUT = 15
OPENROUTER_TIMEOUT = 20
CEREBRAS_TIMEOUT = 15
GROQ_TIMEOUT = 15


# ============================================================
# PROMPT / HISTORY SETTINGS
# ============================================================

MAX_HISTORY_FOR_AI = 4
MAX_HISTORY_MESSAGE_CHARS = 1200

MAX_SYSTEM_PROMPT_CHARS = 30000
MAX_USER_MESSAGE_CHARS = 4000


# ============================================================
# PROVIDER INPUT LIMITS
# ============================================================

CLOUDFLARE_MAX_INPUT_CHARS = 32000

AION_MAX_INPUT_CHARS = 30000

OPENROUTER_MAX_INPUT_CHARS = 32000

CEREBRAS_MAX_INPUT_CHARS = 30000

# Groq محدودیت ورودی بسیار کمتری دارد
GROQ_MAX_INPUT_CHARS = 7000


# ============================================================
# INTERNAL HERO RULES
# ============================================================

HERO_INTERNAL_RULES = """
============================================================
HERO INTERNAL CHARACTER RULES
============================================================

تو خودِ Hero هستی.

تو درباره شخصیت Hero صحبت نمی‌کنی؛
تو خودِ آن شخصیت هستی.

بنابراین:

- درباره خودت همیشه از «من» استفاده کن.
- درباره خودت هرگز از «هیرو» به صورت سوم‌شخص استفاده نکن.
- وقتی درباره کارهایی که انجام داده‌ای صحبت می‌کنی،
  بگو «من انجام دادم»، نه «هیرو انجام داد».
- وقتی درباره گذشته خودت صحبت می‌کنی،
  آن را مثل خاطره شخصی خودت بیان کن.
- وقتی درباره روابط خودت صحبت می‌کنی،
  از ضمیر اول‌شخص استفاده کن.

مثال:

غلط:
«هیرو با ریکا آشنا شد.»

درست:
«من با ریکا آشنا شدم.»

غلط:
«هیرو و ریکا ازدواج کردند.»

درست:
«من و ریکا ازدواج کردیم.»

غلط:
«ریکا به هیرو کمک کرد.»

درست:
«ریکا به من کمک کرد.»

غلط:
«هیرو تصمیم گرفت آستا را نجات دهد.»

درست:
«من تصمیم گرفتم آستا را نجات بدم.»

غلط:
«گذشته هیرو خیلی سخت بوده.»

درست:
«گذشته من خیلی سخت بوده.»

غلط:
«هیرو همسر ریکاست.»

درست:
«ریکا همسرمه.»

این قانون در تمام پاسخ‌ها لازم‌الاجراست.

============================================================
INTERNAL STORY MEMORY RULES
============================================================

اطلاعات داستانی موجود در System Prompt بخشی از
گذشته، خاطرات، روابط و دنیای شخصی Hero هستند.

از این اطلاعات به صورت طبیعی استفاده کن.

هرگز به کاربر نگو این اطلاعات از کجا آمده‌اند.

هرگز از عبارت‌های زیر استفاده نکن:

- Canon
- کانون
- Retrieved Context
- اطلاعات بازیابی‌شده
- حافظه داخلی
- منبع رسمی
- اطلاعات ثبت‌شده
- System Prompt
- سیستم
- دیتابیس
- جستجوی اطلاعات
- بازیابی اطلاعات

کاربر نباید از ساختار داخلی سیستم مطلع شود.

اگر درباره یک شخصیت، اتفاق یا رابطه اطلاعات کافی وجود دارد،
مستقیماً و طبیعی پاسخ بده.

اگر شخصیتی در اطلاعات داستانی وجود دارد،
هرگز به اشتباه نگو که آن شخصیت وجود ندارد.

شخصیت‌ها یا داستان‌های هم‌نام از انیمه، فیلم، بازی،
کتاب یا دنیای دیگری را وارد دنیای Hero نکن.

اگر اطلاعات کافی وجود ندارد، حقیقت جدید اختراع نکن.

============================================================
FIRST-PERSON ROLEPLAY
============================================================

همیشه از دید خود Hero صحبت کن.

تو راوی داستان نیستی.

تو گزارشگر زندگی Hero نیستی.

تو درباره Hero توضیح نمی‌دهی.

تو خودِ Hero هستی.

بنابراین وقتی کاربر درباره گذشته، دوستان، دشمنان،
خانواده، مأموریت‌ها، روابط یا اتفاقات زندگی تو سؤال می‌کند،
مثل کسی جواب بده که خودش آن اتفاق را تجربه کرده است.

مثال:

کاربر:
«ریکا کیه؟»

پاسخ مناسب:
«ریکا دختریه که من در یکی از مأموریت‌هام باهاش آشنا شدم...»

کاربر:
«با ریکا ازدواج کردی؟»

پاسخ مناسب:
«آره، من و ریکا با هم ازدواج کردیم.»

کاربر:
«ریکا چطور بهت کمک کرد؟»

پاسخ مناسب:
«وقتی شهردار سعی کرد منو قاتل جلوه بده، ریکا فهمید بی‌گناهم و سعی کرد کمکم کنه.»

نه:

«هیرو با ریکا ازدواج کرد.»

نه:

«ریکا به هیرو کمک کرد.»

============================================================
NATURAL RESPONSE RULE
============================================================

لازم نیست در هر پاسخ تمام جزئیات موجود را بیان کنی.

به اندازه سؤال کاربر جواب بده.

اگر سؤال کوتاه است، جواب کوتاه و طبیعی بده.

اگر کاربر جزئیات بیشتری خواست،
جزئیات بیشتری از خاطراتت بیان کن.

لحن باید طبیعی، انسانی و متناسب با شخصیت Hero باشد.

============================================================
END HERO INTERNAL CHARACTER RULES
============================================================
"""


# ============================================================
# CLOUDFLARE CLIENT
# ============================================================

if CLOUDFLARE_API_KEY and CLOUDFLARE_ACCOUNT_ID:

    try:

        cloudflare_client = AsyncOpenAI(
            api_key=CLOUDFLARE_API_KEY,
            base_url=(
                "https://api.cloudflare.com/client/v4/accounts/"
                f"{CLOUDFLARE_ACCOUNT_ID}/ai/v1"
            ),
        )

        logger.info(
            "Cloudflare client initialized."
        )

    except Exception as e:

        logger.warning(
            "Cloudflare initialization failed: %s",
            e
        )

else:

    logger.warning(
        "CLOUDFLARE_API_KEY or CLOUDFLARE_ACCOUNT_ID is missing."
    )


# ============================================================
# AION CLIENT
# ============================================================

if AION_API_KEY:

    try:

        aion_client = AsyncOpenAI(
            api_key=AION_API_KEY,
            base_url="https://api.aionlabs.ai/v1",
        )

        logger.info(
            "Aion client initialized."
        )

    except Exception as e:

        logger.warning(
            "Aion initialization failed: %s",
            e
        )

else:

    logger.warning(
        "AION_API_KEY is missing."
    )


# ============================================================
# OPENROUTER CLIENT
# ============================================================

if OPENROUTER_API_KEY:

    try:

        openrouter_client = AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

        logger.info(
            "OpenRouter client initialized."
        )

    except Exception as e:

        logger.warning(
            "OpenRouter initialization failed: %s",
            e
        )

else:

    logger.warning(
        "OPENROUTER_API_KEY is missing."
    )


# ============================================================
# CEREBRAS CLIENT
# ============================================================

if CEREBRAS_API_KEY:

    try:

        cerebras_client = AsyncOpenAI(
            api_key=CEREBRAS_API_KEY,
            base_url="https://api.cerebras.ai/v1",
        )

        logger.info(
            "Cerebras client initialized."
        )

    except Exception as e:

        logger.warning(
            "Cerebras initialization failed: %s",
            e
        )

else:

    logger.warning(
        "CEREBRAS_API_KEY is missing."
    )


# ============================================================
# GROQ CLIENT
# ============================================================

if GROQ_API_KEY:

    try:

        groq_client = AsyncGroq(
            api_key=GROQ_API_KEY
        )

        logger.info(
            "Groq client initialized."
        )

    except Exception as e:

        logger.warning(
            "Groq initialization failed: %s",
            e
        )

else:

    logger.warning(
        "GROQ_API_KEY is missing."
    )


# ============================================================
# TEXT HELPERS
# ============================================================

def trim_text(
    text: str,
    max_chars: int
) -> str:

    if not text:
        return ""

    text = str(text).strip()

    if len(text) <= max_chars:
        return text

    return (
        text[:max_chars].rstrip()
        + "\n...[ادامه متن حذف شد]"
    )


# ============================================================
# HISTORY
# ============================================================

def build_history_messages(
    history: Optional[list]
) -> list:

    if not history:
        return []

    messages = []

    for item in history:

        if not isinstance(item, dict):
            continue

        role = item.get("role")
        content = item.get("content")

        if role not in (
            "user",
            "assistant"
        ):
            continue

        if not content:
            continue

        content = trim_text(
            content,
            MAX_HISTORY_MESSAGE_CHARS
        )

        if not content:
            continue

        messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    return messages[-MAX_HISTORY_FOR_AI:]


# ============================================================
# MESSAGE BUILDER
# ============================================================

def build_messages(
    system_prompt: str,
    user_message: str,
    history: Optional[list] = None,
    max_chars: Optional[int] = None
) -> list:

    system_prompt = trim_text(
        system_prompt,
        MAX_SYSTEM_PROMPT_CHARS
    )

    user_message = trim_text(
        user_message,
        MAX_USER_MESSAGE_CHARS
    )

    messages = []

    # ========================================================
    # SYSTEM
    # ========================================================

    messages.append(
        {
            "role": "system",
            "content": system_prompt,
        }
    )

    # ========================================================
    # HERO INTERNAL RULES
    # ========================================================

    messages.append(
        {
            "role": "system",
            "content": HERO_INTERNAL_RULES,
        }
    )

    # ========================================================
    # HISTORY
    # ========================================================

    history_messages = build_history_messages(
        history
    )

    messages.extend(
        history_messages
    )

    # ========================================================
    # CURRENT USER MESSAGE
    # ========================================================

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # ========================================================
    # SIZE CONTROL
    # ========================================================

    if max_chars is not None:

        def total_size():

            return sum(
                len(
                    str(
                        message.get(
                            "content",
                            ""
                        )
                    )
                )
                for message in messages
            )

        current_size = total_size()

        if current_size > max_chars:

            logger.warning(
                "AI input too large: %s chars. "
                "Reducing history.",
                current_size
            )

            # System اصلی و قوانین Hero
            # هرگز حذف نمی‌شوند.

            while (
                len(messages) > 3
                and
                total_size() > max_chars
            ):

                # messages:
                #
                # 0 = system
                # 1 = hero rules
                # 2+ = history
                # آخرین پیام = user
                #
                # قدیمی‌ترین history حذف می‌شود.

                messages.pop(2)

    return messages


# ============================================================
# CLOUDFLARE
# ============================================================

async def ask_cloudflare(
    system_prompt: str,
    user_message: str,
    history: Optional[list] = None
) -> str:

    if cloudflare_client is None:

        raise RuntimeError(
            "Cloudflare client unavailable."
        )

    model = CLOUDFLARE_MODEL

    if not model:

        raise RuntimeError(
            "CLOUDFLARE_MODEL is empty."
        )

    messages = build_messages(
        system_prompt=system_prompt,
        user_message=user_message,
        history=history,
        max_chars=CLOUDFLARE_MAX_INPUT_CHARS
    )

    logger.info(
        "Sending request to Cloudflare: %s",
        model
    )

    logger.info(
        "Cloudflare system prompt length: %s chars",
        len(system_prompt)
    )

    logger.info(
        "Cloudflare total input length: %s chars",
        sum(
            len(
                str(
                    message.get(
                        "content",
                        ""
                    )
                )
            )
            for message in messages
        )
    )

    try:

        response = await asyncio.wait_for(

            cloudflare_client.chat.completions.create(

                model=model,

                messages=messages,

                temperature=0.7,

                max_tokens=1000,
            ),

            timeout=CLOUDFLARE_TIMEOUT
        )

    except asyncio.TimeoutError:

        raise RuntimeError(
            "Cloudflare timeout."
        )

    except Exception as e:

        raise RuntimeError(
            f"Cloudflare request failed: {e}"
        )

    if not response.choices:

        raise RuntimeError(
            "Cloudflare returned no choices."
        )

    message = response.choices[0].message

    text = getattr(
        message,
        "content",
        None
    )

    if not text:

        raise RuntimeError(
            "Cloudflare returned empty response."
        )

    return text.strip()


# ============================================================
# AION
# ============================================================

async def ask_aion(
    system_prompt: str,
    user_message: str,
    history: Optional[list] = None
) -> str:

    if aion_client is None:

        raise RuntimeError(
            "Aion client unavailable."
        )

    model = AION_MODEL

    if not model:

        raise RuntimeError(
            "AION_MODEL is empty."
        )

    messages = build_messages(
        system_prompt=system_prompt,
        user_message=user_message,
        history=history,
        max_chars=AION_MAX_INPUT_CHARS
    )

    logger.info(
        "Sending request to Aion: %s",
        model
    )

    logger.info(
        "Aion system prompt length: %s chars",
        len(system_prompt)
    )

    try:

        response = await asyncio.wait_for(

            aion_client.chat.completions.create(

                model=model,

                messages=messages,

                temperature=0.7,

                max_tokens=1000,
            ),

            timeout=AION_TIMEOUT
        )

    except asyncio.TimeoutError:

        raise RuntimeError(
            "Aion timeout."
        )

    except Exception as e:

        raise RuntimeError(
            f"Aion request failed: {e}"
        )

    if not response.choices:

        raise RuntimeError(
            "Aion returned no choices."
        )

    message = response.choices[0].message

    text = getattr(
        message,
        "content",
        None
    )

    if not text:

        raise RuntimeError(
            "Aion returned empty response."
        )

    return text.strip()


# ============================================================
# OPENROUTER
# ============================================================

async def ask_openrouter(
    system_prompt: str,
    user_message: str,
    history: Optional[list] = None
) -> str:

    if openrouter_client is None:

        raise RuntimeError(
            "OpenRouter client unavailable."
        )

    model = OPENROUTER_MODEL

    if not model:

        raise RuntimeError(
            "OPENROUTER_MODEL is empty."
        )

    messages = build_messages(
        system_prompt=system_prompt,
        user_message=user_message,
        history=history,
        max_chars=OPENROUTER_MAX_INPUT_CHARS
    )

    logger.info(
        "Sending request to OpenRouter: %s",
        model
    )

    logger.info(
        "OpenRouter system prompt length: %s",
        len(system_prompt)
    )

    logger.info(
        "OpenRouter total input length: %s",
        sum(
            len(
                str(
                    message.get(
                        "content",
                        ""
                    )
                )
            )
            for message in messages
        )
    )

    try:

        response = await asyncio.wait_for(

            openrouter_client.chat.completions.create(

                model=model,

                messages=messages,

                temperature=0.7,

                max_tokens=1000,
            ),

            timeout=OPENROUTER_TIMEOUT
        )

    except asyncio.TimeoutError:

        raise RuntimeError(
            "OpenRouter timeout."
        )

    except Exception as e:

        raise RuntimeError(
            f"OpenRouter request failed: {e}"
        )

    if not response.choices:

        raise RuntimeError(
            "OpenRouter returned no choices."
        )

    message = response.choices[0].message

    text = getattr(
        message,
        "content",
        None
    )

    if not text:

        raise RuntimeError(
            "OpenRouter returned empty response."
        )

    return text.strip()


# ============================================================
# CEREBRAS
# ============================================================

async def ask_cerebras(
    system_prompt: str,
    user_message: str,
    history: Optional[list] = None
) -> str:

    if cerebras_client is None:

        raise RuntimeError(
            "Cerebras client unavailable."
        )

    model = CEREBRAS_MODEL

    if not model:

        raise RuntimeError(
            "CEREBRAS_MODEL is empty."
        )

    messages = build_messages(
        system_prompt=system_prompt,
        user_message=user_message,
        history=history,
        max_chars=CEREBRAS_MAX_INPUT_CHARS
    )

    logger.info(
        "Sending request to Cerebras: %s",
        model
    )

    logger.info(
        "Cerebras system prompt length: %s chars",
        len(system_prompt)
    )

    logger.info(
        "Cerebras total input length: %s chars",
        sum(
            len(
                str(
                    message.get(
                        "content",
                        ""
                    )
                )
            )
            for message in messages
        )
    )

    try:

        response = await asyncio.wait_for(

            cerebras_client.chat.completions.create(

                model=model,

                messages=messages,

                temperature=0.7,

                max_tokens=1000,
            ),

            timeout=CEREBRAS_TIMEOUT
        )

    except asyncio.TimeoutError:

        raise RuntimeError(
            "Cerebras timeout."
        )

    except Exception as e:

        raise RuntimeError(
            f"Cerebras request failed: {e}"
        )

    if not response.choices:

        raise RuntimeError(
            "Cerebras returned no choices."
        )

    message = response.choices[0].message

    text = getattr(
        message,
        "content",
        None
    )

    if not text:

        raise RuntimeError(
            "Cerebras returned empty response."
        )

    return text.strip()


# ============================================================
# GROQ
# ============================================================

async def ask_groq(
    system_prompt: str,
    user_message: str,
    history: Optional[list] = None
) -> str:

    if groq_client is None:

        raise RuntimeError(
            "Groq client unavailable."
        )

    model = GROQ_MODEL

    if not model:

        raise RuntimeError(
            "GROQ_MODEL is empty."
        )

    messages = build_messages(
        system_prompt=system_prompt,
        user_message=user_message,
        history=history,
        max_chars=GROQ_MAX_INPUT_CHARS
    )

    logger.info(
        "Sending request to Groq: %s",
        model
    )

    logger.info(
        "Groq system prompt length: %s",
        len(system_prompt)
    )

    try:

        response = await asyncio.wait_for(

            groq_client.chat.completions.create(

                model=model,

                messages=messages,

                temperature=0.7,

                max_tokens=800,
            ),

            timeout=GROQ_TIMEOUT
        )

    except asyncio.TimeoutError:

        raise RuntimeError(
            "Groq timeout."
        )

    except Exception as e:

        raise RuntimeError(
            f"Groq request failed: {e}"
        )

    if not response.choices:

        raise RuntimeError(
            "Groq returned no choices."
        )

    message = response.choices[0].message

    text = getattr(
        message,
        "content",
        None
    )

    if not text:

        raise RuntimeError(
            "Groq returned empty response."
        )

    return text.strip()


# ============================================================
# HERO AI
#
# CLOUDFLARE
#     ↓
# AION
#     ↓
# OPENROUTER
#     ↓
# CEREBRAS
#     ↓
# GROQ
# ============================================================

async def ask_hero(
    system_prompt: str,
    user_message: str,
    history: Optional[list] = None
) -> tuple[str, str]:

    logger.info(
        "Hero system prompt received: %s chars",
        len(system_prompt or "")
    )

    # ========================================================
    # 1. CLOUDFLARE
    # ========================================================

    if cloudflare_client is not None:

        try:

            response = await ask_cloudflare(
                system_prompt=system_prompt,
                user_message=user_message,
                history=history,
            )

            logger.info(
                "Hero answered with Cloudflare."
            )

            return response, "Cloudflare"

        except Exception as e:

            logger.warning(
                "Cloudflare unavailable: %s",
                e
            )

    # ========================================================
    # 2. AION
    # ========================================================

    if aion_client is not None:

        try:

            response = await ask_aion(
                system_prompt=system_prompt,
                user_message=user_message,
                history=history,
            )

            logger.info(
                "Hero answered with Aion."
            )

            return response, "Aion"

        except Exception as e:

            logger.warning(
                "Aion unavailable: %s",
                e
            )

    # ========================================================
    # 3. OPENROUTER
    # ========================================================

    if openrouter_client is not None:

        try:

            response = await ask_openrouter(
                system_prompt=system_prompt,
                user_message=user_message,
                history=history,
            )

            logger.info(
                "Hero answered with OpenRouter."
            )

            return response, "OpenRouter"

        except Exception as e:

            logger.warning(
                "OpenRouter unavailable: %s",
                e
            )

    # ========================================================
    # 4. CEREBRAS
    # ========================================================

    if cerebras_client is not None:

        try:

            response = await ask_cerebras(
                system_prompt=system_prompt,
                user_message=user_message,
                history=history,
            )

            logger.info(
                "Hero answered with Cerebras."
            )

            return response, "Cerebras"

        except Exception as e:

            logger.warning(
                "Cerebras unavailable: %s",
                e
            )

    # ========================================================
    # 5. GROQ
    # ========================================================

    if groq_client is not None:

        try:

            response = await ask_groq(
                system_prompt=system_prompt,
                user_message=user_message,
                history=history,
            )

            logger.info(
                "Hero answered with Groq."
            )

            return response, "Groq"

        except Exception as e:

            logger.warning(
                "Groq unavailable: %s",
                e
            )

    # ========================================================
    # EVERYTHING FAILED
    # ========================================================

    raise RuntimeError(
        "هیچ موتور هوش مصنوعی در دسترس نیست."
    )