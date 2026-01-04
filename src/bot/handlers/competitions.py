"""
Handlers para comandos de competiciones.
"""

from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.messages import UPCOMING_COMPETITIONS, NO_UPCOMING, GENERIC_ERROR, NO_SUBSCRIPTIONS
from src.database.engine import get_session_factory
from src.database.repositories import CompetitionRepository
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def upcoming_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
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
                comps_text += (
                    f"• <b>{date_str}</b> - {comp.name}{mod_icon}\n"
                    f"  📍 {comp.location}\n"
                )
            
            await update.message.reply_text(
                UPCOMING_COMPETITIONS.format(competitions=comps_text),
                parse_mode="HTML",
            )
            
    except Exception as e:
        logger.error(f"Error obteniendo competiciones: {e}")
        await update.message.reply_text(GENERIC_ERROR, parse_mode="HTML")
            
async def check_subscriptions_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handler para /revisar - muestra competiciones de sus suscripciones."""
    if not update.effective_user or not update.message:
        return
    
    session_factory = get_session_factory()
    telegram_id = update.effective_user.id
    
    try:
        async with session_factory() as session:
            from src.database.repositories import UserRepository, SubscriptionRepository, CompetitionRepository
            user_repo = UserRepository(session)
            sub_repo = SubscriptionRepository(session)
            comp_repo = CompetitionRepository(session)
            
            # Obtener usuario y sus suscripciones
            user = await user_repo.get_by_telegram_id(telegram_id)
            if not user:
                await update.message.reply_text(NO_SUBSCRIPTIONS, parse_mode="HTML")
                return
            
            subscriptions = await sub_repo.get_by_user(user.id)
            if not subscriptions:
                await update.message.reply_text(NO_SUBSCRIPTIONS, parse_mode="HTML")
                return
            
            # Obtener próximas competiciones
            competitions = await comp_repo.get_upcoming(from_date=date.today())
            
            # Encontrar coincidencias
            user_notifications = []
            sub_set = {(s.discipline.lower(), s.sex) for s in subscriptions}
            
            for comp in competitions:
                for event in comp.events:
                    if (event.discipline.lower(), event.sex) in sub_set:
                        user_notifications.append({
                            "competition": comp,
                            "event": event,
                        })
            
            if not user_notifications:
                await update.message.reply_text(
                    "📭 No hay competiciones próximas para tus pruebas suscritas.",
                    parse_mode="HTML"
                )
                return
            
            # Formatear y enviar mensaje
            from src.notifications.service import format_notification_message
            message = format_notification_message(user_notifications)
            
            # Cambiar el encabezado para que sea más apropiado para consulta manual
            message = message.replace("🏃 ¡Nuevas competiciones para ti!", "<b>📋 Competiciones para tus pruebas:</b>")
            
            await update.message.reply_text(message, parse_mode="HTML")
            
    except Exception as e:
        logger.error(f"Error en /revisar: {e}")
        await update.message.reply_text(GENERIC_ERROR, parse_mode="HTML")
