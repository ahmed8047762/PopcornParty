# movies/views.py

from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import requests
from django.conf import settings
from .models import Movie
from .serializers import MovieSerializer, OMDbSearchSerializer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MovieSearchView(generics.ListAPIView):
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        if query:
            return Movie.objects.filter(title__icontains=query).order_by('-id')
        return Movie.objects.all().order_by('-id')[:20]  # Return last 20 movies by default

class OMDbSearchView(generics.GenericAPIView):
    serializer_class = OMDbSearchSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        title = serializer.validated_data['title']
        
        cache_key = f'omdb_{title}'
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return Response(cached_result)
            
        try:
            api_key = settings.OMDB_API_KEY
            # Get exact match by using t= instead of s=
            response = requests.get(
                f'http://www.omdbapi.com/?apikey={api_key}&t={title}'
            )
            data = response.json()
            
            if data.get('Response') == 'True':
                try:
                    # Save or update movie in database
                    movie, created = Movie.objects.update_or_create(
                        imdb_id=data['imdbID'],
                        defaults={
                            'title': data['Title'],
                            'description': data.get('Plot', ''),
                            'release_date': datetime.strptime(data.get('Released', '01 Jan 1900'), '%d %b %Y').date(),
                            'poster_url': data.get('Poster', ''),
                        }
                    )
                    
                    result = {
                        'id': movie.id,
                        'title': movie.title,
                        'description': movie.description,
                        'release_date': movie.release_date,
                        'poster': movie.poster_url,
                        'imdb_id': movie.imdb_id,
                    }
                    
                    cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour
                    return Response(result)
                    
                except Exception as e:
                    logger.error(f"Error saving movie {data['Title']}: {str(e)}")
                    return Response(
                        {'message': 'Error saving movie'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
            return Response({'message': 'No movie found'}, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            logger.error(f"Error searching OMDB: {str(e)}")
            return Response(
                {'message': 'Error searching movie'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )