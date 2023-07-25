"Get radar file from dmi"
from datetime import datetime
from time import mktime
from pathlib import Path
from urllib import parse
from wsgiref.handlers import format_date_time
import requests
# from shutil import copy
import h5py
import numpy as np
from PIL import Image #, ImageOps
from PIL.PngImagePlugin import PngInfo
import piexif

from django.conf import settings
from .utils import colorize_as_dmi # , colorize_std convert_img_transparent

_DEBUG = False


RADAR_DIR = settings.DATA_DIR / 'radar'
RADAR_API_KEY="adb8af9d-94a5-4782-9827-c2b2e775dba3"
HTTP_TIMEOUT = 10
LIMIT = "1"    # number of radar pictures
SCAN_TYPE = "&scanType=fullRange"
#SCAN_TYPE = ""
RADAR_URL = "https://dmigw.govcloud.dk/v1/radardata/collections/composite/items?sortorder=datetime,DESC&limit=" + LIMIT + "&api-key=" + RADAR_API_KEY + SCAN_TYPE


def rfc3339_date(date):
    "return rfc datestring"
    datestr = date.astimezone().isoformat('T', 'seconds')
    return datestr


def rfc1123_date(date):
    "generate a rfc1123 date string"
    stamp = mktime(date.timetuple())
    mystr= format_date_time(stamp)
    return mystr


def get_radar_data():
    "get radar data to temp dir"
    Path(RADAR_DIR).mkdir(parents=True, exist_ok=True)

    today = datetime.now()
    url = RADAR_URL + '&datetime=../' + parse.quote_plus(rfc3339_date(today))
    if _DEBUG:
        print("URL: ", url)
    response = requests.get(url, timeout=HTTP_TIMEOUT)
    if response.status_code:
        data = response.json()
        radarfile = open(RADAR_DIR / 'response.json','w', encoding='utf8')
        radarfile.write(response.text)
        radarfile.close()
        if 'error' in data:
            print('Error in request')
            print(data['error'], data['message'])
            return False
        features = data['features']
        number = 1
        for feature in features:
            fileid = feature['id']
            tempfile = RADAR_DIR / fileid
            if not tempfile.is_file():
                downloadurl = feature['asset']['data']['href']
                downloaddata = requests.get(downloadurl, timeout=HTTP_TIMEOUT)
                if _DEBUG:
                    print("Loading:",tempfile)
                with open(tempfile, 'wb') as filed:
                    for chunk in downloaddata.iter_content(chunk_size=128):
                        filed.write(chunk)
            #convert_h5_to_png(tempfile)
            #copy(tempfile.with_suffix('.cut.png'), RADAR_DIR / ('radar'+str(number) + '.png'))
            number += 1
        return True
    else:
        print("H5 request status", response.status_code)
        return False

def gen_pic(arr, filename, datetimeset=None, h5_coords=None, pic_coords=None):
    "create png file from np array"
    # array has 255 values for nordata
    img2 = Image.fromarray(arr, mode='L')
    imga = img2.convert(mode='LA')
    for w in range(imga.width):
        for h in range(imga.height):
            if imga.getpixel((w,h))[0]==255:
                imga.putpixel((w,h),(0,0))
    # generating metadata
    datetaken = datetimeset
    metadata = exif_bytes = None
    if datetimeset:
        metadata = PngInfo()
        metadata.add_text('Title', 'Radardata from '+ datetaken.strftime("%d/%m-%y %H:%M:%S"))
        rfc1123_dat =  rfc1123_date(datetaken)
        metadata.add_text('Creation Time', rfc1123_dat )
        metadata.add_text('CreationTime', datetaken.strftime("%d/%m-%y %H:%M:%S"))
        exif_datetime = datetaken.strftime("%Y:%m:%d %H:%M:%S")
        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: exif_datetime,
            piexif.ExifIFD.DateTimeDigitized: exif_datetime,
        }
        exif_dict = {"Exif": exif_ifd}
        exif_bytes = piexif.dump(exif_dict)
    if _DEBUG:
        img2.save(filename.with_suffix('org.png'), exif=exif_bytes, pnginfo=metadata)
    imga.save(filename.with_suffix('.png'), exif=exif_bytes, pnginfo=metadata)
    return imga, exif_bytes, metadata

def create_img_files(img, filename, exif_bytes=None, metadata=None):
    "create other image files"
    #print(img.mode)
    # img3 = colorize_std(img)
    # img3.save(filename.with_suffix('.color.png'), exif=exif_bytes, pnginfo=metadata)
    img7 = colorize_as_dmi(img)
    img7.save(filename.with_suffix('.mycol.png'), exif=exif_bytes, pnginfo=metadata)
    # img5 = convert_img_transparent(img8)
    # img5.save(filename.with_suffix('.trans.png'), exif=exif_bytes, pnginfo=metadata)

def convert_h5_to_png(filename):
    "Read and convert h5 file to png and add attributes"
    #pylint: disable=unsubscriptable-object, invalid-name,no-member
    f5_data = h5py.File(filename)
    #print(f5_data)
    dset = f5_data['dataset1']
    data = dset['data1']
    data2 = data['data']
    date1 = f5_data['what'].attrs['date']
    time = f5_data['what'].attrs['time']
    radar_datetime = datetime.strptime(date1.decode('utf-8') + time.decode('utf-8'), "%Y%m%d%H%M%S")
    if _DEBUG:
        print("Radar Datetime", radar_datetime)
    where = where =f5_data['where']
    attr = where.attrs
    LL = (attr['LL_lat'][0], attr['LL_lon'][0])
    LR = (attr['LR_lat'][0], attr['LR_lon'][0])
    UL = (attr['UL_lat'][0], attr['UL_lon'][0])
    UR = (attr['UR_lat'][0], attr['UR_lon'][0])
    if _DEBUG:
        print("attributes:", LL, LR, UL, UR)
    img = np.array(data2.astype('uint8'))
    img, exif, meta = gen_pic(img, filename.with_suffix('.png'), datetimeset=radar_datetime, h5_coords=(LL,LR,UL,UR), pic_coords=((8.01,54.58),(12.73,54.58),(8.01,57.7),(12.73,57.7)))
    #print(img.mode)
    create_img_files(img, filename.with_suffix('.png'), exif_bytes=exif, metadata=meta)

def convert_missing_h5(datapath: Path, convert_all=False):
    "traverse folder and generate missing png"
    for fil in sorted(datapath.glob("*.h5")):
        png_file = fil.with_suffix('.png')
        if convert_all or not png_file.exists():
            print("converting:", fil)
            convert_h5_to_png(fil)
            