# Loading the Data

## Generic Methods for Loading Data
[io.py](io.py) contains:

`read_mantid_imaging_data(file_path, pixel_size)`
    Reads processed data from TIFF files and a comma-separated angles file.
    Reads the centre of rotation and tilt angle from Mantid Imaging JSON file.

`read_angles_from_mi_log_file(file_path, roi=None)`
    Reads angles from a Mantid Imaging log CSV file.

## Aluminium Cylinder - Flexible Neutron Tomography Dataset

This is available on zenodo at: https://zenodo.org/records/17250237

### Update filepaths for use in the Notebooks

To be able to read the raw and pre-processed data, you will need to update the following variables in '.alum_cyl_file_paths':

processed_data_path - this must point to the pre-processed data folder downloaded from zenodo

raw_data_base_path = this must point to the raw data downloaded from zenodo (if you wish to load this)

### Methods for Reading and Writing different combinations of the raw data

There are a number of methods in [.alum_cyl_io](.alum_cyl_io) which you can use for reading different combinations of the data - see the docstrings for more info.

The following methods can be used to read the raw data, flat, dark and angle info with any exposure time that it possible to create by adding the acquired exposure times in any combination:
options include: 3.75, 7.5, 11.25, 15, 18.75, 22.5, 26.25, 30, 33.75, 37.5, 41.25, 45, 48.75, 52.5, 56.25, 60.0

Plus, the roi can be used to reduce the angles loaded.

`read_raw_data(exposure_time, roi=None, variant='a')`
 
`read_flat_data(exposure_time, roi=None)`
 
`read_dark_data(exposure_time, roi=None)`

`read_angles(exposure_time=7.5, roi=None, variant='a')`

There is also a method for both reading and writing out, this allows the creation of a custom exposure time dataset and writes out tiff files and an angle.csv file which can be used to load the data into Mantid Imaging:

`read_and_write_data(exposure_time, file_path, roi=None, variant='a')`


### Methods for reading pre-processed data
In [.alum_cyl_io](.alum_cyl_io) the `read_processed_data(exposure_time, num_angles)` will read any data that has been pre-processed in M.I which is stored within your processed_data_path, as long as it's in a subdirectory named 'exp_{exposure_time_str}_angles_{num_angles}'.
(This was created just to make it nice and simple for loading data in the notebooks!)



