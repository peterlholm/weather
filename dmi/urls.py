"urls for dmi app"
from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="dmi_index"),
    path('radardata', views.radar_data, name="radardata"),
    path("process_h5", views.process_h5, name="process_h5"),
    path("clean_png", views.clean_png, name="clean_png"),
    path("show_png", views.show_png, name="show_png"),
    path("copy_last", views.copy_last_png, name="copy_last"),

    path("test", views.test),
    # path('radar', views.radar,name="radarpicture"),
    # path('convert', views.convert),
    # path('readh5', views.read_h5),
    # path('create_radar', views.create_radar),
    # path('gen_all_png', views.gen_png)
]
