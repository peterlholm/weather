"""
URL configuration for weather project.

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
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from web.views import index

urlpatterns = [
    path('', index, name="home"),
    path('dmi/', include('dmi.urls')),
    path('web/', include('web.urls')),
    path('map/', include('map.urls')),
    path('maptest/', include('maptest.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^data/(?P<path>.*)$', serve,{'document_root': settings.DATA_DIR}),
]
