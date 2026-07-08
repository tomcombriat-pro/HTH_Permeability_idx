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

def find_time(st):
    stt = int(os.path.basename(st).rsplit("_",maxsplit=1)[1][1::].split("min")[0])
    return stt
    


parser = argparse.ArgumentParser(
                    prog='ProgramName',
                    description='What the program does',
                    epilog='Text at the bottom of help')

parser.add_argument('filename')
parser.add_argument('-m', '--median', type=int, default=4,help="Number of successive median filter to apply for initial finding")
parser.add_argument('-ms', '--median_size', type=int, default=6,help="Size of the median filter")
parser.add_argument('-n', '--n_roi', type=int, default=2,help="Number of rois per image")
parser.add_argument('-mi', '--max_iter', type=int,default=20,help="Max number of iterations to find correct ROIs")
parser.add_argument('-s','--size_roi', type=int,default=50,help="Radius of the ROIs")
parser.add_argument('-d','--distance', type=int,default=10,help="Distance between adjactent ROIs")


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
                rois.append(make_rois(img[j],med,args.n_roi,100,10,args.max_iter))
                plt.clf()
                plt.subplot(121)
                plt.imshow(img[j],cmap="gist_gray")
                plt.imshow(rois[j],alpha=0.4)
                plt.colorbar()
                plt.subplot(122)
                plt.imshow(med)
                plt.savefig(folder+os.sep+"res"+os.sep+basename+"_overviewROI_"+str(j)+".png")
            """
            except:
                valid[j] = False
                rois.append(np.zeros_like(img[j]))
            """
            imsave(folder+os.sep+"res"+os.sep+basename+"_ROIS_"+str(j)+".tiff",rois[j],check_contrast=False)

            

        for r in range(args.n_roi):
            if (np.sum(rois[j]==2*r+2) > 0):
                res[i][j].append(np.mean(img[j][rois[j]==2*r+2])/np.mean(img[j][rois[j]==2*r+1]))
            else:
                res[i][j].append(0)

out = open(folder+os.sep+"res"+os.sep+basename+"_table.txt","w")
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
        

out.close()

plt.clf()

for i in range(len(res)):
    for j in range(len(res[i])):
        plt.plot(times,res[i][j],label = "Im"+str(j)+"_ROI"+str(i))
plt.xlabel("Time")
plt.legend()
plt.savefig(folder+os.sep+"res"+os.sep+basename+"_glob.png")
            



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

