"""
Celery Configuration for Halilit Support Center v8.0

Defines task queues, worker routing, and distributed execution settings
for async product sync pipeline (CommercialScout → OfficialVerifier → ExternalValidator).
"""

import os
from celery import Celery
from kombu import Exchange, Queue
from datetime import timedelta

# Initialize Celery application
celery_app = Celery(
    'halilit',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
)

# Core Celery Configuration
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Timezone
    timezone='UTC',
    enable_utc=True,

    # Task execution
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Time limits (prevent infinite loops)
    task_time_limit=3600,        # 1 hour hard limit
    task_soft_time_limit=3400,   # 56 min soft limit (SoftTimeLimitExceeded)

    # Workers
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Results
    result_expires=3600,  # Keep results for 1 hour
    result_persistent=True,

    # Task auto-retry configuration
    task_auto_retry_for=(Exception,),
    task_max_retries=3,
    task_default_retry_delay=60,  # 1 min retry interval
)

# Define Task Routing (which worker processes which task)
celery_app.conf.task_routes = {
    'backend.tasks.harvest.*': {'queue': 'harvest', 'routing_key': 'harvest.*'},
    'backend.tasks.enrich.*': {'queue': 'enrich', 'routing_key': 'enrich.*'},
    'backend.tasks.validate.*': {'queue': 'validate', 'routing_key': 'validate.*'},
    'backend.tasks.learn.*': {'queue': 'learn', 'routing_key': 'learn.*'},
    'backend.tasks.feedback.*': {'queue': 'feedback', 'routing_key': 'feedback.*'},
}

# Define Queue Topology (priority, routing, durability)
default_exchange = Exchange('tasks', type='direct', durable=True)

celery_app.conf.task_queues = (
    # Harvest Queue (High Priority - Scraping)
    Queue(
        'harvest',
        exchange=default_exchange,
        routing_key='harvest.*',
        queue_arguments={'x-max-length': 10000}  # Max 10k tasks in queue
    ),

    # Enrich Queue (High Priority - Agent Processing)
    Queue(
        'enrich',
        exchange=default_exchange,
        routing_key='enrich.*',
        queue_arguments={'x-max-length': 10000}
    ),

    # Validate Queue (Medium Priority - Auditing)
    Queue(
        'validate',
        exchange=default_exchange,
        routing_key='validate.*',
        queue_arguments={'x-max-length': 5000}
    ),

    # Learning Queue (Low Priority - Background Learning)
    Queue(
        'learn',
        exchange=default_exchange,
        routing_key='learn.*',
        queue_arguments={'x-max-length': 5000}
    ),

    # Feedback Queue (Low Priority - User feedback)
    Queue(
        'feedback',
        exchange=default_exchange,
        routing_key='feedback.*',
        queue_arguments={'x-max-length': 5000}
    ),

    # Default Queue (Fallback)
    Queue('default', exchange=default_exchange, routing_key='default'),
)

# Periodic Tasks (if using celery beat in the future)
celery_app.conf.beat_schedule = {
    # Can add periodic tasks here
    # 'refresh-learning-cache': {
    #     'task': 'backend.tasks.learn.refresh_learning_cache',
    #     'schedule': timedelta(hours=6),
    # },
}

# Configure logging


def setup_celery_logging():
    """Configure structured logging for Celery tasks"""
    import logging

    logger = logging.getLogger('celery')
    logger.setLevel(logging.INFO)

    # Structured format for task logging
    formatter = logging.Formatter(
        '[%(asctime)s] [CELERY] [%(levelname)s] %(message)s'
    )

    # Console handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


celery_logger = setup_celery_logging()

# Health check endpoint


def health_check():
    """Check if Celery broker is healthy"""
    try:
        with celery_app.connection() as conn:
            conn.connect()
        return {'status': 'healthy', 'broker': 'connected'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}
