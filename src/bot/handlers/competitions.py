"""
Handlers para comandos de competiciones.
"""

from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.messages import GENERIC_ERROR, NO_UPCOMING, UPCOMING_COMPETITIONS
from src.database.engine import get_session_factory
from src.database.repositories import CompetitionRepository
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def upcoming_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """Handler para /proximas - muestra próximas competiciones."""
    if not update.message:
        return

    session_factory = get_session_factory()

    try:
        async with session_factory() as session:
            comp_repo = CompetitionRepository(session)
            competitions = await comp_repo.get_upcoming(from_date=date.today())

            if not competitions:
                await update.message.reply_text(
                    NO_UPCOMING,
                    parse_mode="HTML",
                )
                return

            # Limitar a las próximas 10
            competitions = competitions[:10]

            comps_text = ""
            for comp in competitions:
                date_str = comp.competition_date.strftime("%d/%m")
                mod_icon = " ⚠️" if comp.has_modifications else ""
                comps_text += f"• <b>{date_str}</b> - {comp.name}{mod_icon}\n  📍 {comp.location}\n"

            await update.message.reply_text(
                UPCOMING_COMPETITIONS.format(competitions=comps_text),
                parse_mode="HTML",
            )

    except Exception as e:
        logger.error(f"Error obteniendo competiciones: {e}")
        await update.message.reply_text(GENERIC_ERROR, parse_mode="HTML")
