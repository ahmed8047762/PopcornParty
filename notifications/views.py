from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from events.models import Event, Invitation
from .models import Notification
from .tasks import send_join_request_email
from .serializers import NotificationSerializer, JoinRequestSerializer
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class JoinRequestView(generics.CreateAPIView):
    serializer_class = JoinRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return Response(
                {"error": "Invalid request data"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        event_id = serializer.validated_data['event_id']
        user = request.user

        try:
            event = Event.objects.get(pk=event_id)
            
            # Don't allow join requests from the host
            if event.host == user:
                return Response(
                    {"error": "You cannot send a join request for your own event"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if user is already invited
            if Invitation.objects.filter(event=event, invitee=user).exists():
                return Response(
                    {"error": "You have already been invited to this event"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create notification for the host
            notification = Notification.objects.create(
                user=event.host,  # recipient is stored in user field
                sender=user,
                event=event,
                notification_type='join_request',
                message=f"{user.email} wants to join your event"
            )

            logger.info(f"Created notification {notification.id} for join request to event {event_id}")

            # Send email to host
            send_join_request_email.delay(
                user.email,
                event.id
            )

            logger.info(f"Queued join request email for event {event_id}")

            return Response({
                "message": "Join request sent successfully",
                "notification_id": notification.id
            }, status=status.HTTP_201_CREATED)

        except Event.DoesNotExist:
            logger.error(f"Event {event_id} not found")
            return Response(
                {"error": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error processing join request: {str(e)}")
            return Response(
                {"error": f"Failed to send join request: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )