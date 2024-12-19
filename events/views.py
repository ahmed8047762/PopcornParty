from rest_framework import generics, permissions, status, exceptions, serializers, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
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

class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for managing events"""
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Event.objects.all()  # Added queryset

    def get_queryset(self):
        """
        Get events where the user is either the host or an invitee
        """
        user = self.request.user
        return Event.objects.filter(
            Q(host=user) |  # Events hosted by the user
            Q(invitations__invitee_email=user.email)  # Events where user is invited
        ).distinct().order_by('-created_at')  # Most recent first

    def perform_create(self, serializer):
        with transaction.atomic():
            event = serializer.save(host=self.request.user)
            # Check if invitee email is provided in the request
            invitee_email = self.request.data.get('invitee_email')
            if invitee_email:
                # Check if invitation already exists
                existing_invitation = Invitation.objects.select_for_update().filter(
                    event=event,
                    invitee_email=invitee_email
                ).first()

                if not existing_invitation:
                    # Create invitation
                    invitation = Invitation.objects.create(
                        event=event,
                        invitee_email=invitee_email,
                        status='pending'
                    )
                    # Send invitation email
                    transaction.on_commit(lambda: send_invitation_email.delay(invitation.id))

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

class InvitationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing invitations"""
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Invitation.objects.all()

    def get_queryset(self):
        """Get invitations sent to the user (excluding self-invitations)"""
        user = self.request.user
        # Only return invitations where:
        # 1. The user is the invitee (invitee_email matches user's email)
        # 2. AND the user is NOT the host of the event
        return Invitation.objects.filter(
            invitee_email=user.email
        ).exclude(
            event__host=user
        ).select_related('event').order_by('-created_at')

    @action(detail=True, methods=['put'])
    def rsvp(self, request, pk=None):
        """Handle RSVP responses to invitations"""
        invitation = self.get_object()
        user = request.user
        
        # Verify the user is the invitee
        if invitation.invitee_email != user.email:
            return Response(
                {"error": "You can only respond to your own invitations"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Verify the user is not the host
        if invitation.event.host == user:
            return Response(
                {"error": "You cannot respond to your own event's invitations"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get and validate the status
        new_status = request.data.get('status')
        if new_status not in ['accepted', 'declined']:
            return Response(
                {"error": "Status must be 'accepted' or 'declined'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the invitation status
        invitation.status = new_status
        invitation.responded_at = timezone.now()
        invitation.save()
        
        return Response({
            "message": f"Successfully {new_status} the invitation",
            "invitation": InvitationSerializer(invitation).data
        })

class InvitationCreateView(generics.CreateAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_id')
        try:
            with transaction.atomic():
                event = Event.objects.get(id=event_id)
                
                # Check if user is the host
                if event.host != request.user:
                    return Response(
                        {"error": "Only the event host can send invitations"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Get email from request data
                invitee_email = request.data.get('email')
                if not invitee_email:
                    return Response(
                        {"error": "Email is required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Check if invitation already exists, using select_for_update to prevent race conditions
                existing_invitation = Invitation.objects.select_for_update().filter(
                    event=event,
                    invitee_email=invitee_email
                ).first()

                if existing_invitation:
                    if existing_invitation.status == 'pending':
                        return Response(
                            {"error": "A pending invitation already exists for this email"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    else:
                        return Response(
                            {"error": f"This user has already {existing_invitation.status} this invitation"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Create invitation
                invitation = Invitation.objects.create(
                    event=event,
                    invitee_email=invitee_email,
                    status='pending'
                )

                # Send invitation email
                transaction.on_commit(lambda: send_invitation_email.delay(invitation.id))

                return Response({
                    "message": "Invitation sent successfully",
                    "invitation_id": invitation.id
                }, status=status.HTTP_201_CREATED)

        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to create invitation: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class InvitationListView(generics.ListAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return invitations where the user's email matches invitee_email
        return Invitation.objects.filter(invitee_email=self.request.user.email)

class RSVPView(generics.UpdateAPIView):
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter by invitee_email instead of invitee
        return Invitation.objects.filter(invitee_email=self.request.user.email)

    def perform_update(self, serializer):
        invitation = self.get_object()
        
        # Check if the status is provided in the validated data
        if 'status' not in serializer.validated_data:
            raise serializers.ValidationError({"status": "Status field is required"})
        
        new_status = serializer.validated_data['status']
        if new_status not in ['accepted', 'declined']:
            raise serializers.ValidationError({"status": "Status must be either 'accepted' or 'declined'"})
        
        # Update the invitation
        invitation.status = new_status
        invitation.responded_at = timezone.now()
        
        # Always link the responding user to the invitation
        invitation.invitee = self.request.user
        
        invitation.save()
        
        # Return success response
        return Response({
            "message": f"Successfully {new_status} the invitation",
            "invitation_id": invitation.id,
            "status": new_status
        }, status=status.HTTP_200_OK)
