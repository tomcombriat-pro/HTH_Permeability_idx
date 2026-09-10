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
from skimage.registration import phase_cross_correlation

import argparse
from src.ROImaker import *
from skimage.io import imsave
from matplotlib.patches import Circle
from src.ROI_filter import *

from src.LineUtils import *
from src.ImUtils import *
from src.FitUtils import *

def find_time(st):
    stt = int(os.path.basename(st).rsplit("_",maxsplit=1)[1][1::].split("min")[0])
    return stt
    


parser = argparse.ArgumentParser(
                    prog='HTH_Permeability_idx',
                    description='This program computes the fluorescence index between couples of ROIs, that it automatically finds',
                    epilog='Created with salt and coffein. Copyright: Combriat 2026',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('filename', type=str, help="Input stack, can be any of the time serie" )
parser.add_argument('-m', '--median', type=int, default=2,help="Number of successive median filter to apply for initial finding")
parser.add_argument('-ms', '--median_size', type=int, default=6,help="Size of the median filter")
parser.add_argument('-n', '--n_roi', type=int, default=2,help="Number of rois per image")
parser.add_argument('-mi', '--max_iter', type=int,default=20,help="Max number of iterations to find correct ROIs")
parser.add_argument('-s','--size_roi', type=int,default=50,help="Radius of the ROIs")
parser.add_argument('-d','--distance', type=int,default=10,help="Distance between adjactent ROIs")
parser.add_argument('-f','--manual_filter', type=int,default=True,help="Manual filtering of the ROIs")
parser.add_argument('-nd', '--n_dilation', type=int, default=5,help="Number of successive dilation of the mask for registration")
parser.add_argument('-u', '--upsample', type=int, default=1,help="Upsample factor for the registration")
parser.add_argument('-w', '--width', type=int, default=50,help="Width of the line to find the profile")
parser.add_argument('-x', '--extra_length', type=int, default=50,help="Line extra length beyond the ROIs")


args = parser.parse_args()


print("--------------------\n    PERMEABILITY IDX  ")
print("                    \n        REBORN...    \n --------------------")




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


sorting = np.argsort(times)
ls_filtered = np.array(ls_filtered)[sorting]
times = np.array(times)[sorting]

print(ls_filtered,times) 



#### Data loading ####

imgs = []
for i in tqdm(range(len(ls_filtered))):  ## opening and storing all images
    imgs.append(nd2.imread(folder+os.sep+ls_filtered[i]))
print("Data Loaded!")



print(" * Registering (this might take some time...)")
for i in tqdm(range(len(imgs[0]))): # loop on sub-images
    #out.write("\n\n### IMAGE#" + str(i)+"\n")

    slopes = []
    amps = []
    for t in range(len(imgs)): ## loop on time points
        slopes.append([])
        amps.append([])
        plt.clf()
        if (t!=0): # needs registration
            shift, _,_ = phase_cross_correlation(normalize(imgs[0][i]),normalize(imgs[t][i]),reference_mask=n_dilate(imgs[0][i]>threshold_otsu(imgs[0][i]),args.n_dilation),upsample_factor=args.upsample)
    
