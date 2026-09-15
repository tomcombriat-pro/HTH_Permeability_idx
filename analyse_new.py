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
import colorama as cl

from skimage.filters import laplace, gaussian, threshold_otsu, median
from skimage.feature import peak_local_max
from scipy.ndimage import distance_transform_edt
from skimage.morphology import disk
from skimage.registration import phase_cross_correlation
from matplotlib.widgets import PolygonSelector

import argparse
from src.ROImaker import *
from skimage.io import imsave
from matplotlib.patches import Circle
from src.ROI_filter import *
from skimage.util import img_as_ubyte

from src.LineUtils import *
from src.ImUtils import *
from src.FitUtils import *
import skimage as ski

def find_time(st):
    stt = int(os.path.basename(st).rsplit("_",maxsplit=1)[1][1::].split("min")[0])
    return stt


from skimage.transform import AffineTransform, warp

def shift(image, vector):
    for i in range(len(vector)):
        vector[i]=-vector[i]
    transform = AffineTransform(translation=vector)
    shifted = warp(image, transform, mode='wrap', preserve_range=True)

    shifted = shifted.astype(image.dtype)
    return shifted
    


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
parser.add_argument('-sr', '--sanity_registering', type=bool, default=False,help="Whether to output, or not an RGB image showing the registration done")

args = parser.parse_args()


print("--------------------\n  PERMEABILITY IDX  ")
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
print(cl.Back.GREEN+"Data Loaded!"+ cl.Style.RESET_ALL)


masks_pol = []
rois = []
fig = plt.figure(figsize=(30,20))
#print(" * Registering (this might take some time...)")
print(cl.Fore.BLUE+cl.Back.RED+ " * Main area selection, draw a polygon to restrict the algorithm to this area. You can close the window without drawing anything. Esc to reset."+ cl.Style.RESET_ALL)
for i in tqdm(range(len(imgs[0]))): # loop on sub-images, polygon drawing

    ## Defining the ROIs main area
    #plt.clf()
     masks_pol.append(select_main_area(imgs[0][i]))
     #break



meds = []
print(" * Finding ROIs...")
for i in tqdm(range(len(imgs[0]))): # loop on sub-images, ROIs finding
     med = median(imgs[0][i]>threshold_otsu(imgs[0][i][masks_pol[i]]),disk(args.median_size))
     for m in range(args.median-1):
         med = median(med,disk(args.median_size))
     med *= masks_pol[i]
     meds.append(med)
     rois.append(make_rois(imgs[0][i],med,args.n_roi,args.size_roi,args.distance,args.max_iter))
     imsave(folder+os.sep+"res"+os.sep+basename+os.sep+basename+"_mask_"+str(i)+".tiff",img_as_ubyte(np.array(med,dtype=bool)),check_contrast=False)
     #break


print(cl.Fore.BLUE+cl.Back.RED+" * ROIs filtering. Right-click on the ROIs you want to have removed. Enter to finish"  + cl.Style.RESET_ALL)

for i in tqdm(range(len(imgs[0]))): # loop on sub-images, ROIs filtering
    rois[i] = filter_roi(imgs[0][i],rois[i])
    plt.subplot(121)
    plt.imshow(imgs[0][i],cmap="gist_gray")
    plt.imshow(rois[i],alpha=0.4,cmap="Set2")
    plt.colorbar(shrink=0.5)
    plt.subplot(122)
    plt.imshow(meds[i])
    plt.tight_layout()
    plt.savefig(folder+os.sep+"res"+os.sep+basename+os.sep+basename+"_overviewROI_"+str(i)+".png")
    plt.clf()
    #break



print(" * Registering... This may take a while (go get yourself a coffee)")
shifts = []
for i in tqdm(range(len(imgs[0]))): # loop on sub-images, registration
    shifts.append([])
    for t in range(len(imgs)): ## loop on time points
        
        if (t!=0): # needs registration
            shiftt, _,_ = phase_cross_correlation(normalize(imgs[0][i]),normalize(imgs[t][i]),reference_mask=n_dilate(imgs[0][i]>threshold_otsu(imgs[0][i]),args.n_dilation),upsample_factor=args.upsample)
            shifts[i].append(shiftt)
        else:
            shifts[i].append([0.,0.])

    #break
            
#print(np.array(shifts).shape)

#print(shifts)

#shifts = np.zeros((16,4,2))         

print(cl.Back.GREEN+"Registering done!"+ cl.Style.RESET_ALL)




out = open(folder+os.sep+"res"+os.sep+basename+os.sep+basename+"_table.txt","w")
out_detail = open(folder+os.sep+"res"+os.sep+basename+os.sep+basename+"_table_detail.txt","w")
out_detail.write("# Command: ")
for i in sys.argv:
    out_detail.write(i+" ")
out_detail.write("\n")


rgb = np.zeros((len(imgs[0][0]),len(imgs[0][0][0]),3))

for i in tqdm(range(len(imgs[0]))): # loop on sub-images

    if (args.sanity_registering):
        rgb_out = np.zeros((len(imgs[t][i]),len(imgs[t][i][0]),3),dtype=np.uint8)
        
    out_detail.write("\n## IMG_"+str(i)+"\n")
    out.write("## IMG_"+str(i)+"\n")
    out.write("#Time Ratio_circle Ratio_fit Slope N\n")    
    props = ski.measure.regionprops(rois[i])
    for t in range(len(imgs)): ## loop on time points

        
        out_detail.write("### Time "+str(times[t])+"\n")
        out_detail.write("### Registration " + str(shifts[i][t][0])+ " "+str(shifts[i][t][1])+"\n")
        curr_img = shift(imgs[t][i],shifts[i][t])
        if (args.sanity_registering and t<3):
            rgb_out[:,:,t] = normalize(curr_img)*255
        
        res = []
        popts = []
        for r in range(1,int(np.amax(rois[i])/2+1)):
            #if (np.sum(rois[i]==2*r+2) > 0):
            if (True):
                res.append(np.mean(curr_img[rois[i]==2*r])/np.mean(curr_img[rois[i]==2*r-1]))
                
                rect_mask = aligned_rectangle_distance_along_segment((int(props[2*r-2].centroid[1]),int(props[2*r-2].centroid[0])),(int(props[r*2-1].centroid[1]),int(props[2*r-1].centroid[0])),rois[i].shape,args.width,outside_value=0,extra_length=args.extra_length)

                distances = rect_mask[rect_mask!=0]
                if (np.sum(distances) > 0):
                    values = curr_img[rect_mask!=0]

                    sorting = np.argsort(distances)
                    distances = distances[sorting]
                    values = values[sorting]

                    popt, _ = curve_fit(moved_arctan,distances,values,p0 = [np.amax(distances)/2,1,np.amax(values)-np.amin(values),np.mean(values)],maxfev=int(1e6))
                    popts.append(popt)

                    
                    plt.subplot(211)
                    plt.scatter(distances,values,alpha=.2)
                    plt.plot(distances,moved_arctan(distances,*popt),label = "ROI_"+str(r))
                    plt.legend()

                    plt.subplot(212)
                    plt.scatter(distances,values-moved_arctan(distances,*popt),alpha=.1)
                    plt.axhline(0)

                    out_detail.write("#ROI_"+str(r)+ " Fit parameters:")
                    for p in popt:
                        out_detail.write(" "+str(p))
                    out_detail.write("\n")



        plt.savefig(folder+os.sep+"res"+os.sep+basename+os.sep+"line_IMG"+str(i)+"_time"+str(times[t])+".png")
        plt.clf()
        out.write(str(times[t])+" "+str(np.mean(res)))
        popts = np.array(popts)
        out.write(" "+str(1/np.mean((popts[:,3]+popts[:,2])/(popts[:,3]-popts[:,2])))+" "+str(np.mean(popts[:,1]))+" "+str(len(res))+"\n")
    if (args.sanity_registering):
        #print(rgb_out.shape,rgb_out.dtype)
        #plt.imshow(rgb_out)
        #plt.savefig(folder+os.sep+"res"+os.sep+basename+os.sep+"registering_IMG"+str(i)+".png")
        ski.io.imsave(folder+os.sep+"res"+os.sep+basename+os.sep+"registering_IMG"+str(i)+".png",rgb_out)
        #plt.clf()
    #break

                

out.close()
out_detail.close()
