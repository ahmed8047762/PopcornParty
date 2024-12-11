# movies/views.py

import requests
from django.conf import settings
from django.core.cache import cache
from datetime import datetime
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Movie, MovieEvent
from .serializers import MovieEventSerializer, MovieSerializer, OMDbSearchSerializer

class MovieSearchView(generics.ListAPIView):
    serializer_class = MovieSerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', None)
        if query:
            return Movie.objects.filter(title__icontains=query)
        return Movie.objects.all()

class OMDbSearchView(generics.GenericAPIView):
    serializer_class = OMDbSearchSerializer
    
    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        title = serializer.validated_data['title']
        
        cache_key = f'omdb_{title}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        url = f"http://www.omdbapi.com/?t={title}&apikey={settings.OMDB_API_KEY}"
        response = requests.get(url)
        movie_data = response.json()

        # Check if the movie exists in the database
        if movie_data.get('Response') == 'True':
            imdb_id = movie_data['imdbID']
            # Convert the release date to YYYY-MM-DD format
            release_date_str = movie_data.get('Released')
            if release_date_str:
                release_date = datetime.strptime(release_date_str, '%d %b %Y').date()
            else:
                release_date = None

            movie, created = Movie.objects.update_or_create(
                imdb_id=imdb_id,
                defaults={
                    'title': movie_data.get('Title'),
                    'description': movie_data.get('Plot'),
                    'release_date': release_date,
                    'poster_url': movie_data.get('Poster'),
                }
            )

            # Optionally, include the movie ID in the response
            movie_data['id'] = movie.id

        cache.set(cache_key, movie_data, timeout=60*15)  # Cache for 15 minutes
        return Response(movie_data)
    
class MovieEventListCreateView(generics.ListCreateAPIView):
    queryset = MovieEvent.objects.all()
    serializer_class = MovieEventSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can create events

class MovieEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MovieEvent.objects.all()
    serializer_class = MovieEventSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can modify events