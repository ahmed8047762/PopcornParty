from rest_framework import generics, permissions, status, exceptions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model
from .models import Event, Invitation
from .serializers import EventSerializer, InvitationSerializer, RSVPSerializer

User = get_user_model()

def index(request):
    return render(request, 'index.html')  # This will render the main HTML file for React

class EventViewSet(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Show events where user is host or invited
        # return Event.objects.filter(
        #     models.Q(host=self.request.user) |
        #     models.Q(invitations__invitee=self.request.user)
        # ).distinct()
        return Event.objects.all()

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only view events they're hosting or invited to
        # return Event.objects.filter(
        #     models.Q(host=self.request.user) |
        #     models.Q(invitations__invitee=self.request.user)
        # )
        return Event.objects.all()

    def perform_update(self, serializer):
        event = self.get_object()
        if event.host != self.request.user:
            raise exceptions.PermissionDenied("Only the host can update this event.")
        serializer.save()

class InvitationCreateView(generics.CreateAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        event = get_object_or_404(Event, pk=self.kwargs['event_pk'])
        if event.host != self.request.user:
            raise exceptions.PermissionDenied("Only the host can send invitations")
        
        invitee_email = serializer.validated_data.pop('invitee_email')
        invitee = User.objects.get(email=invitee_email)
        
        # Check if the host is trying to invite themselves
        if invitee == self.request.user:
            raise serializers.ValidationError("You cannot invite yourself.")
        
        # Check if invitation already exists
        if Invitation.objects.filter(event=event, invitee=invitee).exists():
            raise serializers.ValidationError("Invitation already exists for this user")
        
        serializer.save(event=event, invitee=invitee)

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
