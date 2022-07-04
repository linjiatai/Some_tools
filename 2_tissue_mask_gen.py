from PIL import Image
import os
import openslide
import numpy as np
import cv2
from skimage import morphology
folds = os.listdir('dataset')
wsidir = 'WSIs/'
anadir = 'annotations/'
newanadir = 'annotations_update/'
level = 2
palette = [0]*6
palette[0:3] = [0,0,0]
palette[3:6] = [255,255,255]
def gen_bg_mask(orig_img):
    orig_img = np.asarray(orig_img)
    img_array = np.array(orig_img).astype(np.uint8)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    ret, binary = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    binary = np.uint8(binary)    
    dst = morphology.remove_small_objects(binary!=255,min_size=10000,connectivity=1)
    dst = morphology.remove_small_objects(dst==False,min_size=10000,connectivity=1)
    bg_mask = np.ones(orig_img.shape[:2])
    bg_mask[dst==True]=0
    return bg_mask

for root,_,files in os.walk(wsidir):
    for file in sorted(files):
        if file.split('.')[-1] != 'svs':
            continue
        if os.path.exists('tissue_mask/'+file[:-4]+'.png'):
            continue
        print(file)
        slide = openslide.open_slide('WSIs/'+file[:-4]+'.svs')
        image = slide.read_region((0,0),level,slide.level_dimensions[level])
        tissue_mask = gen_bg_mask(image)
        new_mask = Image.fromarray(np.uint8(tissue_mask), 'P')
        new_mask.putpalette(palette)
        new_mask.save('tissue_mask/'+file[:-4]+'.png')
        test = 1

        
