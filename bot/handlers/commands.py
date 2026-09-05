from telegram import Update
from telegram.ext import ContextTypes

from database.users import save_user
from hero.memory import get_user_memories, forget_all


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.effective_user:
        return

    user = update.effective_user

    save_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    await update.message.reply_text(
        "هیرو آنلاین شد.\n\n"
        "من فقط یه ربات چت نیستم.\n"
        "می‌تونم کنارت باشم، کارهات رو مدیریت کنم، "
        "چیزهایی که برات مهمه رو به خاطر بسپارم "
        "و هر وقت لازم شد باهات حرف بزنم.\n\n"
        "بگو ببینم چی کار داری."
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "دستورهای Hero AI:\n\n"
        "/start - شروع کار\n"
        "/help - راهنما\n"
        "/memory - دیدن حافظه ذخیره‌شده\n"
        "/forget - پاک کردن حافظه\n"
        "/tasks - دیدن کارها\n"
    )


async def memory_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    memories = get_user_memories(user_id)

    await update.message.reply_text(
        "چیزهایی که فعلاً ازت به خاطر دارم:\n\n"
        + memories
    )


async def forget_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    forget_all(user_id)

    await update.message.reply_text(
        "حافظه مربوط به تو پاک شد."
    )