from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_notification_email(user_email, message):
    logger.info(f'Sending email from {settings.DEFAULT_FROM_EMAIL} to {user_email}')
    subject = 'New Event Invitation'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)