#  Copyright 2025 United Kingdom Research and Innovation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#   Authored by:    Laura Murgatroyd (UKRI-STFC)


import itertools
from cil.io import TIFFStackReader
import numpy as np


# These methods are for the aluminium cylinder dataset only:

def _read_summed_data(exposure_time, path_dict,  roi=None, variant='a'):
    """
    Parameters
    ----------
    - data_label (str): The label signifying the exposure time.
      `3.75, 7.5, 11.25, 15, 18.75, 22.5, 26.25, 30, 33.75, 37.5, 41.25, 45, 48.75, 52.5, 56.25, 60.0
    - path_dict (dict): A dictionary mapping data labels to file paths. Expected keys in dict are:
      {'3.75', '3.75_b', '7.5', '15', '30'}
    - roi (tuple): A CIL ROI dict

    Returns
    -------
    - result (numpy.ndarray): The summed data for the given data_label.

    """
    if roi is not None:
        roi_for_tiff = {}
        # Convert each axis name to axis label expected by TIFF reader
        if 'angle' in roi:
            roi_for_tiff.update({'axis_0': roi['angle']})
        if 'horizontal' in roi:
            roi_for_tiff.update({'axis_1': roi['horizontal']})
        if 'vertical' in roi:
            roi_for_tiff.update({'axis_2': roi['vertical']})
    else:
        roi_for_tiff = roi
        
    if exposure_time == 3.75:
        # Special case for 3.75s_b as it is never used in any summed data except for 1min and itself
        # This is the only path_dict key which is not a float
        if variant == 'b':
            return TIFFStackReader(file_name=path_dict['3.75_b'], roi=roi_for_tiff, mode='slice').read()

        elif variant != 'a':
            raise ValueError("Variant must be 'a' or 'b' for 3.75s exposure time")
    
    keys = _get_data_labels_to_sum_from_exp_time(float(exposure_time))

    result = None

    for key in keys:
        data_temp = TIFFStackReader(file_name = path_dict[key], roi=roi_for_tiff, mode='slice').read()
        if result is None:
            result = data_temp
        else:
            result = np.sum((result, data_temp), axis=0)

    return result


def _get_data_labels_to_sum_from_exp_time(exp_time):
    '''
    Returns the data_labels for the datasets to sum
    For example, if exp_time is 22.5, it will return ['7.5', '15'].
    Parameters
    ----------
    exp_time: float
        Must be one of: 3.75, 7.5, 11.25, 15, 18.75, 22.5, 26.25, 30, 33.75, 37.5, 41.25, 45, 48.75, 52.5, 56.25, 60.0
    '''
    all_keys = ['3.75', '7.5', '15', '30']
    all_combos = []
    for r in range(1, len(all_keys) + 1):
        all_combos.extend(itertools.combinations(all_keys, r))

    if exp_time == 60:
        keys = ['3.75', '3.75_b', '7.5', '15', '30']
    else:
        target = exp_time

        keys = next(
            (list(combo) for combo in all_combos if sum(float(x) for x in combo) == target),
                None
        )

        if keys is None:
            raise Exception(f"exposure_time {exp_time} is not valid")

    return keys
