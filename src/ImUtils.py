import numpy as np

def normalize(im):
    im_tamp = np.array(im,dtype=float)
    im_tamp -= np.amin(im_tamp)
    im_tamp /= np.amax(im_tamp)
    return im_tamp

from skimage.morphology import dilation

def n_dilate(im,n):
    im_tamp = np.array(im)
    for i in range(n):
        im_tamp = dilation(im_tamp)
    return im_tamp
