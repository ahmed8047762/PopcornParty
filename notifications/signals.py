import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from events.models import Invitation
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Notification
from .tasks import send_invitation_email

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Invitation)
def invitation_post_save(sender, instance, created, **kwargs):
    """
    Signal handler to send email notifications when a new invitation is created
    """
    try:
        if created:
            logger.info(f"Sending invitation email for invitation {instance.id}")
            send_invitation_email.delay(instance.id)
    except Exception as e:
        logger.error(f"Error queuing invitation email: {str(e)}")
