#  Copyright 2024 - 2025 United Kingdom Research and Innovation
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
#   Authored by:    Rasmia Kulan (UKRI-STFC)
#                   Laura Murgatroyd (UKRI-STFC)

from cil.io import TIFFStackReader, TIFFWriter
from cil.framework import AcquisitionData, AcquisitionGeometry
import numpy as np
import os
#import sys
#sys.path.append('../')
from data_io.file_paths import *
import warnings

from data_io.utils import _read_summed_data


def read_raw_data(exposure_time, roi=None, variant='a'):
    """
        Reads raw experimental data based on the provided exposure_time.

        It supports both the acquired exposure times and times summed from these.

        Parameters
        ----------
        - exposure_time (float, int): The exposure time in seconds
          options include: 3.75, 7.5, 11.25, 15, 18.75, 22.5, 26.25, 30, 33.75, 37.5, 41.25, 45, 48.75, 52.5, 56.25, 60.0
          
        - roi (dict): Region of interest for the data. Default is None. Can be used to slice on the angles dimension. 
            e.g. {'angle': (start, end, step)}

        - variant (str): {'a', 'b'}
            Only applicable for 3.75 exposure time, which has two datasets: a and b.

        Returns
        -------
        - data (cil AcquisitionData): The raw experimental data. Depending on  `exposure_time`, the data may be summed from multiple acquisitions.

        Notes
        ------
        You may use the ROI to slice on the 'angles' dimension.
        The roi is defined as (start, end, step)

        For example, to get every other angle in a dataset, use:
        roi = {'angle':(None, None, 2)}
        Providing None for the start and end returns the full data range.

        Or to get all angles in the range 0 to 180:
        roi = {'angle':(0, 180, 1)}

        If an exposure time is given which is a sum of the acquired exposure times including a 3.75s exposure time scan, the 'a' variant is used.

    """

    path_dict = {
        '3.75': exp_3_75s_a_path,
        '3.75_b': exp_3_75s_b_path,
        '7.5': exp_7_5s_path,
        '15': exp_15s_path,
        '30': exp_30s_path
    }

    data = _read_summed_data(exposure_time=exposure_time, path_dict=path_dict, roi=roi, variant=variant)

    data_angles = read_angles(roi=roi)

    try:
        acquisition_geometry = AcquisitionGeometry.create_Parallel2D()\
                    .set_panel(num_pixels=data.shape[1])\
                    .set_angles(angles=data_angles)
        ac_data = AcquisitionData(data, geometry=acquisition_geometry)
            
    except:
        acquisition_geometry = AcquisitionGeometry.create_Parallel3D().set_panel(num_pixels=[data.shape[1], data.shape[2]], pixel_size = [48e-4, 48e-4]).set_angles(angles=data_angles)
        acquisition_geometry.set_labels(['angle', 'horizontal', 'vertical'])
        ac_data = AcquisitionData(data, geometry=acquisition_geometry)
        
        #This is equivalent to rotating data in Mantid Imaging
        ac_data.geometry.set_labels(['angle', 'horizontal', 'vertical'])
 

    return ac_data
 
def read_flat_data(exposure_time, roi=None):
    '''
    Returns two numpy arrays - flats before and flats after

    Parameters
    ----------
    - exposure_time (float, int): The exposure time in seconds
        options include: 3.75, 7.5, 11.25, 15, 18.75, 22.5, 26.25, 30, 33.75, 37.5, 41.25, 45, 48.75, 52.5, 56.25, 60.0
    - roi (dict): Region of interest for the data. Default is None. Can be used to slice on the angles dimension. 
        e.g. {'angle': (start, end, step)}
    Returns
    -------
    - flat_B (numpy.ndarray): The flat field data for the B acquisition.
    - flat_A (numpy.ndarray): The flat field data for the A acquisition.
    '''

    flats_map_B = {
        '3.75': exp_3_75s_flat_B_path,
        '3.75_b': exp_3_75s_flat_B_path,
        '7.5': exp_7_5s_flat_B_path,
        '15': exp_15s_flat_B_path,
        '30': exp_30s_flat_B_path,
    }

    flats_map_A = {
        '3.75': exp_3_75s_flat_A_path,
        '3.75_b': exp_3_75s_flat_A_path,
        '7.5': exp_7_5s_flat_A_path,
        '15': exp_15s_flat_A_path,
        '30': exp_30s_flat_A_path,
    }

    flat_B = _read_summed_data(exposure_time, flats_map_B, roi)
    flat_A = _read_summed_data(exposure_time, flats_map_A, roi)

    return flat_B, flat_A
        
def read_dark_data(exposure_time, roi=None):
    '''
    Returns two numpy arrays - darks before and darks after

    Parameters
    ----------
    - exposure_time (float, int): The exposure time in seconds
        options include: 3.75, 7.5, 11.25, 15, 18.75, 22.5, 26.25, 30, 33.75, 37.5, 41.25, 45, 48.75, 52.5, 56.25, 60.0
    - roi (dict): Region of interest for the data. Default is None. Can be used to slice on the angles dimension. 
        e.g. {'angle': (start, end, step)}
    Returns
    -------
    - dark_B (numpy.ndarray): The dark field data for the B acquisition.
    - dark_A (numpy.ndarray): The dark field data for the A acquisition.
    '''

    darks_map_B = {
        '3.75': exp_3_75s_dark_B_path,
        '3.75_b': exp_3_75s_dark_B_path,
        '7.5': exp_7_5s_dark_B_path,
        '15': exp_15s_dark_B_path,
        '30': exp_30s_dark_B_path,
    }

    darks_map_A = {
        '3.75': exp_3_75s_dark_A_path,
        '3.75_b': exp_3_75s_dark_A_path,
        '7.5': exp_7_5s_dark_A_path,
        '15': exp_15s_dark_A_path,
        '30': exp_30s_dark_A_path,
    }

    dark_B = _read_summed_data(exposure_time, darks_map_B, roi)
    dark_A = _read_summed_data(exposure_time, darks_map_A, roi)

    return dark_B, dark_A

def read_angles(exposure_time=7.5, roi=None, variant='a'):
    """
    Reads angle values from log file and returns them in a list.

    Parameters
    ----------
    exposure_time: float
        Time for the experiment

    roi (dict): Region of interest for the data. Default is None. Can be used to slice on the angles dimension. 
        e.g. {'angle': (start, end, step)}

    Returns
    -------
    - list: A list of angle values extracted from the log file for experiment given by exposure_time

    """

    angles_map = {
        '3.75': exp_3_75s_a_log_combined,
        '3.75_b': exp_3_75s_b_log_combined,
        '7.5': exp_7_5s_log_combined,
        '15': exp_15s_log_combined,
        '30': exp_30s_log_combined,
    }

    if str(exposure_time) not in angles_map:
        warnings.warn("Warning, angle file for {exposure_time} doesn't exist, using '7.5s' angle file. \
              This is nothing to worry about as all exposure times measured the same angles.", UserWarning)
        exposure_time = 7.5

    if exposure_time == 3.75 and variant == 'b':
        exposure_time = '3.75_b'
    else:
        exposure_time = str(exposure_time)

    # Iterate over each file path and extract angles
    file_path = angles_map[exposure_time]
    angles = []
    with open(file_path, "r") as csvfile:
        for line in csvfile:
            if "Projection" in line and "Angle:" in line:
                parts = line.split('Angle:')
                if len(parts) > 1:
                    angle_part = parts[1].split(',')[0].strip()
                    angles.append(float(angle_part))

    if roi is not None and 'angle' in roi:
        start, stop, step = roi['angle']
        angles = angles[start:stop:step]

    return angles

def read_and_write_data(exposure_time, file_path, roi=None, variant='a'):
    """
    Reads the projections, dark and flat fields corresponding to the data_label and writes them to TIFF files, plus a comma-separated angles file.

    Parameters
    ----------
    - exposure_time (float, int): The exposure time in seconds
        options include: 3.75, 7.5, 11.25, 15, 18.75, 22.5, 26.25, 30, 33.75, 37.5, 41.25, 45, 48.75, 52.5, 56.25, 60.0
    - file_path (str): The path where the TIFF files and angles file will be written.
    - roi (dict): Region of interest for the data. Default is None. Not applied to flats and darks
    - variant (str): {'a', 'b'}
        Only applicable for 3.75 exposure time, which has two datasets: a and b.
    Returns
    -------
    - None: The function writes the data to files and does not return anything.
    """
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    proj_path = os.path.join(file_path, f'projections_{exposure_time}')
    flat_before_path = os.path.join(file_path, f'flats_before_{exposure_time}')
    flat_after_path = os.path.join(file_path, f'flats_after_{exposure_time}')
    dark_before_path = os.path.join(file_path, f'darks_before_{exposure_time}')
    dark_after_path = os.path.join(file_path, f'darks_after_{exposure_time}')
    
    for p in [proj_path, flat_before_path, flat_after_path, dark_before_path, dark_after_path]:
        if not os.path.exists(p):
            os.makedirs(p)
    
    # Read the data
    data = read_raw_data(exposure_time, roi, variant)
    flat_before, flat_after = read_flat_data(exposure_time)
    dark_before, dark_after = read_dark_data(exposure_time)
    angles = read_angles(exposure_time, roi)

    # Use TIFF stack writer to write out each
    TIFFWriter(data, os.path.join(proj_path, f'proj_{exposure_time}')).write()

    print(flat_before.shape, flat_after.shape, dark_before.shape, dark_after.shape)
    print(type(flat_before), type(flat_after), type(dark_before), type(dark_after))

    # can only use TIFFWriter for AcquisitionData or ImageData so use PIL
    from PIL import Image
    def save_stack(arr, folder, prefix):
        for i in range(arr.shape[0]):
            img = Image.fromarray(arr[i])
            img.save(os.path.join(folder, f"{prefix}_{exposure_time}_{i}.tiff"), 'tiff')
    save_stack(flat_before, flat_before_path, 'flat_before')
    save_stack(flat_after, flat_after_path, 'flat_after')
    save_stack(dark_before, dark_before_path, 'dark_before')
    save_stack(dark_after, dark_after_path, 'dark_after')

    # write out the angles comma separated
    angles_file = os.path.join(file_path, f'angles_{exposure_time}.csv')

    with open(angles_file, 'w') as f:
        for angle in angles:
            f.write(f"{angle}\n")
    

    