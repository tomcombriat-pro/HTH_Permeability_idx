#!/usr/bin/python3


"""
Copyright: Combriat Thomas, 2026
Hybrid Technology Hub

This script quantifies the permeability index from nd2 images
"""

import matplotlib.pyplot as plt 
import numpy as np  # numerics
import math as math  # math
import os as os
import nd2
import sys
import skimage.io as io
from tqdm import tqdm

from skimage.filters import laplace, gaussian, threshold_otsu, median
from skimage.feature import peak_local_max
from scipy.ndimage import distance_transform_edt
from skimage.morphology import disk

import argparse
from src.ROImaker import * 


parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('filename')
parser.add_argument('-m', '--median', type=int, default=4,help="Number of successive median filter to apply for initial finding")
parser.add_argument('-ms', '--median_size', type=int, default=6,help="Size of the median filter")  


args = parser.parse_args()



img = nd2.imread(args.filename)

print(img.shape)

med = median(img[0]>threshold_otsu(img[0]),disk(args.median_size))
for i in range(args.median-1):
    med = median(med,disk(args.median_size))


edt = make_rois(img[0],med,10,100,10)

plt.figure()
ax = plt.subplot(231)
plt.imshow(img[0])

plt.subplot(232,sharex=ax,sharey=ax)
plt.imshow(img[0]> threshold_otsu(img[0]))

plt.subplot(233,sharex=ax,sharey=ax)
meds = median(img[0]> threshold_otsu(img[0]))
plt.imshow(med)

plt.subplot(234,sharex=ax,sharey=ax)
plt.imshow(edt)
plt.colorbar()
plt.subplot(235,sharex=ax,sharey=ax)
#plt.imshow(conv)

plt.show()

