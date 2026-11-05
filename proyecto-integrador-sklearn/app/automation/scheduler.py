"""
Tareas automáticas del servicio IA.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from app.core.config import settings
from app.ml.model import sentiment_model
from app.metrics.prometheus import MODEL_LOADED

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _health_check_job():
    """Verifica el modelo; reintenta carga si falló."""
    try:
        if not sentiment_model.is_loaded:
            logger.warning("Model not loaded — retrying...")
            sentiment_model.load(
                settings.MODEL_PATH, settings.MODEL_NAME
            )

        MODEL_LOADED.set(1 if sentiment_model.is_loaded else 0)
        status = "OK" if sentiment_model.is_loaded else "DOWN"
        logger.info(f"[automation] Model health: {status}")
    except Exception as e:
        logger.error(f"[automation] Health check failed: {e}")
        MODEL_LOADED.set(0)


def start_scheduler():
    if scheduler.running:
        return
    scheduler.add_job(
        _health_check_job,
        trigger=IntervalTrigger(
            minutes=settings.HEALTH_CHECK_INTERVAL_MINUTES
        ),
        id="model_health_check",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"Scheduler started — health check every "
        f"{settings.HEALTH_CHECK_INTERVAL_MINUTES} min"
    )


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
