"""
Celery application configuration.
"""

from celery import Celery

from app.config import settings


# -------------------------
# Create Celery application
# -------------------------

celery_app = Celery(
    "rag_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


# -------------------------
# Celery configuration
# -------------------------

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Automatically retry failed connections to Redis.
    broker_connection_retry_on_startup=True,

    # Import tasks automatically.
    include=[
        "app.worker.tasks",
    ],
)