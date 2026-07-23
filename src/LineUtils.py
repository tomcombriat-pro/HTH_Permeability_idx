import numpy as np


def moving_average(a, n):
    'numpy.cumsum, edge handling'
    assert n%2 == 1
   
    N = len(a)
    cumsum_vec = np.cumsum(np.insert(np.pad(a, (n-1, n-1), 'constant'), 0, 0))
    d = np.hstack((np.arange(n//2 + 1, n), np.ones(N-n)*n, np.arange(n, n//2, -1)))
    return (cumsum_vec[n + n//2:-n//2 + 1] - cumsum_vec[n//2:-n - n//2]) / d

def aligned_rectangle_distance_along_segment(
    p1, p2,
    image_shape,
    width,
    edge="positive",
    extra_length=0.0,
    outside_value=0,
):
    """
    Create a float32 image with a rectangle aligned with the line p1->p2.

    Inside the rectangle, each pixel's value is the distance ALONG the segment
    direction to one of the rectangle ends (which can extend beyond p1/p2).

    Parameters
    ----------
    p1, p2 : (y, x)
        Endpoints of the segment, in image coordinates.
    image_shape : (H, W)
        Shape of the output image (H, W).
    width : float
        Total width of the rectangle (perpendicular to the line), in pixels.
        Rectangle is centered around the line: v in [-width/2, +width/2].
    edge : {"positive", "negative"}
        Which end along the segment to measure distance to:
        - "positive": distance to u = +L_eff/2 (forward end, direction p1->p2)
        - "negative": distance to u = -L_eff/2 (backward end)
    extra_length : float
        Extra length added beyond the segment, on EACH side, in pixels.
        Total rectangle length is L_eff = L + 2 * extra_length.
        extra_length = 0 => rectangle exactly spans from p1 to p2.
    outside_value : float
        Value for pixels outside the rectangle.

    Returns
    -------
    img : ndarray, shape (H, W), dtype float32
        Distance image.
    """


    
    p1 = np.asarray(p1, dtype=np.float64)
    p2 = np.asarray(p2, dtype=np.float64)

    # Segment direction and length
    d = p2 - p1
    L = np.linalg.norm(d)
    if L == 0:
        raise ValueError("p1 and p2 must be different points")

    # Effective length with extension on both sides
    L_eff = L + 2.0 * extra_length

    # Local axes: u along segment, v perpendicular
    u_dir = d / L
    v_dir = np.array([-u_dir[1], u_dir[0]])

    # Rectangle center: still the segment midpoint
    center = 0.5 * (p1 + p2)

    H, W = image_shape

    # Grid of image coords: (x, y) = (col, row)
    rows = np.arange(H)
    cols = np.arange(W)
    YY, XX = np.meshgrid(rows, cols, indexing="ij")

    # Vector from center to each pixel
    rel = np.stack([XX - center[0], YY - center[1]], axis=-1)  # (H, W, 2)

    # Local coordinates (u along line, v perpendicular)
    u_coord = rel @ u_dir
    v_coord = rel @ v_dir

    half_L_eff = L_eff / 2.0
    half_W = width / 2.0

    # Inside rectangle: |u| <= L_eff/2 and |v| <= width/2
    inside = (np.abs(u_coord) <= half_L_eff) & (np.abs(v_coord) <= half_W)

    img = np.full(image_shape, outside_value, dtype=np.float32)

    if edge == "positive":
        # Distance to forward end at u = +L_eff/2
        dist = (half_L_eff - u_coord).astype(np.float32)
    elif edge == "negative":
        # Distance to backward end at u = -L_eff/2
        dist = (u_coord + half_L_eff).astype(np.float32)
    else:
        raise ValueError("edge must be 'positive' or 'negative'")

    img[inside] = dist[inside]
    return img
