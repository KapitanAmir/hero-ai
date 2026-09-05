import logging

from telegram import Update
from telegram.ext import ContextTypes

from hero.ai import ask_hero
from hero.prompts import build_system_prompt
from hero.canon_retriever import retrieve_canon

from database.database import (
    save_message,
    get_recent_messages,
)


logger = logging.getLogger(__name__)


# ============================================================
# CHAT HANDLER
# ============================================================

async def chat_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    دریافت پیام معمولی کاربر و ارسال آن به Hero AI.

    مسیر AI:

    Aion
       ↓
    OpenRouter
       ↓
    Groq

    همچنین Local Story Retrieval برای پیدا کردن
    اطلاعات مرتبط از داستان Hero استفاده می‌شود.

    اطلاعات داستانی فقط در صورت مرتبط بودن با سؤال
    وارد Prompt می‌شوند.
    """

    print("🔥 CHAT HANDLER CALLED")

    # ========================================================
    # 1. VALIDATE UPDATE
    # ========================================================

    if update is None:

        logger.warning(
            "Update is None."
        )

        return

    if not update.message:

        logger.warning(
            "Update has no message."
        )

        return

    if not update.message.text:

        logger.warning(
            "Message has no text."
        )

        return

    # ========================================================
    # 2. USER
    # ========================================================

    user = update.effective_user

    if not user:

        logger.warning(
            "Could not identify user."
        )

        return

    user_id = user.id

    user_message = update.message.text.strip()

    if not user_message:
        return

    logger.info(
        "User %s sent message: %s",
        user_id,
        user_message
    )

    # ========================================================
    # 3. BUILD BASE SYSTEM PROMPT
    # ========================================================

    try:

        logger.info(
            "Building Hero system prompt..."
        )

        system_prompt = build_system_prompt(
            user_id=user_id
        )

        logger.info(
            "Hero system prompt created successfully."
        )

        logger.info(
            "Base system prompt length: %s characters",
            len(system_prompt)
        )

    except Exception as e:

        logger.exception(
            "❌ ERROR BUILDING SYSTEM PROMPT: %s",
            e
        )

        await update.message.reply_text(
            "یه مشکلی توی حافظه‌م پیش اومده. "
            "یه لحظه دیگه امتحان کن."
        )

        return

    # ========================================================
    # 4. LOCAL STORY RETRIEVAL
    # ========================================================

    story_context = ""

    try:

        logger.info(
            "🔎 Searching Hero story memory..."
        )

        story_context = retrieve_canon(
            query=user_message,
            max_sections=4,
            max_chars=9000,
        )

        if story_context:

            logger.info(
                "✅ Relevant story memory retrieved."
            )

            logger.info(
                "Retrieved story memory length: %s characters",
                len(story_context)
            )

        else:

            logger.info(
                "ℹ️ No relevant story memory found."
            )

    except Exception as e:

        logger.exception(
            "❌ ERROR RETRIEVING HERO STORY: %s",
            e
        )

        story_context = ""

    # ========================================================
    # 5. INJECT STORY MEMORY
    # ========================================================

    if story_context:

        system_prompt = f"""
{system_prompt}

========================================================
HERO PERSONAL STORY MEMORY
========================================================

اطلاعات زیر بخشی از خاطرات، گذشته و دنیای شخصی Hero است.

از این اطلاعات برای پاسخ دادن به سؤال فعلی استفاده کن.

این اطلاعات را به صورت طبیعی در پاسخ خودت استفاده کن.

هرگز درباره این بخش یا نحوه دریافت آن با کاربر صحبت نکن.

هرگز نگو:
- Canon
- کانون
- اطلاعات بازیابی‌شده
- حافظه داخلی
- منبع اطلاعات
- سیستم
- دیتابیس
- Retrieved Context

اگر اطلاعاتی در این بخش وجود دارد، آن را بخشی از
تجربه و خاطرات خودت در نظر بگیر.

مهم‌ترین نکته:

تو خودِ Hero هستی.

بنابراین وقتی درباره اتفاقات این اطلاعات صحبت می‌کنی،
از اول‌شخص استفاده کن.

مثلاً:

«هیرو با ریکا آشنا شد»
غلط است.

«من با ریکا آشنا شدم»
درست است.

«هیرو و ریکا ازدواج کردند»
غلط است.

«من و ریکا ازدواج کردیم»
درست است.

========================================================
BEGIN HERO PERSONAL STORY MEMORY
========================================================

{story_context}

========================================================
END HERO PERSONAL STORY MEMORY
========================================================
"""

        logger.info(
            "✅ Story memory injected into system prompt."
        )

        logger.info(
            "Final system prompt length: %s characters",
            len(system_prompt)
        )

    else:

        logger.info(
            "⚠️ No story memory injected."
        )

    # ========================================================
    # 6. LOAD HISTORY
    # ========================================================

    history = []

    try:

        logger.info(
            "Loading conversation history..."
        )

        recent_messages = get_recent_messages(
            user_id=user_id
        )

        if recent_messages:

            for message in recent_messages:

                if not isinstance(
                    message,
                    dict
                ):
                    continue

                role = message.get(
                    "role"
                )

                content = message.get(
                    "content"
                )

                if not role:
                    continue

                if not content:
                    continue

                if role not in (
                    "user",
                    "assistant"
                ):
                    continue

                history.append(
                    {
                        "role": role,
                        "content": content,
                    }
                )

        logger.info(
            "Loaded %s previous messages.",
            len(history)
        )

    except Exception as e:

        logger.warning(
            "⚠️ Could not load chat history: %s",
            e
        )

        history = []

    # ========================================================
    # 7. SAVE USER MESSAGE
    # ========================================================

    try:

        save_message(
            user_id=user_id,
            role="user",
            content=user_message,
        )

        logger.info(
            "User message saved."
        )

    except Exception as e:

        logger.warning(
            "⚠️ Could not save user message: %s",
            e
        )

    # ========================================================
    # 8. TYPING
    # ========================================================

    try:

        await update.message.chat.send_action(
            action="typing"
        )

    except Exception as e:

        logger.debug(
            "Could not send typing action: %s",
            e
        )

    # ========================================================
    # 9. ASK HERO
    # ========================================================

    try:

        logger.info(
            "=========================================="
        )

        logger.info(
            "🤖 Sending message to Hero AI..."
        )

        if story_context:

            logger.info(
                "Story Memory: ENABLED"
            )

        else:

            logger.info(
                "Story Memory: NO MATCHING CONTEXT"
            )

        logger.info(
            "System prompt length: %s characters",
            len(system_prompt)
        )

        logger.info(
            "History messages: %s",
            len(history)
        )

        logger.info(
            "=========================================="
        )

        response_text, provider = await ask_hero(
            system_prompt=system_prompt,
            user_message=user_message,
            history=history,
        )

        logger.info(
            "=========================================="
        )

        logger.info(
            "✅ Hero AI responded successfully."
        )

        logger.info(
            "Provider used: %s",
            provider
        )

        logger.info(
            "=========================================="
        )

    except Exception as e:

        logger.exception(
            "❌ HERO AI ERROR: %s",
            e
        )

        await update.message.reply_text(
            "الان مسیرهای هوش مصنوعی در دسترس نیستن. "
            "یه لحظه دیگه امتحان کن."
        )

        return

    # ========================================================
    # 10. RESPONSE VALIDATION
    # ========================================================

    if not response_text:

        logger.error(
            "❌ AI returned an empty response."
        )

        await update.message.reply_text(
            "این دفعه جوابم خالی برگشت 😐 "
            "دوباره امتحان کن."
        )

        return

    response_text = response_text.strip()

    logger.info(
        "Hero response length: %s characters",
        len(response_text)
    )

    # ========================================================
    # 11. SAVE HERO RESPONSE
    # ========================================================

    try:

        save_message(
            user_id=user_id,
            role="assistant",
            content=response_text,
        )

        logger.info(
            "Hero response saved."
        )

    except Exception as e:

        logger.warning(
            "⚠️ Could not save Hero response: %s",
            e
        )

    # ========================================================
    # 12. SEND TO TELEGRAM
    # ========================================================

    try:

        await update.message.reply_text(
            response_text
        )

        logger.info(
            "✅ Hero response sent to Telegram."
        )

    except Exception as e:

        logger.exception(
            "❌ Could not send Hero response to Telegram: %s",
            e
        )