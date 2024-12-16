from rest_framework import generics, permissions, status, exceptions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from .models import Event, Invitation
from .serializers import EventSerializer, InvitationSerializer, RSVPSerializer
from rest_framework import serializers
from notifications.tasks import send_invitation_email
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

def index(request):
    return render(request, 'index.html')  # This will render the main HTML file for React

class PublicEventListView(generics.ListAPIView):
    """View for listing all events without authentication"""
    serializer_class = EventSerializer
    permission_classes = []  # No authentication required

    def get_queryset(self):
        # Return all future events, ordered by creation date
        return Event.objects.filter(
            date__gte=timezone.now()
        ).order_by('-created_at')

class EventViewSet(generics.ListCreateAPIView):
    """View for creating events and listing user-specific events"""
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Show events where user is host or invited, ordered by most recent first
        return Event.objects.filter(
            models.Q(host=self.request.user) |
            models.Q(invitations__invitee=self.request.user)
        ).distinct().order_by('-created_at')  # Most recent first

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only view events they're hosting or invited to
        return Event.objects.filter(
            models.Q(host=self.request.user) |
            models.Q(invitations__invitee=self.request.user)
        )

    def perform_update(self, serializer):
        event = self.get_object()
        if event.host != self.request.user:
            raise exceptions.PermissionDenied("Only the host can update this event.")
        serializer.save()

class InvitationCreateView(generics.CreateAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('event_pk')
        print(f"Creating invitation for event {event_pk}")
        print(f"Request data: {request.data}")
        
        # Get the event or return 404
        event = get_object_or_404(Event, pk=event_pk)
        
        # Check if user is the host
        if event.host != request.user:
            raise exceptions.PermissionDenied("Only the host can send invitations")
        
        # Validate invitee email
        invitee_email = request.data.get('invitee_email')
        if not invitee_email:
            raise serializers.ValidationError({
                "invitee_email": "Please provide an email address for the invitee."
            })
        
        try:
            invitee = User.objects.get(email=invitee_email)
            print(f"Found invitee: {invitee.email}")
        except User.DoesNotExist:
            print(f"No user found with email: {invitee_email}")
            raise serializers.ValidationError({
                "invitee_email": f"No user found with email: {invitee_email}. They need to register first."
            })
        
        # Check if the host is trying to invite themselves
        if invitee == request.user:
            print("Host tried to invite themselves")
            raise serializers.ValidationError({
                "invitee_email": "You cannot invite yourself to your own event."
            })
        
        # Check if invitation already exists
        if Invitation.objects.filter(event=event, invitee=invitee).exists():
            print(f"Invitation already exists for {invitee.email}")
            raise serializers.ValidationError({
                "invitee_email": "This user has already been invited to this event."
            })
        
        try:
            # Create the invitation
            invitation = Invitation.objects.create(
                event=event,
                invitee=invitee,
                status='pending'
            )
            print(f"Successfully created invitation for {invitee.email}")
            
            # Send invitation email asynchronously
            send_invitation_email.delay(invitee_email, event.id)
            print(f"Queued invitation email to {invitee_email}")
            
            # Serialize and return the response
            serializer = self.get_serializer(invitation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error creating invitation: {str(e)}")
            raise serializers.ValidationError({
                "error": f"Failed to create invitation: {str(e)}"
            })

class InvitationListView(generics.ListAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return invitations where the user is the invitee
        return Invitation.objects.filter(invitee=self.request.user)

class RSVPView(generics.UpdateAPIView):
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Invitation.objects.filter(invitee=self.request.user)

    def perform_update(self, serializer):
        invitation = self.get_object()
        # Check if the status is provided in the validated data
        if 'status' in serializer.validated_data:
            invitation.status = serializer.validated_data['status']
        else:
            raise serializers.ValidationError("Status must be provided.")
        invitation.responded_at = timezone.now()
        invitation.save()  # Save the updated invitation
        return Response(serializer.data, status=status.HTTP_200_OK)
