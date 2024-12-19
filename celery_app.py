import os
from celery import Celery

import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie2gether.settings')

# Load environment variables
load_dotenv(override=True)

# Get Redis URL from environment variable, default to Redis service URL in Docker
broker_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

# Log environment variables
logger.info(f"EMAIL_HOST_USER: {os.environ.get('EMAIL_HOST_USER')}")
logger.info(f"REDIS_URL: {os.environ.get('REDIS_URL')}")

# Create celery app
app = Celery('movie2gether', broker=broker_url)

# Configure Celery to use Redis as broker and result backend
app.conf.update(
    broker_url=broker_url,
    result_backend=broker_url,
)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
