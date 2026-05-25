from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "araf_ecommerce",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
)


@celery_app.task(name="app.workers.healthcheck")
def healthcheck() -> str:
    return "ok"
