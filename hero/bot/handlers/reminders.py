from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes


async def reminder_test(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "سیستم یادآوری Hero در نسخه بعدی "
        "به صورت کامل به مدیریت زمان متصل می‌شود."
    )