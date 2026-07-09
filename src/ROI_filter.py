import matplotlib.pyplot as plt  # plotting
import numpy as np


def filter_roi(img, roi):
    plt.imshow(img,cmap="gist_gray")
    plt.imshow(roi,alpha=.3)
    pts = plt.ginput(n=-1,mouse_add = 3,mouse_pop = 2, mouse_stop = None,timeout = -1)
    plt.show()

    #print(pts.shape,pts)

    #print(np.array(pts,dtype=int))

    for i in range(len(pts)):
        loc_y = int(pts[i][1])
        loc_x = int(pts[i][0])

        loc_roi = roi[loc_y,loc_x]
        if (loc_roi != 0):
            roi[roi==loc_roi]=0
            #print("Removing ",loc_roi)
            if (loc_roi %2 ==0): # even number, remove also the previous
                roi[roi==loc_roi-1] = 0
                #print("Removing", loc_roi+1)
            else: # odd, remove also the next
                roi[roi==loc_roi+1] = 0
                #print("Removing", loc_roi-1)

    
    plt.imshow(img,cmap="gist_gray")
    plt.imshow(roi,alpha=.3)
    #pts = plt.ginput(n=-1,mouse_add = 3,mouse_pop = 2, mouse_stop = None,timeout = -1)
    #plt.title("Right click to remove rois, PRESS ENTER before closing")
    plt.show()

    return roi
