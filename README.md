# HTH_Permeability_idx


## Usage 

usage: ProgramName [-h] [-m MEDIAN] [-ms MEDIAN_SIZE] [-n N_ROI]
                   [-mi MAX_ITER] [-s SIZE_ROI] [-d DISTANCE]
                   filename

What the program does

positional arguments:
  filename

options:
  -m, --median MEDIAN   Number of successive median filter to apply for
                        initial finding
  -ms, --median_size MEDIAN_SIZE
                        Size of the median filter
  -n, --n_roi N_ROI     Number of rois per image
  -mi, --max_iter MAX_ITER
                        Max number of iterations to find correct ROIs
  -s, --size_roi SIZE_ROI
                        Radius of the ROIs
  -d, --distance DISTANCE
                        Distance between adjactent ROIs
