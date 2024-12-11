# movies/urls.py

from django.urls import path
from .views import MovieSearchView, OMDbSearchView, MovieEventListCreateView, MovieEventDetailView

urlpatterns = [
    path('search/', MovieSearchView.as_view(), name='movie_search'),
    path('omdb/', OMDbSearchView.as_view(), name='omdb_search'),
    path('events/', MovieEventListCreateView.as_view(), name='movieevent-list-create'),
    path('events/<int:pk>/', MovieEventDetailView.as_view(), name='movieevent-detail'),
]