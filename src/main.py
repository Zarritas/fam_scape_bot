"""
Entry point principal del bot de Telegram.

Inicializa todos los componentes y arranca el bot.
"""

import asyncio
import signal

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
)

from src.bot.handlers.admin import (
    force_scrape_callback,
    force_scrape_command,
    last_errors_command,
    status_command,
)
from src.bot.handlers.competitions import (
    upcoming_command,
)
from src.bot.handlers.search import (
    SELECT_DATE,
    SELECT_DISCIPLINE,
    SELECT_METHOD,
    SELECT_SEX,
    SELECT_TYPE,
    cancel_handler,
    date_selected,
    discipline_selected,
    method_selected,
    search_command,
    search_slider_callback,
    sex_selected,
    type_selected,
)
from src.bot.handlers.start import help_command, start_command
from src.bot.handlers.subscriptions import (
    smart_subscribe_callback,
    subscriptions_command,
    unsubscribe_callback,
)
from src.config import settings
from src.database.engine import close_db, init_db
from src.scheduler.runner import setup_scheduler, start_scheduler, stop_scheduler
from src.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)


def create_application() -> Application:
    """
    Crea y configura la aplicación del bot.

    Registra todos los handlers y configura la aplicación.
    """
    # Crear aplicación
    application = Application.builder().token(settings.telegram_bot_token).build()

    # Handlers básicos
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ayuda", help_command))
    application.add_handler(CommandHandler("help", help_command))

    # Handlers de suscripciones
    application.add_handler(CommandHandler("suscripciones", subscriptions_command))

    # Conversation handler para búsquedas
    search_conv = ConversationHandler(
        entry_points=[
            CommandHandler("buscar", search_command),
            CommandHandler("prueba", search_command),
        ],
        states={
            SELECT_METHOD: [
                CallbackQueryHandler(method_selected, pattern=r"^method:"),
                CallbackQueryHandler(cancel_handler, pattern=r"^cancel$"),
            ],
            SELECT_DATE: [
                CallbackQueryHandler(date_selected, pattern=r"^date:"),
                CallbackQueryHandler(method_selected, pattern=r"^back:date$"),
                CallbackQueryHandler(cancel_handler, pattern=r"^cancel$"),
            ],
            SELECT_TYPE: [
                CallbackQueryHandler(type_selected, pattern=r"^type:"),
                CallbackQueryHandler(method_selected, pattern=r"^back:method$"),
                CallbackQueryHandler(cancel_handler, pattern=r"^cancel$"),
            ],
            SELECT_DISCIPLINE: [
                CallbackQueryHandler(discipline_selected, pattern=r"^disc:"),
                CallbackQueryHandler(type_selected, pattern=r"^back:type$"),
                CallbackQueryHandler(cancel_handler, pattern=r"^cancel$"),
            ],
            SELECT_SEX: [
                CallbackQueryHandler(sex_selected, pattern=r"^sex:"),
                CallbackQueryHandler(discipline_selected, pattern=r"^back:disc$"),
                CallbackQueryHandler(cancel_handler, pattern=r"^cancel$"),
            ],
        },
        fallbacks=[
            CommandHandler("cancelar", cancel_handler),
        ],
        allow_reentry=True,
    )
    application.add_handler(search_conv)

    # Otros handlers de usuario
    application.add_handler(CommandHandler("proximas", upcoming_command))
    application.add_handler(CallbackQueryHandler(search_slider_callback, pattern="^search:"))
    application.add_handler(CallbackQueryHandler(smart_subscribe_callback, pattern="^smart_sub:"))
    application.add_handler(CallbackQueryHandler(unsubscribe_callback, pattern="^unsub:"))
    application.add_handler(CallbackQueryHandler(cancel_handler, pattern=r"^cancel$"))

    # Handlers de admin
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("force_scrape", force_scrape_command))
    application.add_handler(CommandHandler("last_errors", last_errors_command))

    # Callback para force_scrape
    application.add_handler(CallbackQueryHandler(force_scrape_callback, pattern=r"^admin:"))

    return application


async def main() -> None:
    """
    Función principal del bot.

    Inicializa componentes y arranca el bot en modo polling.
    """
    # Configurar logging
    setup_logging()
    logger.info("Iniciando Bot de Atletismo Madrid...")

    # Inicializar base de datos
    logger.info("Inicializando base de datos...")
    await init_db()

    # Crear aplicación
    application = create_application()

    # Configurar scheduler con referencia al bot
    logger.info("Configurando scheduler...")
    await setup_scheduler(bot=application.bot)
    start_scheduler()

    # Manejar señales para shutdown limpio
    def handle_shutdown(sig, frame):  # noqa: ARG001
        logger.info(f"Recibida señal {sig}, cerrando...")
        asyncio.create_task(shutdown(application))

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Iniciar bot
    logger.info("Bot iniciado. Presiona Ctrl+C para detener.")

    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )

        # Mantener el bot corriendo
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Error fatal: {e}")
    finally:
        await shutdown(application)


async def shutdown(application: Application) -> None:
    """Cierra todos los componentes de forma ordenada."""
    logger.info("Cerrando componentes...")

    try:
        stop_scheduler()
    except Exception as e:
        logger.error(f"Error deteniendo scheduler: {e}")

    try:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
    except Exception as e:
        logger.error(f"Error deteniendo bot: {e}")

    try:
        await close_db()
    except Exception as e:
        logger.error(f"Error cerrando BD: {e}")

    logger.info("Bot cerrado correctamente.")
