"urls for dmi app"
from django.urls import path
from . import views
urlpatterns = [
    path("", views.leaflet, name="maptest_index"),
    path("leaflet", views.leaflet),
    path("error", views.error)
]
