# movies/urls.py

from django.urls import path
from .views import MovieSearchView, OMDbSearchView

urlpatterns = [
    path('search/', MovieSearchView.as_view(), name='movie-search'),
    path('omdb/', OMDbSearchView.as_view(), name='omdb-search'),
    # Deprecated: Event URLs have been moved to the events app
    # path('events/', MovieEventListCreateView.as_view(), name='event-list'),
    # path('events/<int:pk>/', MovieEventDetailView.as_view(), name='event-detail'),
]