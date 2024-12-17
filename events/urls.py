from django.urls import path
from . import views
from .views import InvitationListView, PublicEventListView

app_name = 'events'

urlpatterns = [
    # Public endpoints
    path('public/', PublicEventListView.as_view(), name='public-event-list'),
    
    # Authenticated endpoints
    path('', views.EventViewSet.as_view(), name='event-list'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('<int:event_id>/invite/', views.InvitationCreateView.as_view(), name='create-invitation'),
    path('invitations/', InvitationListView.as_view(), name='invitation-list'),
    path('invitations/<int:pk>/rsvp/', views.RSVPView.as_view(), name='rsvp'),
]