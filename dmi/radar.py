"get radar images from dmi"
#import sys
from datetime import datetime
from time import mktime
from pathlib import Path
from wsgiref.handlers import format_date_time
from shutil import copy
from urllib import parse
import requests
import h5py
import numpy as np
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo
import piexif
from django.conf import settings
#from vejr.utils import convert_img_transparent, colorize
#from .coord import radar_pic_cut
#print(sys.path)

RADAR_DIR = settings.DATA_DIR / 'radar'
RADAR_API_KEY="adb8af9d-94a5-4782-9827-c2b2e775dba3"
HTTP_TIMEOUT = 10
LIMIT = "1"    # number of radar pictures
SCAN_TYPE = "&scanType=fullRange"
#SCAN_TYPE = ""
RADAR_URL = "https://dmigw.govcloud.dk/v1/radardata/collections/composite/items?sortorder=datetime,DESC&limit=" + LIMIT + "&api-key=" + RADAR_API_KEY + SCAN_TYPE

_DEBUG = True

# class coords():
dk_nw = (57.7,8.01)
dk_se = (54.58, 12.73)

def rfc3339_date(date):
    "return rfc datestring"
    datestr = date.astimezone().isoformat('T', 'seconds')
    return datestr

def rfc1123_date(date):
    "generate a rfc1123 date string"
    stamp = mktime(date.timetuple())
    mystr= format_date_time(stamp)
    return mystr

def convert_img_transparent(img, bg_color=(0,0,0)):
    "Convert alle pixels with bg_color to transparant from image"
    #image = Image.open(src_file).convert("RGBA")
    array = np.array(img, dtype=np.ubyte)
    mask = (array[:,:,:3] == bg_color).all(axis=2)
    alpha = np.where(mask, 0, 255)
    array[:,:,-1] = alpha
    return Image.fromarray(np.ubyte(array))

def colorize(img):
    "make colors ala DMI"
    nimg = Image.new('RGB',img.size)
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            pic = img.getpixel((x,y))
            if pic < 20:
                nimg.putpixel((x,y), (0,0,0))
            elif pic < 80:
                nimg.putpixel((x,y), (158, 242, 233))   # lys blå
            elif pic < 103:
                nimg.putpixel((x,y), (125, 238, 226))   # lid blå
            elif pic < 105:
                nimg.putpixel((x,y), (22, 225, 204))    # turkis
            elif pic < 110:
                nimg.putpixel((x,y), (109, 191,242))    # grå blå
            elif pic < 120:
                nimg.putpixel((x,y), (61, 171, 238))    # mørk blå
            elif pic < 130:
                nimg.putpixel((x,y), (0, 143, 233))     # blå
            elif pic < 135:
                nimg.putpixel((x,y), (255, 217, 0))     # gul
            elif pic < 140:
                nimg.putpixel((x,y), (255, 178, 0))     # lys orange
            elif pic < 150:
                nimg.putpixel((x,y), (255, 142, 82))    # orange
            elif pic < 160:
                nimg.putpixel((x,y), (255,181,181))     # pink
            elif pic < 170:
                nimg.putpixel((x,y), (255,124,124))     # blegrød
            elif pic < 200:
                nimg.putpixel((x,y), (255, 82, 82))     # rød
            elif pic < 210:
                nimg.putpixel((x,y), (230, 57, 57))     # mørk rød
            elif pic < 220:
                nimg.putpixel((x,y), (204, 31, 31))     # mere mørk rød
            else:
                nimg.putpixel((x,y), (128,0,0))         # meget mørk rød
    return nimg

def save_png(arr, filename, datetimeset=None, h5_coords=None, pic_coords=None ):
    "Save np array as png files"
    img = Image.fromarray(arr)
    metadata = exif_bytes = None
    if datetimeset:
        metadata = PngInfo()
        metadata.add_text('Title', 'Radardata from '+ datetimeset.strftime("%d/%m-%y %H:%M:%S"))
        rfc1123_dat =  rfc1123_date(datetimeset)
        metadata.add_text('Creation Time', rfc1123_dat )
        metadata.add_text('CreationTime', datetimeset.strftime("%d/%m-%y %H:%M:%S"))
        exif_datetime = datetimeset.strftime("%Y:%m:%d %H:%M:%S")
        exif_ifd = {
            piexif.ExifIFD.DateTimeOriginal: exif_datetime,
            piexif.ExifIFD.DateTimeDigitized: exif_datetime,
        }
        exif_dict = {"Exif": exif_ifd}
        exif_bytes = piexif.dump(exif_dict)
    img.save(filename.with_suffix('.bw.png'), exif=exif_bytes, pnginfo=metadata)


def h5_to_png(filename):
    "Read and convert h5 file to png and add attributes"
    #pylint: disable=unsubscriptable-object, invalid-name
    f5_data = h5py.File(filename)
    print(f5_data)
    dset = f5_data['dataset1']
    data = dset['data1']
    data2 = data['data']
    date1 = f5_data['what'].attrs['date']
    time = f5_data['what'].attrs['time']
    radar_datetime = datetime.strptime(date1.decode('utf-8') + time.decode('utf-8'), "%Y%m%d%H%M%S") # pylint: disable=no-member
    if _DEBUG:
        print("Radar Datetime", radar_datetime)
    where = where =f5_data['where']
    attr = where.attrs
    print(attr)
    LL = (attr['LL_lat'][0], attr['LL_lon'][0])
    LR = (attr['LR_lat'][0], attr['LR_lon'][0])
    UL = (attr['UL_lat'][0], attr['UL_lon'][0])
    UR = (attr['UR_lat'][0], attr['UR_lon'][0])
    if _DEBUG:
        print(f"LL: {LL}, LR: {LR}, UL: {UL}, UR: {UR}")
    img = np.array(data2.astype('uint8'))
    image = Image.fromarray(img)
    metadata = exif_bytes = None
    metadata = PngInfo()
    metadata.add_text('Title', 'Radardata from '+ radar_datetime.strftime("%d/%m-%y %H:%M:%S"))
    rfc1123_dat =  rfc1123_date(radar_datetime)
    metadata.add_text('Creation Time', rfc1123_dat )
    metadata.add_text('CreationTime', radar_datetime.strftime("%d/%m-%y %H:%M:%S"))
    metadata.add_text('Coordinats', f"LL: {LL}, LR: {LR}, UL: {UL}, UR: {UR}" )
    exif_datetime = radar_datetime.strftime("%Y:%m:%d %H:%M:%S")
    exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: exif_datetime,
        piexif.ExifIFD.DateTimeDigitized: exif_datetime,
    }
    exif_dict = {"Exif": exif_ifd}
    exif_bytes = piexif.dump(exif_dict)
    image.save(filename.with_suffix('.org.png'), exif=exif_bytes, pnginfo=metadata)
    create_color_file(filename.with_suffix('.org.png'))
    return
    gen_pic(img, filename.with_suffix('.png'), datetimeset=radar_datetime, h5_coords=(LL,LR,UL,UR), pic_coords=((8.01,54.58),(12.73,54.58),(8.01,57.7),(12.73,57.7)))


def create_color_file(filename):
    "Generate color transperant file"
    img = Image.open(filename)
    img.load()
    info = img.info
    print("info", info)
    img2 = colorize(img).convert(mode="RGBA")
    img3 = convert_img_transparent(img2)
    #imgout.save(filename.with_suffix('.col.png'), exif=exif_bytes, pnginfo=info)
    #img3.save(filename.with_suffix('.col.png'), pnginfo=info)
    img3.save(filename.with_suffix('.col.png'))




def gen_pic(arr, filename, datetimeset=None, h5_coords=None, pic_coords=None):
    "create png file from np array"
    if _DEBUG:
        print("Coordinater", h5_coords, pic_coords)
    arr[arr == 255] = 0     # set 0 in stead of 255
    datetaken = datetimeset
    img2 = Image.fromarray(arr)
    #print("info",img2.info)
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
    img2.save(filename.with_suffix('.bw.png'), exif=exif_bytes, pnginfo=metadata)
    img3 = ImageOps.colorize(img2, "#000", "#F22", mid="#05F", blackpoint=50, midpoint=100, whitepoint=180)
    #img3 = ImageOps.colorize(img2, "#000", "#00F", whitepoint=180)
    img4 = img3.convert(mode="RGBA")
    img4.save(filename.with_suffix('.color.png'), exif=exif_bytes, pnginfo=metadata)
    img7 = colorize(img2)
    img8 = img7.convert(mode="RGBA")
    img8.save(filename.with_suffix('.mycol.png'), exif=exif_bytes, pnginfo=metadata)
    img5 = convert_img_transparent(img8)
    img5.save(filename, exif=exif_bytes, pnginfo=metadata)

#     ne = (52.2942, 18.8932)
#     nw = (52.2943, 4.3790)
#     sw = (60.0,3.0)
#     se = (59.8277, 20.7351)
    img6 = radar_pic_cut(img5,(60,3), (52.2942, 20.7351), (56.0, 7.01), (54.7, 15.29))
    img6.save(filename.with_suffix('.cut.png'), exif=exif_bytes, pnginfo=metadata)

def radar_pic(infile, outfile):
    "Create the radar picture for display"
    img = Image.open(infile)
    out = radar_pic_cut(img,(60,3), (52.2942, 20.7351), (56.0, 7.01), (54.7, 15.29))
    out.save(outfile)

def create_radar_pic():
    "pass radar folder and make radar.png files"
    radar_dir = Path(RADAR_DIR)
    clean_radar_files()
    radar_files = radar_dir.glob('*max.color.png')
    file_list = list(radar_files)
    file_list.sort(reverse=True)
    i = 1
    for f in file_list:
        print(f)
        radar_pic(f, RADAR_DIR / ('radar'+str(i) + '.png'))
        img = Image.open(f)
        i = +1



def convert_h5_to_png(filename):
    "Read and convert h5 file to png and add attributes"
    #pylint+ disable=unsubscriptable-object, invalid-name
    f5_data = h5py.File(filename)
    #print(f5_data)
    dset = f5_data['dataset1']
    data = dset['data1']
    data2 = data['data']
    date1 = f5_data['what'].attrs['date']
    time = f5_data['what'].attrs['time']
    #print("date", date1, "time", time)
    radar_datetime = datetime.strptime(date1.decode('utf-8') + time.decode('utf-8'), "%Y%m%d%H%M%S")
    if _DEBUG:
        print("Radar Datetime", radar_datetime)
    where = where =f5_data['where']
    attr = where.attrs
    print("attr", attr)
    LL = (attr['LL_lat'][0], attr['LL_lon'][0])
    LR = (attr['LR_lat'][0], attr['LR_lon'][0])
    UL = (attr['UL_lat'][0], attr['UL_lon'][0])
    UR = (attr['UR_lat'][0], attr['UR_lon'][0])
    if _DEBUG:
        print(LL, LR, UL, UR)
        print("ll_lat", where.attrs['LL_lat'])
        print(type(data2))
        print(data2)
    img = np.array(data2.astype('uint8'))
    gen_pic(img, filename.with_suffix('.png'), datetimeset=radar_datetime, h5_coords=(LL,LR,UL,UR), pic_coords=((8.01,54.58),(12.73,54.58),(8.01,57.7),(12.73,57.7)))

def clean_radar_files():
    "Delete all radar display files"
    radar_dir = Path(RADAR_DIR)
    radar_files = radar_dir.glob('radar*.png')
    for f in radar_files:
        f.unlink()
        #print(str(f))

def get_last_radar_data():
    "get radar data to temp dir and create img files"
    Path(RADAR_DIR).mkdir(parents=True, exist_ok=True)
    clean_radar_files()
    today = datetime.now()
    url = RADAR_URL + '&datetime=../' + parse.quote_plus(rfc3339_date(today))
    #url = RADAR_URL + '&datetime=../2022-10-24T17:00:00Z'
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
                with open(tempfile, 'wb') as fd:
                    for chunk in downloaddata.iter_content(chunk_size=128):
                        fd.write(chunk)
            convert_h5_to_png(tempfile)
            copy(tempfile.with_suffix('.cut.png'), RADAR_DIR / ('radar'+str(number) + '.png'))
            number += 1
        return True
    else:
        print("H5 request status", response.status_code)
        return False

# test procedures

def read_h5_info(filename):
    "Read and convert h5 file"
    f5_data = h5py.File(filename)
    print("Keys",f5_data.keys())
    print("Attibutes", list(f5_data.attrs))
    print('Items', f5_data['how'].items(),f5_data['where'].items(),f5_data['what'].items(), f5_data['dataset1'].items())
    what = f5_data['what']
    print("What keys", what.keys(), "attr", list(what.attrs))
    print("date", what.attrs['date'], "time", what.attrs['time'])
    where =f5_data['where']
    print("Where keys", where.keys(), "attr", list(where.attrs))
    print(where.attrs['LL_lat'])
    dset = f5_data['dataset1']
    #print ("type",  dset.dtype )
    #print("dataset1 : shape", dset.shape, "dtype", dset.dtype, "keys", dset.keys())
    data = dset['data1']
    print(data.keys())
    data = data['data']
    print(data)
    print("0,0", data[0][0])
    #img = np.array(data.astype('uint8'))
    #gen_pic(img, filename.with_suffix('.png'))

def gen_all_png(hfolder):
    "generate png for all files"
    for fil in hfolder.glob('*.h5'):
        print(fil)
        convert_h5_to_png(fil)

if __name__=='__main__':
    get_last_radar_data()
    # file = Path(__file__).parent / 'temp/dk.com.202211031550.500_max.h5'
    # read_h5_info(file)
    # folder = Path(__file__).parent.parent / 'data' / 'radar'
    #file = folder = Path(__file__).parent.parent / 'data' / 'radar' / 'dk.com.202212091610.500_max.bw.png'
    file = folder = Path(__file__).parent.parent / 'data' / 'radar' / 'dk.com.202212091610.500_max.h5'
    #myimg = Image.open(file)
    # myimg.load()
    # print(myimg.info)
    #x = radar_pic_cut(myimg, (52.29, 4.37), (60, 20.7), (52.29, 4.37), (60, 20.7) )
    #x =pixel_pos(52.29, 60, 1984, 59.99)
    #print ("val", x)
    # if not file.is_file():
    #     print("File does not exist:", file)
    # h5_to_png(file)
    