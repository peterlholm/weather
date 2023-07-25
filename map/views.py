"map pages"
from pathlib import Path
from math import radians, asinh, tan, pi
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.conf import settings

_DEBUG = True
DK = [[57.71525594703098, 7.855249818280667], [54.458507015448085, 15.074420107864261]]


def find_tile(coord, zoom):
    print(coord)
    lat_rad = radians(coord[0])
    n = 2 ** zoom
    xtile =  int((coord[1] + 180.0) / 360.0 * n)
    ytile = int((1.0 - asinh(tan(lat_rad)) / pi) / 2.0 * n)
    return xtile,ytile

def index(request):
    "index for map page"
    print(find_tile(DK[0],0))
    print(find_tile(DK[0],8))
    return HttpResponse(str(DK))


def tile(request, zoom, x, y):
    "get map tile"
    mapdir = settings.MAP_DIR
    file = mapdir / str(zoom) / str(x) / (str(y)+".png")
    print(file)
    if not file.exists():
        print("Generating file:", zoom, x, y)
        file = mapdir / "0/0/0.png"
        #return HttpResponse("NOT OK")
    
    img = open(file, 'rb')
    response = FileResponse(img)
    return response
    print("Map", zoom, x, y)
    return HttpResponse("OK")
