from rest_framework import serializers

class JoinRequestSerializer(serializers.Serializer):
    user_email = serializers.EmailField(required=True)
    event_id = serializers.IntegerField(required=True)