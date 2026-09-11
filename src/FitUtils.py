import numpy as np
from scipy.optimize import curve_fit

def moved_arctan(x,x0,s,A,y0):
    return y0 + A*np.arctan(s*(x-x0))*2/np.pi


