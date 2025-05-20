"""
URL configuration for owlpha_university project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf.urls import handler404, handler403, handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('blog.urls')),
    path('', include('channels.urls')),
    path('', include('chat.urls')),
    path('', include('conference.urls')),
    path('', include('courses.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
]

#This is a flag for serving errors pages
#handler404 = 'accounts.views.error_404'
#handler403 = 'accounts.views.error_403'
#handler500 = 'accounts.views.error_500'

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
