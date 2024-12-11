# movies/serializers.py

from rest_framework import serializers
from .models import Movie

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class OMDbSearchSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)  # Changed from query to title

# Deprecated: MovieEventSerializer has been moved to the events app
# class MovieEventSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MovieEvent
#         fields = '__all__'