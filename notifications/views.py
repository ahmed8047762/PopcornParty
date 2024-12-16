# notifications/views.py
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from events.models import Event, Invitation
from .tasks import send_notification_email
from .serializers import JoinRequestSerializer
import logging

logger = logging.getLogger(__name__)

class JoinRequestView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JoinRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        event_id = serializer.validated_data['event_id']
        user_email = request.user.email
        
        try:
            event = Event.objects.get(id=event_id)
            
            # Check if the user is already a participant
            if Invitation.objects.filter(
                event=event, 
                invitee=request.user, 
                status='accepted'
            ).exists():
                return Response(
                    {"message": "You are already a participant of this event."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create a pending invitation
            Invitation.objects.get_or_create(
                event=event,
                invitee=request.user,
                defaults={'status': 'pending'}
            )

            # Send email notification
            try:
                send_notification_email.delay(user_email, event_id)
                return Response(
                    {"message": "Join request sent successfully. Please wait for approval."}, 
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                logger.error(f"Failed to send notification email: {str(e)}")
                return Response(
                    {"message": "Join request recorded but notification failed to send."}, 
                    status=status.HTTP_200_OK
                )

        except Event.DoesNotExist:
            return Response(
                {"error": "Event does not exist."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error processing join request: {str(e)}")
            return Response(
                {"error": "Failed to process join request."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )