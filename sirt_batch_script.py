from cil.utilities.display import show2D
import numpy as np
import matplotlib.pyplot as plt
import os
from cil.utilities.display import show1D
from data_io.io import read_mantid_imaging_data
from cil.utilities.jupyter import islicer, link_islicer
from cil.plugins.astra import FBP as FBP_ASTRA
from cil.processors import Slicer 
from cil.framework import DataContainer
from cil.optimisation.algorithms import SIRT
from cil.plugins.astra import ProjectionOperator
from cil.optimisation.functions import IndicatorBox
import numpy as np
from cil.io import TIFFWriter
base_path = "/home/lhe97136/Data/Lego GR Investigation/"

angle_file = os.path.join(base_path, "GR scan", "all_angles.csv")
gr_full = read_mantid_imaging_data(os.path.join(base_path, "GR scan", "Golden_Full_Normalised", "Proj"), 100*10**-4, angle_file)

angle_file = r"/mnt/share/IMAT_share/CMOS_LegoScan_EquiDis_PH60/IMAT00021865_CMOS_LegoScan_EquiDis_PH60Tomo_log.csv"
equi_full = read_mantid_imaging_data(os.path.join(base_path, "Equidistant", "Full Preprocessed Normed"), 100*10**-4, angle_file)

cor= equi_full.geometry.get_centre_of_rotation()['offset'][0]
equi_full.geometry.set_centre_of_rotation(cor)

cor = gr_full.geometry.get_centre_of_rotation()['offset'][0]
gr_full.geometry.set_centre_of_rotation(cor)

gr_slices = [Slicer(roi={'angle':(0,457/4), 'vertical':(317,318)})(gr_full),
             Slicer(roi={'angle':(0,457/2), 'vertical':(317,318)})(gr_full),
             Slicer(roi={'angle':(0,3*457/4), 'vertical':(317,318)})(gr_full),
             Slicer(roi={'angle':(0,int(np.floor(0.8*457))), 'vertical':(317,318)})(gr_full),
             Slicer(roi={'angle':(0,int(np.floor(0.9*457))), 'vertical':(317,318)})(gr_full)]
gr_scales=[0.25, 0.5,0.75, 0.8, 0.9]

# gr_slices = [Slicer(roi={'angle':(0,3*457/4), 'vertical':(317,318)})(gr_full)]
# gr_scales=[0.75]
sirt_nn_algos = []
initials = []
sirt_algos = []

i=0
for gr_slice in gr_slices:
    A = ProjectionOperator(gr_slice.geometry.get_ImageGeometry(), gr_slice.geometry)

    ig = gr_slice.geometry.get_ImageGeometry()
    initials.append(ig.allocate(0))
    constraint = IndicatorBox(lower=0)

    sirt_nn = SIRT(initial=initials[i], operator=A, data=gr_slice, constraint=constraint)
    sirt_nn.update_objective_interval = 10
    sirt_nn_algos.append(sirt_nn)
    i+=1
    initials.append(ig.allocate(0))

    sirt = SIRT(initial=initials[i], operator=A, data=gr_slice)
    sirt.update_objective_interval = 10
    sirt_algos.append(sirt)


# 
sirt_nn_results = {g: [] for g in gr_scales}
sirt_results = {g: [] for g in gr_scales}
sirt_objectives = {}
sirt_iterations = {}
sirt_nn_iterations = {}
# iteration_nums = [20,80,300,400, 1200] #20,80,300,400, 1200

# for i in range(0,50):
#     iteration_nums.append(1000)
# want 1D list of 400 ones
iteration_nums = [1]*1000

# each dataset should be a tiff file
base_path = "/home/lhe97136/CIL-IMAT-Correct/IMAT-Demos/batch_outputs"

total_iteration_nums = np.cumsum(iteration_nums)

zipped = zip(sirt_nn_algos, sirt_algos)

for i in range(len(sirt_algos)):
    sirt = sirt_algos[i]
    sirt_nn = sirt_nn_algos[i]
    gr_scale = gr_scales[i]
    for x in iteration_nums: #20,80,300,400, 1200
        sirt_nn.run(x)
        sirt.run(x)
        sirt_nn_results[gr_scale].append(sirt_nn.solution.copy())
        sirt_results[gr_scale].append(sirt.solution.copy())
    sirt_nn_objective = sirt_nn.objective.copy()
    sirt_objective = sirt.objective.copy()
    sirt_iterations = sirt.iterations.copy()
    sirt_nn_iterations = sirt_nn.iterations.copy()

        # make directory for this gr scale if it doesn't exist
    gr_scale_dir = os.path.join(base_path, f'gr_scale_{gr_scale}')
    if not os.path.exists(gr_scale_dir):
        os.makedirs(gr_scale_dir)
    print("Directory: ", gr_scale_dir)
    sirt_nn_result = sirt_nn_results[gr_scale]
    sirt_result = sirt_results[gr_scale]

    # make subdirs for sirt and sirt_nn if they don't exist
    sirt_dir = os.path.join(gr_scale_dir, 'sirt')
    sirt_nn_dir = os.path.join(gr_scale_dir, 'sirt_nn')
    if not os.path.exists(sirt_dir):
        os.makedirs(sirt_dir)
    if not os.path.exists(sirt_nn_dir):
        os.makedirs(sirt_nn_dir)

    for j, total_iter in enumerate(total_iteration_nums):
        sirt_nn = sirt_nn_result[j]
        sirt = sirt_result[j]

        writer = TIFFWriter(sirt_nn, file_name = os.path.join(sirt_nn_dir, f'sirt_nn_result_{gr_scale}_{total_iter}_iters.tiff'))
        writer.write()
        writer = TIFFWriter(sirt, file_name = os.path.join(sirt_dir, f'sirt_result_{gr_scale}_{total_iter}_iters.tiff'))
        writer.write()

    # Save the objectives and iterations as numpy files
    np.save(os.path.join(gr_scale_dir, f'sirt_nn_objective_{gr_scale}.npy'), sirt_nn_objective)
    np.save(os.path.join(gr_scale_dir, f'sirt_objective_{gr_scale}.npy'), sirt_objective)
    np.save(os.path.join(gr_scale_dir, f'sirt_iterations_{gr_scale}.npy'), sirt_iterations)
    np.save(os.path.join(gr_scale_dir, f'sirt_nn_iterations_{gr_scale}.npy'), sirt_nn_iterations)




