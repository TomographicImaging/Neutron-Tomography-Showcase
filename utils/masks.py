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

def create_circular_mask(id, center, radius, in_place=True):

        ig = id.geometry
        # grid
        y_range = (ig.voxel_num_y-1)/2
        x_range = (ig.voxel_num_x-1)/2

        Y, X = np.ogrid[-y_range:y_range+1,-x_range:x_range+1]

        # center is given in pixels as (row, col). X and Y are offsets from the image centre,
        # so shift to pixel indices, then scale by voxel size to account for aspect ratio of pixels
        dist_from_center = np.sqrt(((X + x_range - center[1])*ig.voxel_size_x)**2 + ((Y + y_range - center[0])*ig.voxel_size_y)**2)

        size_x = ig.voxel_num_x * ig.voxel_size_x
        size_y = ig.voxel_num_y * ig.voxel_size_y

        if size_x > size_y:
            radius_applied =radius * size_x/2
        else:
            radius_applied =radius * size_y/2

        # approximate the voxel as a circle and get the radius
        # ie voxel area = 1, circle of area=1 has r = 0.56
        r=((ig.voxel_size_x * ig.voxel_size_y )/np.pi)**(1/2)

        # we have the voxel centre distance to mask. voxels with distance greater than |r| are fully inside or outside.
        # values on the border region between -r and r are preserved
        mask =(radius_applied-dist_from_center).clip(-r,r)

        #  rescale to -pi/2->+pi/2
        mask *= (0.5*np.pi)/r

        # the sin of the linear distance gives us an approximation of area of the circle to include in the mask
        np.sin(mask, out = mask)

        # rescale the data 0 - 1
        mask = 0.5 + mask * 0.5

        # reorder dataset so 'horizontal_y' and 'horizontal_x' are the final dimensions
        labels_orig = id.dimension_labels
        labels = list(labels_orig)

        labels.remove('horizontal_y')
        labels.remove('horizontal_x')
        labels.append('horizontal_y')
        labels.append('horizontal_x')


        if in_place == True:
            id.reorder(labels)
            np.multiply(id.array, mask, out=id.array)
            id.reorder(labels_orig)

        else:
            image_data_out = id.copy()
            image_data_out.reorder(labels)
            np.multiply(image_data_out.array, mask, out=image_data_out.array)
            image_data_out.reorder(labels_orig)

            return image_data_out

