from rest_framework import serializers
from .models import Event, Invitation
from movies.serializers import MovieSerializer
import logging

logger = logging.getLogger(__name__)

class EventSerializer(serializers.ModelSerializer):
    movie_details = MovieSerializer(source='movie', read_only=True)
    host_email = serializers.EmailField(source='host.email', read_only=True)
    poster_url = serializers.SerializerMethodField()
    is_host = serializers.SerializerMethodField()
    
    def get_poster_url(self, obj):
        if obj.movie and obj.movie.poster_url:
            return obj.movie.poster_url
        return "https://via.placeholder.com/300x450?text=No+Poster+Available"
    
    def get_is_host(self, obj):
        request = self.context.get('request')
        logger.info(f"get_is_host - Request: {request}")
        logger.info(f"get_is_host - User authenticated: {request.user.is_authenticated if request and hasattr(request, 'user') else False}")
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            is_host = obj.host == request.user
            logger.info(f"get_is_host - Event host: {obj.host.email}, User: {request.user.email}, Is host: {is_host}")
            return is_host
        return False
    
    class Meta:
        model = Event
        fields = ['id', 'movie', 'movie_details', 'title', 'description', 'date', 
                 'location', 'host', 'host_email', 'created_at', 'updated_at',
                 'poster_url', 'is_host']
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
