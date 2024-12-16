from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_notification_email(user_email, event_id):
    try:
        # Validate event_id is an integer
        if not isinstance(event_id, int):
            try:
                event_id = int(event_id)
            except (TypeError, ValueError):
                logger.error(f'Invalid event_id: {event_id}. Expected an integer.')
                raise ValueError(f'Invalid event_id: {event_id}. Expected an integer.')

        # Import Event model here to avoid AppRegistryNotReady error
        from events.models import Event
        
        # Get the event details
        event = Event.objects.get(id=event_id)
        
        subject = f'Join Request for Event: {event.title}'
        message = (
            f"Hello,\n\n"
            f"A join request has been received for the event: {event.title}\n\n"
            f"Request Details:\n"
            f"- Event: {event.title}\n"
            f"- From: {user_email}\n"
            f"- Date: {event.date}\n\n"
            f"Best regards,\n"
            f"Movie2gether Team"
        )
        
        email_from = settings.DEFAULT_FROM_EMAIL
        # Send to event host
        recipient_list = [event.host.email]
        
        logger.info(f'Sending email notification for event {event_id} to {event.host.email}')
        
        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=email_from,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f'Email sent successfully to {event.host.email}')
        return True
        
    except Event.DoesNotExist:
        logger.error(f'Event with id {event_id} not found')
        raise
    except Exception as e:
        logger.error(f'Error sending notification email: {str(e)}')
        raise