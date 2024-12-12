from celery_app import app as celery_application
from notifications.tasks import send_notification_email  # Explicitly import the task

__all__ = ('celery_application','send_notification_email')
