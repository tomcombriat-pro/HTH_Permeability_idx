#!/usr/bin/python3


"""
Copyright: Combriat Thomas, 2026
Hybrid Technology Hub

This script quantifies the permeability index from nd2 images and preprocessing done with analyse.py script. It uses a rectangle to compute the profile accross the boundary between a couple of ROIs.
"""

import matplotlib.pyplot as plt 
import numpy as np  # numerics
import math as math  # math
import os as os
import nd2
import sys
import skimage.io as io
from tqdm import tqdm
import skimage as ski

from skimage.filters import laplace, gaussian, threshold_otsu, median
from skimage.feature import peak_local_max
from scipy.ndimage import distance_transform_edt
from skimage.morphology import disk

import argparse
from skimage.io import imsave
from src.LineUtils import *

def find_time(st):
    stt = int(os.path.basename(st).rsplit("_",maxsplit=1)[1][1::].split("min")[0])
    return stt


parser = argparse.ArgumentParser(
                    prog='HTH_LinePostProcessing',
                    description='This script quantifies the permeability index from nd2 images and preprocessing done with analyse.py script. It uses a rectangle to compute the profile accross the boundary between a couple of ROIs.',
                    epilog='Created with blood and coffein. Copyright: Combriat 2026',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('filename', type=str, help="Input stack, can be any of the time serie" )
#parser.add_argument('-m', '--median', type=int, default=2,help="Number of successive median filter to apply for initial finding")


args = parser.parse_args()




#### Find all other files
folder = os.path.dirname(args.filename)
try:
    os.mkdir(folder+os.sep+"res")
except:
    pass




ls = os.listdir(folder)
basename= os.path.basename(args.filename).rsplit("_",maxsplit=1)[0]
#print(basename,find_time(args.filename))
ls_filtered = []
times = []
for i in ls:
    if (basename in i and ".nd2" in i):
        ls_filtered.append(i)
        times.append(find_time(i))

try:
    os.mkdir(folder+os.sep+"res"+os.sep+basename)
except:
    pass

try:
    os.mkdir(folder+os.sep+"res"+os.sep+basename+os.sep+"line")
except:
    pass




sorting = np.argsort(times)
ls_filtered = np.array(ls_filtered)[sorting]
times = np.array(times)[sorting]

print(ls_filtered,times)

plt.figure(figsize= (15,10))


for i in tqdm(range(len(ls_filtered))):
    print(" * Opening", ls_filtered[i])
    img = nd2.imread(folder+os.sep+ls_filtered[i])

    rois = []
    for r in range(len(img)):
        rois=io.imread(folder+os.sep+"res"+os.sep+basename+os.sep+basename+"_ROIS_"+str(r)+".tiff")

        props = ski.measure.regionprops(rois)
        print(len(props))
        for j in range(int(len(props)/2)):
            print(np.amax(rois),2*j)
            rect_mask = aligned_rectangle_distance_along_segment((props[2*j].centroid[1],props[2*j].centroid[0]),(props[2*j+1].centroid[1],props[2*j+1].centroid[0]),rois.shape,50,outside_value=0,extra_length=0)

            distances = rect_mask[rect_mask!=0]
            values = img[r][rect_mask!=0]

            sorting = np.argsort(distances)
            distances = distances[sorting]
            values = values[sorting]
            
            plt.scatter(distances,values,alpha=.02)
            plt.plot(distances,moving_average(values,101),label = str(j*2))

        plt.legend()
        plt.show()
