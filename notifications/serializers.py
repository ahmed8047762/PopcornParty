# notifications/serializers.py
from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'sender', 'event', 'notification_type', 'message', 'created_at', 'is_read']

class JoinRequestSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=True)