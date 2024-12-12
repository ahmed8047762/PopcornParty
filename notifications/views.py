from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from events.models import Event, Invitation  # Import Invitation model
from .tasks import send_notification_email
from .serializers import JoinRequestSerializer

class JoinRequestView(generics.CreateAPIView):
    serializer_class = JoinRequestSerializer  # Add this line

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_email = serializer.validated_data['user_email']
        event_id = serializer.validated_data['event_id']
        
        # Check if the event id is of a non existant event
        try:
            Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Event does not exist."}, status=status.HTTP_404_NOT_FOUND)
        

        # Check if the user is already a participant of the event
        try:
            event = Event.objects.get(id=event_id)
            if Invitation.objects.filter(event=event, invitee__email=user_email, status='accepted').exists():
                return Response({"message": "You are already a participant of this event."}, status=status.HTTP_400_BAD_REQUEST)

            # Send email notification to the event creator via Celery task
            send_notification_email.delay(event.host.email, f"{user_email} wants to join the event: {event.title}")
            return Response({"message": "Join request sent successfully."}, status=status.HTTP_201_CREATED)
        except Event.DoesNotExist:
            return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)