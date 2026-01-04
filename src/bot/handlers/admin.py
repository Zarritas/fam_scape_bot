"""
Handlers para comandos de administrador.
"""

from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.keyboards import get_admin_confirm_scrape_keyboard
from src.bot.messages import (
    ADMIN_ERROR_LOG,
    ADMIN_FORCE_SCRAPE_RESULT,
    ADMIN_FORCE_SCRAPE_START,
    ADMIN_STATUS,
    GENERIC_ERROR,
)
from src.config import settings
from src.database.engine import get_session_factory
from src.database.repositories import (
    CompetitionRepository,
    ErrorRepository,
    UserRepository,
)
from src.scheduler.runner import get_scheduler_status
from src.utils.logging import get_logger

logger = get_logger(__name__)


def admin_required(func):
    """Decorador que verifica si el usuario es admin."""

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or update.effective_user.id != settings.admin_user_id:
            if update.message:
                await update.message.reply_text("⛔ Este comando es solo para administradores.")
            return
        return await func(update, context)

    return wrapper


@admin_required
async def status_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """Handler para /status - muestra estado del sistema."""
    if not update.message:
        return

    session_factory = get_session_factory()

    try:
        async with session_factory() as session:
            user_repo = UserRepository(session)
            comp_repo = CompetitionRepository(session)
            error_repo = ErrorRepository(session)

            # Obtener estadísticas
            users_count = await user_repo.count_active()
            competitions_count = await comp_repo.count_upcoming()
            errors_count = await error_repo.count_recent(hours=24)

        # Estado del scheduler
        scheduler_status = get_scheduler_status()
        scheduler_running = "🟢 Activo" if scheduler_status["running"] else "🔴 Detenido"

        # Próximos jobs
        next_jobs = ""
        for job in scheduler_status.get("jobs", []):
            next_run = job.get("next_run", "No programado")
            if next_run and isinstance(next_run, str):
                try:
                    dt = datetime.fromisoformat(next_run)
                    next_run = dt.strftime("%H:%M %d/%m")
                except ValueError:
                    pass
            next_jobs += f"• {job['name']}: {next_run}\n"

        if not next_jobs:
            next_jobs = "No hay jobs programados"

        await update.message.reply_text(
            ADMIN_STATUS.format(
                scheduler_status=scheduler_running,
                last_scrape="Ver logs",
                last_notify="Ver logs",
                users_count=users_count,
                competitions_count=competitions_count,
                errors_count=errors_count,
                next_jobs=next_jobs,
            ),
            parse_mode="HTML",
        )

    except Exception as e:
        logger.error(f"Error en /status: {e}")
        await update.message.reply_text(GENERIC_ERROR, parse_mode="HTML")


@admin_required
async def force_scrape_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """Handler para /force_scrape - ejecuta scraping manual."""
    if not update.message:
        return

    await update.message.reply_text(
        "⚠️ <b>¿Ejecutar scraping ahora?</b>\n\n"
        "Esto descargará y procesará todas las competiciones del calendario.",
        reply_markup=get_admin_confirm_scrape_keyboard(),
        parse_mode="HTML",
    )


async def force_scrape_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Callback para confirmar force_scrape."""
    query = update.callback_query
    if not query or not query.from_user:
        return

    await query.answer()

    # Verificar admin
    if query.from_user.id != settings.admin_user_id:
        await query.edit_message_text("⛔ No autorizado.")
        return

    if query.data == "cancel":
        await query.edit_message_text("❌ Scraping cancelado.")
        return

    if query.data != "admin:scrape:confirm":
        return

    await query.edit_message_text(
        ADMIN_FORCE_SCRAPE_START,
        parse_mode="HTML",
    )

    # Ejecutar scraping
    from src.scheduler.jobs import scraping_job

    try:
        stats = await scraping_job()

        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=ADMIN_FORCE_SCRAPE_RESULT.format(**stats),
            parse_mode="HTML",
        )

    except Exception as e:
        logger.error(f"Error en force_scrape: {e}")
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=f"❌ Error durante el scraping:\n<code>{str(e)}</code>",
            parse_mode="HTML",
        )


@admin_required
async def last_errors_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """Handler para /last_errors - muestra últimos errores."""
    if not update.message:
        return

    session_factory = get_session_factory()

    try:
        async with session_factory() as session:
            error_repo = ErrorRepository(session)
            errors = await error_repo.get_recent(limit=10, hours=24)

            if not errors:
                await update.message.reply_text("✅ No hay errores en las últimas 24 horas.")
                return

            errors_text = ""
            for error in errors:
                timestamp = error.timestamp.strftime("%H:%M %d/%m")
                errors_text += (
                    f"<b>[{timestamp}] {error.component}</b>\n"
                    f"<code>{error.error_type}: {error.message[:100]}</code>\n\n"
                )

            await update.message.reply_text(
                ADMIN_ERROR_LOG.format(errors=errors_text),
                parse_mode="HTML",
            )

    except Exception as e:
        logger.error(f"Error en /last_errors: {e}")
        await update.message.reply_text(GENERIC_ERROR, parse_mode="HTML")
