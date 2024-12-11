# movies/serializers.py

from rest_framework import serializers
from .models import Movie, MovieEvent

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'  # or specify fields explicitly

class MovieEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieEvent
        fields = '__all__'  # or specify fields explicitly
        
class OMDbSearchSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)