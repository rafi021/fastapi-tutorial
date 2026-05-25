from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "araf_ecommerce",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
)


@celery_app.task(name="app.workers.healthcheck")
def healthcheck() -> str:
    return "ok"
