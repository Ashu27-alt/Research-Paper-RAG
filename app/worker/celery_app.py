"""
Celery application configuration.
"""

import ssl

from celery import Celery

from app.config import settings


celery_app = Celery(
    "rag_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    timezone="UTC",
    enable_utc=True,

    broker_connection_retry_on_startup=True,

    broker_use_ssl={
        "ssl_cert_reqs": ssl.CERT_REQUIRED,
    },

    redis_backend_use_ssl={
        "ssl_cert_reqs": ssl.CERT_REQUIRED,
    },

    include=[
        "app.worker.tasks",
    ],
)