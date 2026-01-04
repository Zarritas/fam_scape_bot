"""
Handlers para comandos de inicio y ayuda.
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.messages import HELP_MESSAGE, WELCOME_MESSAGE
from src.database.engine import get_session_factory
from src.database.repositories import UserRepository
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """
    Handler para el comando /start.

    Registra al usuario si es nuevo y muestra mensaje de bienvenida.
    """
    if not update.effective_user or not update.message:
        return

    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name or ""
    username = update.effective_user.username

    session_factory = get_session_factory()

    async with session_factory() as session:
        user_repo = UserRepository(session)
        user, is_new = await user_repo.get_or_create(
            telegram_id=telegram_id,
            first_name=first_name,
            username=username,
        )
        await session.commit()

        if is_new:
            logger.info(f"Nuevo usuario registrado: {telegram_id} ({first_name})")
        else:
            # Reactivar si estaba inactivo
            if not user.is_active:
                await user_repo.activate(user)
                await session.commit()
                logger.info(f"Usuario reactivado: {telegram_id}")

    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode="HTML",
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """Handler para el comando /ayuda."""
    if not update.message:
        return

    await update.message.reply_text(
        HELP_MESSAGE,
        parse_mode="HTML",
    )
