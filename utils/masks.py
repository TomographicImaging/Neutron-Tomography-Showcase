import numpy as np
def create_cuboid_mask(shape, x_range, y_range):
    mask = np.zeros(shape, dtype=bool)

    x0, x1 = x_range
    y0, y1 = y_range

    x0 = max(0, x0)
    x1 = min(shape[1], x1)
    y0 = max(0, y0)
    y1 = min(shape[0], y1)

    mask[y0:y1, x0:x1] = True
    return mask


# make a circular ring mask:
def create_ring_mask(shape, center, radius, thickness):
    Y, X = np.ogrid[:shape[0], :shape[1]]
    dist_from_center = np.sqrt((X - center[1])**2 + (Y - center[0])**2)
    mask = (dist_from_center <= radius) & (dist_from_center >= radius-thickness)  # pixel thickness
    return mask

# Make mask for outside ring:
def create_outer_circular_mask(shape, center, radius):
    Y, X = np.ogrid[:shape[0], :shape[1]]
    dist_from_center = np.sqrt((X - center[1])**2 + (Y - center[0])**2)
    mask = dist_from_center > radius
    return mask
