"application pages"
from pathlib import Path
from django.shortcuts import render
from django.conf import settings
from dmi.dmi_radar import get_radar_data, convert_missing_h5
#from web.utils import get_img_tags

_DEBUG = True


def last_file():
    files = sorted(Path(settings.RADAR_DIR).glob("*.mycol.png"), reverse=True)
    return "/data/radar/" + files[0].name

def updata_radar():
    "update radar with latest picture"
    if _DEBUG:
        print("getting radar data")
    get_radar_data()
    if _DEBUG:
        print("converting data")
    convert_missing_h5(settings.RADAR_DIR)
    if _DEBUG:
        print("update finish")


def index(request):
    "Start side"
    return render(request, 'web/index.html')

def radar_picture(request):
    "radar picture"
    #file= settings.MEDIA_ROOT / "radar/radar1.png"
    #tags = get_img_tags(file)
    #print("tags", tags)
    context={'title':'Tittel',
             'radar_img': '/data/radar/dk.com.202307120910.500_max.trans.png',
             'background_img': '/static/img/dk.png' }

    return render(request, 'web/radar.html', context=context)

def show_radar(request):
    "show radar picture for current place"
    updata_radar()
    return render(request, 'web/index.html')


def map(request):
    "leaflet map"
    filename = "/data/radar/dk.com.202307170950.500_max.mycol.png"
    filename = "/data/radar/last.png"
    filename = last_file()
    tile_url = "https://tile2.openstreetmap.org/{z}/{x}/{y}.png"
    tile_url = "http://localhost:8000/map/tile/{z}/{x}/{y}"
    context = {'tile_url': tile_url, 'filename': filename}
    return render (request, "web/map.html", context=context)
