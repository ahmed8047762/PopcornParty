from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_invitation_email(invitee_email, event_id):
    """Send an invitation email to a user for an event"""
    try:
        # Import Event model here to avoid AppRegistryNotReady error
        from events.models import Event
        
        # Get the event details
        event = Event.objects.get(id=event_id)
        
        subject = f'Invitation to Movie Event: {event.title}'
        message = (
            f"Hello!\n\n"
            f"You have been invited to join a movie event!\n\n"
            f"Event Details:\n"
            f"- Movie: {event.title}\n"
            f"- Date: {event.date}\n"
            f"- Location: {event.location}\n"
            f"- Host: {event.host.email}\n\n"
            f"Description: {event.description}\n\n"
            f"Please log in to Movie2gether to accept or decline this invitation.\n\n"
            f"Best regards,\n"
            f"Movie2gether Team"
        )
        
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [invitee_email]
        
        logger.info(f'Sending invitation email for event {event_id} to {invitee_email}')
        
        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=email_from,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f'Invitation email sent successfully to {invitee_email}')
        return True
        
    except Event.DoesNotExist:
        logger.error(f'Event with id {event_id} not found')
        raise
    except Exception as e:
        logger.error(f'Error sending invitation email: {str(e)}')
        raise

@shared_task
def send_join_request_email(user_email, event_id):
    """Send a notification to the event host about a join request"""
    try:
        # Import Event model here to avoid AppRegistryNotReady error
        from events.models import Event
        
        # Get the event details
        event = Event.objects.get(id=event_id)
        
        subject = f'Join Request for Event: {event.title}'
        message = (
            f"Hello,\n\n"
            f"A join request has been received for your event!\n\n"
            f"Request Details:\n"
            f"- Event: {event.title}\n"
            f"- From: {user_email}\n"
            f"- Date: {event.date}\n"
            f"- Location: {event.location}\n\n"
            f"Please log in to Movie2gether to manage this request.\n\n"
            f"Best regards,\n"
            f"Movie2gether Team"
        )
        
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [event.host.email]  # Send to event host
        
        logger.info(f'Sending join request email for event {event_id} to {event.host.email}')
        
        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=email_from,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f'Join request email sent successfully to {event.host.email}')
        return True
        
    except Event.DoesNotExist:
        logger.error(f'Event with id {event_id} not found')
        raise
    except Exception as e:
        logger.error(f'Error sending join request email: {str(e)}')
        raise