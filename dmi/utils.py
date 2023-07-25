"img utils"
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

def convert_img_transparent(img, bg_color=(0,0,0)):
    "Convert alle pixels with bg_color to transparant from image"
    array = np.array(img, dtype=np.ubyte)
    mask = (array[:,:,:3] == bg_color).all(axis=2)
    alpha = np.where(mask, 250, 255)
    array[:,:,-1] = alpha
    return Image.fromarray(np.ubyte(array))

def colorize_std(img):
    "colorize with standard function"

    if img.mode == "LA":
        img_l = img.getchannel('L')
        img_res = ImageOps.colorize(img_l, "#000", "#F22", mid="#05F", blackpoint=50, midpoint=100, whitepoint=180)
        img_res.putalpha(img.getchannel('A'))
    elif img.mode == "L":
        img_res = ImageOps.colorize(img, "#000", "#00F", whitepoint=180)
    else:
        raise TypeError("illegal img format")
    return img_res

def colorize_as_dmi(img):
    "make colors ala DMI"
    nimg = Image.new('RGBA',img.size)
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            pic = img.getpixel((x,y))
            #print(pic)
            alfa = pic[1]
            # if alfa == 0:
            #     alfa = 0
            if pic[0] < 20:
                nimg.putpixel((x,y), (0,0,0, 0))
            elif pic[0] < 80:
                nimg.putpixel((x,y), (158, 242, 233, alfa))   # lys blå
            elif pic[0] < 103:
                nimg.putpixel((x,y), (125, 238, 226, alfa))   # lid blå
            elif pic[0] < 105:
                nimg.putpixel((x,y), (22, 225, 204, alfa))    # turkis
            elif pic[0] < 110:
                nimg.putpixel((x,y), (109, 191,242, alfa))    # grå blå
            elif pic[0] < 120:
                nimg.putpixel((x,y), (61, 171, 238, alfa))    # mørk blå
            elif pic[0] < 130:
                nimg.putpixel((x,y), (0, 143, 233, alfa))     # blå
            elif pic[0] < 135:
                nimg.putpixel((x,y), (255, 217, 0, alfa))     # gul
            elif pic[0] < 140:
                nimg.putpixel((x,y), (255, 178, 0, alfa))     # lys orange
            elif pic[0] < 150:
                nimg.putpixel((x,y), (255, 142, 82, alfa))    # orange
            elif pic[0] < 160:
                nimg.putpixel((x,y), (255,181,181, alfa))     # pink
            elif pic[0] < 170:
                nimg.putpixel((x,y), (255,124,124, alfa))     # blegrød
            elif pic[0] < 200:
                nimg.putpixel((x,y), (255, 82, 82, alfa))     # rød
            elif pic[0] < 210:
                nimg.putpixel((x,y), (230, 57, 57, alfa))     # mørk rød
            elif pic[0] < 220:
                nimg.putpixel((x,y), (204, 31, 31, alfa))     # mere mørk rød
            else:
                nimg.putpixel((x,y), (128,0,0, alfa))         # meget mørk rød
    return nimg

if __name__=='__main__':
    file = Path(__file__).parent.parent / 'data/radar' / 'dk.com.202307120910.500_max.png'
    myimg = Image.open(file)
    #myimg2 = colorize_std(myimg)
    myimg2 = colorize_as_dmi(myimg)
    myimg2.save("tmp.png")
 