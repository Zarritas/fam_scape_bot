"""
Handlers para gestión de suscripciones.

Permite a los usuarios suscribirse/desuscribirse de pruebas específicas
y recibir notificaciones automáticas.
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.keyboards import get_subscriptions_management_keyboard
from src.database.engine import get_session_factory
from src.database.repositories import SubscriptionRepository, UserRepository
from src.utils.logging import get_logger

logger = get_logger(__name__)





async def subscriptions_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """
    Handler para el comando /suscripciones.

    Muestra la lista de suscripciones del usuario con opciones para desuscribirse.
    """
    if not update.message:
        return

    user_id = update.effective_user.id
    session_factory = get_session_factory()

    try:
        async with session_factory() as session:
            # Obtener usuario
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(user_id)
            if not user:
                await update.message.reply_text("❌ Usuario no encontrado. Usa /start primero.")
                return

            # Obtener suscripciones
            sub_repo = SubscriptionRepository(session)
            subscriptions = list(await sub_repo.get_by_user(user.id))

            if not subscriptions:
                await update.message.reply_text(
                    "<b>📋 Tus suscripciones</b>\n\n"
                    "No tienes suscripciones activas.\n\n"
                    "<b>¿Cómo suscribirte?</b>\n"
                    "• Usa <code>/buscar</code> para encontrar pruebas\n"
                    "• Selecciona una disciplina y sexo\n"
                    "• Click en ⭐ <b>Suscribirse</b> en los resultados\n\n"
                    "<b>¡Las suscripciones se hacen con botones, no hay que escribir!</b>",
                    parse_mode="HTML",
                )
                return

            # Crear teclado de gestión
            keyboard = get_subscriptions_management_keyboard(subscriptions)

            # Crear mensaje con lista de suscripciones
            subs_text = "<b>📋 Tus suscripciones activas:</b>\n\n"
            for i, sub in enumerate(subscriptions, 1):
                sex_label = (
                    "Masculino" if sub.sex == "M" else ("Femenino" if sub.sex == "F" else "Ambos")
                )
                subs_text += f"{i}. {sub.discipline} {sex_label}\n"

            subs_text += "\n<i>Click en ❌ para desuscribirte</i>"

            await update.message.reply_text(
                subs_text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )

    except Exception as e:
        logger.error(f"Error obteniendo suscripciones: {e}")
        await update.message.reply_text(
            "❌ Error al obtener tus suscripciones. Inténtalo de nuevo."
        )


async def unsubscribe_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """
    Callback para desuscribirse desde la lista de suscripciones.

    Patrón: "unsub:disciplina:sexo"
    """
    query = update.callback_query
    await query.answer()

    if not query:
        return

    # Parsear callback data: "unsub:400m:M"
    parts = query.data.split(":")
    if len(parts) != 3 or parts[0] != "unsub":
        await query.edit_message_text("❌ Callback inválido")
        return

    discipline = parts[1]
    sex = parts[2]
    user_id = query.from_user.id

    session_factory = get_session_factory()

    try:
        async with session_factory() as session:
            # Obtener usuario
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(user_id)
            if not user:
                await query.edit_message_text("❌ Usuario no encontrado")
                return

            user_id_db = user.id

            # Desuscribir
            sub_repo = SubscriptionRepository(session)
            success = await sub_repo.unsubscribe(
                user_id=user_id_db,
                discipline=discipline,
                sex=sex,
            )

            if success:
                sex_label = "Masculino" if sex == "M" else ("Femenino" if sex == "F" else "Ambos")
                await query.edit_message_text(
                    f"✅ <b>Desuscrito correctamente</b>\n\n"
                    f"📋 {discipline} {sex_label}\n\n"
                    f"Ya no recibirás notificaciones para esta prueba.\n\n"
                    f"📱 Usa <code>/suscripciones</code> para ver tus suscripciones restantes.",
                    parse_mode="HTML",
                )
            else:
                await query.edit_message_text(
                    "❌ No se encontró la suscripción o ya estaba eliminada."
                )

            await session.commit()

    except Exception as e:
        logger.error(f"Error en desuscripción: {e}")
        await query.edit_message_text("❌ Error al procesar la desuscripción. Inténtalo de nuevo.")


async def smart_subscribe_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,  # noqa: ARG001
) -> None:
    """
    Callback inteligente para suscribirse/desuscribirse desde búsqueda.

    Patrón: "smart_sub:disciplina:sexo:action"
    Donde action es "sub" o "unsub"
    """
    query = update.callback_query
    await query.answer()

    if not query:
        return

    # Parsear callback data: "smart_sub:400m:M:sub"
    parts = query.data.split(":")
    if len(parts) != 4 or parts[0] != "smart_sub":
        await query.edit_message_text("❌ Callback inválido")
        return

    discipline = parts[1]
    sex = parts[2]
    action = parts[3]  # "sub" o "unsub"
    user_id = query.from_user.id

    session_factory = get_session_factory()

    try:
        async with session_factory() as session:
            # Obtener usuario
            user_repo = UserRepository(session)
            user = await user_repo.get_by_telegram_id(user_id)
            if not user:
                await query.edit_message_text("❌ Usuario no encontrado")
                return

            user_id_db = user.id
            sub_repo = SubscriptionRepository(session)
            sex_label = "Masculino" if sex == "M" else ("Femenino" if sex == "F" else "Ambos")

            if action == "sub":
                # Suscribir
                subscription, created = await sub_repo.subscribe(
                    user_id=user_id_db,
                    discipline=discipline,
                    sex=sex,
                )

                if created:
                    response = (
                        f"✅ <b>Suscrito correctamente</b>\n\n"
                        f"📋 {discipline} {sex_label}\n\n"
                        f"🔔 Recibirás notificaciones automáticas diarias "
                        f"a las 10:00 cuando haya nuevas competiciones "
                        f"con esta prueba."
                    )
                else:
                    response = (
                        f"ℹ️ <b>Ya estabas suscrito</b>\n\n"
                        f"📋 {discipline} {sex_label}\n\n"
                        f"Sigues recibiendo notificaciones para esta prueba."
                    )

            elif action == "unsub":
                # Desuscribir
                success = await sub_repo.unsubscribe(
                    user_id=user.id,
                    discipline=discipline,
                    sex=sex,
                )

                if success:
                    response = (
                        f"✅ <b>Desuscrito correctamente</b>\n\n"
                        f"📋 {discipline} {sex_label}\n\n"
                        f"Ya no recibirás notificaciones para esta prueba."
                    )
                else:
                    response = "❌ No se encontró la suscripción."

            else:
                response = "❌ Acción inválida"

            await query.edit_message_text(response, parse_mode="HTML")
            await session.commit()

    except Exception as e:
        logger.error(f"Error en suscripción inteligente: {e}")
        await query.edit_message_text("❌ Error al procesar la solicitud. Inténtalo de nuevo.")
