from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'events'

# Create routers for ViewSets
router = DefaultRouter()
router.register(r'invitations', views.InvitationViewSet, basename='invitation')
router.register(r'', views.EventViewSet, basename='event')

urlpatterns = [
    # Public endpoints
    path('public/', views.PublicEventListView.as_view(), name='public-event-list'),
    
    # ViewSet URLs - include both event and invitation URLs
    path('', include(router.urls)),
    
    # Event-specific invitation creation
    path('<int:event_id>/invite/', views.InvitationCreateView.as_view(), name='create-invitation'),
]