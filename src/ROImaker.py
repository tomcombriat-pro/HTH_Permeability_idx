import numpy as np  # numerics
from scipy.ndimage import distance_transform_edt
from scipy.signal import convolve2d
from skimage.morphology import disk
from skimage.draw import disk as disk_draw
import matplotlib.pyplot as plt


def make_rois(img,mask, number, radius ,distance,nmax =10):
    ## clear the borders
    mask_copy = mask.copy()
    rois = np.zeros_like(mask,dtype=np.uint16)
    mask_copy[0] = 0
    mask_copy[-1] = 0
    mask_copy[:,0] = 0
    mask_copy[:,-1] = 0
    n = 0
    i=0
    #for i in range(number):
    while(np.amax(rois) < 2*number and n<nmax):
        n+=1
        #try:
        if (True):
            rois_local = np.zeros_like(mask,dtype=np.uint16)
            print(i,"/",number)
            edt = distance_transform_edt(mask_copy)

            val_distances = edt > distance/2+radius-1
            val_distances = np.logical_and(val_distances,edt < distance/2+radius +1)
            if (i>0):
                edt_rois = distance_transform_edt(rois ==0) ## to avoid superimposition
                edt_rois = edt_rois > distance + radius
                val_distances = np.logical_and(val_distances,edt_rois)

            #conv = convolve2d(mask, disk(radius),mode="same")
            #val_distances = np.logical_and(conv==np.sum(disk(radius)),val_distances)



            mask_loc = np.where(val_distances)  # get (loc_y, loc_x) of all positive indices (https://stackoverflow.com/questions/79283584/what-is-the-most-efficient-way-to-randomly-pick-one-positive-location-within-a-l)
            idx = np.random.randint(low=0, high=len(mask_loc[0]))
            rr, cc = disk_draw((mask_loc[0][idx],mask_loc[1][idx]), radius, shape=rois.shape)
            rois_local[rr,cc] = 2*i+1



            ## Dirty way of finding the companion point, might be optimized later
            edt_local = np.zeros_like(edt)
            edt_local[mask_loc[0][idx],mask_loc[1][idx]] = 1
            edt_local = distance_transform_edt(np.logical_not(edt_local))

            val_two_distance = edt_local < distance + 2*radius +1
            val_two_distance = np.logical_and(val_two_distance, edt_local> distance + 2*radius -1)

            edt = distance_transform_edt(np.logical_not(mask_copy))
            val_two_distance = np.logical_and(val_two_distance,edt > distance/2+radius-1)

            if (i>0):
                edt_rois = distance_transform_edt(rois ==0) ## to avoid superimposition with previouses
                edt_rois = edt_rois > distance + radius
                val_two_distance = np.logical_and(val_two_distance,edt_rois)


            if (np.sum(val_two_distance) > 0):
                mask_two_loc = np.where(val_two_distance)

                local_min = np.amax(img)
                for m in range(len(mask_two_loc[0])):
                    #print(img[mask_two_loc[0][m],mask_two_loc[1][m]])
                    if (img[mask_two_loc[0][m],mask_two_loc[1][m]] < local_min):
                        local_min = img[mask_two_loc[0][m],mask_two_loc[1][m]]
                        idx_min = m

                rr, cc = disk_draw((mask_two_loc[0][idx_min],mask_two_loc[1][idx_min]), radius, shape=rois.shape)
                rois_local[rr,cc] = 2*i+2

                rois+=rois_local
                i+=1
        """
        except:
            pass
        """

    return rois
    
