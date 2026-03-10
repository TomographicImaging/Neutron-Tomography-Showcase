from cil.optimisation.functions import L2NormSquared
import numpy as np
def calculate_L2Norm_error(ground_truth, rec):
    """Compute normalized L2 error between ground truth and reconstruction."""
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
