"urls for map app"

from django.urls import path
from . import views
urlpatterns = [
    path ('', views.index, name="index"),
    path( "tile/<int:zoom>/<int:x>/<int:y>", views.tile
         , name="map_png")
    #path('radar', views.radar_picture,name="radarpicture"),
    # path('create_radar', views.create_radar),
    # path('gen_all_png', views.gen_png)
]
