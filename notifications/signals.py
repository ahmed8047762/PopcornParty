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
def send_invitation_notification(sender, instance, created, **kwargs):
    """
    Signal handler to send email notifications when a new invitation is created
    """
    if created:
        try:
            # Queue the invitation email task
            send_invitation_email.delay(instance.invitee.email, instance.event.id)
        except Exception as e:
            print(f"Error queuing invitation email: {str(e)}")
        logger.info(f'Invitation created for {instance.invitee.email}')
        Notification.objects.create(
            user=instance.invitee,
            message=f'You have received an invitation to the event: {instance.event.title}'
        )
