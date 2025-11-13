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
#   Authored by:    Laura Murgatroyd (UKRI-STFC)


from data_io.alum_cyl_file_paths import *
from cil.processors import Slicer

from cil.io import TIFFStackReader

from data_io.alum_cyl_io import read_and_write_data, read_raw_data, read_flat_data, read_dark_data, read_angles
from data_io.utils import _read_summed_data
import unittest
import os
import csv

import numpy as np


class Test_read_raw_data(unittest.TestCase):

    def setUp(self):
        self.time_lengths = [3.75, 7.5, 11.25, 15, 18.75, 22.5, 26.25, 30, 33.75, 37.5, 41.25, 45, 48.75, 52.5, 56.25, 60.0] 


    def test_read_raw_data(self):
        for time_length in self.time_lengths:
            data = read_raw_data(time_length)
            self.assertEqual(data.shape, (840,620,1550))
        # Special case for 3.75b
        data = read_raw_data(3.75, variant='b')
        print("Data for 3.75 b read successfully")

    def read_flat_data(self):
        for time_length in self.time_lengths:
            data_b, data_a = read_flat_data(time_length)
            print(f"Data for {time_length} read successfully with shape {data_b.shape}, {data_a.shape}")
            self.assertEqual(data_b.shape[1:], (620,1550))
            self.assertEqual(data_a.shape[1:], (620,1550))

    def test_read_raw_data_angle_roi(self):
        time_length = 3.75
        roi = {'angle': (None, None, 2)}
        data = read_raw_data(time_length, roi=roi)
        self.assertEqual(data.shape, (420,620,1550))
        full_data = read_raw_data(time_length)
        sliced_data = Slicer(roi=roi)(full_data)
        self.assertEqual(data, sliced_data)

class Test_read_flat_and_dark_data(unittest.TestCase):

    def setUp(self):
        self.time_lengths = [3.75, 7.5, 11.25, 15, 18.75, 22.5, 26.25, 30, 33.75, 37.5, 41.25, 45, 48.75, 52.5, 56.25, 60.0] 

    def test_read_flat_data_shape(self):
        for time_length in self.time_lengths:
            flat_before, flat_after = read_flat_data(time_length)
            self.assertEqual(flat_before.shape, (10,620,1550))
            self.assertEqual(flat_after.shape, (10,620,1550))

    def test_read_dark_data_shape(self):
        for time_length in self.time_lengths:
            dark_before, dark_after = read_dark_data(time_length)
            self.assertEqual(dark_before.shape, (10,620,1550))
            self.assertEqual(dark_after.shape, (10,620,1550))

class Test_read_angles(unittest.TestCase):

    def setUp(self):
        self.exposure_times = [3.75, 7.5, 15, 30]
        self.summed_times = [11.25, 18.75, 22.5, 26.25, 33.75, 37.5, 41.25, 45, 48.75, 52.5, 56.25, 60.0] 

    def test_read_angles(self):
        for time_length in self.exposure_times:
            angles = read_angles(time_length)
            self.assertEqual(len(angles), 840)
        
        for time_length in self.summed_times:
            with self.assertWarns(UserWarning):
                angles = read_angles(time_length)
                self.assertEqual(len(angles), 840)
        
        angles = read_angles()
        self.assertEqual(len(angles), 840)

    def test_read_angles_roi(self):
        roi = {'angle': (None, None, 2)}
        for time_length in self.exposure_times:
            angles = read_angles(time_length, roi=roi)
            self.assertEqual(len(angles), 420)
        roi = {'angle': (None, None, 4)}
        for time_length in self.summed_times:
            with self.assertWarns(UserWarning):
                angles = read_angles(time_length, roi=roi)
                self.assertEqual(len(angles), 210)
        
        angles = read_angles(roi=roi)
        self.assertEqual(len(angles), 210)

class TestWriteData(unittest.TestCase):

    def setUp(self):
        self.file_path = "./test_output"

    def test_read_and_write_combo_data(self):

        exposure_time = 11.25
        read_and_write_data(exposure_time, self.file_path)


    def test_read_and_write_roi_data(self):
        file_path = "./test_output"
        exposure_time = 3.75
        roi = {'angle': (None, None, 8)}
        read_and_write_data(exposure_time, file_path, roi=roi)


    def _read_and_check_data(self, exposure_time, roi):
        generated_raw_data = TIFFStackReader(os.path.join(self.file_path, f'projections_{exposure_time}')).read()
        generated_flat_before = TIFFStackReader(os.path.join(self.file_path, f'flats_before_{exposure_time}')).read()
        generated_flat_after = TIFFStackReader(os.path.join(self.file_path, f'flats_after_{exposure_time}')).read()
        generated_dark_before = TIFFStackReader(os.path.join(self.file_path, f'darks_before_{exposure_time}')).read()
        generated_dark_after = TIFFStackReader(os.path.join(self.file_path, f'darks_after_{exposure_time}')).read()
        angles_file = os.path.join(self.file_path, f'angles_{exposure_time}.csv')
        with open(angles_file, 'r') as f:
            reader = csv.reader(f)
            angles = list(reader)
            angles = [float(item) for item in angles]
        generated_angles = angles
        expected_data = read_raw_data(exposure_time, roi=roi)
        expected_flat_before, expected_flat_after = read_flat_data(exposure_time)
        expected_dark_before, expected_dark_after = read_dark_data(exposure_time)
        expected_angles = read_angles(exposure_time, roi=roi)
        self.assertEqual(generated_raw_data.shape, expected_data.shape)
        self.assertEqual(generated_raw_data.shape, expected_data.shape)
        self.assertEqual(generated_flat_before.shape, expected_flat_before.shape)
        self.assertEqual(generated_flat_after.shape, expected_flat_after.shape)
        self.assertEqual(generated_dark_before.shape, expected_dark_before.shape)
        self.assertEqual(generated_dark_after.shape, expected_dark_after.shape)
        self.assertEqual(len(generated_angles), len(expected_angles))

        # assert data values are the same
        np.testing.assert_allclose(generated_raw_data, expected_data)
        np.testing.assert_allclose(generated_flat_before, expected_flat_before)
        np.testing.assert_allclose(generated_flat_after, expected_flat_after)
        np.testing.assert_allclose(generated_dark_before, expected_dark_before)
        np.testing.assert_allclose(generated_dark_after, expected_dark_after)
        self.assertTrue((generated_angles == expected_angles).all())

    def tearDown(self):
        import shutil
        if os.path.exists(self.file_path):
            shutil.rmtree(self.file_path)


        

if __name__ == '__main__':
    unittest.main()
    #read_and_write_data('1min', r"C:\Users\lhe97136\Work\Data\Cropped\angle")  # Example usage

