from django.urls import path
from .views import JoinRequestView

urlpatterns = [
    path('join-request/', JoinRequestView.as_view(), name='join-request'),
]