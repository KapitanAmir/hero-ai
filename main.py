import logging

from telegram import Update
from telegram.error import NetworkError, TimedOut
from telegram.request import HTTPXRequest
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN

from database.database import init_database

from bot.handlers.commands import (
    start_command,
    help_command,
    memory_command,
    forget_command,
)

from bot.handlers.tasks import (
    tasks_command,
    add_task_command,
    complete_task_command,
)

from bot.handlers.chat import chat_handler

from utils.logger import setup_logger


# ============================================================
# LOGGING
# ============================================================

def configure_logging():

    logging.getLogger("httpx").setLevel(
        logging.WARNING
    )

    logging.getLogger("httpcore").setLevel(
        logging.WARNING
    )

    logging.getLogger("telegram").setLevel(
        logging.WARNING
    )

    logging.getLogger("telegram.ext").setLevel(
        logging.WARNING
    )

    logging.getLogger("apscheduler").setLevel(
        logging.WARNING
    )

    logging.getLogger("google").setLevel(
        logging.WARNING
    )

    logging.getLogger("google.genai").setLevel(
        logging.WARNING
    )

    logging.getLogger("groq").setLevel(
        logging.WARNING
    )


# ============================================================
# TELEGRAM ERROR HANDLER
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger = logging.getLogger("HeroAI")

    error = context.error

    # خطاهای موقت شبکه را فقط گزارش کن
    # و اجازه بده polling ادامه پیدا کند.
    if isinstance(
        error,
        (
            NetworkError,
            TimedOut,
        )
    ):

        logger.warning(
            "Temporary Telegram network problem. "
            "Polling will continue."
        )

        return

    logger.error(
        "Telegram handler error: %s",
        error
    )


# ============================================================
# TELEGRAM REQUEST
# ============================================================

def create_telegram_request():

    return HTTPXRequest(

        connect_timeout=30.0,

        read_timeout=60.0,

        write_timeout=30.0,

        pool_timeout=30.0,

        connection_pool_size=20,
    )


# ============================================================
# APPLICATION
# ============================================================

def create_application():

    request = create_telegram_request()

    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .request(request)
        .build()
    )

    return application


# ============================================================
# HANDLERS
# ============================================================

def register_handlers(
    application
):

    # --------------------------------------------------------
    # COMMANDS
    # --------------------------------------------------------

    application.add_handler(
        CommandHandler(
            "start",
            start_command
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )

    application.add_handler(
        CommandHandler(
            "memory",
            memory_command
        )
    )

    application.add_handler(
        CommandHandler(
            "forget",
            forget_command
        )
    )

    # --------------------------------------------------------
    # TASKS
    # --------------------------------------------------------

    application.add_handler(
        CommandHandler(
            "tasks",
            tasks_command
        )
    )

    application.add_handler(
        CommandHandler(
            "addtask",
            add_task_command
        )
    )

    application.add_handler(
        CommandHandler(
            "done",
            complete_task_command
        )
    )

    # --------------------------------------------------------
    # CHAT
    # --------------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            chat_handler
        )
    )

    # --------------------------------------------------------
    # ERRORS
    # --------------------------------------------------------

    application.add_error_handler(
        error_handler
    )


# ============================================================
# MAIN
# ============================================================

def main():

    logger = setup_logger()

    configure_logging()

    logger.info(
        "Starting Hero AI..."
    )

    # --------------------------------------------------------
    # TOKEN
    # --------------------------------------------------------

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN داخل .env تنظیم نشده است."
        )

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    try:

        init_database()

        logger.info(
            "Database initialized."
        )

    except Exception as e:

        logger.exception(
            "Database initialization failed: %s",
            e
        )

        raise

    # --------------------------------------------------------
    # APPLICATION
    # --------------------------------------------------------

    application = create_application()

    register_handlers(
        application
    )

    logger.info(
        "Hero AI is running."
    )

    # --------------------------------------------------------
    # POLLING
    # --------------------------------------------------------

    try:

        application.run_polling(

            timeout=20,

            drop_pending_updates=True,

            allowed_updates=Update.ALL_TYPES,

            stop_signals=None,
        )

    except KeyboardInterrupt:

        logger.info(
            "Hero AI stopped by user."
        )

    except Exception as e:

        # خطای شبکه نباید کل ربات را بی‌دلیل بکشد.
        if isinstance(
            e,
            (
                NetworkError,
                TimedOut,
            )
        ):

            logger.warning(
                "Telegram network connection lost. "
                "Restarting polling..."
            )

        else:

            logger.exception(
                "Hero AI stopped because of an unexpected error: %s",
                e
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()