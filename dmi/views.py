"dmi testviews"
from pathlib import Path
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest

# Create your views here.
from django.conf import settings
#from dmi.radar import *
from . dmi_radar import get_radar_data, convert_missing_h5
#from vejr.utils import get_img_tags

def index(request):
    "Start side"
    return render(request, 'dmi/index.html')

def test(request):
    "test side"
    print("Testing", request)
    return redirect('dmi/index.html')


def radar_data(request):
    "radar data test"
    if request.method != "GET":
        return HttpResponseBadRequest()
    get_radar_data()
    return redirect('dmi_index')

def process_h5(request):
    "Process h5 file and generate png files"
    if request.method != "GET":
        return HttpResponseBadRequest()
    convert_missing_h5(settings.RADAR_DIR)
    return redirect('dmi_index')

def clean_png(request):
    "delete all png files"
    if request.method != "GET":
        return HttpResponseBadRequest()
    for fil in settings.RADAR_DIR.glob("*.png"):
        print("deleting:", fil)
        fil.unlink()
    return redirect('dmi_index')

def show_png(request):
    "show all pictures"
    abspath = settings.RADAR_DIR
    filelist = sorted(abspath.glob('*.h5'))
    pictures = []
    for pic in filelist:
        name = pic.stem
        plist = []
        for ext in ['.png', '.mycol.png']:
            plist.append('/data/radar/'+name+ext)
        pictures.append(plist)
    context = { 'pictures': pictures}
    return render(request, 'dmi/show_png.html', context=context)

def copy_last_png(request):
    "copy last png file to last.png"
    data_path =  settings.RADAR_DIR
    filelist = sorted(data_path.glob('*.mycol.png'),reverse=True)
    print(filelist)
    Path(settings.RADAR_DIR / "last.png").unlink(missing_ok=True)
    (settings.RADAR_DIR / "last.png").symlink_to(filelist[0])
    return redirect('dmi_index')



# def create_radar(request):
#     "create radar files"
#     create_radar_pic()
#     return redirect('radarpicture')
#     #return render(request, 'test.html')

# def convert(request):
#     "convert function"
#     filename = settings.DATA_DIR / 'radar' / "dk.com.202211051340.500_max.h5"
#     convert_h5_to_png(filename)
#     return render(request, 'test.html')


# def read_h5(request):
#     "get information from h5 file"
#     filename = settings.DATA_DIR / 'radar' / "dk.com.202211051340.500_max.h5"
#     filename = list((settings.DATA_DIR / 'radar').glob('*.h5'))[0]
#     read_h5_info(filename)
#     return render(request, 'test.html')

# def gen_png(request):
#     "test function"
#     folder = settings.DATA_DIR / 'radar'
#     gen_all_png(folder)
#     return redirect('index')
