# notifications/serializers.py
from rest_framework import serializers

class JoinRequestSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=True)