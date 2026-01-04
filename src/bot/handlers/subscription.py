"""
Handlers para comandos de suscripción.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.bot.keyboards import (
    get_event_type_keyboard,
    get_track_events_keyboard,
    get_field_events_keyboard,
    get_sex_keyboard,
    get_subscriptions_keyboard,
)
from src.bot.messages import (
    SUBSCRIPTION_SUCCESS,
    ALREADY_SUBSCRIBED,
    UNSUBSCRIPTION_SUCCESS,
    NOT_SUBSCRIBED,
    SUBSCRIPTIONS_LIST,
    NO_SUBSCRIPTIONS,
    GENERIC_ERROR,
)
from src.database.engine import get_session_factory
from src.database.repositories import UserRepository, SubscriptionRepository
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Estados de conversación para el flujo de suscripción
SELECT_TYPE, SELECT_DISCIPLINE, SELECT_SEX = range(3)

# Almacenamiento temporal del tipo seleccionado
_user_event_type: dict[int, str] = {}


async def subscribe_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """
    Inicia el flujo de suscripción.
    
    Muestra teclado para seleccionar tipo de prueba.
    """
    if not update.message:
        return ConversationHandler.END
    
    await update.message.reply_text(
        "<b>📝 Suscribirse a una prueba</b>\n\n"
        "¿Qué tipo de prueba te interesa?",
        reply_markup=get_event_type_keyboard(),
        parse_mode="HTML",
    )
    return SELECT_TYPE


async def type_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handler cuando el usuario selecciona tipo de prueba."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END
    
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Suscripción cancelada.")
        return ConversationHandler.END
    
    # Extraer tipo seleccionado
    event_type = query.data.split(":")[1]  # "type:carrera" -> "carrera"
    
    # Guardar temporalmente
    user_id = query.from_user.id
    _user_event_type[user_id] = event_type
    
    # Mostrar teclado de disciplinas
    if event_type == "carrera":
        keyboard = get_track_events_keyboard()
        msg = "🏃 Selecciona la prueba de carrera:"
    else:
        keyboard = get_field_events_keyboard()
        msg = "🎯 Selecciona la prueba de campo:"
    
    await query.edit_message_text(
        f"<b>{msg}</b>",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    return SELECT_DISCIPLINE


async def discipline_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handler cuando el usuario selecciona disciplina."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END
    
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Suscripción cancelada.")
        return ConversationHandler.END
    
    if query.data == "back:type":
        await query.edit_message_text(
            "<b>📝 Suscribirse a una prueba</b>\n\n"
            "¿Qué tipo de prueba te interesa?",
            reply_markup=get_event_type_keyboard(),
            parse_mode="HTML",
        )
        return SELECT_TYPE
    
    # Extraer disciplina seleccionada
    discipline = query.data.split(":")[1]  # "disc:400" -> "400"
    
    await query.edit_message_text(
        f"<b>👤 Selecciona el sexo para {discipline}:</b>",
        reply_markup=get_sex_keyboard(discipline),
        parse_mode="HTML",
    )
    return SELECT_SEX


async def sex_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handler cuando el usuario selecciona sexo. Finaliza la suscripción."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END
    
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("❌ Suscripción cancelada.")
        return ConversationHandler.END
    
    if query.data == "back:disc":
        user_id = query.from_user.id
        event_type = _user_event_type.get(user_id, "carrera")
        
        if event_type == "carrera":
            keyboard = get_track_events_keyboard()
            msg = "🏃 Selecciona la prueba de carrera:"
        else:
            keyboard = get_field_events_keyboard()
            msg = "🎯 Selecciona la prueba de campo:"
        
        await query.edit_message_text(
            f"<b>{msg}</b>",
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        return SELECT_DISCIPLINE
    
    # Extraer disciplina y sexo
    parts = query.data.split(":")  # "sex:400:M"
    discipline = parts[1]
    sex = parts[2]
    
    telegram_id = query.from_user.id
    
    # Procesar suscripción(es)
    session_factory = get_session_factory()
    
    try:
        async with session_factory() as session:
            user_repo = UserRepository(session)
            sub_repo = SubscriptionRepository(session)
            
            user = await user_repo.get_by_telegram_id(telegram_id)
            if not user:
                await query.edit_message_text(GENERIC_ERROR, parse_mode="HTML")
                return ConversationHandler.END
            
            if sex == "B":  # Ambos
                sexes = ["M", "F"]
            else:
                sexes = [sex]
            
            results = []
            for s in sexes:
                _, is_new = await sub_repo.subscribe(
                    user_id=user.id,
                    discipline=discipline,
                    sex=s,
                )
                sex_label = "Masculino" if s == "M" else "Femenino"
                if is_new:
                    results.append(f"✅ {discipline} {sex_label}")
                else:
                    results.append(f"ℹ️ Ya suscrito a {discipline} {sex_label}")
            
            await session.commit()
            
            response = "<b>Resultado:</b>\n" + "\n".join(results)
            response += "\n\n<i>Usa /mis_pruebas para ver tus suscripciones</i>"
            
            await query.edit_message_text(response, parse_mode="HTML")
            logger.info(f"Usuario {telegram_id} suscrito a {discipline}")
            
    except Exception as e:
        logger.error(f"Error en suscripción: {e}")
        await query.edit_message_text(GENERIC_ERROR, parse_mode="HTML")
    
    # Limpiar estado temporal
    _user_event_type.pop(telegram_id, None)
    
    return ConversationHandler.END


async def my_subscriptions_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handler para /mis_pruebas."""
    if not update.message or not update.effective_user:
        return
    
    telegram_id = update.effective_user.id
    session_factory = get_session_factory()
    
    try:
        async with session_factory() as session:
            sub_repo = SubscriptionRepository(session)
            subs = await sub_repo.get_by_user_telegram_id(telegram_id)
            
            if not subs:
                await update.message.reply_text(
                    NO_SUBSCRIPTIONS,
                    parse_mode="HTML",
                )
                return
            
            subs_text = ""
            for sub in subs:
                sex_emoji = "👨" if sub.sex == "M" else "👩"
                subs_text += f"• {sub.discipline} {sex_emoji}\n"
            
            await update.message.reply_text(
                SUBSCRIPTIONS_LIST.format(subscriptions=subs_text),
                parse_mode="HTML",
            )
            
    except Exception as e:
        logger.error(f"Error obteniendo suscripciones: {e}")
        await update.message.reply_text(GENERIC_ERROR, parse_mode="HTML")


async def unsubscribe_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handler para /desuscribir."""
    if not update.message or not update.effective_user:
        return
    
    telegram_id = update.effective_user.id
    session_factory = get_session_factory()
    
    try:
        async with session_factory() as session:
            sub_repo = SubscriptionRepository(session)
            subs = await sub_repo.get_by_user_telegram_id(telegram_id)
            
            if not subs:
                await update.message.reply_text(
                    NO_SUBSCRIPTIONS,
                    parse_mode="HTML",
                )
                return
            
            await update.message.reply_text(
                "<b>🗑️ Selecciona la suscripción a eliminar:</b>",
                reply_markup=get_subscriptions_keyboard(list(subs)),
                parse_mode="HTML",
            )
            
    except Exception as e:
        logger.error(f"Error obteniendo suscripciones: {e}")
        await update.message.reply_text(GENERIC_ERROR, parse_mode="HTML")


async def unsubscribe_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Callback para botones de desuscripción."""
    query = update.callback_query
    if not query or not query.from_user:
        return
    
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("🔙 Cerrado.")
        return
    
    # Extraer datos: "unsub:400:M"
    parts = query.data.split(":")
    if len(parts) != 3 or parts[0] != "unsub":
        return
    
    discipline = parts[1]
    sex = parts[2]
    telegram_id = query.from_user.id
    
    session_factory = get_session_factory()
    
    try:
        async with session_factory() as session:
            user_repo = UserRepository(session)
            sub_repo = SubscriptionRepository(session)
            
            user = await user_repo.get_by_telegram_id(telegram_id)
            if not user:
                await query.edit_message_text(GENERIC_ERROR, parse_mode="HTML")
                return
            
            removed = await sub_repo.unsubscribe(
                user_id=user.id,
                discipline=discipline,
                sex=sex,
            )
            
            await session.commit()
            
            if removed:
                sex_label = "Masculino" if sex == "M" else "Femenino"
                await query.edit_message_text(
                    UNSUBSCRIPTION_SUCCESS.format(
                        discipline=discipline,
                        sex=sex_label,
                    ),
                    parse_mode="HTML",
                )
            else:
                await query.edit_message_text(
                    NOT_SUBSCRIBED.format(discipline=discipline, sex=sex),
                    parse_mode="HTML",
                )
            
    except Exception as e:
        logger.error(f"Error desuscribiendo: {e}")
        await query.edit_message_text(GENERIC_ERROR, parse_mode="HTML")


async def cancel_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    """Handler genérico para cancelar conversaciones."""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text("❌ Operación cancelada.")
    elif update.message:
        await update.message.reply_text("❌ Operación cancelada.")
    
    return ConversationHandler.END
