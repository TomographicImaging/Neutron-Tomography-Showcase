from cil.optimisation.functions import L2NormSquared
import numpy as np
from cil.optimisation.functions import L2NormSquared
def calculate_L2Norm_error(ground_truth, rec, apply_mask=True):
    """Compute normalized L2 error between ground truth and reconstruction."""
    # need a circle mask of the same size as the images to compute the error only within the region of interest
    if apply_mask:
        mask = np.zeros_like(ground_truth.as_array(), dtype=bool)
        center = (mask.shape[0] // 2, mask.shape[1] // 2)
        radius = min(center)
        Y, X = np.ogrid[:mask.shape[0], :mask.shape[1]]
        dist_from_center = np.sqrt((X - center[1])**2 + (Y - center[0])**2)
        mask[dist_from_center <= radius] = True
        rec_masked = rec.as_array()*mask
        gt_masked = ground_truth.as_array()*mask
        ground_truth = ground_truth.copy()
        ground_truth.array = gt_masked
        rec = rec.copy()
        rec.array = rec_masked
    return np.sqrt(L2NormSquared(b=ground_truth)(rec) / L2NormSquared()(ground_truth))

def calculate_snr(data, mask=None):
    if mask is not None:
        data_array = data.as_array()[mask]
    else:
        data_array = data.as_array()
    mean_roi = np.mean(data_array)
    std_roi = np.std(data_array)
    snr = mean_roi / std_roi
    return snr

def calculate_cnr(data, background_data=None, roi_mask=None, background_mask=None):
    if roi_mask is not None:
        roi_data = data.as_array()[roi_mask]
    else:
        roi_data = data.as_array()
    if background_mask is not None:
        background_data = data.as_array()[background_mask]
    elif background_data is not None:
        background_data = background_data.as_array()
    else:
        raise ValueError("Either background_data or background_mask must be provided.")
    mean_roi = np.mean(roi_data)
    mean_bkg = np.mean(background_data)
    std_bkg = np.std(background_data)
    cnr = (mean_roi - mean_bkg) / std_bkg
    return cnr
