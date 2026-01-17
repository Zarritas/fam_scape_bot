"""
Definición de jobs del scheduler.

Jobs:
- scraping_job: Ejecuta a las 09:00, scraping del calendario FAM
- notification_job: Ejecuta a las 10:00, envía notificaciones a usuarios
"""

from datetime import date, timedelta

from src.database.engine import get_session, get_session_factory
from src.database.repositories import (
    CompetitionRepository,
    ErrorRepository,
    NotificationRepository,
    SubscriptionRepository,
)
from src.scraper.pdf_parser import PDFParser
from src.scraper.web_scraper import WebScraper, get_current_and_next_months
from src.utils.hash import calculate_message_hash
from src.utils.logging import get_logger

logger = get_logger(__name__)


async def scraping_job() -> dict:
    """
    Job de scraping diario.

    1. Obtiene mes actual y siguiente
    2. Scrapea el calendario para cada mes
    3. Para cada competición:
       - Descarga PDF
       - Calcula hash
       - Si es nuevo o cambió: parsear y guardar
    4. Registra errores si los hay

    Returns:
        Dict con estadísticas del job
    """
    logger.info("Iniciando job de scraping")

    stats = {
        "months_scraped": 0,
        "competitions_found": 0,
        "competitions_new": 0,
        "competitions_updated": 0,
        "competitions_deleted": 0,
        "errors": 0,
    }



    scraper = WebScraper()
    parser = PDFParser()

    try:
        # Obtener meses a scrapear
        months = get_current_and_next_months()
        logger.info(f"Scrapeando {len(months)} meses: {months}")

        async with get_session() as session:
            comp_repo = CompetitionRepository(session)
            error_repo = ErrorRepository(session)

            for month, year in months:
                try:
                    # Scrapear calendario del mes
                    raw_competitions = scraper.get_competitions(month, year)
                    stats["months_scraped"] += 1
                    stats["competitions_found"] += len(raw_competitions)

                    for raw_comp in raw_competitions:
                        try:
                            # 1. Determinar si es un PDF o link externo
                            is_pdf = raw_comp.pdf_url and ".pdf" in raw_comp.pdf_url.lower()

                            competition = None
                            pdf_content = None

                            if is_pdf and raw_comp.pdf_url is not None:
                                try:
                                    # Descargar y parsear PDF
                                    pdf_content = scraper.download_pdf(raw_comp.pdf_url)
                                    competition = parser.parse(
                                        pdf_content=pdf_content,
                                        name=raw_comp.name,
                                        pdf_url=raw_comp.pdf_url,
                                        enrollment_url=raw_comp.enrollment_url,
                                        has_modifications=raw_comp.has_modifications,
                                        competition_type=raw_comp.competition_type,
                                    )
                                except Exception as e:
                                    logger.warning(
                                        f"Error parseando PDF de {raw_comp.name}: {e}. Usando datos básicos."
                                    )

                            # 2. Si no es PDF o falló el parseo, usar datos básicos del calendario
                            if not competition:
                                from src.scraper.models import Competition
                                from src.utils.hash import calculate_pdf_hash

                                # Normalizar fecha de raw_comp.date_str si fuera necesario
                                # pero el repo ya recibe la fecha como date si la tenemos
                                # Intentamos extraer una fecha date de raw_comp.date_str simplificada
                                try:
                                    day, month_num = raw_comp.date_str.split("/")
                                    comp_date = date(year, int(month_num), int(day))
                                except:  # noqa: E722
                                    comp_date = date(year, month, 1)  # Fallback al 1 del mes

                                competition = Competition(
                                    name=raw_comp.name,
                                    competition_date=comp_date,
                                    location=raw_comp.location or "Madrid",
                                    pdf_url=raw_comp.pdf_url,
                                    enrollment_url=raw_comp.enrollment_url,
                                    pdf_hash=calculate_pdf_hash(pdf_content)
                                    if pdf_content
                                    else None,
                                    has_modifications=raw_comp.has_modifications,
                                    competition_type=raw_comp.competition_type,
                                    events=[],
                                )

                            # 3. Preparar datos de eventos
                            events_data = [
                                {
                                    "discipline": e.discipline,
                                    "event_type": e.event_type.value,
                                    "sex": e.sex.value,
                                    "scheduled_time": e.scheduled_time,
                                    "category": e.category,
                                }
                                for e in competition.events
                            ]

                            # Preparar fechas adicionales
                            fechas_adicionales_parsed = None
                            if hasattr(raw_comp, 'fechas_adicionales') and raw_comp.fechas_adicionales:
                                try:
                                    fechas_adicionales_parsed = []
                                    for fecha_str in raw_comp.fechas_adicionales:
                                        # Convertir "DD/MM/YYYY" a date object
                                        parts = fecha_str.split('/')
                                        if len(parts) == 3:
                                            day, month, year = parts
                                            fecha_obj = date(int(year), int(month), int(day))
                                            fechas_adicionales_parsed.append(fecha_obj)
                                except (ValueError, IndexError) as e:
                                    logger.warning(f"Error parseando fechas adicionales: {e}")
                                    fechas_adicionales_parsed = None

                            # 4. Guardar en BD (upsert)
                            _, is_new_or_updated = await comp_repo.upsert_with_hash(
                                pdf_url=competition.pdf_url,
                                pdf_hash=competition.pdf_hash,
                                name=competition.name,
                                competition_date=competition.competition_date,
                                location=competition.location,
                                has_modifications=competition.has_modifications,
                                competition_type=competition.competition_type,
                                enrollment_url=competition.enrollment_url,
                                events=events_data,
                                fechas_adicionales=fechas_adicionales_parsed,
                            )

                            if is_new_or_updated:
                                stats["competitions_new"] += 1
                                logger.info(
                                    f"Guardada competición: {competition.name} ({len(events_data)} pruebas)"
                                )
                            else:
                                logger.debug(f"Competición sin cambios: {competition.name}")

                        except Exception as e:
                            stats["errors"] += 1
                            logger.error(f"Error procesando {raw_comp.name}: {e}")
                            await error_repo.log_error(
                                component="scraper",
                                error=e,
                                message=f"Error procesando competición: {raw_comp.name}",
                            )

                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error scrapeando mes {month}/{year}: {e}")
                    await error_repo.log_error(
                        component="scraper",
                        error=e,
                        message=f"Error scrapeando mes {month}/{year}",
                    )

            await session.commit()

            # Limpiar competiciones pasadas
            try:
                deleted_count = await comp_repo.delete_past_competitions(date.today())
                stats["competitions_deleted"] = deleted_count
                logger.info(f"Eliminadas {deleted_count} competiciones pasadas")
            except Exception as e:
                stats["errors"] += 1
                logger.error(f"Error eliminando competiciones pasadas: {e}")
                await error_repo.log_error(
                    component="scraper",
                    error=e,
                    message="Error eliminando competiciones pasadas",
                )

    except Exception as e:
        stats["errors"] += 1
        logger.error(f"Error fatal en scraping job: {e}")
        # Intentar registrar el error
        try:
            async with get_session() as session:
                error_repo = ErrorRepository(session)
                await error_repo.log_error(
                    component="scraper",
                    error=e,
                    message="Error fatal en scraping job",
                )
                await session.commit()
        except Exception:
            pass

    logger.info(f"Scraping completado: {stats}")
    return stats


async def notification_job(bot=None) -> dict:
    """
    Job de notificaciones diario.

    1. Obtiene competiciones con fecha >= hoy
    2. Para cada evento en esas competiciones:
       - Obtiene usuarios suscritos a esa disciplina+sexo
       - Filtra usuarios ya notificados
       - Envía mensaje
       - Guarda log de notificación

    Args:
        bot: Instancia del bot de Telegram (opcional)

    Returns:
        Dict con estadísticas del job
    """
    logger.info("Iniciando job de notificaciones")

    stats = {
        "users_notified": 0,
        "notifications_sent": 0,
        "notifications_skipped": 0,  # Ya enviadas
        "errors": 0,
    }

    today = date.today()

    if bot is None:
        logger.warning("Bot no configurado, saltando notificaciones")
        return stats

    # Obtener competiciones del día siguiente (para notificar con anticipación)
    tomorrow = today + timedelta(days=1)

    try:
        async with get_session() as session:
            comp_repo = CompetitionRepository(session)
            sub_repo = SubscriptionRepository(session)
            notif_repo = NotificationRepository(session)
            error_repo = ErrorRepository(session)

            # Obtener competiciones futuras y filtrar las de mañana
            all_future = await comp_repo.get_upcoming(from_date=today)
            competitions = [c for c in all_future if c.competition_date == tomorrow]

            logger.info(f"Encontradas {len(competitions)} competiciones para mañana")

            # Agrupar notificaciones por usuario para enviar mensajes consolidados
            user_notifications: dict[int, list[dict]] = {}

            for competition in competitions:
                logger.debug(f"Procesando competición: {competition.name}")

                for event in competition.events:
                    # Obtener usuarios suscritos a esta disciplina+sexo
                    user_ids = await sub_repo.get_users_for_event(
                        discipline=event.discipline,
                        sex=event.sex,
                    )

                    logger.debug(f"Evento {event.discipline} {event.sex}: {len(user_ids)} usuarios suscritos")

                    for user_id in user_ids:
                        # Verificar si ya fue notificado de este evento específico
                        if await notif_repo.was_notified(user_id, event.id):
                            stats["notifications_skipped"] += 1
                            continue

                        # Agregar a las notificaciones del usuario
                        if user_id not in user_notifications:
                            user_notifications[user_id] = []

                        user_notifications[user_id].append(
                            {
                                "competition": competition,
                                "event": event,
                            }
                        )

            # Enviar notificaciones agrupadas por usuario
            from src.notifications.service import send_notification

            for user_id, notifications in user_notifications.items():
                try:
                    logger.debug(f"Enviando {len(notifications)} notificaciones a usuario {user_id}")

                    # Enviar notificación consolidada
                    success = await send_notification(
                        bot=bot,
                        user_id=user_id,
                        notifications=notifications,
                    )

                    if success:
                        stats["users_notified"] += 1

                        # Registrar cada notificación enviada en los logs
                        for notif in notifications:
                            competition = notif["competition"]
                            message_hash = calculate_message_hash(
                                f"{user_id}_{notif['event'].id}_{competition.competition_date.isoformat()}"
                            )

                            await notif_repo.log_notification(
                                user_id=user_id,
                                event_id=notif["event"].id,
                                message_hash=message_hash,
                            )

                            stats["notifications_sent"] += 1

                        logger.info(f"Notificación enviada exitosamente a usuario {user_id}")

                    else:
                        logger.warning(f"Falló envío de notificación a usuario {user_id}")
                        stats["errors"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error enviando notificación a usuario {user_id}: {e}")

                    await error_repo.log_error(
                        component="notifications",
                        error=e,
                        message=f"Error enviando notificación a usuario {user_id}",
                    )

            await session.commit()

    except Exception as e:
        stats["errors"] += 1
        logger.error(f"Error fatal en notification job: {e}")

        try:
            async with get_session() as session:
                error_repo = ErrorRepository(session)
                await error_repo.log_error(
                    component="notifications",
                    error=e,
                    message="Error fatal en notification job",
                )
                await session.commit()
        except Exception:
            pass

    session_factory = get_session_factory()
    today = date.today()

    try:
        async with session_factory() as session:
            comp_repo = CompetitionRepository(session)
            sub_repo = SubscriptionRepository(session)
            notif_repo = NotificationRepository(session)
            error_repo = ErrorRepository(session)

            # Obtener competiciones futuras
            competitions = await comp_repo.get_upcoming(from_date=today)
            logger.info(f"Encontradas {len(competitions)} competiciones futuras")

            # Agrupar notificaciones por usuario para enviar un solo mensaje
            user_notifications: dict[int, list[dict]] = {}

            for competition in competitions:
                for event in competition.events:
                    # Obtener usuarios suscritos a esta prueba
                    user_ids = await sub_repo.get_users_for_event(
                        discipline=event.discipline,
                        sex=event.sex,
                    )

                    for user_id in user_ids:
                        # Verificar si ya fue notificado
                        if await notif_repo.was_notified(user_id, event.id):
                            stats["notifications_skipped"] += 1
                            continue

                        # Agregar a la lista de notificaciones del usuario
                        if user_id not in user_notifications:
                            user_notifications[user_id] = []

                        user_notifications[user_id].append(
                            {
                                "competition": competition,
                                "event": event,
                            }
                        )

            # Enviar notificaciones agrupadas
            from src.notifications.service import send_notification

            for user_id, notifications in user_notifications.items():
                try:
                    success = await send_notification(
                        bot=bot,
                        user_id=user_id,
                        notifications=notifications,
                    )

                    if success:
                        stats["users_notified"] += 1

                        # Registrar cada notificación enviada
                        for notif in notifications:
                            message_hash = calculate_message_hash(f"{user_id}_{notif['event'].id}")
                            await notif_repo.log_notification(
                                user_id=user_id,
                                event_id=notif["event"].id,
                                message_hash=message_hash,
                            )
                            stats["notifications_sent"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error enviando notificación a user {user_id}: {e}")
                    await error_repo.log_error(
                        component="notifications",
                        error=e,
                        message=f"Error enviando notificación a user {user_id}",
                    )

            await session.commit()

    except Exception as e:
        stats["errors"] += 1
        logger.error(f"Error fatal en notification job: {e}")
        try:
            async with session_factory() as session:
                error_repo = ErrorRepository(session)
                await error_repo.log_error(
                    component="notifications",
                    error=e,
                    message="Error fatal en notification job",
                )
                await session.commit()
        except Exception:
            pass

    logger.info(f"Notificaciones completadas: {stats}")
    return stats
