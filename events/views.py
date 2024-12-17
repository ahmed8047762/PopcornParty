from rest_framework import generics, permissions, status, exceptions, serializers, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from django.db.models import Q
from .models import Event, Invitation
from .serializers import EventSerializer, InvitationSerializer, RSVPSerializer
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
    authentication_classes = []  # No authentication required

    def get_queryset(self):
        # Return all future events, ordered by creation date
        return Event.objects.filter(
            date__gte=timezone.now()
        ).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Add request to context even for unauthenticated users
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        # Log authentication status for debugging
        logger.info(f"User authenticated: {request.user.is_authenticated if request.user else False}")
        if request.user.is_authenticated:
            logger.info(f"User email: {request.user.email}")
        response = super().list(request, *args, **kwargs)
        return response

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
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only view events they're hosting or invited to
        return Event.objects.filter(
            models.Q(host=self.request.user) |
            models.Q(invitations__invitee=self.request.user)
        ).distinct()  # Add distinct to prevent duplicates

    def perform_update(self, serializer):
        event = self.get_object()
        if event.host != self.request.user:
            raise exceptions.PermissionDenied("Only the host can update this event.")
        serializer.save()

class InvitationCreateView(generics.CreateAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_id')
        logger.info(f"Creating invitation for event {event_id}")
        logger.info(f"Request data: {request.data}")
        logger.info(f"Request user: {request.user.email}")
        
        try:
            # Get the event or return 404
            event = get_object_or_404(Event, pk=event_id)
            logger.info(f"Found event: {event.title}")
            
            # Check if user is the host
            if event.host != request.user:
                logger.warning(f"Permission denied: {request.user.email} is not the host of event {event.id}")
                raise exceptions.PermissionDenied("Only the host can send invitations")
            
            # Validate invitee email
            invitee_email = request.data.get('invitee_email')
            if not invitee_email:
                logger.warning("No invitee email provided")
                raise serializers.ValidationError({
                    "invitee_email": "Please provide an email address for the invitee."
                })

            logger.info(f"Checking for existing invitation for {invitee_email}")
            # Check if invitation already exists
            existing_invitation = Invitation.objects.filter(
                event=event,
                invitee_email=invitee_email,
                status='pending'
            ).first()
            
            if existing_invitation:
                logger.warning(f"Found existing pending invitation for {invitee_email}")
                raise serializers.ValidationError({
                    "invitee_email": "A pending invitation already exists for this email."
                })

            # Try to find a user with this email
            invitee = User.objects.filter(email=invitee_email).first()
            logger.info(f"Found existing user for email: {invitee is not None}")
            
            # Create the invitation
            invitation = Invitation.objects.create(
                event=event,
                invitee=invitee,  # This might be None if user doesn't exist
                invitee_email=invitee_email,
                status='pending'
            )
            logger.info(f"Created invitation {invitation.id}")

            # Send email notification (async)
            send_invitation_email.delay(invitation.id)
            logger.info(f"Queued invitation email for {invitation.id}")

            # Return the serialized invitation
            serializer = self.get_serializer(invitation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error creating invitation: {str(e)}")
            raise serializers.ValidationError({
                "error": f"Failed to create invitation: {str(e)}"
            })

class InvitationListView(generics.ListAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return invitations where the user's email matches invitee_email
        return Invitation.objects.filter(invitee_email=self.request.user.email)

class RSVPView(generics.UpdateAPIView):
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        # Filter by invitee_email
        return Invitation.objects.filter(invitee_email=self.request.user.email)

    def perform_update(self, serializer):
        invitation = self.get_object()
        logger.info(f"Processing RSVP for invitation {invitation.id}")
        logger.info(f"Current status: {invitation.status}")
        logger.info(f"New status: {serializer.validated_data.get('status')}")
        
        # Check if the status is provided in the validated data
        if 'status' not in serializer.validated_data:
            raise serializers.ValidationError({"status": "Status field is required"})
        
        new_status = serializer.validated_data['status']
        if new_status not in ['accepted', 'declined']:
            raise serializers.ValidationError({"status": "Status must be either 'accepted' or 'declined'"})
        
        # Update the invitation
        invitation.status = new_status
        invitation.responded_at = timezone.now()
        
        # If accepting, ensure the user is linked
        if new_status == 'accepted' and not invitation.invitee:
            invitation.invitee = self.request.user
        
        invitation.save()
        logger.info(f"Updated invitation {invitation.id} status to {new_status}")
        
        # Return success response
        return Response({
            "message": f"Successfully {new_status} the invitation",
            "invitation_id": invitation.id,
            "status": new_status
        }, status=status.HTTP_200_OK)
