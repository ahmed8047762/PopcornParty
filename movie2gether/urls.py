"""
URL configuration for movie2gether project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from events.views import index
from django.views.generic import TemplateView

urlpatterns = [
    path('', index, name='index'),  # This will render the main HTML file for React
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/movies/', include('movies.urls')),  # Include movies app URLs
    path('api/events/', include('events.urls')),  # New events app URLs
    path('api/notifications/', include('notifications.urls')),  # New notifications app URLs
    path('api-auth/', include('rest_framework.urls')),  # This adds the login/logout views
    # Catch-all route for React Router
    path('<path:resource>', TemplateView.as_view(template_name='index.html')),  # Serve index.html for all unmatched routes
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
