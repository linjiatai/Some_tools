# -*- coding: utf-8 -*-
from unicodedata import category
import numpy as np
import cv2
import os
import xml.etree.ElementTree as ET
import openslide
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

def xml2mask(file, dir, dimension, save_dir, classes, palette):
    filename = file[:-4]

    xml = os.path.join(dir, file)

    mask = np.zeros([dimension[1], dimension[0]], dtype=np.uint8)
    
    tree = ET.parse(xml)
    root = tree.getroot()
    categories = root.findall('Annotation')
    for category in categories:
        name = category.attrib['Name']
        i = 1
        for subcls in classes:
            if subcls == name:
                cls_index = i
            i += 1
        regions = category.findall('Regions/Region')
        for region in regions:
            points = []
            for point in region.findall('Vertices/Vertex'):
                x = float(point.attrib['X'])
                y = float(point.attrib['Y'])
                points.append([x, y])

            pts = np.asarray([points], dtype=np.int32)
            cv2.fillPoly(img=mask, pts=pts, color=cls_index)
    mask = cv2.resize(mask,(int(mask.shape[1]/10), int(mask.shape[0]/10)), cv2.INTER_NEAREST)
    vis_mask = Image.fromarray(np.uint8(mask), 'P')
    # vis_mask = vis_mask.resize((int(vis_mask.size[0]/10),int(vis_mask.size[1]/10)), Image.NEAREST)
    vis_mask.putpalette(palette)
    vis_mask.save(os.path.join(save_dir, filename+".png"))
def find_wsi(fname, wsidir):
    for root, _, wsis in os.walk(wsidir):
        for wsi in wsis:
            wsi_name = wsi[:-4]
            if fname != wsi_name:
                continue
            print(os.path.join(root, wsi))
            slide = openslide.open_slide(os.path.join(root, wsi))
            dimensions = slide.dimensions
            return dimensions

xml_dir = "./xmls/"
wsi_dir = './WSIs/'
save_dir = './annotations/'
files = os.listdir(xml_dir)
i = 0
class_dict = ['normal', 'tumor', 'stroma', 'mucus', 'necrosis', 'muscle']
palette = [0]*((len(class_dict)+1)*3)
palette[0:3] = [255,255,255]
palette[3:6] = [120,120,120]
palette[6:9] = [255,0,0]
palette[9:12] = [0,255,0]
palette[12:15] = [0,255,255]
palette[15:18] = [255,0,255]
palette[18:21] = [237,145,33]
for file in sorted(files, reverse=False):
    print(file)
    fname = file[:-4]
    dimension = find_wsi(fname=fname, wsidir=wsi_dir)
    xml2mask(file, xml_dir, dimension, save_dir, class_dict, palette)
    i+=1
    print('已完成{0}幅图像!'.format(i))
print("全部完成!")