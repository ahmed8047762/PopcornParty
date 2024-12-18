import os
from celery import Celery
from pathlib import Path
from dotenv import load_dotenv

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie2gether.settings')

# Force reload environment variables from .env file
env_path = os.path.join(Path(__file__).resolve().parent, '.env')

# Force reload environment variables
load_dotenv(env_path, override=True)

app = Celery('movie2gether')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
