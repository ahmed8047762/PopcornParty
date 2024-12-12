import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
from events.models import Invitation
from .tasks import send_notification_email

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Invitation)
def create_notification(sender, instance, created, **kwargs):
    if created:
        logger.info(f'Invitation created for {instance.invitee.email}')
        Notification.objects.create(
            user=instance.invitee,
            message=f'You have received an invitation to the event: {instance.event.title}'
        )
        # Send email notification
        send_notification_email.delay(instance.invitee.email, f'You have received an invitation to the event: {instance.event.title}')
