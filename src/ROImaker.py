import numpy as np  # numerics
from scipy.ndimage import distance_transform_edt
from scipy.signal import convolve2d
from skimage.morphology import disk
from skimage.draw import disk as disk_draw
import matplotlib.pyplot as plt



def make_rois(img, mask, number, radius, distance, nmax=10):
    mask_copy = mask.copy()
    # Clear borders
    mask_copy[0] = 0
    mask_copy[-1] = 0
    mask_copy[:, 0] = 0
    mask_copy[:, -1] = 0

    rois = np.zeros_like(mask, dtype=np.uint16)

    # --- Precompute constant EDTs (2 calls total, instead of every iteration) ---
    edt_mask = distance_transform_edt(mask_copy)                    # dist to mask boundary
    edt_inv_mask = distance_transform_edt(np.logical_not(mask_copy)) # dist to mask interior

    # Precompute boundary band for the first point of each pair
    band_low = distance / 2 + radius - 1
    band_high = distance / 2 + radius + 1
    val_band = (edt_mask > band_low) & (edt_mask < band_high)

    # Precompute mask-proximity condition for the companion point
    val_mask_proximity = edt_inv_mask > distance / 2 + radius - 1

    # Coordinate grids for direct distance-from-point computation
    yy, xx = np.ogrid[:rois.shape[0], :rois.shape[1]]

    # Companion-point annulus bounds (squared, to avoid sqrt)
    lower_sq = (distance + 2 * radius - 1) ** 2
    upper_sq = (distance + 2 * radius + 1) ** 2

    n = 0
    i = 0

    while i < number and n < nmax:
        n += 1

        # --- ROI avoidance mask: 1 EDT call (was 2 in original) ---
        if i > 0:
            edt_rois_far = distance_transform_edt(rois == 0) > (distance + radius)
            val_distances = val_band & edt_rois_far
        else:
            val_distances = val_band

        if np.any(val_distances):
            mask_loc = np.where(val_distances)
            idx = np.random.randint(0, len(mask_loc[0]))
            y0, x0 = int(mask_loc[0][idx]), int(mask_loc[1][idx])

            rois_local = np.zeros_like(mask, dtype=np.uint16)
            rr, cc = disk_draw((y0, x0), radius, shape=rois.shape)
            rois_local[rr, cc] = 2 * i + 1

            # --- Direct distance from first point (replaces EDT, O(N) via broadcasting) ---
            dist_sq = (yy - y0) ** 2 + (xx - x0) ** 2
            val_two_distance = (dist_sq > lower_sq) & (dist_sq < upper_sq)
            val_two_distance &= val_mask_proximity
            if i > 0:
                val_two_distance &= edt_rois_far

            if np.any(val_two_distance):
                mask_two_loc = np.where(val_two_distance)

                # Vectorized minimum-finding (was a Python for-loop)
                idx_min = np.argmin(img[mask_two_loc])

                rr, cc = disk_draw(
                    (int(mask_two_loc[0][idx_min]), int(mask_two_loc[1][idx_min])),
                    radius, shape=rois.shape,
                )
                rois_local[rr, cc] = 2 * i + 2

                rois += rois_local
                i += 1
                print(i, "/", number)
                n = 0
        else:
            # No more valid points
            return rois

    return rois
