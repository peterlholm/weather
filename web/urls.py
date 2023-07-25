"urls for web app"
from django.urls import path
from . import views
urlpatterns = [
    path ('', views.index, name="index"),
    path('radar', views.radar_picture,name="radarpicture"),
    path('map', views.map),
    # path('gen_all_png', views.gen_png)
]
