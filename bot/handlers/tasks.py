from telegram import Update
from telegram.ext import ContextTypes

from database.tasks import (
    add_task,
    get_tasks,
    complete_task,
)


async def tasks_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    tasks = get_tasks(user_id)

    if not tasks:

        await update.message.reply_text(
            "فعلاً کاری ثبت نکردی."
        )

        return

    lines = [
        "کارهای تو:\n"
    ]

    for task in tasks:

        status = (
            "✅"
            if task["completed"]
            else "⬜"
        )

        lines.append(
            f"{status} {task['id']}. {task['title']}"
        )

    await update.message.reply_text(
        "\n".join(lines)
    )


async def add_task_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if not context.args:

        await update.message.reply_text(
            "بعد از /addtask کاری که باید انجام بدی رو بنویس."
        )

        return

    title = " ".join(context.args).strip()

    task_id = add_task(
        user_id,
        title
    )

    await update.message.reply_text(
        f"ثبت شد.\n"
        f"شماره کار: {task_id}"
    )


async def complete_task_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if not context.args:

        await update.message.reply_text(
            "شماره کار رو بده.\n"
            "مثلاً:\n"
            "/done 3"
        )

        return

    try:
        task_id = int(context.args[0])

    except ValueError:

        await update.message.reply_text(
            "شماره کار باید عدد باشه."
        )

        return

    success = complete_task(
        user_id,
        task_id
    )

    if success:

        await update.message.reply_text(
            "انجام‌شده ثبتش کردم."
        )

    else:

        await update.message.reply_text(
            "چنین کاری پیدا نکردم."
        )