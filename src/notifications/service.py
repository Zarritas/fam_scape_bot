"""
Servicio de notificaciones de Telegram.

Genera y envía mensajes personalizados a los usuarios
basándose en sus suscripciones.
"""

from typing import Any

from telegram import Bot
from telegram.error import TelegramError

from src.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def send_notification(
    bot: Bot,
    user_id: int,
    notifications: list[dict[str, Any]],
) -> bool:
    """
    Envía notificación a un usuario con sus pruebas suscritas.
    
    Args:
        bot: Instancia del bot de Telegram
        user_id: ID interno del usuario (no telegram_id)
        notifications: Lista de {'competition': Competition, 'event': Event}
        
    Returns:
        True si se envió correctamente
    """
    from src.database.engine import get_session_factory
    from src.database.repositories import UserRepository
    
    # Obtener telegram_id del usuario
    session_factory = get_session_factory()
    async with session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_id(user_id)
        
        if not user:
            logger.warning(f"Usuario {user_id} no encontrado")
            return False
        
        telegram_id = user.telegram_id
    
    # Generar mensaje
    message = format_notification_message(notifications)
    
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="HTML",
        )
        logger.info(f"Notificación enviada a {telegram_id}")
        return True
        
    except TelegramError as e:
        logger.error(f"Error enviando mensaje a {telegram_id}: {e}")
        return False


def format_notification_message(notifications: list[dict[str, Any]]) -> str:
    """
    Formatea el mensaje de notificación en HTML.
    
    Args:
        notifications: Lista de {'competition': Competition, 'event': Event}
        
    Returns:
        Mensaje formateado en HTML para Telegram
    """
    if not notifications:
        return "No hay nuevas competiciones para tus pruebas suscritas."
    
    # Agrupar por competición
    by_competition: dict[int, dict] = {}
    for notif in notifications:
        comp = notif["competition"]
        event = notif["event"]
        
        if comp.id not in by_competition:
            by_competition[comp.id] = {
                "competition": comp,
                "events": [],
            }
        by_competition[comp.id]["events"].append(event)
    
    # Construir mensaje
    lines = ["<b>🏃 ¡Nuevas competiciones para ti!</b>\n"]
    
    for comp_data in by_competition.values():
        comp = comp_data["competition"]
        events = comp_data["events"]
        
        # Formatear fecha
        date_str = comp.competition_date.strftime("%d/%m/%Y")
        
        lines.append(f"\n<b>📅 {comp.name}</b>")
        lines.append(f"📆 Fecha: {date_str}")
        lines.append(f"📍 Lugar: {comp.location}")
        
        if comp.has_modifications:
            lines.append("⚠️ <i>Convocatoria modificada</i>")
        
        lines.append("\n<b>Tus pruebas:</b>")
        
        for event in events:
            sex_emoji = "👨" if event.sex == "M" else "👩"
            time_str = ""
            if event.scheduled_time:
                time_str = f" <b>{event.scheduled_time.strftime('%H:%M')}</b>"
            
            lines.append(f"  • {event.discipline} {sex_emoji}{time_str}")
        
        lines.append(f"\n<a href=\"{comp.pdf_url}\">📄 Ver convocatoria</a>")
    
    lines.append("\n\n<i>Usa /mis_pruebas para ver tus suscripciones</i>")
    
    return "\n".join(lines)


async def send_error_to_admin(
    bot: Bot,
    error_message: str,
    stack_trace: str = "",
) -> None:
    """
    Envía un mensaje de error detallado al administrador.
    
    Args:
        bot: Instancia del bot de Telegram
        error_message: Mensaje de error
        stack_trace: Stack trace completo (opcional)
    """
    message = f"🚨 <b>Error en el sistema</b>\n\n<code>{error_message}</code>"
    
    if stack_trace:
        # Limitar longitud del stack trace
        max_length = 3000
        if len(stack_trace) > max_length:
            stack_trace = stack_trace[:max_length] + "..."
        message += f"\n\n<pre>{stack_trace}</pre>"
    
    try:
        await bot.send_message(
            chat_id=settings.admin_user_id,
            text=message,
            parse_mode="HTML",
        )
    except TelegramError as e:
        logger.error(f"Error enviando mensaje de error al admin: {e}")


async def send_calm_message_to_user(
    bot: Bot,
    telegram_id: int,
    message: str = "",
) -> None:
    """
    Envía un mensaje tranquilizador al usuario cuando hay errores.
    
    El usuario no necesita ver detalles técnicos.
    """
    if not message:
        message = (
            "🔧 Estamos experimentando algunas dificultades técnicas.\n"
            "No te preocupes, seguiremos notificándote cuando se resuelva.\n"
            "Gracias por tu paciencia."
        )
    
    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=message,
            parse_mode="HTML",
        )
    except TelegramError as e:
        logger.error(f"Error enviando mensaje a usuario {telegram_id}: {e}")
