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
from skimage.io import imsave
from matplotlib.patches import Circle
from src.ROI_filter import *

def find_time(st):
    stt = int(os.path.basename(st).rsplit("_",maxsplit=1)[1][1::].split("min")[0])
    return stt
    


parser = argparse.ArgumentParser(
                    prog='HTH_Permeability_idx',
                    description='This program computes the fluorescence index between couples of ROIs, that it automatically finds',
                    epilog='Created with sweat and coffein. Copyright: Combriat 2026',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('filename', type=str, help="Input stack, can be any of the time serie" )
parser.add_argument('-m', '--median', type=int, default=2,help="Number of successive median filter to apply for initial finding")
parser.add_argument('-ms', '--median_size', type=int, default=6,help="Size of the median filter")
parser.add_argument('-n', '--n_roi', type=int, default=2,help="Number of rois per image")
parser.add_argument('-mi', '--max_iter', type=int,default=20,help="Max number of iterations to find correct ROIs")
parser.add_argument('-s','--size_roi', type=int,default=50,help="Radius of the ROIs")
parser.add_argument('-d','--distance', type=int,default=10,help="Distance between adjactent ROIs")
parser.add_argument('-f','--manual_filter', type=int,default=True,help="Manual filtering of the ROIs")


args = parser.parse_args()


print("--------------------\n    PERMEABILITY IDX \n --------------------")



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


rois = []
res = []

fig = plt.figure(figsize=(15,15))
for i in range(len(ls_filtered)):
    res.append([])
    print(" * Opening", ls_filtered[i])
    img = nd2.imread(folder+os.sep+ls_filtered[i])

    if (i==0):
        valid = np.ones((len(img)))
    for j in tqdm(range(len(img))):
        res[i].append([])
        if (i==0): ## we need to make rois
            print(" * Making ROIs")
            med = median(img[j]>threshold_otsu(img[j]),disk(args.median_size))
            for m in range(args.median-1):
                med = median(med,disk(args.median_size))
            #try:
            if (True):
                tamp_roi = make_rois(img[j],med,args.n_roi,args.size_roi,args.distance,args.max_iter)
                rois.append(tamp_roi)

                

                
for i in range(len(ls_filtered)):
    print(" * Opening", ls_filtered[i])
    img = nd2.imread(folder+os.sep+ls_filtered[i])
    if (i==0 and args.manual_filter):
        for j in tqdm(range(len(img))):
            rois[j] = filter_roi(img[j],rois[j])
    for j in tqdm(range(len(img))):
        plt.clf()
        plt.subplot(121)
        plt.imshow(img[j],cmap="gist_gray")
        plt.imshow(rois[j],alpha=0.4,cmap="okabe_ito")
        plt.colorbar(shrink=0.5)
        plt.subplot(122)
        plt.imshow(med)
        plt.tight_layout()
        plt.savefig(folder+os.sep+"res"+os.sep+basename+os.sep+basename+"_overviewROI_"+str(j)+".png")

        imsave(folder+os.sep+"res"+os.sep+basename+os.sep+basename+"_ROIS_"+str(j)+".tiff",rois[j],check_contrast=False)

            

        for r in range(args.n_roi):
            if (np.sum(rois[j]==2*r+2) > 0):
                res[i][j].append(np.mean(img[j][rois[j]==2*r+2])/np.mean(img[j][rois[j]==2*r+1]))
            else:
                res[i][j].append(0)

out = open(folder+os.sep+"res"+os.sep+basename+os.sep+basename+"_table.txt","w")
for i in range(len(sys.argv)):
    out.write(sys.argv[i])
    out.write(" ")
out.write("\n")
out.write("## Hello there, comments to come\n")

res = np.array(res)
for i in range(len(res[0])): ## sub-images loop
    out.write("#IMAGE_N"+str(i)+"\n")
    out.write("Time")
    for k in range(len(res[0][i])):
        out.write(" ROI_"+str(2*k+1)+"_"+str(2*k+2))
    out.write("\n")
    for t in range(len(res)):
        out.write(str(times[t]))
        for k in range(len(res[t][i])):
            out.write(" ")
            out.write(str(res[t][i][k]))
        out.write("\n")

out.write("\n#SUMMARY\n")

if (len(res[0])%4==0): ## Dividable by four
    for i in range(int(len(res[0])/4)): ## sub-images group
        sub_res = res[:,4*i:4*i+4,:]
        out.write("#Chip_"+str(i)+"\n")
        for t in range(len(sub_res)): # loop on time
            sub_sub_res = sub_res[t]
            non_zero_mask = sub_sub_res!=0
            if (np.sum(non_zero_mask) !=0): ## check whether there is actually some data
                non_zero_mean = np.mean(sub_sub_res[non_zero_mask])
            else:
                non_zero_mean = 0
            out.write(str(times[t]))
            out.write(" "+str(non_zero_mean)+"\n")
            
                      
                

out.close()

plt.clf()

for i in range(len(res[0])): ## sub images
    for j in range(len(res[0][i])): #rois
        if (res[0][i][j] !=0):
            plt.plot(times,res[:,i,j],label = "Im"+str(i)+"_ROI"+str(j))
plt.xlabel("Time")
plt.legend()
plt.savefig(folder+os.sep+"res"+os.sep+basename+os.sep+basename+"_glob.png")
            



"""
#rois = make_rois(img[0],med,2,100,10)

plt.figure()
ax = plt.subplot(231)
plt.imshow(img[0])

plt.subplot(232,sharex=ax,sharey=ax)
plt.imshow(img[0]> threshold_otsu(img[0]))

plt.subplot(233,sharex=ax,sharey=ax)
meds = median(img[0]> threshold_otsu(img[0]))
plt.imshow(med)

plt.subplot(234,sharex=ax,sharey=ax)
plt.imshow(rois)
plt.colorbar()
plt.subplot(235,sharex=ax,sharey=ax)
#plt.imshow(conv)

plt.show()
"""

