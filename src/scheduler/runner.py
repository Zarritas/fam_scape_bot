"""
Configuración del scheduler con APScheduler.

Ejecuta jobs automáticos para scraping (09:00) y notificaciones (10:00).
"""

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Scheduler global
_scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    """Obtiene o crea el scheduler."""
    global _scheduler

    if _scheduler is None:
        timezone = pytz.timezone(settings.timezone)
        _scheduler = AsyncIOScheduler(timezone=timezone)

    return _scheduler


async def setup_scheduler(bot=None) -> AsyncIOScheduler:
    """
    Configura el scheduler con todos los jobs.

    Args:
        bot: Instancia del bot de Telegram (opcional, para notificaciones)

    Returns:
        AsyncIOScheduler configurado y listo para iniciar
    """
    from src.scheduler.jobs import notification_job, scraping_job

    scheduler = get_scheduler()
    timezone = pytz.timezone(settings.timezone)

    # Job de scraping a las 09:00
    scheduler.add_job(
        scraping_job,
        CronTrigger(
            hour=settings.scrape_hour,
            minute=settings.scrape_minute,
            timezone=timezone,
        ),
        id="scraping_job",
        name="Scraping diario del calendario FAM",
        replace_existing=True,
        misfire_grace_time=3600,  # 1 hora de gracia
    )
    logger.info(
        f"Job de scraping configurado: {settings.scrape_hour:02d}:{settings.scrape_minute:02d}"
    )

    # Job de notificaciones a las 10:00
    scheduler.add_job(
        notification_job,
        CronTrigger(
            hour=settings.notify_hour,
            minute=settings.notify_minute,
            timezone=timezone,
        ),
        id="notification_job",
        name="Envío diario de notificaciones",
        replace_existing=True,
        kwargs={"bot": bot},
        misfire_grace_time=3600,
    )
    logger.info(
        f"Job de notificaciones configurado: {settings.notify_hour:02d}:{settings.notify_minute:02d}"
    )

    return scheduler


def start_scheduler() -> None:
    """Inicia el scheduler si no está corriendo."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler iniciado")


def stop_scheduler() -> None:
    """Detiene el scheduler."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler detenido")
        _scheduler = None


async def run_job_now(job_id: str) -> bool:
    """
    Ejecuta un job inmediatamente (para /force_scrape).

    Args:
        job_id: ID del job a ejecutar

    Returns:
        True si se encontró y ejecutó, False si no existe
    """
    scheduler = get_scheduler()
    job = scheduler.get_job(job_id)

    if job is None:
        logger.warning(f"Job no encontrado: {job_id}")
        return False

    # Modificar el job para ejecutar ahora
    scheduler.modify_job(job_id, next_run_time=None)  # Reset
    job.modify(next_run_time=job.trigger.get_next_fire_time(None, None))

    logger.info(f"Job {job_id} programado para ejecución inmediata")
    return True


def get_scheduler_status() -> dict:
    """
    Obtiene el estado actual del scheduler.

    Returns:
        Dict con información de estado
    """
    scheduler = get_scheduler()

    jobs_info = []
    for job in scheduler.get_jobs():
        jobs_info.append(
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            }
        )

    return {
        "running": scheduler.running,
        "jobs": jobs_info,
    }
