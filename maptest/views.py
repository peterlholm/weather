"Test map views"
from pathlib import Path
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings



def index(request):
    "index side"
    return HttpResponse("ok")


def start(request):
    "Start side"
    return render(request, 'dmi/index.html')

def leaflet(request):
    "leaflet test"
    filename = "/data/radar/dk.com.202307170950.500_max.mycol.png"
    filename = "/data/radar/last.png"
    filename = last_file()
    print(filename)
    context = {'filename': filename}
    return render (request, "leaflet.html", context=context)

def error(request):
    "error from map"
    print("GET", request.GET)
    print("POST", request.POST)
    print("BODY", request.body)
    return HttpResponse("Error")

def last_file():
    files = sorted(Path(settings.RADAR_DIR).glob("*.mycol.png"), reverse=True)
    return "/data/radar/" + files[0].name