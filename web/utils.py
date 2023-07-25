"Div img utils"
from PIL import Image
import numpy as np

def convert_png_transparent(src_file, dst_file, bg_color=(0,0,0)):
    "Convert alle pixels with bg_color to transparant"
    image = Image.open(src_file).convert("RGBA")
    array = np.array(image, dtype=np.ubyte)
    mask = (array[:,:,:3] == bg_color).all(axis=2)
    alpha = np.where(mask, 0, 255)
    array[:,:,-1] = alpha
    Image.fromarray(np.ubyte(array)).save(dst_file, "PNG")

def convert_img_transparent(img, bg_color=(0,0,0)):
    "Convert alle pixels with bg_color to transparant from image"
    #image = Image.open(src_file).convert("RGBA")
    array = np.array(img, dtype=np.ubyte)
    mask = (array[:,:,:3] == bg_color).all(axis=2)
    alpha = np.where(mask, 0, 255)
    array[:,:,-1] = alpha
    return Image.fromarray(np.ubyte(array))

def get_img_tags(file):
    "return the tags as dict"
    img=Image.open(file)
    img.load()
    info = img.info
    return info

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
