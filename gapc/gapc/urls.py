"""
URL configuration for gapc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# gapc/urls.py
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views  # Import views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Catalog.as_view(), name='home'),  # Route the home page to the home view
    path('catalog/', views.Catalog.as_view(), name='catalog'),  # Route the catalog page to the Catalog view
    path('catalog/<str:target_name>/', views.AsteroidDetail.as_view(), name='asteroid_detail'),  # Route the asteroid detail page using target_name
    
    path('export_votable/<int:obs_id>/', views.export_votable, name='export_votable'),  # Route the export_votable page using obs_id
    path('download/fits/<str:filename>/', views.download_fits, name='download_fits'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)