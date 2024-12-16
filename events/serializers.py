from rest_framework import serializers
from .models import Event, Invitation
from movies.serializers import MovieSerializer

class EventSerializer(serializers.ModelSerializer):
    movie_details = MovieSerializer(source='movie', read_only=True)
    host_email = serializers.EmailField(source='host.email', read_only=True)
    
    class Meta:
        model = Event
        fields = ['id', 'movie', 'movie_details', 'title', 'description', 'date', 
                 'location', 'host', 'host_email', 'created_at', 'updated_at']
        read_only_fields = ('host', 'host_email', 'created_at', 'updated_at')

class InvitationSerializer(serializers.ModelSerializer):
    event_details = EventSerializer(source='event', read_only=True)
    invitee_email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = Invitation
        fields = ['id', 'event', 'event_details', 'invitee', 'invitee_email',
                 'status', 'invited_at', 'responded_at']
        read_only_fields = ('invited_at', 'responded_at', 'invitee', 'event')

class RSVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['status']
