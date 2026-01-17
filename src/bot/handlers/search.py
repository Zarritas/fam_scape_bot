"""
Handlers para búsqueda de pruebas.
Reemplaza al sistema de suscripciones.
"""

from telegram import InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes, ConversationHandler

from src.bot.keyboards import (
    build_subscription_text,
    get_dates_keyboard,
    get_event_type_keyboard,
    get_field_events_keyboard,
    get_search_method_keyboard,
    get_sex_keyboard,
    get_smart_subscription_keyboard,
    get_track_events_keyboard,
    subscription_keyboard,
)
from src.bot.messages import GENERIC_ERROR
from src.database.engine import get_session_factory
from src.database.repositories import CompetitionRepository, SubscriptionRepository, UserRepository
from src.notifications.service import (
    format_competition_details,
    format_notification_message,
)
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Estados de conversación
SELECT_METHOD, SELECT_TYPE, SELECT_DISCIPLINE, SELECT_SEX, SELECT_DATE = range(5)

# Almacenamiento temporal
_user_event_type: dict[int, str] = {}


def combine_keyboards(
    nav_keyboard: InlineKeyboardMarkup, sub_keyboard: InlineKeyboardMarkup
) -> InlineKeyboardMarkup:
    """
    Combina teclado de navegación con teclado de suscripción.

    Args:
        nav_keyboard: Teclado de navegación (prev/next)
        sub_keyboard: Teclado de suscripción (subscribe/unsubscribe)

    Returns:
        Teclado combinado
    """
    combined_buttons = []

    # Agregar botones de navegación primero
    if nav_keyboard.inline_keyboard:
        combined_buttons.extend(nav_keyboard.inline_keyboard)

    # Agregar botones de suscripción
    if sub_keyboard.inline_keyboard:
        combined_buttons.extend(sub_keyboard.inline_keyboard)

    return InlineKeyboardMarkup(combined_buttons)


async def search_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> int:
    """
    Inicia el flujo de búsqueda de pruebas.
    """
    if not update.message:
        return ConversationHandler.END

    await update.message.reply_text(
        "<b>🔎 Buscar competiciones</b>\n\n¿Cómo quieres buscar?",
        reply_markup=get_search_method_keyboard(),
        parse_mode="HTML",
    )
    return SELECT_METHOD


async def method_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> int:
    """Handler cuando el usuario selecciona método de búsqueda."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Búsqueda cancelada.")
        return ConversationHandler.END

    method = query.data.split(":")[1]

    if method == "type":
        await query.edit_message_text(
            "<b>🔎 Buscar competiciones</b>\n\n¿Qué tipo de prueba buscas?",
            reply_markup=get_event_type_keyboard(),
            parse_mode="HTML",
        )
        return SELECT_TYPE

    elif method == "date":
        session_factory = get_session_factory()
        async with session_factory() as session:
            comp_repo = CompetitionRepository(session)
            # Obtenemos competiciones futuras para sacar las fechas
            competitions = await comp_repo.get_upcoming()

            # Extraer fechas únicas
            dates = sorted({c.competition_date for c in competitions})

            if not dates:
                await query.edit_message_text(
                    "📭 No hay competiciones programadas próximamente.",
                    parse_mode="HTML",
                )
                return ConversationHandler.END

            await query.edit_message_text(
                "<b>📅 Selecciona una fecha:</b>",
                reply_markup=get_dates_keyboard(dates),
                parse_mode="HTML",
            )
            return SELECT_DATE

    return ConversationHandler.END


async def type_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> int:
    """Handler cuando el usuario selecciona tipo de prueba."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Búsqueda cancelada.")
        return ConversationHandler.END

    # Extraer tipo seleccionado
    event_type = query.data.split(":")[1]  # "type:carrera"

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
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> int:
    """Handler cuando el usuario selecciona disciplina."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Búsqueda cancelada.")
        return ConversationHandler.END

    if query.data == "back:type":
        await query.edit_message_text(
            "<b>🔎 Buscar competiciones</b>\n\n¿Qué tipo de prueba buscas?",
            reply_markup=get_event_type_keyboard(),
            parse_mode="HTML",
        )
        return SELECT_TYPE

    # Extraer disciplina seleccionada
    discipline = query.data.split(":")[1]  # "disc:400"

    try:
        await query.edit_message_text(
            f"<b>👤 Selecciona el sexo para {discipline}:</b>",
            reply_markup=get_sex_keyboard(discipline),
            parse_mode="HTML",
        )
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            raise e
    return SELECT_SEX


async def sex_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> int:
    """Handler cuando el usuario selecciona sexo. Realiza la búsqueda."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Búsqueda cancelada.")
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

    # Realizar búsqueda
    session_factory = get_session_factory()

    await query.edit_message_text("⏳ Buscando competiciones...")

    try:
        async with session_factory() as session:
            comp_repo = CompetitionRepository(session)

            competitions = await comp_repo.get_by_event_type(discipline, sex)

            # Filtrar eventos específicos
            results = []
            for comp in competitions:
                current_events = []
                for event in comp.events:
                    # Comparar disciplina y sexo
                    # discipline viene del botón, debería coincidir con DB
                    if event.discipline == discipline and (sex == "B" or event.sex == sex):
                        current_events.append(event)

                # Crear entradas para el resultado
                for ev in current_events:
                    results.append({"competition": comp, "event": ev})

            if not results:
                sex_label = "Masculino" if sex == "M" else ("Femenino" if sex == "F" else "Ambos")
                await query.edit_message_text(
                    f"📭 No se encontraron competiciones futuras para <b>{discipline} ({sex_label})</b>.",
                    parse_mode="HTML",
                )
                return ConversationHandler.END

            # Formatear resultados (similar a check_subscriptions)
            slides = []

            # Agrupar por competición para visualización limpia?
            # format_notification_message maneja una lista pero suele generar un mensaje largo.
            # Vamos a usar la lógica de carrusel de check_subscriptions

            # format_notification_message espera una lista de items para un solo usuario.
            # Genera un bloque de texto.
            # Si tenemos 20 resultados, puede ser muy largo.
            # check_subscriptions crea un slide por competición (si agrupamos).
            # En check_subscriptions:
            # for item in user_notifications: slide = format_notification_message([item]) -> slides.append(slide)
            # Esto crea UN slide por CADA (competición, evento).

            for item in results:
                slide = format_notification_message([item])
                # Ajustar título
                slide = slide.replace(
                    "🏃 ¡Nuevas competiciones para ti!", f"<b>🔎 Resultados para {discipline}:</b>"
                )
                slides.append(slide)

            # Guardar slides y datos de búsqueda para navegación
            context.user_data["search_slides"] = slides
            context.user_data["search_discipline"] = discipline
            context.user_data["search_sex"] = sex

            # Verificar si el usuario está suscrito a esta disciplina/sexo
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(query.from_user.id)
            is_subscribed = False
            if user:
                sub_repo = SubscriptionRepository(session)
                subscription = await sub_repo.get_subscription(user.id, discipline, sex)
                is_subscribed = subscription is not None

            # Crear teclado combinado (navegación + suscripción)
            nav_keyboard = subscription_keyboard(0, len(slides), prefix="search")
            sub_keyboard = get_smart_subscription_keyboard(discipline, sex, is_subscribed)

            # Combinar teclados
            combined_keyboard = combine_keyboards(nav_keyboard, sub_keyboard)

            # Enviar primer resultado
            await query.edit_message_text(
                build_subscription_text(slides, 0),
                reply_markup=combined_keyboard,
                parse_mode="HTML",
            )

    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        await query.edit_message_text(GENERIC_ERROR, parse_mode="HTML")

    # Limpiar estado temporal
    _user_event_type.pop(query.from_user.id, None)

    return ConversationHandler.END


async def date_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> int:
    """Handler cuando el usuario selecciona una fecha."""
    query = update.callback_query
    if not query:
        return ConversationHandler.END

    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Búsqueda cancelada.")
        return ConversationHandler.END

    # Extraer fecha
    date_str = query.data.split(":")[1]  # "date:2026-01-07"
    from datetime import date

    target_date = date.fromisoformat(date_str)

    session_factory = get_session_factory()
    async with session_factory() as session:
        comp_repo = CompetitionRepository(session)
        competitions = await comp_repo.get_by_exact_date(target_date)

    if not competitions:
        await query.edit_message_text("📭 No se encontraron competiciones para esa fecha.")
        return ConversationHandler.END

    # Formatear resultados
    # Aquí queremos mostrar TODOS los eventos de la competición

    slides = []

    for comp in competitions:
        # Usamos el nuevo formateador que maneja lista de eventos vacía
        slide = format_competition_details(
            competition=comp,
            events=comp.events,  # Esto ya es una lista de objetos Event
        )
        slides.append(slide)

    context.user_data["search_slides"] = slides

    await query.edit_message_text(
        build_subscription_text(slides, 0),
        reply_markup=subscription_keyboard(0, len(slides), prefix="search"),
        parse_mode="HTML",
    )

    return ConversationHandler.END


async def cancel_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> int:
    """Handler genérico para cancelar."""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text("❌ Operación cancelada.")
    elif update.message:
        await update.message.reply_text("❌ Operación cancelada.")

    return ConversationHandler.END


async def search_slider_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Callback para navegación de resultados de búsqueda."""
    query = update.callback_query
    await query.answer()

    # "search:next:0"
    _, action, index = query.data.split(":")
    index = int(index)

    slides = context.user_data.get("search_slides")
    discipline = context.user_data.get("search_discipline")
    sex = context.user_data.get("search_sex")

    if not slides:
        await query.edit_message_text("⚠️ La sesión ha caducado. Vuelve a buscar.")
        return

    if action == "next":
        index += 1
    else:
        index -= 1

    # Recrear teclado combinado con suscripción
    nav_keyboard = subscription_keyboard(index, len(slides), prefix="search")

    # Verificar estado de suscripción si tenemos los datos
    is_subscribed = False
    if discipline and sex:
        session_factory = get_session_factory()
        try:
            async with session_factory() as session:
                user_repo = UserRepository(session)
                user = await user_repo.get_by_telegram_id(query.from_user.id)
                if user:
                    sub_repo = SubscriptionRepository(session)
                    subscription = await sub_repo.get_subscription(user.id, discipline, sex)
                    is_subscribed = subscription is not None

            sub_keyboard = get_smart_subscription_keyboard(discipline, sex, is_subscribed)
            combined_keyboard = combine_keyboards(nav_keyboard, sub_keyboard)
        except Exception as e:
            logger.error(f"Error verificando suscripción en navegación: {e}")
            combined_keyboard = nav_keyboard
    else:
        combined_keyboard = nav_keyboard

    await query.edit_message_text(
        build_subscription_text(slides, index),
        reply_markup=combined_keyboard,
        parse_mode="HTML",
    )
