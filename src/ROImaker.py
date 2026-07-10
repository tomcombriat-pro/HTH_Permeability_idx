import numpy as np  # numerics
from scipy.ndimage import distance_transform_edt
from scipy.signal import convolve2d
from skimage.morphology import disk
from skimage.draw import disk as disk_draw
import matplotlib.pyplot as plt



def make_rois(img, mask, number, radius, distance, nmax=10):
    H, W = mask.shape
    mask_copy = mask.copy()
    mask_copy[0] = 0
    mask_copy[-1] = 0
    mask_copy[:, 0] = 0
    mask_copy[:, -1] = 0

    rois = np.zeros_like(mask, dtype=np.uint16)

    # ── Precompute constant EDTs (2 calls, total) ──
    edt_mask = distance_transform_edt(mask_copy)
    edt_inv_mask = distance_transform_edt(np.logical_not(mask_copy))

    band_low = distance / 2 + radius - 1
    band_high = distance / 2 + radius + 1
    val_band = (edt_mask > band_low) & (edt_mask < band_high)
    val_mask_proximity = edt_inv_mask > distance / 2 + radius - 1

    # ── Precompute annulus template for companion-point search ──
    annulus_outer = int(distance + 2 * radius + 1)
    annulus_lower_sq = (distance + 2 * radius - 1) ** 2
    annulus_upper_sq = annulus_outer ** 2
    dy_g, dx_g = np.ogrid[-annulus_outer:annulus_outer + 1,
                          -annulus_outer:annulus_outer + 1]
    annulus_sq = dy_g ** 2 + dx_g ** 2
    annulus_offsets = np.where(
        (annulus_sq > annulus_lower_sq) & (annulus_sq < annulus_upper_sq)
    )
    annulus_dy, annulus_dx = annulus_offsets[0] - annulus_outer, annulus_offsets[1] - annulus_outer

    # ── Incremental squared-distance field for ROI avoidance ──
    exclusion_radius = distance + 2 * radius
    exclusion_sq = exclusion_radius ** 2
    r_excl = int(np.ceil(exclusion_radius))
    edt_rois_sq = np.full((H, W), np.inf, dtype=np.float32)

    # ── Track valid first-point candidates (band pixels) ──
    band_flat = np.flatnonzero(val_band.ravel())
    band_y, band_x = np.unravel_index(band_flat, (H, W))
    band_valid = np.ones(len(band_flat), dtype=bool)

    n = 0
    i = 0

    while i < number and n < nmax:
        n += 1

        # ── Pick first point from valid band candidates ──
        valid_idx = np.flatnonzero(band_valid)
        if len(valid_idx) == 0:
            return rois
        pick = valid_idx[np.random.randint(0, len(valid_idx))]
        y0, x0 = int(band_y[pick]), int(band_x[pick])

        # Place first ROI disk (write directly, undo on failure)
        rr, cc = disk_draw((y0, x0), radius, shape=rois.shape)
        rois[rr, cc] = 2 * i + 1

        # ── Companion-point search via annulus template ──
        cand_y = y0 + annulus_dy
        cand_x = x0 + annulus_dx
        in_bounds = (cand_y >= 0) & (cand_y < H) & (cand_x >= 0) & (cand_x < W)
        cand_y, cand_x = cand_y[in_bounds], cand_x[in_bounds]

        # Check mask proximity + ROI avoidance at candidate points only
        ok = (val_mask_proximity[cand_y, cand_x] &
              (edt_rois_sq[cand_y, cand_x] > exclusion_sq))
        cand_y, cand_x = cand_y[ok], cand_x[ok]

        if len(cand_y) > 0:
            idx_min = np.argmin(img[cand_y, cand_x])
            y1, x1 = int(cand_y[idx_min]), int(cand_x[idx_min])

            # Place companion disk
            rr2, cc2 = disk_draw((y1, x1), radius, shape=rois.shape)
            rois[rr2, cc2] = 2 * i + 2

            # ── Update incremental distance field (localized) ──
            for yc, xc in [(y0, x0), (y1, x1)]:
                y_lo, y_hi = max(0, yc - r_excl), min(H, yc + r_excl + 1)
                x_lo, x_hi = max(0, xc - r_excl), min(W, xc + r_excl + 1)
                sub_y = np.arange(y_lo, y_hi, dtype=np.float32)[:, None]
                sub_x = np.arange(x_lo, x_hi, dtype=np.float32)[None, :]
                dist_sq_sub = (sub_y - yc) ** 2 + (sub_x - xc) ** 2
                np.minimum(edt_rois_sq[y_lo:y_hi, x_lo:x_hi],
                           dist_sq_sub,
                           out=edt_rois_sq[y_lo:y_hi, x_lo:x_hi])

            # ── Invalidate band candidates near new ROIs ──
            for yc, xc in [(y0, x0), (y1, x1)]:
                vy = band_y[band_valid]
                vx = band_x[band_valid]
                close = (vy - yc) ** 2 + (vx - xc) ** 2 <= exclusion_sq
                valid_positions = np.flatnonzero(band_valid)
                band_valid[valid_positions[close]] = False

            i += 1
            print(i, "/", number)
            n = 0
        else:
            # No valid companion — undo first disk and retry
            rois[rr, cc] = 0

    return rois

